"""Actual saved Rigid3 guide motion,not guessed hardware angular limits."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[]
 for case in a.cases:
  src=BASE/'results'/case;summary=json.loads((src/'summary.json').read_text());fingers=[]
  for i in range(3):
   path=src/f'guide_frames{i}.csv';rows=list(csv.DictReader(path.open()));q=np.array([np.fromstring(r['rigid_q'],sep=' ').reshape(-1,7) for r in rows]);v=np.array([np.fromstring(r['rigid_v'],sep=' ').reshape(-1,6) for r in rows]);finite=bool(np.isfinite(q).all() and np.isfinite(v).all());norm_error=float(abs(np.linalg.norm(q[:,:,3:],axis=2)-1).max());before=Rotation.from_quat(q[:-1,:,3:].reshape(-1,4));after=Rotation.from_quat(q[1:,:,3:].reshape(-1,4));angles=np.linalg.norm((before.inv()*after).as_rotvec(),axis=1).reshape(len(q)-1,-1);k,j=np.unravel_index(angles.argmax(),angles.shape);fingers.append(dict(finger=i,finite=finite,maximum_quaternion_norm_error=norm_error,maximum_saved_angular_step_rad=float(angles[k,j]),angular_step_body=int(j),angular_step_time_s=float(rows[k+1]['time_s']),maximum_saved_angular_speed_rad_s=float(np.linalg.norm(v[:,:,3:],axis=2).max()),maximum_saved_translational_speed_m_s=float(np.linalg.norm(v[:,:,:3],axis=2).max()),raw_sha256=sha(path)))
  records.append(dict(case=case,duration_s=summary['duration_s'],fingers=fingers))
 d=dict(status='RIGID_GUIDE_MOTION_INVENTORY_ONLY',records=records,hardware_angular_speed_allowable=None,physical_guide_mass_inertia='NOT MEASURED',scope='Actual accepted quaternion change and stored velocity;not a causal proof,convergence or hardware limitPASS. No guide motion corrected/filtered.',source_sha256=sha(Path(__file__)));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
