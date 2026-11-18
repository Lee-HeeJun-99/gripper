"""Read-only instantaneous frictionless wrench cone of actual accepted rows.

This is NOT an actual twelve-wrench loading experiment or a holding capacity.
"""
import argparse,csv,json,shutil
import numpy as np
from scipy.optimize import nnls
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='20261118_three_film_hold_end1022');a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);proof=json.loads((src/'summary.json').read_text())
 if proof['status'] not in ('PASS','EXPERIMENTAL') or proof['process']['exit_code'] or proof['sofa_errors']:raise ValueError('complete actual contact data required')
 for name,digest in proof['raw_hashes'].items():
  if sha(src/name)!=digest:raise ValueError('actual raw changed')
 rows=list(csv.DictReader((src/'three.rows.csv').open()));time=max(float(r['time']) for r in rows);selected=[r for r in rows if float(r['time'])==time]
 if len(selected)!=3 or {int(r['owner_finger']) for r in selected}!={0,1,2}:raise ValueError('three actual simultaneous rows required')
 normals=np.array([[float(r[k]) for k in ('nx','ny','nz')] for r in selected]);points=np.array([[float(r[k]) for k in ('px','py','pz')] for r in selected]);states=[np.fromstring(r['stage_q'],sep=' ') for r in selected];J=np.array([np.fromstring(r['jacobian'],sep=' ')[-6:] for r in selected]);force=np.array([float(r['force']) for r in selected]);center=states[0][-6:-3]
 if not all(np.array_equal(q,states[0]) for q in states):raise ValueError('rows are not same actual stage state')
 if np.any(force<0):raise ValueError('negative physical normal force')
 pullback_error=float(np.max(abs(J[:,:3]+normals)));radial=np.cross(points-center,-normals);moment_error=float(np.max(abs(radial-J[:,3:])))
 if pullback_error>1e-12 or moment_error>1e-10 or np.max(abs(np.linalg.norm(normals,axis=1)-1))>1e-12:raise ValueError('actual normal/Jacobian/moment parity failed')
 # Nondimensional row scaling only for cone feasibility;no physical force change.
 A=J.T.copy();A[3:]/=30.;tests=[]
 for i,label in enumerate(('Fx','Fy','Fz','Tx','Ty','Tz')):
  for sign in (-1,1):
   target=np.zeros(6);target[i]=-sign;weights,residual=nnls(A,target);tests.append(dict(external_direction=('+' if sign>0 else '-')+label,unit_target='1N force or30Nmm torque for normalized direction',relative_balance_residual=float(residual),normal_coefficients=weights.tolist(),instantaneous_cone_feasible=bool(residual<1e-10)))
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');result=dict(status='PASS',scope='actual-row reconstruction and independent instantaneous frictionless wrench-cone audit;NOT grasp/holding/12-wrench dynamic PASS',case=a.case,parent_summary_sha256=sha(src/'summary.json'),binary_sha256=proof['binary_sha256'],time_s=time,force_on_body_N=(J.T@force)[:3].tolist(),moment_on_body_Nmm=(J.T@force)[3:].tolist(),applied_row_normal_forces_N=force.tolist(),body_normal_jacobian_error=pullback_error,radial_moment_error_mm=moment_error,normalized_wrench_rank=int(np.linalg.matrix_rank(A)),unilateral_wrench_tests=tests,full_spatial_force_closure=False,torque_resistance='zero ideal frictionless sphere normal torque;NOT missing/frozen Rigid3 DOFs',holding_capacity=None,actual_dynamic_12_wrench='NOT RUN',earth_weight_reference_N=.1*9.81,earth_gravity_trial='NOT RUN;actual gravity0 and Fz=-.001N',friction='OFF;no invented frictional torque');write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k!='unilateral_wrench_tests'}))
if __name__=='__main__':main()
