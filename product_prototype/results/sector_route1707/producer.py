"""Necessary pointwise outward-route/finite-guide sector compatibility.
Actual r,z/orientation held fixed. NOT a new trajectory or universal design
impossibility proof. Guide faces are finite actual meshes, not sphere proxies.
"""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha

def outward_interval(radial,height,object_local,normal_extent,wire_radius=.00025,sphere_radius=.03,buffer=.0002):
 D=(sphere_radius+wire_radius)**2-(radial-object_local[0])**2-(height-object_local[2])**2
 lower=max(0.,object_local[1]+np.sqrt(D)) if D>0 else 0.
 upper=np.sqrt(3)*radial-2*normal_extent-buffer
 return float(lower),float(upper)

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);results=[]
 for case in ('dispatch_finite_holding1586','terminal_setback_prefix1687','capillary_hold1700'):
  src=BASE/'results'/case;root=ET.parse(src/'scene.scn').getroot();cfg=json.loads((src/'config.json').read_text());obj=list(csv.DictReader((src/'object.csv').open()));centres=np.array([np.fromstring(r['rigid_q'],sep=' ')[:3] for r in obj]);records=[];purity=0.
  for i,theta in enumerate(cfg['palm']['angles_deg']):
   er=np.array([np.cos(np.deg2rad(theta)),np.sin(np.deg2rad(theta)),0]);et=np.array([-er[1],er[0],0]);parent=root.find(f"Node[@name='guides{i}']");q0=np.fromstring(parent.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7);frames=list(csv.DictReader((src/f'guide_frames{i}.csv').open()));film=list(csv.DictReader((src/f'finger{i}.csv').open()));assert [r['time_s'] for r in frames]==[r['time_s'] for r in film]==[r['time_s'] for r in obj]
   for j in range(2):
    cable=parent.find(f"Node[@name='cable{j}']")
    for k in (4,5):
     node=cable.find(f"Node[@name='eyelet{k}']");vertices=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);centre0=vertices.mean(0);owner=int(node.find('RigidMapping').get('rigidIndexPerPoint').split()[0]);side=float(np.sign(centre0@et));assert side!=0;normal=(-np.sqrt(3)*er+side*et)/2;local=Rotation.from_quat(q0[owner,3:]).inv().apply(vertices-centre0);localcentre=Rotation.from_quat(q0[owner,3:]).inv().apply(centre0-q0[owner,:3]);objectlocal=np.column_stack([centres@er,side*(centres@et),centres[:,2]])
     for n,(fr,fl) in enumerate(zip(frames,film)):
      q=np.fromstring(fr['rigid_q'],sep=' ').reshape(-1,7)[owner];rot=Rotation.from_quat(q[3:]);c=rot.apply(localcentre)+q[:3];logged=np.fromstring(fl[f'guide{j}_q_m'],sep=' ').reshape(-1,3)[k];purity=max(purity,float(abs(c-logged).max()));r=float(c@er);b=float(side*(c@et));h=float((rot.apply(local)@normal).max());lower,upper=outward_interval(r,c[2],objectlocal[n],h);records.append(dict(time_s=float(fr['time_s']),finger=i,cable=j,guide=k,radial_mm=r*1000,height_mm=c[2]*1000,actual_lateral_mm=b*1000,outward_wire_lower_bound_mm=lower*1000,finite_ring_sector_upper_bound_mm=upper*1000,interval_width_mm=(upper-lower)*1000,actual_sector_excess_mm=(b-upper)*1000))
  assert purity<=1e-12,'guide centre clock/mapping mismatch'
  hold=[r for r in records if 1.6-1e-12<=r['time_s']<=2+1e-12];bad=[r for r in records if r['interval_width_mm']<0];badhold=[r for r in hold if r['interval_width_mm']<0];results.append(dict(case=case,actual_pose_guide_point_error_m=purity,samples=len(records),hold_samples=len(hold),infeasible_outward_intervals=len(bad),hold_infeasible_outward_intervals=len(badhold),minimum_interval_width_mm=min(r['interval_width_mm'] for r in records),maximum_actual_sector_excess_mm=max(r['actual_sector_excess_mm'] for r in records),worst_interval=min(records,key=lambda r:r['interval_width_mm']),worst_actual_sector=min(records,key=lambda r:-r['actual_sector_excess_mm']),input_hashes={f:sha(src/f) for f in ['scene.scn','object.csv']+[f'guide_frames{i}.csv' for i in range(3)]+[f'finger{i}.csv' for i in range(3)]}));(out/(case+'_history.json')).write_text(json.dumps(records))
 d=dict(status='ACTUAL_POSE_NECESSARY_ROUTING_INTERVAL_INVENTORY_ONLY',results=results,scope='At ACTUAL fixed r,z/orientation, outward wire centre must clear R30+.25mm and entire finite ring must stay in own120deg sector with.1mm boundary allowance on each side (.2mm total). Exact actual ring support function,not larger spherical proxy. Negative interval disproves this SPECIFIC fixed-pose/outward-branch sector certificate; NOT every guide routing/shape/dynamic trajectory. Positive interval is only pointwise necessary,not connected wire-segment/swept/FEM feasibility. No Native rerun or candidate pose prescribed.',source_sha256=sha(Path(__file__)));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
