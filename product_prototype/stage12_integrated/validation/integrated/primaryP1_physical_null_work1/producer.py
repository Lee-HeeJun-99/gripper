"""Actual P1 physical-P rigid-null/affine-work compatibility audit.
No solver retry, physical constraint deletion, nonlinear update or design claim.
"""
import sys,json,time,shutil
import numpy as np
from scipy import sparse
from scipy.linalg import svd
from baseline_registry import ROOT,REPO,ref,dump

def main():
 t=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');src=ROOT/'validation/integrated/primaryP1_affine_finite_projection1/summary.json';s=json.loads(src.read_text());P=sparse.load_npz(REPO/s['physical_P']['path']);A=sparse.load_npz(REPO/s['physical_A']['path']);p=np.load(REPO/s['problem']['path']);a=np.load(REPO/s['source_field']['path']);local=json.loads((ROOT/'validation/integrated/primaryP1_local_surface2/summary.json').read_text());x=np.load(REPO/s['output']['path'])['after_x'];n=len(x);N=n-15;sl=A@x-p['lower'];eq=np.isfinite(p['upper'])&(p['lower']==p['upper']);ineq=~eq;active=np.union1d(np.flatnonzero(eq),np.flatnonzero(ineq&(sl<=1e-10)));modes=[];labels=[]
 for name in local['elastic_bodies']:
  X=a[name+'_points_mm'];o=int(a[name+'_offset']);current=X+a['u_mm'][o:o+3*len(X)].reshape(-1,3);centered=current-current.mean(axis=0)
  for j in range(6):
   v=np.zeros_like(X)
   if j<3:v[:,j]=1.
   else:v=np.cross(np.eye(3)[j-3],centered)
   z=np.zeros(n);z[o:o+3*len(X)]=v.ravel();modes.append(z);labels.append(name+'_'+str(j))
 for j in list(range(N-6,N))+[n-1]:
  z=np.zeros(n);z[j]=1.;modes.append(z);labels.append('rigid_or_gamma_'+str(j))
 R=np.column_stack(modes);R/=np.linalg.norm(R,axis=0);B=np.asarray(A[active]@R);U,w,Vh=svd(B,full_matrices=True);cut=max(w[0]*1e-11,1e-13);rank=int(sum(w>cut));Z=Vh[rank:].T;force=P@x+p['q'];work=Z.T@(R.T@force);records=[]
 for j in range(Z.shape[1]):
  v=R@Z[:,j];v/=max(float(np.max(abs(v))),1e-30);pv=P@v;av=A@v;vd=float(v@force);norm1=float(np.sum(abs(v)));records.append(dict(mode=j,physical_P_null_residual_N=float(np.max(abs(pv))),active_row_motion_mm=float(np.max(abs(av[active]))),external_affine_work_Nmm=vd,normalized_force_projection_N=abs(vd)/norm1,minimum_all_inequality_direction_mm=float(np.min(av[ineq])),global_feasible_recession=bool(np.min(av[ineq])>=-1e-10 and np.max(abs(av[eq]))<1e-10),physical_tension_mode_max=float(np.max(abs(v[N:N+14])))));np.savez_compressed(out/f'mode{j}.npz',v=v,Pv=pv,Av=av,physical_force=force)
 wrong=P@R;rr=np.asarray(A[active]@R);np.savez_compressed(out/'rigid_analysis.npz',R=R,active=active,restricted_constraint=rr,singular_values=w,Z=Z,force=force,rigid_P_action=wrong)
 result=dict(status='ACTUAL_P1_PHYSICAL_RIGID_NULL_AFFINE_WORK_DIAGNOSTIC',candidate=s['candidate'],source=ref(src),source_field=s['source_field'],physical_P=s['physical_P'],physical_A=s['physical_A'],problem=s['problem'],producer=ref(out/'producer.py'),output=ref(out/'rigid_analysis.npz'),mode_labels=labels,rigid_modes=len(labels),active_rows=len(active),active_rigid_rank=rank,unconstrained_rigid_modes=Z.shape[1],rank_cut=cut,maximum_P_rigid_action_N=float(np.max(abs(wrong))),null_modes=records,actual_support_updates=0,accepted_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-t,limitations=['Diagnostic numeric null candidates require measured original P/A residuals; singular values alone are not a physical equivalence proof. Active equality-null is not full inequality-cone recession.','Nonzero affine work on a retained physical null direction can obstruct equality Newton. This does not prove no coupled nonlinear equilibrium, no full-system impossible design, and does not authorize springs/fixation/row deletion/Base cancellation.']);dump(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
