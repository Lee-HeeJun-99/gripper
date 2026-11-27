"""Same finite P1 body Ritz spaces; adaptive positive quadrature ONLY.
Sub-tetra integration adds no mechanical DOF or physical boundary condition.
"""
import sys,json,time,shutil
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import splu
from skfem import MeshTet,Basis,ElementTetP1,ElementVector,asm
from skfem.models.elasticity import linear_elasticity,lame_parameters
from skfem.quadrature import get_quadrature_tet
from baseline_registry import ROOT,REPO,ref,sha,dump
from primary_finite_body34 import kelvin,stress

RULES=[]
for order in [5,6]:
 x,w=get_quadrature_tet(order);RULES.append((np.vstack([1-x.sum(0),x]).T,6*w))

def children(v):
 a,b,c,d=v;ab=(a+b)/2;ac=(a+c)/2;ad=(a+d)/2;bc=(b+c)/2;bd=(b+d)/2;cd=(c+d)/2
 return np.array([[a,ab,ac,ad],[ab,b,bc,bd],[ac,bc,c,cd],[ad,bd,cd,d],[ab,ac,ad,cd],[ab,ac,bc,cd],[ab,ad,bd,cd],[ab,bc,bd,cd]])

def moments(v,centers,dirs,E,nu,rule):
 bc,w=rule;V=abs(np.linalg.det((v[:,1:]-v[:,0,None]).transpose(0,2,1)))/6;q=np.einsum('qa,tai->tqi',bc,v);_,eps=kelvin(q,centers,dirs,E,nu);s=stress(eps,E,nu);wt=V[:,None]*w;sg=np.einsum('tqmij,tq->tmij',s,wt);en=np.einsum('tqkij,tqlij,tq->tkl',eps,s,wt);return sg,en

def integrate(p,t,centers,dirs,E,nu,tol,maxdepth):
 M=len(centers);SG=np.zeros((len(t),M,3,3));HH=np.zeros((len(t),M,M));pending=[(i,p[tt],0) for i,tt in enumerate(t)];hist={};rejected=0;unresolved=0;max_unresolved=0.;max_accepted=0.
 while pending:
  assert not(ROOT/'runtime/STOP').exists();batch=pending[-300:];del pending[-300:];v=np.array([v for i,v,d in batch]);s0,h0=moments(v,centers,dirs,E,nu,RULES[0]);s1,h1=moments(v,centers,dirs,E,nu,RULES[1]);es=np.linalg.norm((s1-s0).reshape(len(v),-1),axis=1)/np.maximum(np.linalg.norm(s1.reshape(len(v),-1),axis=1),1e-30);eh=np.linalg.norm((h1-h0).reshape(len(v),-1),axis=1)/np.maximum(np.linalg.norm(h1.reshape(len(v),-1),axis=1),1e-30)
  for j,(i,vert,depth) in enumerate(batch):
   err=max(es[j],eh[j])
   if err>tol and depth<maxdepth:
    rejected+=1;pending.extend((i,c,depth+1) for c in children(vert));continue
   hist[depth]=hist.get(depth,0)+1;SG[i]+=s1[j];HH[i]+=h1[j]
   if err>tol:unresolved+=1;max_unresolved=max(max_unresolved,float(err))
   else:max_accepted=max(max_accepted,float(err))
 return SG,HH,dict(local_relative_quadrature_estimator=tol,max_depth=maxdepth,accepted_subtetra_by_depth=hist,subdivided_cells=rejected,unresolved_cells=unresolved,maximum_unresolved_estimator=max_unresolved,maximum_accepted_estimator=max_accepted,estimator_is_rigorous_bound=False)

def main():
 start=time.monotonic();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');sp=ROOT/'validation/integrated'/sys.argv[2]/'summary.json';s=json.loads(sp.read_text());tol=float(sys.argv[3]);depth=int(sys.argv[4]);dump(out/'inputs.json',dict(candidate=s['candidate'],source=ref(sp),producer=ref(out/'producer.py'),dependencies=[ref(ROOT/'scripts/primary_finite_body34.py')],tolerance=tol,max_depth=depth,scope='Same4actual finitebody geometry/DOFs/conditional patch and source modes. Positive5/6Keast local integration estimator with8subtetra; NOT a rigorous integration bound or criterion change. Original1percent response and force checks unchanged.'))
 results=[]
 for row in s['results']:
  bs=time.monotonic();a=np.load(REPO/row['fields']['path']);p=a['points_mm'];t=a['tetra'];N=3*len(p);M=a['F'].shape[1];E=row['conditional_E_MPa'];nu=row['conditional_nu'];mu=E/(2*(1+nu));la=E*nu/((1+nu)*(1-2*nu));msh=MeshTet(p.T,t.T);K=sparse.csr_matrix((N,N));el=ElementVector(ElementTetP1())
  for first in range(0,len(t),8000):K+=asm(linear_elasticity(la,mu),Basis(msh,el,intorder=2,elements=np.arange(first,min(first+8000,len(t)))))
  sg,hh,info=integrate(p,t,a['centers_mm'],a['directions'],E,nu,tol,depth);G=np.zeros_like(a['G']);H=hh.sum(0);force=np.einsum('tmij,taj->taim',sg,a['gradient_N'])
  for j in range(4):
   for axis in range(3):np.add.at(G,3*t[:,j]+axis,force[:,j,axis,:])
  Q=a['Q'];factor=splu(sparse.bmat([[K,sparse.csr_matrix(Q.T)],[sparse.csr_matrix(Q),None]],format='csc'));UG=factor.solve(np.vstack([G,np.zeros((6,M))]))[:N];UF=a['UF'];F=a['F'];L=a['L'];S=H-G.T@UG;S=(S+S.T)/2;d=L-G.T@UF;alpha=np.linalg.solve(S,d);v=UF-UG@alpha;C=F.T@UF+d.T@alpha;C=(C+C.T)/2;energy=v.T@K@v+v.T@G@alpha+alpha.T@G.T@v+alpha.T@H@alpha;res=max(abs(K@v+G@alpha-F).max(),abs(G.T@v+H@alpha-L).max());bo=out/row['part'];bo.mkdir();fields={k:a[k] for k in a.files};fields.update(G=G,H=H,UG=UG,S=S,alpha=alpha,VFE=v,compliance=C);np.savez_compressed(bo/'fields.npz',**fields);rr=dict(row);rr.update(fields=ref(bo/'fields.npz'),quadrature_order='adaptive_positive_5_6',adaptive_integration=info,compliance_enriched_mm_N=C.tolist(),regular_mode_work_eigenvalues=np.linalg.eigvalsh(S).tolist(),unit_stationarity_N=float(res),energy_identity_relative=float(np.linalg.norm(energy-C)/np.linalg.norm(C)),enrichment_compliance_relative=float(np.linalg.norm(C-F.T@UF)/np.linalg.norm(C)),compliance_change_from_unadapted_relative=float(np.linalg.norm(C-a['compliance'])/np.linalg.norm(C)),elapsed_s=time.monotonic()-bs,free_end_raw_traction_max_MPa_per_unit_N=None,free_end_raw_stress_trace_samples=0,free_surface_pointwise_qualified=False)
  rr['checks']=dict(positive_regular_mode_work=bool(np.linalg.eigvalsh(S).min()>0),positive_elastic_work=bool(np.linalg.eigvalsh(C).min()>0),stationarity=bool(res<1e-8),elastic_work=bool(np.linalg.norm(energy-C)/np.linalg.norm(C)<1e-8),no_unresolved_integration_cells=info['unresolved_cells']==0);dump(bo/'summary.json',rr);results.append(rr);print(json.dumps(rr),flush=True)
 checks=dict(all4bodies=len(results)==4,local_variational_and_estimator_checks=all(all(r['checks'].values()) for r in results));dump(out/'summary.json',dict(status='ACTUAL_P1_ADAPTIVE_FINITE_BODY_OPERATOR_CONDITIONAL' if all(checks.values()) else 'ACTUAL_P1_ADAPTIVE_FINITE_BODY_OPERATOR_FAIL',candidate=s['candidate'],inputs=ref(out/'inputs.json'),checks=checks,results=results,newly_qualified_system_gate_ids=[],accepted_product_equilibria=0,whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['Integration estimator is not independent quadrature certification. Finitebody mesh/endtraction,exact curvedcontact geometry,real clamp/source coupling and physical material minima remain unqualified.','Same prescribed .3rad open-gap load sensitivity; not accepted contact,4port load split,100g demand,physical support/globalenergy or release. No CAD change.']))
if __name__=='__main__':main()
