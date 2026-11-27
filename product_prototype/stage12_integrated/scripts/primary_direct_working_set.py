"""Independent same-P1 numerical rejection audit, no new solver/update.
Rebuild ONE saved QP coefficients and verify physical freeY moment defect.
"""
import sys,json,shutil,time
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
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

 conditioned=ROOT/'validation/integrated/primaryP1_cone_conditioning1/summary.json';c=json.loads(conditioned.read_text());sc=np.load(REPO/c['scales']['path']);pred=np.load(REPO/c['output']['path']);D=sc['D'];E=sc['E'];y0=pred['physical_dual'];eq=np.arange(2169,2169+Q.shape[0]);isineq=np.ones(A.shape[0],dtype=bool);isineq[eq]=False;active=np.sort(np.r_[eq,np.flatnonzero(isineq & (y0<-1e-8))]);Ps=sparse.diags(D)@P@sparse.diags(D);As=sparse.diags(E[active])@A[active]@sparse.diags(D);rhs=np.r_[-D*q,E[active]*lo[active]];matrix=sparse.bmat([[Ps,As.T],[As,None]],format='csc');dump(out/'working_set.json',dict(selected_original_rows=active.tolist(),selection='ALL original equalities + original inequality rows with conditioned lower-bound dual<-1e-8N. No rank filtering, deduplication, signedQR or physical-row deletion. Other rows remain inactive and ALL checked after ONE factorization.',matrix_shape=list(matrix.shape),matrix_nnz=matrix.nnz,conditioned=ref(conditioned),physical_pressure_cutoff_N=1e-8,one_factorization_only=True));warnings_list=[];error=None;solution=None
 try:
  with warnings.catch_warnings(record=True) as ww:
   warnings.simplefilter('always');solution=spsolve(matrix,rhs,permc_spec='COLAMD');warnings_list=[str(w.message) for w in ww]
 except Exception as e:error=type(e).__name__+': '+str(e)
 finite=solution is not None and np.isfinite(solution).all();stats={};qualified=False
 if finite:
  x=D*solution[:len(D)];y=np.zeros(A.shape[0]);y[active]=E[active]*solution[len(D):];sl=A@x-lo;g=P@x+q+A.T@y;primal=max(float(np.max(np.maximum(-sl,0))),float(np.max(abs(sl[eq]))));dual=float(np.max(abs(g)));sign=float(np.max(np.maximum(y[isineq],0)));comp=float(np.max(abs(sl[isineq]*y[isineq])));qualified=primal<1e-8 and dual<1e-8 and sign<1e-8 and comp<1e-8;stats=dict(physical_primal_mm=primal,physical_dual_N=dual,physical_sign_defect_N=sign,physical_complementarity_Nmm=comp,negative_contact_pressure_rows=np.flatnonzero(y[:2169]>1e-8).tolist(),violated_inactive_contact_rows=np.flatnonzero(sl[:2169]<-1e-8).tolist(),maximum_increment_mm=float(np.max(abs(x[:N]))),gauge_dual_N=y[eq].tolist());np.savez_compressed(out/'direct_candidate.npz',increment_mm=x[:N],tension_extension_mm=x[N:],physical_dual=y,physical_slack_mm=sl,physical_stationarity_N=g)
 result=dict(status='ACTUAL_P1_DIRECT_PHYSICAL_WORKING_SET_KKT_PASS_NOT_EQUILIBRIUM' if qualified else 'ACTUAL_P1_DIRECT_PHYSICAL_WORKING_SET_REJECTED',candidate=s['candidate'],source=ref(conditioned),source_field=s['source_field'],producer=ref(out/'producer.py'),working_set=ref(out/'working_set.json'),finite_solution=bool(finite),warnings=warnings_list,error=error,physical_KKT_qualified=qualified,selected_original_contact_rows=int(np.sum(active<2169)),selected_original_rows=len(active),all_original_rows_checked=bool(finite),original_contacts=2169,original_branches=14,rank_filter_applied=False,allphysicalinequalities_retained=True,factorizations_attempted=1,physical_metrics=stats,actual_support_updates=0,accepted_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['One actual physical-row active-set KKT factorization, not OSQP iteration extension or timeout retry. Inactive original rows checked only when factorization returns finite solution; negative multipliers invalidate guessed working set. No equality-cone equivalence assumption from rankQR.','This is the original source-load linear diagnostic. No augmentedRootY/attached-load or nonlinear contact update executed. KKT/gauge/sourceposed load prerequisites still apply.','PositiveSEMIDEFINITE currentmetric is not exactBiot/contact/load tangent. No stress/strength/mesh/global energy/physical anchor/full3Finger certification.'])
 if finite:result['output']=ref(out/'direct_candidate.npz')
 dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if qualified else 2)
if __name__=='__main__':main()
