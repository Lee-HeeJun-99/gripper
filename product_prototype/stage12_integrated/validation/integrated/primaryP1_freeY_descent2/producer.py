"""Actual P1 globally feasible original-row conic projected descent.
AMG is only a direction metric; physical P/q unmodified. No nonlinear update.
All active physical cone rows enter small bound LS; no signed QR cone deletion.
"""
import sys,json,time,shutil
import numpy as np
from scipy import sparse
from scipy.linalg import eigh
from scipy.optimize import lsq_linear
import pyamg
from baseline_registry import ROOT,REPO,ref,dump

def main():
 start=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');src=ROOT/'validation/integrated/primaryP1_freeY_seed1/summary.json';s=json.loads(src.read_text());assert s['phase1_feasible'];P=sparse.load_npz(REPO/s['physical_P']['path']);A=sparse.load_npz(REPO/s['physical_A']['path']);p=np.load(REPO/s['problem']['path']);a=np.load(REPO/s['source_field']['path']);q=p['q'];lo=p['lower'];hi=p['upper'];D=p['D'].copy();E=p['E'];D[-1]=1/E[2175];n=len(D);N=n-15;eq=np.isfinite(hi)&(lo==hi);ineq=~eq;ee=np.flatnonzero(eq);Ps=(sparse.diags(D)@P@sparse.diags(D)).tocsr();As=(sparse.diags(E)@A@sparse.diags(D)).tocsr();seed=np.load(REPO/s['output']['path']);x=seed['physical_x'].copy();z=x/D
 local=json.loads((ROOT/'validation/integrated/primaryP1_local_surface2/summary.json').read_text());diag=Ps.diagonal();Pr=Ps+sparse.diags(1e-6*np.maximum(diag,1.));modes=[]
 for name in local['elastic_bodies']:
  X=a[name+'_points_mm'];o=int(a[name+'_offset']);Xc=X-X.mean(axis=0)
  for j in range(6):
   v=np.zeros_like(X)
   if j<3:v[:,j]=1
   else:v=np.cross(np.eye(3)[j-3],Xc)
   zz=np.zeros(n);zz[o:o+3*len(X)]=v.ravel();modes.append(zz/D)
 for j in list(range(N-6,N))+[n-1]:zz=np.zeros(n);zz[j]=1/D[j];modes.append(zz)
 B=np.column_stack(modes);B/=np.maximum(np.linalg.norm(B,axis=0),1e-30);ml=pyamg.smoothed_aggregation_solver(Pr,B=B,symmetry='symmetric',max_levels=10,max_coarse=120,presmoother=('gauss_seidel',{'sweep':'symmetric'}),postsmoother=('gauss_seidel',{'sweep':'symmetric'}),coarse_solver='pinv');M=ml.aspreconditioner(cycle='V');cache={};history=[];reason='finite12direction limit';qualified=False;last=None
 def objective(xx):return float(.5*xx@(P@xx)+q@xx)
 class Budget(Exception):pass
 def budget():
  if (ROOT/'runtime/STOP').exists():raise Budget('STOP')
  if time.monotonic()-start>240:raise Budget('240s total internal direction budget')
 try:
  for k in range(12):
   budget();sl=A@x-lo;active=np.union1d(ee,np.flatnonzero(ineq&(sl<=1e-12)));Ar=As[active];grad=Ps@z+D*q;mg=M@grad
   for row in active:
    budget()
    if int(row) not in cache:cache[int(row)]=M@As.getrow(row).toarray().ravel()
   V=np.column_stack([cache[int(row)] for row in active]);S=np.asarray(Ar@V);S=.5*(S+S.T);row_scale=1/np.sqrt(np.maximum(np.diag(S),1e-30));Sn=row_scale[:,None]*S*row_scale[None,:];h=row_scale*(Ar@mg);val,U=eigh(Sn);keep=val>max(val[-1]*1e-13,1e-15);factor=np.sqrt(val[keep])[:,None]*U[:,keep].T;target=-(U[:,keep].T@h)/np.sqrt(val[keep]);rec=lsq_linear(factor,target,bounds=(np.full(len(active),-np.inf),np.where(ineq[active],0.,np.inf)),tol=1e-13,max_iter=300,lsq_solver='exact');yy=row_scale*rec.x;ys=np.zeros(A.shape[0]);ys[active]=yy;direction=-mg-V@yy;raw_dx=D*direction;ray_scale=min(1.,1e-4/max(float(np.max(abs(raw_dx))),1e-30));dx=ray_scale*raw_dx;Ad=A@dx;y=E*ys;physical_stationarity=P@x+q+A.T@y;dual=float(np.max(abs(physical_stationarity)));sign=float(np.max(np.maximum(y[ineq],0)));comp=float(np.max(abs(sl[ineq]*y[ineq])));primal=max(float(np.max(np.maximum(-sl[ineq],0))),float(np.max(abs(sl[eq]))));qualified=primal<1e-8 and dual<1e-8 and sign<1e-8 and comp<1e-8 and float(np.max(abs(y[ee])))<1e-8;gt=float((P@x+q)@dx);curv=float(dx@(P@dx));tangent_eq=float(np.max(abs(Ad[eq])));tangent_ineq=float(np.min(Ad[active[ineq[active]]])) if np.any(ineq[active]) else 0.;before=objective(x)
   # Inactive physical rows ALWAYS supply blocking limits. No search-bound reaction.
   blockers=np.flatnonzero(ineq&(Ad<-1e-16));ratios=np.maximum(sl[blockers],0)/(-Ad[blockers]);bound=float(np.min(ratios)) if len(ratios) else float('inf');blocking=int(blockers[np.argmin(ratios)]) if len(ratios) else None;optimal=-gt/curv if curv>0 and gt<0 else 1.;alpha=min(1.,optimal,bound);accepted=False;after=before;backtracks=0;new=x.copy();newsl=sl.copy()
   direction_ok=tangent_eq<1e-10 and tangent_ineq>-1e-10 and gt<0
   if qualified:reason='full original-unit linear KKT including zero gauge reactions; NOT nonlinear equilibrium'
   elif direction_ok and alpha>0:
    for bt in range(20):
     new=x+alpha*dx;newsl=A@new-lo;after=objective(new);newpr=max(float(np.max(np.maximum(-newsl[ineq],0))),float(np.max(abs(newsl[eq]))))
     if newpr<1e-10 and after<=before+1e-4*alpha*gt:accepted=True;break
     alpha*=.5;backtracks+=1
   np.savez_compressed(out/f'step{k}.npz',before_x=x,direction_physical=dx,raw_direction_physical=raw_dx,ray_scale=ray_scale,after_x=new if accepted else x,physical_dual=y,before_slack_mm=sl,after_slack_mm=newsl if accepted else sl,physical_stationarity_N=physical_stationarity,active=active,direction_cone_dual_scaled=yy,small_row_scale=row_scale,small_eigenvalues=val,small_factor=factor,small_target=target,small_dual=rec.x)
   last=out/f'step{k}.npz';row=dict(step=k,active_original_rows=active.tolist(),active_rows=len(active),small_rank=int(np.sum(keep)),small_min_eigenvalue=float(val[0]),small_lsq_status=int(rec.status),ray_scale=ray_scale,maximum_raw_direction_mm_rad=float(np.max(abs(raw_dx))),maximum_direction_mm_rad=float(np.max(abs(dx))),small_lsq_optimality=float(rec.optimality),physical_primal_mm=primal,physical_dual_N=dual,physical_sign_defect_N=sign,physical_complementarity_Nmm=comp,gauge_dual_max_N=float(np.max(abs(y[ee]))),RootY_gamma_stationarity_N=float(abs(y[2175])),physical_KKT_qualified=qualified,directional_objective_Nmm=gt,curvature_Nmm=curv,active_direction_equality_mm=tangent_eq,active_direction_min_inequality_mm=tangent_ineq,direction_qualified=bool(direction_ok),fullrow_blocking_alpha=bound if np.isfinite(bound) else None,blocking_original_row=blocking,objective_optimal_alpha=optimal,accepted_alpha=alpha,accepted_linear_step=accepted,objective_before_Nmm=before,objective_after_Nmm=after if accepted else before,backtracks=backtracks,after_physical_primal_mm=max(float(np.max(np.maximum(-(newsl if accepted else sl)[ineq],0))),float(np.max(abs((newsl if accepted else sl)[eq])))),output=ref(last),elapsed_s=time.monotonic()-start);history.append(row);dump(out/'history.json',history)
   if qualified:break
   if not accepted:reason='no certified feasible Armijo descent: direction/zero blocking/finite backtrack';break
   x=new;z=x/D
 except Budget as e:reason=str(e)
 result=dict(status='ACTUAL_P1_FREEY_FEASIBLE_DESCENT_LINEAR_KKT_PASS_NOT_EQUILIBRIUM' if qualified else 'ACTUAL_P1_FREEY_FEASIBLE_DESCENT_NOT_EQUILIBRIUM',candidate=s['candidate'],source_field=s['source_field'],source=ref(src),producer=ref(out/'producer.py'),physical_P=s['physical_P'],physical_A=s['physical_A'],problem=s['problem'],direction_scaling_gamma=D[-1],physical_regularization=0.,direction_metric_only_shift=1e-6,preconditioner_levels=len(ml.levels),preconditioner_cached_rows=len(cache),all_original_inequalities_retained=True,original_contacts=2169,original_branches=14,steps=history,history=ref(out/'history.json'),output=ref(last) if last else None,reason=reason,physical_KKT_qualified=bool(qualified),accepted_linear_steps=sum(r['accepted_linear_step'] for r in history),actual_support_updates=0,accepted_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['Original-source linear feasibility/descent only, not a nonlinear support equilibrium. All original gauges need negligible reactions; gamma unpenalized in physical P/q.','AMG shift is ONLY SPD search metric. Small dual bound LS uses every active original cone row; eigenspace truncation is numerical and all physical directional/whole-row tests decide acceptance. No QR cone replacement.','Raw search ray is normalized to maximum1e-4mm/rad before all directional/feasibility tests. Blocking uses original negative directional slack below1e-16mm; all rows are still checked on actual proposed state at1e-10mm. This is a numerical search step, not a changed gap/physical limit. Finite12directions/240s and20Armijo backtracks; every inactive row supplies blocking. No increased OSQP/MINRES budget, direct retry, new mesh, physical regularization or removed constraint.']);dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if qualified else 2)
if __name__=='__main__':main()
