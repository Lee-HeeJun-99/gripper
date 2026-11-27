"""Independent all-node point-work derivative audit. No producer import."""
import sys,json,shutil
import numpy as np
from scipy.spatial.transform import Rotation
from baseline_registry import ROOT,REPO,ref,sha,dump

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');assert not(ROOT/'runtime/STOP').exists();source=ROOT/'validation/integrated/primaryP1_objective_port1/summary.json';s=json.loads(source.read_text())
 for k in ('implementation','field','state','curves','port','seed','mass'):assert sha(REPO/s[k]['path'])==s[k]['SHA256']
 a=np.load(REPO/s['field']['path']);saved=np.load(REPO/s['port']['path']);st=json.loads((REPO/s['state']['path']).read_text());name='F0_ROOT_BACK';allp=a[name+'_points_mm'];off=int(a[name+'_offset']);ids=saved['root_nodes'];p=allp[ids];u=a['u_mm'][off:off+3*len(allp)].reshape(-1,3)[ids];weights=a['Root_port_weights_mm2'][ids];center=weights@p/weights.sum();dy=saved['freeY_increment_m'];Q=[st['string']['E_m'],st['tip_world_m']];F=[st['string']['Fe_N'],[st['normal_N'],0,0]]
 for k in ('moving_mass_points','fixed_mass_points'):
  for r in st[k]:Q.append(r['position_m']);F.append([0,0,-9.80665*r['mass_kg']])
 Q=np.array(Q);F=np.array(F);R=saved['root_R'];c=saved['root_center_mm'];refp=(Q-dy-c*.001)@R+center*.001
 def value(v):
  now=p+v;cc=weights@now/weights.sum();rot,_=Rotation.align_vectors(now-cc,p-center,weights=weights);new=(refp-center*.001)@rot.as_matrix().T+cc*.001+dy
  return float(np.sum(new*F))
 g=saved['root_force_N'];numeric=[]
 for i in range(len(p)):
  for j in range(3):
   d=np.zeros_like(u);d[i,j]=.001
   # 5-point derivative avoids leading central-difference truncation.
   numeric.append(1000*(-value(u+2*d)+8*value(u+d)-8*value(u-d)+value(u-2*d))/(12*.001))
 numeric=np.array(numeric).reshape(u.shape);maxerr=float(np.max(abs(numeric-g)));relative=float(np.linalg.norm(numeric-g)/np.linalg.norm(g));bad=g.copy();bad[np.argmax(np.linalg.norm(g,axis=1)),2]+=.001;corrupt=float(np.max(abs(numeric-bad)));eqForce=g.sum(0);eqMoment=np.cross((p+u)*.001,g).sum(0)+np.cross(dy,eqForce);RW=np.array(st['Root_origin_wrench_N_Nm']);err=np.r_[eqForce,eqMoment]-RW
 old=ROOT/'validation/integrated/primaryP1_finite_port1/summary.json';olddoc=json.loads(old.read_text());snapshot=ROOT/'validation/integrated/primaryP1_finite_port1/implementation.py';snapshotOK=sha(snapshot)==olddoc['implementation']['SHA256']
 checks=dict(all984_coordinate_derivatives=maxerr<1e-8,relative_derivative=relative<1e-6,corrupt_load_rejected=corrupt>1e-4,force=np.linalg.norm(err[:3])<1e-8,moment=np.linalg.norm(err[3:])<1e-10,earlier_implementation_snapshot=snapshotOK,all_source_checks=all(s['checks'].values()))
 result=dict(status='ACTUAL_P1_OBJECTIVE_ALL_NODE_INDEPENDENT_PASS' if all(checks.values()) else 'ACTUAL_P1_OBJECTIVE_ALL_NODE_INDEPENDENT_FAIL',candidate=s['candidate'],source=ref(source),verifier=ref(out/'verifier.py'),checks=checks,coordinate_derivatives=len(numeric.ravel()),point_work_evaluations=len(numeric.ravel())*4,max_derivative_error_N=maxerr,relative_derivative_error=relative,corrupt_force_error_N=corrupt,wrench_error_N_Nm=err.tolist(),earlier_source=ref(old),earlier_implementation_snapshot=ref(snapshot),snapshot_note='Earlier summary original path hash was superseded by appending objective implementation. Exact old module bytes preserved at this snapshot; original result and producer untouched.',newly_qualified_system_gate_ids=[],whole_system_release=False,scope='Actual78partP1 saved support face/new upstream227points/984coordinate derivatives. Does not solve support equilibrium or validate strength/mesh/time/full3D/globalenergy.')
 dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
