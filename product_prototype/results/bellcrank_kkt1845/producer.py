"""Read-only initial KKT split: actual multipliers vs exact Schur reference."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
def read(p):return list(csv.DictReader(p.open()))
def skew(x):return np.array([[0,-x[2],x[1]],[x[2],0,-x[0]],[-x[1],x[0],0]])
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/bellcrank_joint1844';summary=json.loads((src/'summary.json').read_text());m=summary['body_mass_kg'];I={k:np.array(v) for k,v in summary['body_inertia_kg_m2'].items()};M=np.zeros((8,8));M[0,0]=I['rotor'][2,2];M[1:4,1:4]=m['rod']*np.eye(3);M[4:7,4:7]=I['rod'];M[7,7]=m['slider'];inv=np.linalg.inv(M)
 H=np.zeros((6,8));H[:3,0]=[0,.01,0];H[:3,1:4]=np.eye(3);H[:3,4:7]=-skew([0,-.015,0]);H[3:,1:4]=-np.eye(3);H[3:,4:7]=skew([0,.015,0]);H[3:,7]=[0,1,0];J=np.zeros(8);J[0]=-.01;f=np.zeros(8);f[7]=-5e-5;dt=.001;results=[]
 for name,omega in [('initial_mass',0.),('finite_velocity',-.2)]:
  folder=src/name;v0=np.array([omega,0,-.01*omega,0,0,0,0,-.01*omega]);lam=np.fromstring(read(folder/'constraints.csv')[0]['impulses_Ns'],sep=' ');assert len(lam)==7;free=v0+dt*inv@f;unconstrained=free+inv@J*lam[6];W=H@inv@H.T;exact_mu=np.linalg.solve(W,-H@unconstrained);exact_v=unconstrained+inv@H.T@exact_mu;actual_mu_v=unconstrained+inv@H.T@lam[:6]
  rigid={k:read(folder/f'{k}.csv')[0] for k in ('lever','rod','slider')};actual=np.r_[np.fromstring(rigid['lever']['rigid_v'],sep=' ')[5],np.fromstring(rigid['rod']['rigid_v'],sep=' '),np.fromstring(rigid['slider']['rigid_v'],sep=' ')[1]]
  impulse_balance_error=float(abs(actual-actual_mu_v).max());exact_error=float(abs(actual-exact_v).max());assert impulse_balance_error<=1e-12
  angle=Rotation.from_quat(np.fromstring(rigid['lever']['rigid_q'],sep=' ')[3:]).as_rotvec()[2];lever_end=np.fromstring(read(folder/'lever_ends.csv')[0]['q'],sep=' ').reshape(-1,3)[1];rod_end=np.fromstring(read(folder/'rod_ends.csv')[0]['q'],sep=' ').reshape(-1,3)[0];closure_x=float(lever_end[0]-rod_end[0]);curved_minus_frozen_x=.01*2*np.sin(angle/2)**2
  results.append(dict(case=name,actual_velocity_from_actual_multipliers_error=impulse_balance_error,actual_velocity_vs_exact_KKT_error=exact_error,actual_joint_velocity_residual=float(abs(H@actual).max()),exact_KKT_joint_velocity_residual=float(abs(H@exact_v).max()),actual_joint_impulses_Ns=lam[:6].tolist(),exact_initial_KKT_joint_impulses_Ns=exact_mu.tolist(),actual_input_rod_force_N=(lam[:3]/dt).tolist(),actual_rod_on_slider_force_N=(lam[3:6]/dt).tolist(),measured_first_closure_x_m=closure_x,curved_minus_frozen_rotation_x_m=float(curved_minus_frozen_x),closure_x_geometric_prediction_error_m=abs(closure_x-curved_minus_frozen_x),actual_solver_report=read(folder/'constraints.csv')[0],input_sha256={f:sha(folder/f) for f in ('constraints.csv','lever.csv','rod.csv','slider.csv','lever_ends.csv','rod_ends.csv')}))
 d=dict(status='PASS_INITIAL_KKT_DIAGNOSIS_ONLY',results=results,M_kg_mixed_units=M.tolist(),H_joint_rows=H.tolist(),source_sha256=sha(Path(__file__)),scope='Actual initial8DOF ideal-pin reference. Actual multipliers reproduce Native response; exact KKT difference isolates iterative termination, NOT a mass-law correction or permitted gate relaxation. Curved-vs-frozen rotation explains initial position residual without modifying coordinates. Original1844FAIL remains; this does not validate full trajectory, pin mass, finite joint/contact, global energy, time convergence, Finger or grasp.')
 (out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({**d,'M_kg_mixed_units':'stored in summary','H_joint_rows':'stored in summary'},indent=2))
if __name__=='__main__':main()
