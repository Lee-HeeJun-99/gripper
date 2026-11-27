"""Actual finite null step: independent physical-rigid constraint rank transition.
Rank certificate applies only to explicit rigid subspace; not full KKT/strength.
"""
import sys,json,time,shutil
import numpy as np
from scipy import sparse
from baseline_registry import ROOT,REPO,ref,dump

def main():
 t=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');src=ROOT/'validation/integrated/primaryP1_finite_null_step1/summary.json';s=json.loads(src.read_text());audit=json.loads((ROOT/'validation/integrated/primaryP1_finite_null_step_audit1/summary.json').read_text());assert all(audit['checks'].values());ns=json.loads((REPO/s['source']['path']).read_text());c=np.load(REPO/s['output']['path']);n=np.load(REPO/ns['output']['path']);R=n['R'];A=sparse.load_npz(REPO/s['physical_A']['path']);p=np.load(REPO/s['problem']['path']);lo=p['lower'];eq=np.isfinite(p['upper'])&(lo==p['upper']);records=[]
 def rank(active):
  B=np.asarray(A[active]@R);w=np.linalg.svd(B,compute_uv=False);cut=max(w[0]*1e-11,1e-13);return B,w,int(sum(w>cut)),cut
 for name in ['before_x','after_x']:
  sl=A@c[name]-lo;active=np.union1d(np.flatnonzero(eq),np.flatnonzero((~eq)&(sl<=1e-10)));B,w,r,cut=rank(active);records.append(dict(state=name,active_rows=len(active),rigid_rank=r,rigid_modes=R.shape[1],nullity=R.shape[1]-r,cut=cut,smallest_singular_values=w[-5:].tolist(),active_original_rows=active.tolist()));np.savez_compressed(out/(name+'.npz'),active=active,B=B,singular_values=w)
 new=np.setdiff1d(records[1]['active_original_rows'],records[0]['active_original_rows']);active=np.asarray(records[1]['active_original_rows']);controls=[]
 for row in new:
  _,w,r,cut=rank(active[active!=row]);controls.append(dict(omitted_original_row=int(row),rigid_rank=r,nullity=R.shape[1]-r))
 checks=dict(certified_actual_step=s['accepted_linear_steps']==1,original37rigid_modes=R.shape[1]==37,initial_two_null_modes=records[0]['nullity']==2,new_blockers_identified=np.array_equal(new,[266,2183]),remaining_rigid_modes_constrained=records[1]['nullity']==0,each_new_blocker_required=all(r['nullity']>0 for r in controls));ok=all(checks.values());result=dict(status='ACTUAL_P1_NULL_STEP_RIGID_RANK_TRANSITION_VERIFIED' if ok else 'ACTUAL_P1_NULL_STEP_RIGID_RANK_TRANSITION_REJECTED',candidate=s['candidate'],source=ref(src),step_audit=ref(ROOT/'validation/integrated/primaryP1_finite_null_step_audit1/summary.json'),verifier=ref(out/'verifier.py'),checks={k:bool(v) for k,v in checks.items()},states=records,omission_controls=controls,actual_support_updates=0,accepted_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-t,limitations=['Explicit37dimensional physical-rigid subspace only. Full-P invertibility, condition number, physical cone duals/gauges and nonlinear equilibrium not proved by this rank transition.','No constraints removed in product; omission controls are rejected audit contrasts only. Original sourcefield unchanged, nullstep remains a linear seed.']);dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if ok else 2)
if __name__=='__main__':main()
