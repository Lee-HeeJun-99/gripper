"""Independent same-P1 numerical rejection audit, no new solver/update.
Rebuild ONE saved QP coefficients and verify physical freeY moment defect.
"""
import sys,json,shutil,time
import numpy as np
from scipy import sparse
import osqp
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
 # Positive diagonal congruence + positive row scaling is an exact cone automorphism.
 # All physical rows stay present. Eight fixed Ruiz iterations, no solver feedback.
 D=np.ones(P.shape[0]);E=np.ones(A.shape[0]);Ps=P.copy();As=A.copy();history=[]
 for k in range(8):
  pn=np.asarray(abs(Ps).max(axis=0).toarray()).ravel();an=np.asarray(abs(As).max(axis=0).toarray()).ravel();d=1/np.sqrt(np.maximum(np.maximum(pn,an),1e-30));Ps=sparse.diags(d)@Ps@sparse.diags(d);As=As@sparse.diags(d);D*=d
  rn=np.asarray(abs(As).max(axis=1).toarray()).ravel();e=1/np.maximum(rn,1e-30);As=sparse.diags(e)@As;E*=e;history.append(dict(iteration=k,column_scale_min=float(D.min()),column_scale_max=float(D.max()),row_scale_min=float(E.min()),row_scale_max=float(E.max())))
 Ps=Ps.tocsc();As=As.tocsc();qs=D*q;ls=E*lo;hs=E*hi
 xp=np.r_[p['increment_mm'],p['linearized_bolt_force_N']/ks];yp=p['QP_dual'];zp=xp/D;vp=yp/E
 gx=P@xp+q+A.T@yp;gz=Ps@zp+qs+As.T@vp
 slack=A@xp-lo;scaledslack=(As@zp-ls)/E
 checks=dict(all_original_rows=A.shape[0]==2169+Q.shape[0]+28,positive_cone_scales=bool(min(D.min(),E.min())>0),slack_bijection=float(np.max(abs(slack-scaledslack)))<1e-10,dual_cotangent=float(np.max(abs(gx-gz/D)))<1e-8,quadratic_energy=abs(float(xp@(P@xp))-float(zp@(Ps@zp)))<1e-10,negative_pressure_control=False)
 # Sign corruption must break physical stationarity; changing y sign is NOT scaling.
 wrong=P@xp+q+A.T@(-yp);wrongdef=float(np.max(abs(wrong-gx)));checks['negative_pressure_control']=wrongdef>1e-3
 free=np.zeros(N);b=model.bodies['F0_ROOT_BACK'];o=b['offset'];free[o+1:o+3*len(b['X']):3]=1
 # This direction is the actual original Root Y translation; do not silently move Motor/gauge.
 free_gauge=float(np.max(abs(Q@free)));free_bolts=B@free;free_contact=J@free
 dump(out/'conditioning_certificate.json',dict(checks={k:bool(v) for k,v in checks.items()},history=history,maximum_slack_roundtrip_mm=float(np.max(abs(slack-scaledslack))),maximum_physical_stationarity_roundtrip_N=float(np.max(abs(gx-gz/D))),wrong_dual_sign_defect_N=wrongdef,original_RootY_gauge_response=free_gauge,original_RootY_contact_response_max=float(np.max(abs(free_contact))),original_RootY_connector_response_max=float(np.max(abs(free_bolts)))))
 np.savez_compressed(out/'scaled_problem.npz',D=D,E=E,free_RootY=free)
 assert all(checks.values())
 # ONE newly conditioned linear QP, same iteration/time budget. No physical update unless KKT qualifies.
 solver=osqp.OSQP();solver.setup(P=Ps,q=qs,A=As,l=ls,u=hs,eps_abs=1e-10,eps_rel=1e-10,max_iter=2400,time_limit=120.,polishing=False,verbose=False,check_termination=25,scaling=0);solver.warm_start(x=zp,y=vp);r=solver.solve(raise_error=False);x=D*r.x;y=E*r.y;grad=P@x+q+A.T@y;sl=A@x-lo;eq=slice(2169,2169+Q.shape[0]);primal=max(float(np.max(np.maximum(-sl,0))),float(np.max(abs(sl[eq]))));dual=float(np.max(abs(grad)));ineq=np.ones(len(y),dtype=bool);ineq[eq]=False;sign=float(np.max(np.maximum(y[ineq],0)));comp=float(np.max(abs(sl[ineq]*y[ineq])));qualified=primal<1e-8 and dual<1e-8 and sign<1e-8 and comp<1e-8
 np.savez_compressed(out/'linear_candidate.npz',increment_mm=x[:N],tension_extension_mm=x[N:],physical_dual=y,stationarity_N=grad,physical_slack_mm=sl)
 info={k:getattr(r.info,k) for k in ['status','iter','prim_res','dual_res','run_time']}
 result=dict(status='ACTUAL_P1_CONE_CONDITIONING_LINEAR_KKT_PASS_NOT_EQUILIBRIUM' if qualified else 'ACTUAL_P1_CONE_CONDITIONING_LINEAR_KKT_REJECTED',candidate=s['candidate'],source=ref(src),source_field=s['source_field'],producer=ref(out/'producer.py'),conditioning=ref(out/'conditioning_certificate.json'),scales=ref(out/'scaled_problem.npz'),output=ref(out/'linear_candidate.npz'),checks={k:bool(v) for k,v in checks.items()},QP=info,physical_primal_mm=primal,physical_dual_N=dual,physical_dual_sign_N=sign,physical_complementarity_Nmm=comp,physical_KKT_qualified=qualified,all_original_contact_rows=2169,all_original_branches=14,original_gauge_rows=Q.shape[0],maximum_increment_mm=float(np.max(abs(x[:N]))),original_RootY_gauge_response=free_gauge,original_RootY_contact_response_max=float(np.max(abs(free_contact))),original_RootY_connector_response_max=float(np.max(abs(free_bolts))),actual_physics_updates=0,accepted_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['Positive diagonal congruence preserves the original linear feasible cone and dual orientation; does not certify nonlinear contact equivalence or Biot Hessian.','All original rows retained. One conditioned solve with same2400/120s limits; original predictor warm start remains rejected. No iteration extension, active row deletion, polish, physical update or Base residual cancellation.','RootY coordinate response is a diagnostic, not permission to impose translation or add fixation. Full upstream/freeY coupling and nonlinear current-load checks remain prerequisite to one corrected physical update.'])
 dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if qualified else 2)
if __name__=='__main__':main()
