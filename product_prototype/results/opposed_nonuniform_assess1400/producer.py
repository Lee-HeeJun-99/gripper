"""Actual no-object opening kinematics and geometric cable-length inventory.
Rest-moment algebra is independent reference,not measured Native moment.
"""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
from mechanism_candidates import world
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',default=['opposed_control_mid1393','opposed_open_mid1394']);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[];hashes={}
 for case in a.cases:
  src=BASE/'results'/case;meta=json.loads((src/'summary.json').read_text());assert meta['status']=='BOUNDED_NO_OBJECT_ACTUATION_ONLY';root=ET.parse(src/'scene.scn').getroot();mesh=json.loads((src/'mesh.json').read_text());cfg=json.loads((BASE/'results/b3_railback_grasp1001298/config.json').read_text());local=np.array(mesh['local_positions_mm']);top=[(local[:,0]==s)&(local[:,2]==.1) for s in np.unique(local[:,0])];finger=root.find("Node[@name='finger0']");q0=np.fromstring(finger.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);guides=root.find("Node[@name='guides0']");frames=np.fromstring(guides.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7);film=read(src/'finger0.csv');rigid=read(src/'guide_frames0.csv');assert len(film)==len(rigid);rest=[]
  reference=world
  if (src/'config.json').exists():cfg=json.loads((src/'config.json').read_text())
  if json.loads((src/'preflight.json').read_text()).get('nonuniform_rest'):
   from contact_adaptation_profile import candidate
   reference=candidate
  def phi(q):
   points=np.array([q[m].mean(0) for m in top]);d=np.diff(points[:,[0,2]],axis=0);return np.degrees(np.unwrap(np.arctan2(-d[:,0],-d[:,1])))[-1]
  for cable in range(2):
   n=guides.find(f"Node[@name='cable{cable}']");points=np.fromstring(n.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);owners=np.fromstring(n.find('RigidMapping').get('rigidIndexPerPoint'),sep=' ',dtype=int);pull=np.fromstring(n.find('CableConstraint').get('pullPoint'),sep=' ');body=Rotation.from_quat(frames[owners,3:]).inv().apply(points-frames[owners,:3]);length=float(np.linalg.norm(np.diff(np.vstack([pull,points]),axis=0),axis=1).sum());forces=np.zeros_like(points);path=np.vstack([pull,points]);unit=np.diff(path,axis=0);unit/=np.linalg.norm(unit,axis=1)[:,None];forces-=unit;forces[:-1]+=unit[1:];moments=[]
   for station in (0,30,50,70,90):
    selected=np.array(cfg['tendon']['guide_stations'])>=station;origin=np.array(reference(cfg,[station,0,0],0))*.001;moment=np.cross(points[selected]-origin,forces[selected]).sum(0);moments.append(dict(material_station_mm=station,reference_bending_moment_y_Nm_per_N=float(moment[1])))
   rest.append(dict(body=body,owners=owners,pull=pull,length=length,moments=moments))
  history=[];errors=[];impulse_errors=[]
  for r,g in zip(film,rigid):
   assert float(r['time_s'])==float(g['time_s']);q=np.fromstring(r['q_m'],sep=' ').reshape(-1,3);fq=np.fromstring(g['rigid_q'],sep=' ').reshape(-1,7);shortening=[]
   for cable,restc in enumerate(rest):
    owners=restc['owners'];route=fq[owners,:3]+Rotation.from_quat(fq[owners,3:]).apply(restc['body']);actual=restc['length']-np.linalg.norm(np.diff(np.vstack([restc['pull'],route]),axis=0),axis=1).sum();internal=float(r[f'cable{cable}_displacement_m']);errors.append(abs(actual-internal));shortening.append(float(actual));impulse_errors.append(abs(float(r[f'cable{cable}_force_raw'])-float(r['command_Ns'])))
   history.append(dict(time_s=float(r['time_s']),tip_angle_deg=float(phi(q)),tip_angle_minus_reference_deg=float(phi(q)-phi(q0)),skin_width_mean_tip_displacement_m=(q[top[-1]].mean(0)-q0[top[-1]].mean(0)).tolist(),command_force_N=float(r['command_N']),actual_geometric_shortening_m=shortening))
  records.append(dict(case=case,endpoint=history[-1],rest_reference_tip_angle_deg=float(phi(q0)),reference_rest_moment_per_cable=[r['moments'] for r in rest],max_internal_vs_geometric_shortening_error_m=max(errors),max_force_impulse_vs_command_error_Ns=max(impulse_errors),minimum_saved_core_volume_ratio=meta['minimum_saved_core_volume_ratio'],history=history));hashes[case]={f:sha(src/f) for f in ('scene.scn','finger0.csv','guide_frames0.csv','preflight.json','summary.json')}
 d=dict(status='ACTUAL_NO_OBJECT_OPENING_INVENTORY_ONLY',records=records,input_hashes=hashes,physical_validation='NOT QUALIFIED',scope='Native accepted q/v,actualRigidMapping route reconstruction,lambda(Ns) not force(N). Reference rest unit-tension bending moments are algebra only. Opening is no-object kinematic direction,not finite-support strength/fullinterference/Holding/time or mesh validation. No prescribed Skin or objectmotion.');(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps([{k:v for k,v in r.items() if k!='history'} for r in records]))
if __name__=='__main__':main()
