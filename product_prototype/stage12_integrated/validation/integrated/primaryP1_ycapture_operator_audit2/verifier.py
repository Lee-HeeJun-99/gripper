"""Independent determinant/complex-step audit, no contact implementation import."""
import sys,json,shutil
import numpy as np
from scipy.spatial.transform import Rotation
from baseline_registry import ROOT,REPO,ref,sha,dump

def scalar(X,orientation):
 q,a,b,c=X.reshape(4,3);e=b-a;f=c-a;v=np.cross(e,f);return orientation*np.linalg.det(np.array([e,f,q-a]))/np.sqrt(v@v)

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');src=ROOT/'validation/integrated'/sys.argv[2]/'summary.json';s=json.loads(src.read_text());rows=json.loads((REPO/s['contact_rows']['path']).read_text());mesh=np.load(REPO/s['mesh']['path']);tests=[];R=Rotation.from_rotvec([.03,-.02,.01]).as_matrix();t=np.array([12.,-3,7]);rng=np.random.default_rng(252)
 for row in rows:
  X=np.vstack([row['root_point_mm'],row['owner_triangle_mm']]);orientation=row['normal_sign'];reference=float(scalar(X,orientation));eps=1e-25;grad=np.zeros(12)
  for j in range(12):
   z=X.astype(complex).ravel();z[j]+=1j*eps;grad[j]=scalar(z.reshape(4,3),orientation).imag/eps
  grad=grad.reshape(4,3);d=rng.normal(size=(4,3))*.01;h=1e-4;fd=(scalar(X+h*d,orientation)-scalar(X-h*d,orientation))/(2*h);work=abs(fd-np.sum(grad*d));objective=abs(scalar(X@R.T+t,orientation)-reference);force=np.linalg.norm(grad.sum(0));moment=np.linalg.norm(np.cross(X,grad).sum(0));# Orientation reversal flips gap and gradient; omitting owner derivative gives spurious rigid work.
  reversed_error=abs(scalar(X,-orientation)+reference);bad_point_only_force=np.linalg.norm(grad[0]);g_y=grad[0,1];penetration=scalar(X+np.array([[0,row['sign']*.101,0],[0,0,0],[0,0,0],[0,0,0]]),orientation)
  tests.append(dict(complex_step_work_error=float(work),objective_error_mm=float(objective),force_error_N=float(force),moment_error_Nmm=float(moment),reversed_sign_error=float(reversed_error),point_only_control_force_error_N=float(bad_point_only_force),point_gradient_Y=float(g_y),penetrated_gap_mm=float(penetration),nominal_gap_mm=reference))
 checks=dict(source_hashes=all(sha(REPO/s[k]['path'])==s[k]['SHA256'] for k in ['candidate','mesh','contact_rows']),allrows=bool(tests),work_allrows=all(v['complex_step_work_error']<1e-8 for v in tests),finite_rigid_objectivity=all(v['objective_error_mm']<1e-10 for v in tests),action_reaction_allrows=all(v['force_error_N']<1e-10 and v['moment_error_Nmm']<1e-8 for v in tests),point1_nominal=all(abs(v['nominal_gap_mm']-.1)<1e-10 for v in tests),point101_penetration=all(v['penetrated_gap_mm']<-.00099 for v in tests),omitted_owner_control_rejected=all(v['point_only_control_force_error_N']>.9 for v in tests),reverse_sign_control=all(v['reversed_sign_error']<1e-12 for v in tests))
 dump(out/'summary.json',dict(status='ACTUAL_P1_YCAPTURE_INDEPENDENT_OPERATOR_PASS' if all(checks.values()) else 'ACTUAL_P1_YCAPTURE_INDEPENDENT_OPERATOR_FAIL',candidate=s['candidate'],source=ref(src),checks=checks,tests=tests,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Independent current finite triangle plane determinant audit. Nominal product contact geometry; no constitutive pressure/complementarity/equilibrium or energy certificate.','Point101penetration is analytical finitegap check; wholeassembly OCP penetration is separately measured. Outside finite-owner projections must reject before this signedgap can supply a reaction.']))
 print(json.dumps(dict(checks=checks,rows=len(tests),max_work_error=max(v['complex_step_work_error'] for v in tests))));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
