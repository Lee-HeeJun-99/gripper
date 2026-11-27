"""Independent quadratic shape/Jacobian/positive-Duffy weak-force audit.
No producer, skfem, gmsh assembler or solver imports. Actual stored P1 solid meshes.
"""
import sys,json,time,shutil
import numpy as np
from baseline_registry import ROOT,REPO,ref,sha,dump

def shape(x):
 l=np.concatenate([1-x.sum(-1,keepdims=True),x],axis=-1);dl=np.array([[-1,-1,-1],[1,0,0],[0,1,0],[0,0,1]])
 N=[l[...,i]*(2*l[...,i]-1) for i in range(4)];D=[(4*l[...,i,None]-1)*dl[i] for i in range(4)]
 for i,j in [(0,1),(1,2),(0,2),(0,3),(1,3),(2,3)]:N.append(4*l[...,i]*l[...,j]);D.append(4*(l[...,i,None]*dl[j]+l[...,j,None]*dl[i]))
 return np.stack(N,-1),np.stack(D,-2)

def rule(n):
 z,w=np.polynomial.legendre.leggauss(n);z=(z+1)/2;w=w/2;u,v,a=np.meshgrid(z,z,z,indexing='ij');wu,wv,wa=np.meshgrid(w,w,w,indexing='ij');return np.array([u,(1-u)*v,(1-u)*(1-v)*a]).reshape(3,-1).T,(wu*wv*wa*(1-u)**2*(1-v)).ravel()

def audit(row,n):
 a=np.load(REPO/row['fields']['path']);p=a['points_mm'].T;ed=a['element_dofs'].T;t=a['tetra'].T;U=a['U'];M=U.shape[1];uv=U.reshape(len(p),3,M);E=row['conditional_E_MPa'];nu=row['conditional_nu'];mu=E/(2*(1+nu));la=E*nu/((1+nu)*(1-2*nu));x,w=rule(n);N,D=shape(x);internal=np.zeros_like(U);work=np.zeros((M,M));volume=0.;fold=0
 for first in range(0,len(ed),100):
  assert not(ROOT/'runtime/STOP').exists();ids=ed[first:first+100];coords=p[ids];J=np.einsum('tai,qaj->tqij',coords,D);det=np.linalg.det(J);fold+=int(np.sum(det.min(1)*det.max(1)<=0));grad=np.einsum('qaj,tqji->tqai',D,np.linalg.inv(J));gu=np.einsum('taim,tqaj->tqmij',uv[ids],grad);eps=(gu+gu.swapaxes(-1,-2))/2;sig=2*mu*eps+la*np.trace(eps,axis1=-2,axis2=-1)[...,None,None]*np.eye(3);weight=abs(det)*w;volume+=weight.sum();work+=np.einsum('tqmij,tqnij,tq->mn',eps,sig,weight);force=np.einsum('tqmij,tqaj,tq->taim',sig,grad,weight)
  for j in range(10):
   for axis in range(3):np.add.at(internal,3*ids[:,j]+axis,force[:,j,axis,:])
 F=a['F'];res=float(abs(internal-F).max());en=float(abs(work-a['compliance']).max()/abs(a['compliance']).max());checks=dict(shape_partition=bool(abs(N.sum(-1)-1).max()<1e-12),shape_gradient_partition=bool(abs(D.sum(-2)).max()<1e-12),no_sampled_mapping_fold=fold==0,independent_work1percent=en<.01,independent_force1e_minus8=res<1e-8)
 result=dict(part=row['part'],source_fields=row['fields'],positive_Duffy_points_per_tetra=n**3,independent_force_max_N=res,independent_force_original1e_minus8_pass=res<1e-8,independent_energy_relative=en,independent_volume_mm3=float(volume),checks=checks)
 if 'boundary_reference' in a:
  xi=a['boundary_reference'].transpose(1,2,0);bn,bd=shape(xi);owner=a['boundary_owner'];coords=p[ed[owner]];reconstructed=np.einsum('fqa,fai->ifq',bn,coords);boundaryF=np.zeros_like(F);tr=a['traction'];weights=a['facet_weights'];local=np.einsum('fqa,mifq,fq->faim',bn,tr,weights)
  for j in range(10):
   for axis in range(3):np.add.at(boundaryF,3*ed[owner,j]+axis,local[:,j,axis,:])
  rng=np.random.default_rng(35);test=rng.normal(size=(len(p),3));qtest=np.einsum('fqa,fai->ifq',bn,test[ed[owner]]);nodalwork=test.ravel()@F;surfacework=np.einsum('ifq,mifq,fq->m',qtest,tr,weights);bforce=float(abs(boundaryF-F).max());vwork=float(abs(nodalwork-surfacework).max());geom=float(abs(reconstructed-a['facet_coordinates']).max())
  result.update(independent_boundary_force_error_N=bforce,arbitrary_nodal_virtual_work_error_Nmm=vwork,independent_geometry_interpolation_error_mm=geom)
  checks.update(independent_load_shape_work=bforce<1e-10,independent_arbitrary_virtual_work=vwork<1e-10,independent_geometry_mapping=geom<1e-10)
 return result

def main():
 start=time.monotonic();tag,n,*names=sys.argv[1:];out=ROOT/'validation/integrated'/tag;out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');results=[];sources=[]
 for name in names:
  sp=ROOT/'validation/integrated'/name/'summary.json';s=json.loads(sp.read_text());sources.append(ref(sp))
  for row in s['results']:
   assert sha(REPO/row['fields']['path'])==row['fields']['SHA256'];r=audit(row,int(n));r['run']=name;results.append(r);print(json.dumps(r),flush=True)
 cp=ROOT/'cad/exports/primaryP1_ycapture24/summary.json';dump(out/'summary.json',dict(status='ACTUAL_P1_CURVED_BODY_INDEPENDENT_FORCE_WORK_AUDIT',candidate=ref(cp),sources=sources,verifier=ref(out/'verifier.py'),results=results,independent_force_all_original_tolerance=all(r['checks']['independent_force1e_minus8'] for r in results),accepted_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['Independent positive Duffy force integration of conditional finite-body test loads, not actual clamp/contact equilibrium.','Original1e-8N force and1percent response criteria retained. Small energy error never supersedes force failure.','Independent boundary virtual work reuses saved surface quadrature; this verifies trace action, NOT independent surface integration convergence or exact rational CAD.']))
if __name__=='__main__':main()
