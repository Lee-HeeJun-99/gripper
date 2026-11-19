"""Independent assembled native RigidSphere J kinematics;not accepted-state tangent."""
import argparse,json,math
from pathlib import Path
import numpy as np
from skin_load_assess import BASE,read,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);meta=json.loads((src/'summary.json').read_text());cfg=json.loads((src/'config.json').read_text())
 if meta['status']!='RUN_COMPLETED_NOT_QUALIFIED' or 'Rigid3d' not in meta.get('sphere_collision_representation','') or cfg['simulation']['friction']<=0:raise ValueError('completed free native Rigid3 sphere with declared three-row friction required')
 R=cfg['simulation']['sphere_radius_mm']*.001;groups={};zero=0
 for row in read(src/'response_rows.csv'):
  if not any('/object/' in row[k] for k in ('model0','model1')):continue
  lam=float(row['lambda_Ns']);offset=int(row['row_id'])-int(row['first_row']);key=(row['time_s'],row['model0'],row['model1'],row['constraint_path'],offset//3);groups.setdefault(key,{})[offset%3]=None if lam==0 else np.fromstring(row['object_impulse_Ns_Nms'],sep=' ')/lam
  if lam==0:zero+=1
 errors=[];normal_errors=[];eps=1e-7
 for key,rows in groups.items():
  normal=rows.get(0)
  if normal is None:continue
  n=normal[:3];normal_errors.append(max(abs(np.linalg.norm(n)-1),float(np.max(abs(normal[3:])))));r=-R*n
  for component in (1,2):
   J=rows.get(component)
   if J is None:continue
   fd=[]
   for d in range(6):
    if d<3:plus=r+np.eye(3)[d]*eps;minus=r-np.eye(3)[d]*eps
    else:
     axis=np.eye(3)[d-3];along=axis*np.dot(axis,r);plus=r*math.cos(eps)+np.cross(axis,r)*math.sin(eps)+along*(1-math.cos(eps));minus=r*math.cos(eps)-np.cross(axis,r)*math.sin(eps)+along*(1-math.cos(eps))
    fd.append(float(np.dot(J[:3],plus-minus)/(2*eps)))
   errors.append(float(np.max(abs(np.array(fd)-J))))
 maximum=max(errors) if errors else None;normal_max=max(normal_errors) if normal_errors else None;result=dict(status='PASS_ASSEMBLED_SPHERE_KINEMATICS_ONLY' if errors and max(maximum,normal_max)<=1e-7 else 'FAIL_OR_NOT_MEASURED',scope='actual J recovered from single-body row impulse/nonzero lambda;independent rigid-point FD at assembled radial sphere geometry,NOT endpoint tangent,time,energy or grasp certification',case=a.case,normal_rows_checked=len(normal_errors),tangent_rows_checked=len(errors),zero_lambda_rows_not_measured=zero,maximum_FD_component_error=maximum,maximum_normal_radial_error=normal_max,FD_epsilon=eps,mathematical_FD_gate=1e-7,relative_error_floor=None,source_sha256=sha(Path(__file__)),input_hashes={f.name:sha(f) for f in (src/'summary.json',src/'response_rows.csv',src/'config.json')});(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
