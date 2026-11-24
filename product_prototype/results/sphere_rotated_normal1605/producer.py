"""Native saved normal angular Jacobian vs detector point/COM stage,read-only."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
def read(p):return list(csv.DictReader(p.open()))
def assess(case):
 src=BASE/'results'/case;root=ET.parse(src/'scene.scn').getroot();dt=float(root.get('dt'));gravity=np.fromstring(root.get('gravity'),sep=' ');rows=read(src/'object.csv');times=[float(r['time_s']) for r in rows];idx={t:k for k,t in enumerate(times)};q=np.array([np.fromstring(r['rigid_q'],sep=' ') for r in rows]);v=np.array([np.fromstring(r['rigid_v'],sep=' ') for r in rows]);q0=np.fromstring(root.find("Node[@name='object']/MechanicalObject").get('position'),sep=' ');previous=np.vstack([q0,q[:-1]])[:,:3];pv=np.vstack([np.zeros((1,6)),v[:-1]]);free=previous+dt*(pv[:,:3]+gravity*dt);centres={'previous_accepted':previous,'independent_free_gravity_prediction':free,'current_accepted':q[:,:3]};points={};records=[]
 for r in read(src/'detector.csv'):
  paths=(r['model0'],r['model1']);t=float(r['accepted_time_s'])
  if not 1.6-1e-12<=t<=2+1e-12 or not any('/object/'in s for s in paths) or not any('/skinCollision/'in s for s in paths):continue
  j=0 if '/object/'in paths[0] else 1;points.setdefault((t,*sorted(paths)),[]).append(np.fromstring(r[f'detected_point{j}'],sep=' '))
 for r in read(src/'response_rows.csv'):
  t=float(r['time_s']);paths=(r['model0'],r['model1']);lam=float(r['lambda_Ns']);offset=int(r['row_id'])-int(r['first_row'])
  if offset%3 or lam<=0 or (t,*sorted(paths))not in points:continue
  J=np.fromstring(r['object_impulse_Ns_Nms'],sep=' ')/lam;n=J[:3];torque=J[3:];ps=np.array(points[(t,*sorted(paths))]);k=idx[t];errors={name:np.linalg.norm(np.cross(ps-c[k],n)-torque,axis=1) for name,c in centres.items()};best={name:float(err.min()) for name,err in errors.items()};radial={name:float(np.linalg.norm(np.cross(ps-c[k],n),axis=1).min()) for name,c in centres.items()};records.append(dict(time_s=t,row_id=int(r['row_id']),actual_normal_J_angular_norm_m=float(np.linalg.norm(torque)),minimum_pointwise_lever_error_by_stage_m=best,minimum_radial_cross_by_stage_m=radial,available_pair_points=len(ps)))
 assert records
 # Installed RigidCoord += Deriv uses exp(dt*worldomega)*previousorientation.
 # Gravity-only isotropic FREE sphere has no external angular acceleration.
 # Evaluate hypothesis without replacing any actual Native state or Jacobian.
 rotation_errors=[]
 for r in read(src/'response_rows.csv'):
  t=float(r['time_s']);paths=(r['model0'],r['model1']);lam=float(r['lambda_Ns']);offset=int(r['row_id'])-int(r['first_row'])
  if offset%3 or lam<=0 or (t,*sorted(paths))not in points:continue
  J=np.fromstring(r['object_impulse_Ns_Nms'],sep=' ')/lam;k=idx[t];ps=np.array(points[(t,*sorted(paths))]);radial=ps-previous[k];dr=Rotation.from_rotvec(dt*pv[k,3:]).apply(radial);current=(Rotation.from_quat(q[k,3:])*Rotation.from_quat((q0 if k==0 else q[k-1])[3:]).inv()).apply(radial);rotation_errors.append(dict(time_s=t,row_id=int(r['row_id']),free_rotation_lever_error_m=float(np.linalg.norm(np.cross(dr,J[:3])-J[3:],axis=1).min()),current_rotation_lever_error_m=float(np.linalg.norm(np.cross(current,J[:3])-J[3:],axis=1).min())))
 return dict(case=case,actual_active_normal_rows=len(records),maximum_actual_normal_J_angular_norm_m=max(r['actual_normal_J_angular_norm_m'] for r in records),maximum_minimum_lever_error_by_stage_m={name:max(r['minimum_pointwise_lever_error_by_stage_m'][name] for r in records) for name in centres},maximum_minimum_radial_cross_by_stage_m={name:max(r['minimum_radial_cross_by_stage_m'][name] for r in records) for name in centres},maximum_free_orientation_rotated_radius_lever_error_m=max(r['free_rotation_lever_error_m'] for r in rotation_errors),maximum_current_orientation_rotated_radius_lever_error_m=max(r['current_rotation_lever_error_m'] for r in rotation_errors),records=records+rotation_errors,input_hashes={f:sha(src/f) for f in ('scene.scn','detector.csv','response_rows.csv','object.csv')})
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[assess(x) for x in ('dispatch_finite_holding1586','chamfer_eyelet_holding1594')]
 for i,r in enumerate(records):(out/f'rows{i}.json').write_text(json.dumps(r.pop('records')))
 d=dict(status='READ_ONLY_NORMAL_LEVER_STAGE_COMPARISON',records=records,scope='Every stage reported separately; minimum over actual samepair detectorpoints,not proven unique point/row bijection. Freecentre is independent gravity-only first-order prediction,NOT observed internal freePosition. No q/v modification or force correction. Agreement maylocalize stage contract,not wholephysics/time/mesh qualification.',source_sha256=sha(Path(__file__)));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
