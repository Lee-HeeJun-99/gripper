"""Actual translational impulse balance and rotation/contact chronology."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',default=['layer_rigid_slip1195','layer_rigid_friction1196']);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records={};files=[]
 for case in a.cases:
  src=BASE/'results'/case;file=src/'rigid.csv';mp=src/'rigid.csv.mass.json';rows=list(csv.DictReader(file.open()));mass=json.loads(mp.read_text())['elements'][0]['mass_kg'];previous=np.zeros(3);res=[];maxomega=0;minz=1.;angular0=None;rowszero=None;trace=[]
  for r in rows:
   t=float(r['time_s']);v=np.fromstring(r['rigid_v'],sep=' ');q=np.fromstring(r['rigid_q'],sep=' ');I=np.fromstring(r['object_impulse_Ns_Nms'],sep=' ')[:3];tau=t-.0002;external=np.array([.01*np.clip((tau-.01)/.002,0,1),0,-.4*np.clip(tau/.01,0,1)]);res.append(float(np.linalg.norm(1.0002*mass*v[:3]-mass*previous-.0002*external-I)));previous=v[:3];omega=float(np.linalg.norm(v[3:]));maxomega=max(maxomega,omega);minz=min(minz,q[2])
   if omega>1 and angular0 is None:angular0=t
   if t>.001 and int(r['object_J_rows'])==0 and rowszero is None:rowszero=t
   trace.append(dict(time_s=t,centre_z_m=float(q[2]),omega_rad_s=omega,contact_Fz_N=float(I[2]/.0002),solver_iterations=int(r['solver_iterations'])))
  records[case]=dict(maximum_translational_impulse_residual_Ns=max(res),maximum_angular_speed_rad_s=maxomega,first_omega_above_1rad_s=angular0,first_no_contact_J_after1ms=rowszero,minimum_centre_z_m=float(minz),final_x_m=float(np.fromstring(rows[-1]['rigid_q'],sep=' ')[0]),iteration_limit_outputs=sum(int(r['solver_iterations'])>=1000 for r in rows),qualification='Local translation impulse identity only;not contact geometry/friction/energy/grasp certification');(out/(case+'.json')).write_text(json.dumps(trace,indent=2));files.extend([file,mp])
 d=dict(status='RIGID_PHASE_DIAGNOSTIC_ONLY',records=records,physical_validation='NOT QUALIFIED',input_hashes={str(f.relative_to(BASE)):sha(f) for f in files});(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d))
if __name__=='__main__':main()
