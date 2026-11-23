"""Actual state/velocity and deformed Cable-J projections on frozen basis."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from scipy.linalg import eigh
from analyse import BASE,sha
from b3_modal_load_response import inputs,state
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);d=inputs();lam,V=eigh((d['K']+d['K'].T)/2,d['M']);samples=[];files=d['files']+[Path(__file__)]
 for case in ('b3_ode_force_candidate1176','b3_ode_force_half1179'):
  rows,t,x,v,errors=state(case,d)
  for target in (.05,.3):
   i=int(np.argmin(abs(t-target)));assert abs(t[i]-target)<1e-12;eta=V.T@d['M']@x[i];velocity=V.T@d['M']@v[i];ids=np.argsort(velocity**2)[-5:][::-1];samples.append(dict(case=case,time_s=float(t[i]),rest_chart_body_L2_error_m=errors[i],largest_velocity_modes=[dict(mode=int(j),Hz=float(np.sqrt(lam[j])/(2*np.pi)),modal_displacement=float(eta[j]),modal_velocity=float(velocity[j]),squared_modal_velocity_fraction=float(velocity[j]**2/(velocity@velocity))) for j in ids]))
  files.extend([BASE/'results'/case/'finger0.csv',BASE/'results'/case/'guide_frames0.csv'])
 src=BASE/'results/b3_ode_force_step1177';ph={r['phase']:r for r in csv.DictReader((src/'step.phases.csv').open())};lam_imp=np.fromstring(ph['accepted_end']['lambda'],sep=' ');J=np.zeros((len(lam_imp),d['N']))
 for r in csv.DictReader((src/'step.build_end.J.csv').open()):
  val=np.fromstring(r['values'],sep=' ');start=int(r['column'])*6 if r['state']=='guide' else d['ng']*6+int(r['column'])*3;J[int(r['row']),start:start+len(val)]=val
 force=(J.T@lam_imp/.0025)[d['free']];projection=V.T@force;weights=projection**2/lam;ids=np.argsort(weights)[-5:][::-1];deformed=dict(previous_time_s=float(ph['begin']['time_s']),force_impulse_time_s=float(ph['accepted_end']['time_s']),top_rest_compliance_modes=[dict(mode=int(j),Hz=float(np.sqrt(lam[j])/(2*np.pi)),generalized_force_projection=float(projection[j]),fraction=float(weights[j]/weights.sum())) for j in ids]);files.extend([src/'step.phases.csv',src/'step.build_end.J.csv']);result=dict(status='ACTUAL_STATE_DEFORMED_LOAD_PROJECTION_ONLY',true_initial_modal_q_v='zero:actual rest/zero scene,not first saved post-step output',samples=samples,deformed_Cable_load=deformed,physical_validation='NOT QUALIFIED',scope='Actual parent J-transpose lambda/dt;reference rest basis. Rotation velocity is spatial angular velocity,not exact derivative of finite SO3 log coordinates. No actual energy/work or nonlinear dominant-mode certification.',energy_work=None,input_hashes={str(f.relative_to(BASE)):sha(f) for f in files});(out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(result))
if __name__=='__main__':main()
