"""Actual P1 bounded cone-aware linear working-set changes.
All physical inequalities always retained/checked. No nonlinear update.
"""
import sys,json,time,shutil
import numpy as np
from scipy import sparse
from scipy.linalg import qr,solve_triangular,cho_factor,cho_solve
from scipy.sparse.linalg import LinearOperator,minres
from scipy.optimize import lsq_linear
import pyamg
from baseline_registry import ROOT,REPO,ref,dump

def main():
 start=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');src=ROOT/'validation/integrated/primaryP1_matrixfree1/summary.json';s=json.loads(src.read_text());P=sparse.load_npz(REPO/s['physical_P']['path']);A=sparse.load_npz(REPO/s['physical_A']['path']);p=np.load(REPO/s['problem']['path']);a=np.load(REPO/s['source_field']['path']);q=p['q'];lo=p['lower'];hi=p['upper'];D=p['D'];E=p['E'];n=len(D);N=s['original_DOF'];eq=np.flatnonzero(np.isfinite(hi)&(lo==hi));ineq=np.ones(A.shape[0],bool);ineq[eq]=False;active=p['active'].copy();Ps=(sparse.diags(D)@P@sparse.diags(D)).tocsr();As=(sparse.diags(E)@A@sparse.diags(D)).tocsr();local=json.loads((REPO/json.loads((REPO/s['source']['path']).read_text())['source']['path']).read_text())
 diag=Ps.diagonal();Pr=Ps+sparse.diags(1e-6*np.maximum(diag,1.));modes=[]
 for name in local['elastic_bodies']:
  X=a[name+'_points_mm'];o=int(a[name+'_offset']);Xc=X-X.mean(axis=0)
  for j in range(6):
   z=np.zeros(n);v=np.zeros_like(X)
   if j<3:v[:,j]=1
   else:v=np.cross(np.eye(3)[j-3],Xc)
   z[o:o+3*len(X)]=v.ravel();modes.append(z/D)
 for j in range(N-6,N):z=np.zeros(n);z[j]=1/D[j];modes.append(z)
 Bnear=np.column_stack(modes);Bnear/=np.maximum(np.linalg.norm(Bnear,axis=0),1e-30)
 prestart=time.monotonic();ml=pyamg.smoothed_aggregation_solver(Pr,B=Bnear,symmetry='symmetric',max_levels=10,max_coarse=120,presmoother=('gauss_seidel',{'sweep':'symmetric'}),postsmoother=('gauss_seidel',{'sweep':'symmetric'}),coarse_solver='pinv');Mbody=ml.aspreconditioner(cycle='V');setup=time.monotonic()-prestart;cache={};history=[];qualified=False;previous_sets=set();last_output=None;reason='bounded working-set transition limit';budget_s=300.;maxpivots=4
 class Budget(Exception):pass
 def budget():
  if (ROOT/'runtime/STOP').exists():raise Budget('STOP')
  if time.monotonic()-start>budget_s:raise Budget('300s internal total budget')
 try:
  for pivotstep in range(maxpivots):
   budget();key=tuple(active)
   if key in previous_sets:reason='repeated working set: stop, no cycling';break
   previous_sets.add(key);dense=As[active].toarray();qq,R,piv=qr(dense.T,mode='economic',pivoting=True);dd=abs(np.diag(R));rank=int(np.sum(dd>np.finfo(float).eps*max(dense.shape)*dd[0]));basis=piv[:rank];Tperm=solve_triangular(R[:rank,:rank],R[:rank,:]).T;T=np.empty_like(Tperm);T[piv]=Tperm;abrows=active[basis];Ab=As[abrows];values=E[abrows]*lo[abrows];rowerr=float(np.max(abs(dense-T@dense[basis])));rhserr=float(np.max(abs((E[active]*lo[active]-T@values)/E[active])));assert rowerr<1e-10 and rhserr<1e-10
   for row in abrows:
    budget()
    if int(row) not in cache:cache[int(row)]=Mbody@As.getrow(row).toarray().ravel()
   schur=np.column_stack([Ab@cache[int(row)] for row in abrows]);asym=float(np.max(abs(schur-schur.T)));chol=cho_factor(.5*(schur+schur.T),lower=True)
   def mv(z):return np.r_[Ps@z[:n]+Ab.T@z[n:],Ab@z[:n]]
   def pre(z):return np.r_[Mbody@z[:n],cho_solve(chol,z[n:])]
   op=LinearOperator((n+rank,n+rank),matvec=mv,dtype=float);mp=LinearOperator(op.shape,matvec=pre,dtype=float);rhs=np.r_[-D*q,values];solution=np.zeros(n+rank);iterations=0;solverinfo=[];linearlog=[]
   def callback(z):
    nonlocal iterations
    iterations+=1;budget()
   # Explicit residual correction on identical operator; acceptance uses original units.
   for refine in range(3):
    budget();rr=rhs-mv(solution);delta,info=minres(op,rr,M=mp,rtol=1e-16,maxiter=500,callback=callback,check=False);solution+=delta;solverinfo.append(int(info));rr=mv(solution)-rhs;physical_stat=float(np.max(abs(rr[:n]/D)));physical_eq=float(np.max(abs((dense@solution[:n]-E[active]*lo[active])/E[active])));linearlog.append(dict(refinement=refine,iterations_total=iterations,original_unit_stationarity_N=physical_stat,active_equality_mm=physical_eq));dump(out/f'pivot{pivotstep}_linear_progress.json',linearlog)
    if physical_stat<1e-8 and physical_eq<1e-8:break
   x=D*solution[:n];yb=solution[n:];rec=lsq_linear(T.T,yb,bounds=(np.full(len(active),-np.inf),np.where(ineq[active],0.,np.inf)),tol=1e-14,max_iter=500,lsq_solver='exact');ys=rec.x;y=np.zeros(A.shape[0]);y[active]=E[active]*ys;sl=A@x-lo;grad=P@x+q+A.T@y;primal=max(float(np.max(np.maximum(-sl,0))),float(np.max(abs(sl[eq]))));dual=float(np.max(abs(grad)));sign=float(np.max(np.maximum(y[ineq],0)));comp=float(np.max(abs(sl[ineq]*y[ineq])));qualified=primal<1e-8 and dual<1e-8 and sign<1e-8 and comp<1e-8;coneres=float(np.max(abs(T.T@ys-yb)));violated=np.flatnonzero(ineq&(sl<-1e-8));r=yb-T.T@ys;w=T@r;wn=max(float(np.max(abs(w))),1e-30);wnorm=w/wn;sep_eq=float(np.max(abs(wnorm[~ineq[active]])));sep_min=float(np.min(wnorm[ineq[active]]));sep_dot=float(yb@(r/wn));sep_margin=sep_dot-float(np.linalg.norm(r/wn))*float(np.linalg.norm(mv(solution)[:n]+D*q))
   # NNLS residual supplies an equality-coordinate cone separator. A verified
   # separator opens eligible physical rows; it does not delete their inequality.
   cone_witness=coneres>1e-8 and sep_eq<1e-8 and sep_min>-1e-8 and sep_dot>1e-8
   release=active[ineq[active]&(wnorm>1e-6)] if cone_witness else np.array([],dtype=int)
   last_output=out/f'pivot{pivotstep}.npz';np.savez_compressed(last_output,increment_mm=x[:N],tension_extension_mm=x[N:],physical_dual=y,physical_slack_mm=sl,physical_stationarity_N=grad,scaled_solution=solution,basis_dual=yb,full_scaled_active_dual=ys,active=active,basis=basis,T=T,cone_separator_basis=r/wn,cone_separator_rows=wnorm)
   row=dict(pivot=pivotstep,active_rows=len(active),equality_rank=rank,active_original_rows=active.tolist(),basis_original_rows=abrows.tolist(),maximum_scaled_row_error=rowerr,maximum_physical_RHS_error_mm=rhserr,Schur_absolute_asymmetry=asym,iterations=iterations,solver_info=solverinfo,linear_residual_checks=linearlog,conic_recovery_max_basis_residual=coneres,physical_primal_mm=primal,physical_dual_N=dual,physical_sign_defect_N=sign,physical_complementarity_Nmm=comp,violated_original_rows=violated.tolist(),physical_KKT_qualified=qualified,cone_separator_verified=bool(cone_witness),cone_separator_equality_defect=sep_eq,cone_separator_min_inequality=sep_min,cone_separator_dot_basis_dual=sep_dot,release_original_rows=release.tolist(),output=ref(last_output),elapsed_s=time.monotonic()-start);history.append(row);dump(out/f'pivot{pivotstep}_summary.json',row);dump(out/'pivot_history.json',history)
   if qualified:reason='full original-unit linear KKT qualified; NOT nonlinear equilibrium';break
   if physical_stat>=1e-8 or physical_eq>=1e-8:reason='linear solve original-unit residual failed; no active-set transition';break
   if len(release):active=np.setdiff1d(active,release);history[-1]['transition']='open separator-supported active rows; retain all as physical inequalities'
   elif coneres<1e-8 and len(violated):active=np.union1d(active,violated);history[-1]['transition']='close all original violated rows'
   else:reason='no certified finite cone transition';break
   dump(out/'pivot_history.json',history)
 except Budget as e:reason=str(e)
 result=dict(status='ACTUAL_P1_MATRIXFREE_PIVOT_LINEAR_KKT_PASS_NOT_EQUILIBRIUM' if qualified else 'ACTUAL_P1_MATRIXFREE_PIVOT_REJECTED',candidate=s['candidate'],source=ref(src),source_field=s['source_field'],producer=ref(out/'producer.py'),physical_P=s['physical_P'],physical_A=s['physical_A'],problem=s['problem'],physical_regularization=0.,preconditioner_only_shift_tau=1e-6,preconditioner_setup_s=setup,preconditioner_levels=len(ml.levels),preconditioner_operator_complexity=ml.operator_complexity(),preconditioner_cached_rows=len(cache),max_pivots=maxpivots,internal_budget_s=budget_s,pivots_executed=len(history),reason=reason,history=ref(out/'pivot_history.json') if history else None,pivot_results=history,physical_KKT_qualified=qualified,actual_support_updates=0,accepted_equilibria=0,all_original_inequalities_retained=True,original_contacts=2169,original_branches=14,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['All working-set changes are LINEAR qualification on original savedsource. No attachedload+gamma or nonlinear contactupdate, no stress/strength claim.','Rank basis is equality coordinates only; full original cone and all inactive rows decide acceptance. Separator needs independent original-unit/corruption audit before an update.','Finite four-transition/300s limit; no increasedmemory/directretry, physicalregularization/newfixation or changedcriteria.'])
 if last_output:result['output']=ref(last_output)
 dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if qualified else 2)
if __name__=='__main__':main()
