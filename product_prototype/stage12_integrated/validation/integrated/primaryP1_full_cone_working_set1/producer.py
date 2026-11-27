"""Independent same-P1 numerical rejection audit, no new solver/update.
Rebuild ONE saved QP coefficients and verify physical freeY moment defect.
"""
import sys,json,shutil,time
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
from scipy.linalg import qr,solve_triangular
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


 conditioned=ROOT/'validation/integrated/primaryP1_cone_conditioning1/summary.json';c=json.loads(conditioned.read_text());sc=np.load(REPO/c['scales']['path']);pred=np.load(REPO/c['output']['path']);D=sc['D'];E=sc['E'];y0=pred['physical_dual'];eq=np.arange(2169,2169+Q.shape[0]);isineq=np.ones(A.shape[0],dtype=bool);isineq[eq]=False;active=np.sort(np.r_[eq,np.flatnonzero(isineq & (y0<-1e-8))]);Ps=sparse.diags(D)@P@sparse.diags(D);As=sparse.diags(E[active])@A[active]@sparse.diags(D);values=E[active]*lo[active];dense=As.toarray();qrQ,R,pivot=qr(dense.T,mode='economic',pivoting=True);diag=abs(np.diag(R));threshold=np.finfo(float).eps*max(dense.shape)*diag[0];rank=int(np.sum(diag>threshold));basis=pivot[:rank];Tperm=solve_triangular(R[:rank,:rank],R[:rank,:]).T;T=np.empty_like(Tperm);T[pivot]=Tperm;rowerror=np.max(abs(dense-T@dense[basis]),axis=1);rhserror=(values-T@values[basis])/E[active];certificate=dict(active_original_rows=active.tolist(),basis_original_rows=active[basis].tolist(),rank=rank,active_rows=len(active),rank_threshold=threshold,QR_diagonal=diag.tolist(),maximum_scaled_row_reconstruction=float(rowerror.max()),maximum_physical_active_rhs_error_mm=float(np.max(abs(rhserror))),equality_basis_only_not_cone_replacement=True,all_physical_dual_rows_retained=True)
 dump(out/'row_basis_certificate.json',certificate);np.savez_compressed(out/'row_basis.npz',active=active,basis=basis,T=T,row_error=rowerror,rhs_error_mm=rhserror)
 assert rowerror.max()<1e-10 and np.max(abs(rhserror))<1e-10,'Basis does not reproduce ALL active physical equalities; no factorization allowed'
 Ab=As[basis];matrix=sparse.bmat([[Ps,Ab.T],[Ab,None]],format='csc');rhs=np.r_[-D*q,values[basis]];error=None;warnings_list=[];solution=None
 try:
  with warnings.catch_warnings(record=True) as ww:
   warnings.simplefilter('always');solution=spsolve(matrix,rhs,permc_spec='COLAMD');warnings_list=[str(w.message) for w in ww]
 except Exception as e:error=type(e).__name__+': '+str(e)
 finite=solution is not None and np.isfinite(solution).all();stats={};qualified=False;recovery=None
 if finite:
  x=D*solution[:len(D)];yb=solution[len(D):];upper=np.where(isineq[active],0.,np.inf);lower=np.full(len(active),-np.inf);recovery=lsq_linear(T.T,yb,bounds=(lower,upper),tol=1e-14,max_iter=500,lsq_solver='exact');ys=recovery.x;y=np.zeros(A.shape[0]);y[active]=E[active]*ys;sl=A@x-lo;g=P@x+q+A.T@y;primal=max(float(np.max(np.maximum(-sl,0))),float(np.max(abs(sl[eq]))));dual=float(np.max(abs(g)));sign=float(np.max(np.maximum(y[isineq],0)));comp=float(np.max(abs(sl[isineq]*y[isineq])));qualified=primal<1e-8 and dual<1e-8 and sign<1e-8 and comp<1e-8;stats=dict(physical_primal_mm=primal,physical_dual_N=dual,physical_sign_defect_N=sign,physical_complementarity_Nmm=comp,violated_contact_rows=np.flatnonzero(sl[:2169]<-1e-8).tolist(),maximum_increment_mm=float(np.max(abs(x[:N]))),gauge_dual_N=y[eq].tolist(),conic_recovery_max_basis_residual=float(np.max(abs(T.T@ys-yb))),conic_recovery_status=int(recovery.status),conic_recovery_optimality=float(recovery.optimality));np.savez_compressed(out/'candidate.npz',increment_mm=x[:N],tension_extension_mm=x[N:],physical_dual=y,physical_slack_mm=sl,physical_stationarity_N=g,basis_dual=yb,full_scaled_active_dual=ys)
 result=dict(status='ACTUAL_P1_EQUALITY_BASIS_FULL_CONE_KKT_PASS_NOT_EQUILIBRIUM' if qualified else 'ACTUAL_P1_EQUALITY_BASIS_FULL_CONE_REJECTED',candidate=s['candidate'],source=ref(conditioned),source_field=s['source_field'],producer=ref(out/'producer.py'),basis_certificate=ref(out/'row_basis_certificate.json'),basis=ref(out/'row_basis.npz'),finite_solution=bool(finite),warnings=warnings_list,error=error,physical_KKT_qualified=qualified,active_rows=len(active),numerical_equality_rank=rank,original_contacts=2169,original_branches=14,all_original_rows_checked=bool(finite),all_original_dual_rows_retained=True,physical_inequality_removed=False,factorizations_attempted=1,physical_metrics=stats,actual_support_updates=0,accepted_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['RankQR used ONLY as active equality row coordinate basis, with allrow/RHS reconstruction checked. Signed QR basis is NEVER treated as a physical cone replacement. Recover fulloriginal physical lower-bound multipliers by bounded constrained leastsquares; full physical KKT/allinequality checks determine acceptance.','ONE factorization of rebuilt originalsourceposedlinear diagnostic; no attached/gamma or nonlinear update. Any inactive inequality violation or failedconicrecovery rejects guessedworkingset.','Currentmetric remains positiveSEMIDEFINITE not exacttangent. No equilibrium/stress/gauge/mesh/globalenergy/physicalanchor qualification without fullcoupledcurrent checks.'])
 if finite:result['output']=ref(out/'candidate.npz')
 dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if qualified else 2)
if __name__=='__main__':main()
