"""Accepted proximal/distal projected turning decomposition,not shell strain."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[];hashes={}
 for case in ('b3_railback_grasp1001298','b3_contact_layer_union_withdraw1352'):
  src=BASE/'results'/case;local=np.array(json.loads((src/'mesh.json').read_text())['local_positions_mm']);stations=np.unique(local[:,0]);masks=[(local[:,0]==x)&(local[:,2]==.1) for x in stations];root=ET.parse(src/'scene.scn').getroot();hashes[case]={f:sha(src/f) for f in ('scene.scn','mesh.json')}
  for i,angle in enumerate((0,120,240)):
   file=src/f'finger{i}.csv';rows=list(csv.DictReader(file.open()));hashes[case][file.name]=sha(file)
   for wanted in (None,.6,1.2):
    r=None if wanted is None else next(r for r in rows if abs(float(r['time_s'])-wanted)<1e-12);q=np.fromstring(root.find(f"Node[@name='finger{i}']/MechanicalObject").get('position') if r is None else r['q_m'],sep=' ').reshape(-1,3);points=np.array([q[m].mean(axis=0) for m in masks]);radial=points[:,0]*np.cos(np.deg2rad(angle))+points[:,1]*np.sin(np.deg2rad(angle));delta=np.diff(np.column_stack([radial,points[:,2]]),axis=0);phi=np.unwrap(np.arctan2(-delta[:,0],-delta[:,1]));mid=.5*(stations[:-1]+stations[1:]);prox=phi[mid<70];dist=phi[mid>70];v=dict(case=case,finger=i,actual_time_s=None if r is None else float(r['time_s']),reference=r is None,proximal_signed_turn_deg=float(np.degrees(prox[-1]-prox[0])),distal_signed_turn_deg=float(np.degrees(dist[-1]-dist[0])),junction_turn_deg=float(np.degrees(dist[0]-prox[-1])),root_segment_angle_deg=float(np.degrees(phi[0])),tip_segment_angle_deg=float(np.degrees(phi[-1])),all_segment_angles_deg=np.degrees(phi).tolist());records.append(v)
 d=dict(status='ACTUAL_PROJECTED_SEGMENT_ROTATION_ONLY',records=records,input_hashes=hashes,scope='Width-mean Skin nodes,actual radial-Z projection at actual0.6/1.2s and Scene reference. Proximal interval midpoints<70mm,distal>70mm,junction separately. Not intrinsic curvature,strain,beam theory,unique cause or improved stiffness proof.',physical_validation='NOT QUALIFIED');(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps([r for r in records if r['finger']==0]))
if __name__=='__main__':main()
