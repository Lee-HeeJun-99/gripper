"""Bounded matrix-free saddle solve of actual P1 savedsource metric.
No physical regularization, cone deletion or accepted nonlinear update.
"""
import sys,json,shutil,time
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import LinearOperator,minres
from scipy.linalg import cho_factor,cho_solve
from scipy.optimize import lsq_linear
import warnings
from skfem import MeshTet,Basis,ElementVector,ElementTetP1,asm
from skfem.models.elasticity import linear_elasticity,lame_parameters
from baseline_registry import ROOT,REPO,ref,dump
from primary_corotated_support import Support

def main():
 start=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');src=ROOT/'validation/integrated/primaryP1_finite_increment2/summary.json';s=json.loads(src.read_text());a=dict(np.load(REPO/s['source_field']['path']));p=np.load(REPO/s['predictor_npz']['path']);trial=np.load(REPO/s['trial_field_npz']['path']);loads=json.loads((REPO/s['trial_loads_json']['path']).read_text());local=json.loads((REPO/s['source']['path']).read_text());field=np.load(REPO/local['output']['path']);model=Support(a,local['elastic_bodies']);u=a['u_mm'];N=len(u);Kparts=[]
 for name in local['elastic_bodies']:
  X=a[name+'_points_mm'];o=int(a[name+'_offset']);current=X+u[o:o+3*len(X)].reshape(-1,3);t=a[name+'_tetra'];mesh=MeshTet(current.T,t.T);el=ElementVector(ElementTetP1());lam,mu=lame_parameters(float(a[name+'_E_MPa']),float(a[name+'_nu']));K=sparse.csr_matrix((3*len(X),3*len(X)))
  # Independent chunk size; same declared currentgeometry linear metric.
  for first in range(0,len(t),10000):K+=asm(linear_elasticity(lam,mu),Basis(mesh,el,intorder=2,elements=np.arange(first,min(first+10000,len(t)))))
  Kparts.append(K)
 K=sparse.block_diag(Kparts+[sparse.csr_matrix((6,6))],format='csc');K=sparse.triu(K,format='csc')+sparse.triu(K,1,format='csc').T;ks=a['bolt_k_N_mm'];B=sparse.csr_matrix(np.vstack([model.connectors(u,np.eye(14)[j])[1] for j in range(14)]));Q=sparse.csr_matrix(a['gauge_Q']);geo=json.loads((ROOT/'validation/integrated/primaryP1_surface_geometry3/summary.json').read_text());g=np.load(REPO/geo['output']['path']);J=sparse.csr_matrix((g['J_data'],g['J_indices'],g['J_indptr']),shape=tuple(g['J_shape']));ext,_=model.connectors(u);
 ext,_=model.connectors(u);ks=a['bolt_k_N_mm'];P=sparse.block_diag([K,sparse.diags(ks)],format='csc');q=np.r_[field['elastic_force_N']-p['source_applied_force_N'],np.zeros(14)];A=sparse.vstack([sparse.hstack([J,sparse.csr_matrix((2169,14))]),sparse.hstack([Q,sparse.csr_matrix((Q.shape[0],14))]),sparse.hstack([-B,sparse.eye(14)]),sparse.hstack([sparse.csr_matrix((14,N)),sparse.eye(14)])],format='csc');lo=np.r_[-p['source_gaps_mm'],a['gauge_targets_mm']-Q@u,ext,np.zeros(14)];hi=np.r_[np.full(2169,np.inf),a['gauge_targets_mm']-Q@u,np.full(28,np.inf)]


 import pyamg
 conditioned=ROOT/'validation/integrated/primaryP1_cone_conditioning1/summary.json';c=json.loads(conditioned.read_text());sc=np.load(REPO/c['scales']['path']);D=sc['D'];E=sc['E'];bc=ROOT/'validation/integrated/primaryP1_full_cone_working_set1/row_basis_certificate.json';bs=ROOT/'validation/integrated/primaryP1_full_cone_working_set1/row_basis.npz';basisdata=np.load(bs);active=basisdata['active'];basis=basisdata['basis'];T=basisdata['T'];eq=np.arange(2169,2169+Q.shape[0]);isineq=np.ones(A.shape[0],dtype=bool);isineq[eq]=False
 Ps=(sparse.diags(D)@P@sparse.diags(D)).tocsr();As=(sparse.diags(E)@A@sparse.diags(D)).tocsr();Ab=As[active[basis]];values=E[active[basis]]*lo[active[basis]];rhs=np.r_[-D*q,values];n=len(D);m=len(basis)
 # Physical matrices are archived before solver. No fill-producing KKT factorization.
 for name,mat in [('physical_P',P),('physical_A',A)]:sparse.save_npz(out/(name+'.npz'),mat)
 np.savez_compressed(out/'problem.npz',q=q,lower=lo,upper=hi,D=D,E=E,active=active,basis=basis,T=T)
 # Only the SPD preconditioner is shifted. Never add a spring to physical P.
 diag=Ps.diagonal();tau=1e-6;reg=tau*np.maximum(diag,1.);Pr=Ps+sparse.diags(reg)
 modes=[]
 for name in local['elastic_bodies']:
  X=a[name+'_points_mm'];o=int(a[name+'_offset']);Xc=X-X.mean(axis=0)
  for j in range(6):
   z=np.zeros(n);v=np.zeros_like(X)
   if j<3:v[:,j]=1
   if j>=3:v=np.cross(np.eye(3)[j-3],Xc)
   z[o:o+3*len(X)]=v.ravel();modes.append(z/D)
 for j in range(N-6,N):z=np.zeros(n);z[j]=1/D[j];modes.append(z)
 Bnear=np.column_stack(modes);Bnear/=np.maximum(np.linalg.norm(Bnear,axis=0),1e-30)
 prestart=time.monotonic();ml=pyamg.smoothed_aggregation_solver(Pr,B=Bnear,symmetry='symmetric',max_levels=10,max_coarse=120,presmoother=('gauss_seidel',{'sweep':'symmetric'}),postsmoother=('gauss_seidel',{'sweep':'symmetric'}),coarse_solver='pinv');Mbody=ml.aspreconditioner(cycle='V')
 # Actual small Schur approximation from the SAME symmetric V cycle, not diagonal row deletion.
 schur=np.empty((m,m))
 for j in range(m):schur[:,j]=Ab@(Mbody@Ab.getrow(j).toarray().ravel())
 asym=float(np.max(abs(schur-schur.T)));S=.5*(schur+schur.T);chol=cho_factor(S,lower=True);preseconds=time.monotonic()-prestart
 def matvec(z):return np.r_[Ps@z[:n]+Ab.T@z[n:],Ab@z[:n]]
 def pre(z):return np.r_[Mbody@z[:n],cho_solve(chol,z[n:])]
 op=LinearOperator((n+m,n+m),matvec=matvec,dtype=float);mp=LinearOperator(op.shape,matvec=pre,dtype=float)
 # Independent symmetry/positive preconditioner checks on deterministic actual vectors.
 gen=np.random.default_rng(1727);v=gen.normal(size=n+m);w=gen.normal(size=n+m);symerr=abs(v@matvec(w)-w@matvec(v))/max(1,abs(v@matvec(w)),abs(w@matvec(v)));presym=abs(v@pre(w)-w@pre(v))/max(1,abs(v@pre(w)),abs(w@pre(v)));prepositive=float(v@pre(v));assert symerr<1e-10 and presym<1e-10 and prepositive>0
 history=[];solve_start=time.monotonic();last=[np.zeros(n+m)];limit='none'
 class Budget(Exception):pass
 def callback(z):
  last[0]=z.copy();k=len(history)+1;r=matvec(z)-rhs;history.append(dict(iteration=k,max_scaled_residual=float(np.max(abs(r))),elapsed_s=time.monotonic()-solve_start))
  if (ROOT/'runtime/STOP').exists():raise Budget('STOP')
  if time.monotonic()-solve_start>180:raise Budget('180s internal solve budget')
 try:solution,info=minres(op,rhs,M=mp,rtol=1e-13,maxiter=1500,callback=callback,check=False)
 except Budget as error:solution=last[0];info=-1;limit=str(error)
 x=D*solution[:n];yb=solution[n:];unbounded=np.linalg.lstsq(T.T,yb,rcond=None)[0];upper=np.where(isineq[active],0.,np.inf);recovery=lsq_linear(T.T,yb,bounds=(np.full(len(active),-np.inf),upper),tol=1e-14,max_iter=500,lsq_solver='exact');ys=recovery.x;y=np.zeros(A.shape[0]);y[active]=E[active]*ys;sl=A@x-lo;grad=P@x+q+A.T@y
 primal=max(float(np.max(np.maximum(-sl,0))),float(np.max(abs(sl[eq]))));dual=float(np.max(abs(grad)));sign=float(np.max(np.maximum(y[isineq],0)));comp=float(np.max(abs(sl[isineq]*y[isineq])));basisres=Ab@solution[:n]-values;linearres=matvec(solution)-rhs;coneres=float(np.max(abs(T.T@ys-yb)));unboundedres=float(np.max(abs(T.T@unbounded-yb)));qualified=primal<1e-8 and dual<1e-8 and sign<1e-8 and comp<1e-8
 np.savez_compressed(out/'candidate.npz',increment_mm=x[:N],tension_extension_mm=x[N:],physical_dual=y,physical_slack_mm=sl,physical_stationarity_N=grad,basis_dual=yb,full_scaled_active_dual=ys,scaled_solution=solution,unbounded_active_dual=unbounded)
 dump(out/'iteration_history.json',history)
 result=dict(status='ACTUAL_P1_MATRIXFREE_FULL_CONE_KKT_PASS_NOT_EQUILIBRIUM' if qualified else 'ACTUAL_P1_MATRIXFREE_FULL_CONE_KKT_REJECTED',candidate=s['candidate'],source_field=s['source_field'],source=ref(src),producer=ref(out/'producer.py'),physical_P=ref(out/'physical_P.npz'),physical_A=ref(out/'physical_A.npz'),problem=ref(out/'problem.npz'),output=ref(out/'candidate.npz'),history=ref(out/'iteration_history.json'),basis_source=ref(bs),basis_certificate=ref(bc),original_DOF=N,original_contacts=2169,original_branches=14,active_rows=len(active),equality_rank=m,solver='MINRES matrix-free saddle / SPD shifted AMG+actualVcycleSchur block preconditioner',physical_regularization=0.,preconditioner_shift_tau=tau,preconditioner_levels=len(ml.levels),preconditioner_operator_complexity=ml.operator_complexity(),preconditioner_setup_s=preseconds,operator_relative_symmetry=symerr,preconditioner_relative_symmetry=presym,preconditioner_positive_probe=prepositive,Schur_absolute_asymmetry=asym,solver_info=int(info),internal_limit=limit,iterations=len(history),solve_s=time.monotonic()-solve_start,max_scaled_saddle_residual=float(np.max(abs(linearres))),max_physical_active_equality_residual_mm=float(np.max(abs(basisres/E[active[basis]]))),conic_recovery_max_basis_residual=coneres,unbounded_recovery_max_basis_residual=unboundedres,unbounded_wrong_sign_rows=active[isineq[active]&(unbounded>1e-8)].tolist(),physical_primal_mm=primal,physical_dual_N=dual,physical_sign_defect_N=sign,physical_complementarity_Nmm=comp,violated_contact_rows=np.flatnonzero(sl[:2169]<-1e-8).tolist(),gauge_dual_N=y[eq].tolist(),physical_KKT_qualified=qualified,all_original_rows_checked=True,physical_inequality_removed=False,actual_support_updates=0,accepted_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['Original savedsource/fixed gauge linear qualification only; attachedload+gamma nonlinear update is prohibited until fullphysicalKKT qualification.','AMG diagonal shift modifies ONLY preconditioner, never physical stiffness or constraints. Signed rank basis only active equality coordinates; all2169contacts/14branches and physicalconic duals checked.','Currentmetric is positiveSEMIDEFINITE, not exact Biot/contact/load tangent. No newstress/strength/mesh/globalenergy or whole-system PASS.'])
 dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if qualified else 2)
if __name__=='__main__':main()
