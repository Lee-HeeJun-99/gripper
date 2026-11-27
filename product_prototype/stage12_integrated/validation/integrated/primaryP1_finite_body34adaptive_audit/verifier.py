"""Independent positive Duffy7 global variational re-solve, fixed actual CAD mesh.
Original force acceptance is reported separately from response1percent.
"""
import sys,json,time,shutil
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import splu
from skfem import MeshTet,Basis,ElementTetP1,ElementVector,asm
from skfem.models.elasticity import linear_elasticity
from baseline_registry import ROOT,REPO,ref,dump
from verify_finite_body34 import integrate,duffy

def main():
 start=time.monotonic();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');sp=ROOT/'validation/integrated'/sys.argv[2]/'summary.json';s=json.loads(sp.read_text());dump(out/'inputs.json',dict(candidate=s['candidate'],source=ref(sp),verifier=ref(out/'verifier.py'),independent_integration=ref(ROOT/'scripts/verify_finite_body34.py'),positive_Duffy_order=7,scope='Same4actual solid meshes/conditional load functional. Independent complex-step Kelvin strains and343positive quadrature points per parent tetra, followed by new elastic variational re-solve. No source/tolerance/physical criteria change.'))
 results=[];bc,w=duffy(7)
 for row in s['results']:
  bs=time.monotonic();a=np.load(REPO/row['fields']['path']);p=a['points_mm'];t=a['tetra'];E=row['conditional_E_MPa'];nu=row['conditional_nu'];N=3*len(p);M=a['F'].shape[1];mu=E/(2*(1+nu));la=E*nu/((1+nu)*(1-2*nu));G,H=integrate(a,bc,w,E,nu);K=sparse.csr_matrix((N,N));msh=MeshTet(p.T,t.T);el=ElementVector(ElementTetP1())
  for first in range(0,len(t),8000):
   assert not(ROOT/'runtime/STOP').exists();K+=asm(linear_elasticity(la,mu),Basis(msh,el,intorder=2,elements=np.arange(first,min(first+8000,len(t)))))
  Q=a['Q'];factor=splu(sparse.bmat([[K,sparse.csr_matrix(Q.T)],[sparse.csr_matrix(Q),None]],format='csc'));UG=factor.solve(np.vstack([G,np.zeros((6,M))]))[:N];S=H-G.T@UG;S=(S+S.T)/2;F=a['F'];UF=a['UF'];L=a['L'];d=L-G.T@UF;alpha=np.linalg.solve(S,d);v=UF-UG@alpha;C=F.T@UF+d.T@alpha;rel=float(np.linalg.norm(C-a['compliance'])/np.linalg.norm(C));original_res=max(abs(K@a['VFE']+G@a['alpha']-F).max(),abs(G.T@a['VFE']+H@a['alpha']-L).max());reference_res=max(abs(K@v+G@alpha-F).max(),abs(G.T@v+H@alpha-L).max());bo=out/row['part'];bo.mkdir();np.savez_compressed(bo/'reference_matrices.npz',G=G,H=H,S=S,alpha=alpha,VFE=v,compliance=C)
  results.append(dict(part=row['part'],source_fields=row['fields'],reference=ref(bo/'reference_matrices.npz'),independent_reference_compliance_mm_N=C.tolist(),adaptive_compliance_mm_N=a['compliance'].tolist(),independent_relative_compliance_change=rel,original1percent_response_pass=rel<.01,adaptive_solution_independent_weak_residual_N=float(original_res),original1e_minus8N_force_pass=bool(original_res<1e-8),reference_own_discrete_weak_residual_N=float(reference_res),positive_reference_regular_work=bool(np.linalg.eigvalsh(S).min()>0),analytic_G_relative_change=float(np.linalg.norm(G-a['G'])/np.linalg.norm(G)),analytic_H_relative_change=float(np.linalg.norm(H-a['H'])/np.linalg.norm(H)),elapsed_s=time.monotonic()-bs));print(json.dumps(results[-1]),flush=True)
 checks=dict(independent_reference_positive_work=all(r['positive_reference_regular_work'] for r in results),independent_reference_discrete_stationarity=all(r['reference_own_discrete_weak_residual_N']<1e-8 for r in results),all4body_responses_1percent=all(r['original1percent_response_pass'] for r in results));dump(out/'summary.json',dict(status='ACTUAL_P1_ADAPTIVE_FINITE_BODY_INDEPENDENT_REFERENCE' if all(checks.values()) else 'ACTUAL_P1_ADAPTIVE_FINITE_BODY_REFERENCE_FAIL',candidate=s['candidate'],inputs=ref(out/'inputs.json'),checks=checks,results=results,independent_force_all_original_tolerance=all(r['original1e_minus8N_force_pass'] for r in results),accepted_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['Duffy7 is independent higher quadrature, not an exact integral bound. Original force tolerance remains separately enforced; response agreement cannot qualify actual contact,finite freeend/curved geometry,mesh convergence or physical source coupling.','All material/patch/source assumptions remain conditional. No new CAD or actual product equilibrium/strength/globalenergy qualification.']))
if __name__=='__main__':main()
