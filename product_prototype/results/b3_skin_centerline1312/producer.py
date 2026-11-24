"""Accepted width-mean Skin centreline turning;NOT intrinsic shell curvature."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def metrics(p):
 d=np.diff(p,axis=0);length=np.linalg.norm(d,axis=1);assert np.all(length>0);unit=d/length[:,None];angles=np.arctan2(np.linalg.norm(np.cross(unit[:-1],unit[1:]),axis=1),(unit[:-1]*unit[1:]).sum(axis=1));curv=2*angles/(length[:-1]+length[1:]);return dict(total_unsigned_turn_deg=float(np.degrees(angles.sum())),max_discrete_centerline_curvature_per_m=float(curv.max()),root_tip_tangent_angle_deg=float(np.degrees(np.arctan2(np.linalg.norm(np.cross(unit[0],unit[-1])),np.dot(unit[0],unit[-1])))),deformed_polyline_length_m=float(length.sum()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[];hashes={}
 for name in ('b3_railback_grasp1001298','b3_railback_force_hold1306'):
  src=BASE/'results'/name;local=np.array(json.loads((src/'mesh.json').read_text())['local_positions_mm']);stations=np.unique(local[:,0]);top=local[:,2].max();masks=[(local[:,0]==s)&(local[:,2]==top) for s in stations];assert all(m.any() for m in masks);root=ET.parse(src/'scene.scn').getroot();hashes[name]={'mesh.json':sha(src/'mesh.json'),'scene.scn':sha(src/'scene.scn')}
  for finger in range(3):
   rows=list(csv.DictReader((src/f'finger{finger}.csv').open()));times=np.array([float(r['time_s']) for r in rows]);q0=np.fromstring(root.find(f"./Node[@name='finger{finger}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3)
   for wanted in (None,1.1,1.4,1.8):
    k=int(np.argmin(abs(times-wanted))) if wanted is not None else None;q=q0 if k is None else np.fromstring(rows[k]['q_m'],sep=' ').reshape(-1,3);points=np.array([q[m].mean(axis=0) for m in masks]);rec=dict(case=name,finger=finger,time_s=None if k is None else float(times[k]),state='MANUFACTURED_REFERENCE' if k is None else 'ACTUAL_ACCEPTED',**metrics(points));records.append(rec)
    with (out/f'{name}_finger{finger}_{"rest" if k is None else k}.csv').open('w') as f:w=csv.writer(f);w.writerow(['material_station_mm','mean_world_x_m','mean_world_y_m','mean_world_z_m']);w.writerows(np.column_stack([stations,points]))
   hashes[name][f'finger{finger}.csv']=sha(src/f'finger{finger}.csv')
 d=dict(status='ACTUAL_SKIN_CENTERLINE_DIAGNOSTIC_ONLY',records=records,input_hashes=hashes,scope='Top-surface nodes grouped by original material station,arithmetic width mean. Turning-angle/polyline proxy,not intrinsic FEM/shell curvature,contact coverage,pressure or Wrapping PASS. No prescribed deformation;actual q only.',physical_validation='NOT QUALIFIED');(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(dict(status=d['status'],records=len(records))))
if __name__=='__main__':main()
