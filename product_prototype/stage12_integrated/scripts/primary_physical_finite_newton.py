"""One physical-P Newton direction from certified actual finite-gap P1 state.
No separator transitions; original full cone/gauge checks precede any support update.
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
 start=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');src=ROOT/'validation/integrated/primaryP1_affine_finite_projection1/summary.json';s=json.loads(src.read_text());audit=json.loads((ROOT/'validation/integrated/primaryP1_affine_finite_audit1/summary.json').read_text());assert all(audit['checks'].values());assert s['accepted_linear_steps']==1;P=sparse.load_npz(REPO/s['physical_P']['path']);A=sparse.load_npz(REPO/s['physical_A']['path']);p=np.load(REPO/s['problem']['path']);a=np.load(REPO/s['source_field']['path']);q=p['q'];lo=p['lower'];hi=p['upper'];D=p['D'].copy();E=p['E'];parent=json.loads((REPO/s['source']['path']).read_text());D[-1]=parent['direction_scaling_gamma'];n=len(D);N=n-15;eq=np.flatnonzero(np.isfinite(hi)&(lo==hi));ineq=np.ones(A.shape[0],bool);ineq[eq]=False;state=np.load(REPO/s['output']['path']);x=state['after_x'];sl=A@x-lo;active=np.union1d(eq,np.flatnonzero(ineq&(sl<=1e-10)));Ps=(sparse.diags(D)@P@sparse.diags(D)).tocsr();As=(sparse.diags(E)@A@sparse.diags(D)).tocsr();local=json.loads((ROOT/'validation/integrated/primaryP1_local_surface2/summary.json').read_text())
 diag=Ps.diagonal();Pr=Ps+sparse.diags(1e-6*np.maximum(diag,1.));modes=[]
 for name in local['elastic_bodies']:
  X=a[name+'_points_mm'];o=int(a[name+'_offset']);Xc=X-X.mean(axis=0)
  for j in range(6):
   z=np.zeros(n);v=np.zeros_like(X)
   if j<3:v[:,j]=1
   else:v=np.cross(np.eye(3)[j-3],Xc)
   z[o:o+3*len(X)]=v.ravel();modes.append(z/D)
 for j in list(range(N-6,N))+[n-1]:z=np.zeros(n);z[j]=1/D[j];modes.append(z)

 Bnear=np.column_stack(modes);Bnear/=np.maximum(np.linalg.norm(Bnear,axis=0),1e-30);ml=pyamg.smoothed_aggregation_solver(Pr,B=Bnear,symmetry='symmetric',max_levels=10,max_coarse=120,presmoother=('gauss_seidel',{'sweep':'symmetric'}),postsmoother=('gauss_seidel',{'sweep':'symmetric'}),coarse_solver='pinv');M=ml.aspreconditioner(cycle='V')
 dense=As[active].toarray();qq,R,piv=qr(dense.T,mode='economic',pivoting=True);dd=abs(np.diag(R));rank=int(np.sum(dd>np.finfo(float).eps*max(dense.shape)*dd[0]));basis=piv[:rank];Tperm=solve_triangular(R[:rank,:rank],R[:rank,:]).T;T=np.empty_like(Tperm);T[piv]=Tperm;Ab=As[active[basis]];values=-E[active[basis]]*sl[active[basis]];rowerr=float(np.max(abs(dense-T@dense[basis])));rhserr=float(np.max(abs((-E[active]*sl[active]-T@values)/E[active])));assert rowerr<1e-10 and rhserr<1e-10;history=[];qualified=False;reason='one physical-P Newton solve completed';iterations=0;finite=False
 class Budget(Exception):pass
 def budget():
  if(ROOT/'runtime/STOP').exists():raise Budget('STOP')
  if time.monotonic()-start>300:raise Budget('300s physicalNewton internal budget')
 try:
  V=[]
  for r in active[basis]:budget();V.append(M@As.getrow(r).toarray().ravel())
  V=np.column_stack(V);S=np.asarray(Ab@V);chol=cho_factor(.5*(S+S.T),lower=True)
  def mv(z):return np.r_[Ps@z[:n]+Ab.T@z[n:],Ab@z[:n]]
  def pre(z):return np.r_[M@z[:n],cho_solve(chol,z[n:])]
  op=LinearOperator((n+rank,n+rank),matvec=mv,dtype=float);mp=LinearOperator(op.shape,matvec=pre,dtype=float);force=P@x+q;rhs=np.r_[-D*force,values];solution=np.zeros(n+rank);infos=[]
  def callback(z):
   nonlocal iterations
   iterations+=1;budget()
  for refine in range(3):
   budget();rr=rhs-mv(solution);delta,info=minres(op,rr,M=mp,rtol=1e-16,maxiter=500,callback=callback,check=False);solution+=delta;infos.append(int(info));rr=mv(solution)-rhs;stat=float(np.max(abs(rr[:n]/D)));aeq=float(np.max(abs((dense@solution[:n]+E[active]*sl[active])/E[active])));history.append(dict(refinement=refine,iterations=iterations,stationarity_N=stat,active_equality_mm=aeq));dump(out/'linear_progress.json',history)
   if stat<1e-8 and aeq<1e-8:break
  dx=D*solution[:n];yb=solution[n:];rec=lsq_linear(T.T,yb,bounds=(np.full(len(active),-np.inf),np.where(ineq[active],0.,np.inf)),tol=1e-14,max_iter=500,lsq_solver='exact',method='bvls');y=np.zeros(A.shape[0]);y[active]=E[active]*rec.x;trial=x+dx;end=A@trial-lo;res=P@trial+q+A.T@y;physical=dict(primal_mm=max(float(np.max(np.maximum(-end[ineq],0))),float(np.max(abs(end[eq])))),stationarity_N=float(np.max(abs(res))),sign_N=float(np.max(np.maximum(y[ineq],0))),complementarity_Nmm=float(np.max(abs(end[ineq]*y[ineq]))),gauge_N=float(np.max(abs(y[eq]))),RootY_gamma_stationarity_N=float(abs(y[2175])));qualified=all(v<1e-8 for v in physical.values());gt=float(force@dx);curv=float(dx@(P@dx));Ad=A@dx;blocked=np.flatnonzero(ineq&(Ad<-1e-16));ratio=np.maximum(sl[blocked],0)/(-Ad[blocked]);alpha=min(1.,float(np.min(ratio))) if len(blocked) else 1.;blocking=int(blocked[np.argmin(ratio)]) if len(blocked) else None;finite=bool(np.all(np.isfinite(trial)));np.savez_compressed(out/'newton.npz',before_x=x,direction=dx,trial_x=trial,physical_dual=y,physical_residual=res,slack=end,active=active,basis=basis,T=T,scaled_solution=solution,physical_force=force)
  diagnostics=dict(physical_KKT=physical,physical_KKT_qualified=qualified,linear_equality_KKT=history,conic_recovery_basis_residual=float(np.max(abs(T.T@rec.x-yb))),physical_objective_direction_Nmm=gt,physical_curvature_Nmm=curv,objective_before_Nmm=float(.5*x@(P@x)+q@x),objective_trial_Nmm=float(.5*trial@(P@trial)+q@trial),allrow_blocking_alpha=alpha,blocking_original_row=blocking,solver_info=infos,violated_original_rows=np.flatnonzero(ineq&(end<-1e-8)).tolist(),output=ref(out/'newton.npz'))
 except Budget as e:reason=str(e);diagnostics=dict(linear_equality_KKT=history)
 except np.linalg.LinAlgError as e:reason='search Schur factorization rejected: '+str(e);diagnostics={}
 result=dict(status='ACTUAL_P1_PHYSICAL_NEWTON_KKT_PASS_NOT_NONLINEAR_EQUILIBRIUM' if qualified else 'ACTUAL_P1_PHYSICAL_NEWTON_REJECTED',candidate=s['candidate'],source=ref(src),source_audit=ref(ROOT/'validation/integrated/primaryP1_affine_finite_audit1/summary.json'),source_field=s['source_field'],physical_P=s['physical_P'],physical_A=s['physical_A'],problem=s['problem'],producer=ref(out/'producer.py'),active_rows=len(active),equality_rank=rank,maximum_scaled_row_error=rowerr,maximum_original_RHS_error_mm=rhserr,iterations=iterations,finite_output=finite,reason=reason,diagnostics=diagnostics,physical_regularization=0.,preconditioner_only_shift=1e-6,actual_support_updates=0,accepted_linear_steps=0,accepted_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['One physical-P equality Newton direction from independently certified finite-gap linear trial; no separator release/add scan or state acceptance. All original inequalities/gauge checks retained.','Original physical P is positiveSEMIDEFINITE currentgeometry metric, not exact Biot/contact/load Hessian. Fullcone/allgauge and nonlinear prerequisites remain mandatory. Searchmetric AMG shift never enters physical P.']);dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if qualified else 2)
if __name__=='__main__':main()
