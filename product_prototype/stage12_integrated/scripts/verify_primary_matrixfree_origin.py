"""Reassemble same actual current P1 FE metric, separate chunk/order audit."""
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
  for first in range(0,len(t),7919):K+=asm(linear_elasticity(lam,mu),Basis(mesh,el,intorder=2,elements=np.arange(first,min(first+7919,len(t)))))
  Kparts.append(K)
 K=sparse.block_diag(Kparts+[sparse.csr_matrix((6,6))],format='csc');K=sparse.triu(K,format='csc')+sparse.triu(K,1,format='csc').T;ks=a['bolt_k_N_mm'];B=sparse.csr_matrix(np.vstack([model.connectors(u,np.eye(14)[j])[1] for j in range(14)]));Q=sparse.csr_matrix(a['gauge_Q']);geo=json.loads((ROOT/'validation/integrated/primaryP1_surface_geometry3/summary.json').read_text());g=np.load(REPO/geo['output']['path']);J=sparse.csr_matrix((g['J_data'],g['J_indices'],g['J_indptr']),shape=tuple(g['J_shape']));ext,_=model.connectors(u);
 ext,_=model.connectors(u);ks=a['bolt_k_N_mm'];P=sparse.block_diag([K,sparse.diags(ks)],format='csc');q=np.r_[field['elastic_force_N']-p['source_applied_force_N'],np.zeros(14)];A=sparse.vstack([sparse.hstack([J,sparse.csr_matrix((2169,14))]),sparse.hstack([Q,sparse.csr_matrix((Q.shape[0],14))]),sparse.hstack([-B,sparse.eye(14)]),sparse.hstack([sparse.csr_matrix((14,N)),sparse.eye(14)])],format='csc');lo=np.r_[-p['source_gaps_mm'],a['gauge_targets_mm']-Q@u,ext,np.zeros(14)];hi=np.r_[np.full(2169,np.inf),a['gauge_targets_mm']-Q@u,np.full(28,np.inf)]



 folder=ROOT/'validation/integrated'/sys.argv[2];target=folder/'producer.py';doc=dict(physical_P=ref(folder/'physical_P.npz'),physical_A=ref(folder/'physical_A.npz'),problem=ref(folder/'problem.npz'),source_field=s['source_field']);savedP=sparse.load_npz(REPO/doc['physical_P']['path']);savedA=sparse.load_npz(REPO/doc['physical_A']['path']);saved=np.load(REPO/doc['problem']['path']);dp=P-savedP;da=A-savedA;perr=float(np.max(abs(dp.data))) if dp.nnz else 0.;aerr=float(np.max(abs(da.data))) if da.nnz else 0.;qerr=float(np.max(abs(q-saved['q'])));loerr=float(np.max(abs(lo-saved['lower'])));hierr=float(np.max(abs(hi[np.isfinite(hi)]-saved['upper'][np.isfinite(hi)])));cad=ROOT/'cad/exports/primaryP1_seated22/summary.json';cd=json.loads(cad.read_text());from baseline_registry import sha
 checks=dict(actual78partCAD=len(cd['part_references'])==78 and all(sha(REPO/r['path'])==r['SHA256'] for r in cd['part_references'].values()),metric_matches=perr<1e-8,all_constraints_match=aerr<1e-12,source_load_vector_matches=qerr<1e-12,lower_bounds_match=loerr<1e-12,equality_upper_bounds_match=hierr<1e-12,upper_finiteness_matches=bool(np.array_equal(np.isfinite(hi),np.isfinite(saved['upper']))),source_field_matches=s['source_field']==doc['source_field'])
 result=dict(status='ACTUAL_P1_MATRIXFREE_ORIGIN_REASSEMBLY_PASS' if all(checks.values()) else 'ACTUAL_P1_MATRIXFREE_ORIGIN_REASSEMBLY_FAIL',candidate=ref(cad),source=ref(target),producer=ref(out/'producer.py'),checks={k:bool(v) for k,v in checks.items()},physical_metric_max_error_N_mm=perr,physical_constraints_max_error=aerr,load_max_error_N=qerr,lower_max_error_mm=loerr,upper_max_error_mm=hierr,independent_assembly_chunk_tetra=7919,actual_product_DOF=N,original_contact_rows=2169,original_branches=14,unchanged_CAD_parts=78,accepted_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['Independent FE chunk/order and savedsource provenance check, uses existing currentgeometry metric model. Not an independent continuum-model/mesh/energy proof.','Actual archived matrices must match product assembly before interpreting solver residual. Savedsource linear diagnosis only, no attachedload+gamma nonlinear update.']);dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
