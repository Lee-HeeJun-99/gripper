"""Actual P1 isoparametric quadratic finite-body Neumann sensitivities.
Not physical pressure, clamp closure, operating demand, or release evidence.
"""
import sys,json,time,shutil,gc
import numpy as np
import gmsh
from scipy import sparse
from scipy.sparse.linalg import splu
from skfem import MeshTet2,Basis,FacetBasis,ElementTetP2,ElementVector,asm
from skfem.mapping import MappingIsoparametric
from skfem.models.elasticity import linear_elasticity,lame_parameters
from baseline_registry import ROOT,REPO,ref,sha,dump
from primary_finite_body34 import wrenchmat

def duffy(n,dim):
 a,w=np.polynomial.legendre.leggauss(n);a=(a+1)/2;w=w/2
 if dim==3:
  u,v,z=np.meshgrid(a,a,a,indexing='ij');wu,wv,wz=np.meshgrid(w,w,w,indexing='ij');return np.array([u,(1-u)*v,(1-u)*(1-v)*z]).reshape(3,-1),(wu*wv*wz*(1-u)**2*(1-v)).ravel()
 u,v=np.meshgrid(a,a,indexing='ij');wu,wv=np.meshgrid(w,w,indexing='ij');return np.array([u,(1-u)*v]).reshape(2,-1),(wu*wv*(1-u)).ravel()

def mesh(path,h,curv):
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1);gmsh.model.add('actual_primary_P2');v=gmsh.model.occ.importShapes(str(path));gmsh.model.occ.synchronize();vol=sum(gmsh.model.occ.getMass(d,t) for d,t in v)
 for key,val in [('Mesh.MeshSizeMax',h),('Mesh.MeshSizeMin',.04),('Mesh.MeshSizeFromCurvature',curv),('Mesh.SecondOrderLinear',0)]:gmsh.option.setNumber(key,val)
 gmsh.model.mesh.generate(3);gmsh.model.mesh.setOrder(2)
 nt,p,_=gmsh.model.mesh.getNodes();ix=np.argsort(nt);nt=np.array(nt)[ix];p=np.array(p).reshape(-1,3)[ix];types,_,elements=gmsh.model.mesh.getElements(3);raw=np.concatenate([np.array(a).reshape(-1,10) for k,a in zip(types,elements) if k==11]);local=np.array(gmsh.model.mesh.getElementProperties(11)[4]).reshape(-1,3)
 expected=ElementTetP2().doflocs;perm=np.array([np.argmin(np.linalg.norm(local-q,axis=1)) for q in expected]);assert len(set(perm))==10
 t=np.searchsorted(nt,raw[:,perm]);gmsh.finalize();m=MeshTet2(p.T,t.T);return m,vol

def integrate_load(fb,traction):
 f=np.zeros(3*fb.N)
 for i,b in enumerate(fb.basis):
  for a in range(3):np.add.at(f,3*fb.element_dofs[i]+a,np.sum(b[0]*traction[a]*fb.dx,axis=1))
 return f

def solve(out,part,cad,geo,h,curv,order):
 start=time.monotonic();po=out/part;po.mkdir();E=200000.;nu=.3;m,vol=mesh(REPO/cad['part_references'][part]['path'],h,curv);el=ElementVector(ElementTetP2());N=3*m.doflocs.shape[1];K=sparse.csr_matrix((N,N));la,mu=lame_parameters(E,nu);meshvol=0.;mindet=float('inf');inverted=0
 for first in range(0,m.nelements,400):
  assert not(ROOT/'runtime/STOP').exists();b=Basis(m,el,mapping=MappingIsoparametric(m,m.elem(),m.bndelem),**({'quadrature':duffy(order-5,3)} if order>=10 else {'intorder':order}),elements=np.arange(first,min(first+400,m.nelements)));K+=asm(linear_elasticity(la,mu),b);meshvol+=b.dx.sum();det=b.mapping.detDF(b.X,tind=b.tind);mindet=min(mindet,float(np.min(abs(det))));inverted+=int(np.sum(det.min(axis=1)*det.max(axis=1)<=0));del b;gc.collect()
 p=m.doflocs.T;r=p-p.mean(0);length=np.sqrt(np.mean(np.sum(r*r,axis=1)));Q=np.zeros((6,N));R=np.zeros((N,6))
 for j,axis in enumerate(np.eye(3)):R[:,j]=np.broadcast_to(axis,p.shape).ravel();R[:,j+3]=np.cross(axis,r).ravel()/length
 Q=R.T/len(p);A=sparse.bmat([[K/E,sparse.csr_matrix(Q.T)],[sparse.csr_matrix(Q),None]],format='csc');gc.collect()
 fb=FacetBasis(m,ElementTetP2(),**({'quadrature':duffy(order-3,2)} if order>=10 else {'intorder':order}));x=np.array(fb.global_coordinates());normal=np.array(fb.normals);root=part=='F0_ROOT_BACK';ports=list(range(4)) if root else [i for i,g in enumerate(geo) if g['part']==part];F=[];journals=[];geometry=[];sourcex=50.5 if root or 'RAIL' in part else 50.
 src=(np.abs(x[0]-sourcex)<1e-7)&(x[2]>3);H=wrenchmat(x.reshape(3,-1).T).reshape(x.shape[1],x.shape[2],6,3);M=np.einsum('fqai,fqbi,fq->ab',H,H,fb.dx*src)
 for port in ports:
  g=geo[port];yc,zc=g['pin']['axis_point_mm'][1:];radius=1. if root else 1.05;lo=max(g['pin']['bounds_mm'][0],g['hole']['bounds_mm'][0]);hi=min(g['pin']['bounds_mm'][3],g['hole']['bounds_mm'][3]);rad=np.sqrt((x[1]-yc)**2+(x[2]-zc)**2);theta=np.arctan2(x[2]-zc,x[1]-yc)
  # Facet identity from all corner vertices, never select another surface by sampled proximity.
  verts=m.p[:,m.facets[:,fb.find]];rv=np.sqrt((verts[1]-yc)**2+(verts[2]-zc)**2);cylinder=np.all(abs(rv-radius)<1e-7,axis=0)
  axial=(x[0]-lo)/(hi-lo);mask=cylinder[:,None]&(abs(theta)<.3)&(axial>0)&(axial<1);profile=np.where(mask,np.cos(np.pi*theta/.6)**2*np.sin(np.pi*axial)**2,0.)
  n=np.array([np.zeros_like(rad),(x[1]-yc)/rad,(x[2]-zc)/rad]);tr=(-1 if root else 1)*n*profile;scale=abs(np.sum(tr[1]*fb.dx));assert scale>0;tr/=scale;W=np.einsum('fqai,ifq,fq->a',H,tr,fb.dx);coeff=np.linalg.solve(M,-W);source=np.einsum('fqai,a->ifq',H,coeff)*src;total=tr+source;f=integrate_load(fb,total);F.append(f);j=np.flatnonzero(mask.ravel());geometry.append(dict(global_port=port,sampled_points=len(j),radial_error_mm=float(np.max(abs(rad.ravel()[j]-radius))),normal_error=float(np.max(np.linalg.norm(np.cross(normal.transpose(1,2,0).reshape(-1,3)[j],n.transpose(1,2,0).reshape(-1,3)[j]),axis=1))),contact_wrench_N_Nmm=W.tolist(),source_wrench_N_Nmm=np.einsum('fqai,ifq,fq->a',H,source,fb.dx).tolist()))
  journals.append(total)
 F=np.array(F).T;factor=splu(A);sol=factor.solve(np.vstack([F/E,np.zeros((6,len(ports)))]));U=sol[:N];dual=sol[N:]*E;del factor;gc.collect();C=F.T@U;res=float(np.max(abs(K@U-F)));rigid=float(np.max(abs(R.T@F)));energy=U.T@K@U;traces=[]
 # Actual free-end only; excludes source-loaded planar region z>=3.
 end=48.5 if root else (50. if part=='F0_ROOT_FRONT' else 50.3);free=(abs(x[0]-end)<1e-8)&(x[2]<3-1e-8)
 for j in range(len(ports)):
  grad=np.array([fb.interpolate(U[a::3,j]).grad for a in range(3)]);eps=(grad+grad.swapaxes(0,1))/2;sig=2*mu*eps+la*np.einsum('iifq->fq',eps)[None,None]*np.eye(3)[:,:,None,None];tn=np.einsum('ijfq,jfq->ifq',sig,normal);mag=np.linalg.norm(tn,axis=0);traces.append(dict(global_port=ports[j],free_end_area_mm2=float(np.sum(fb.dx*free)),free_end_traction_L2_MPa_sqrt_mm2=float(np.sqrt(np.sum(mag**2*fb.dx*free))),free_end_max_MPa=float(mag[free].max())))
 np.savez_compressed(po/'fields.npz',points_mm=m.doflocs,tetra=m.t,element_dofs=m.dofs.element_dofs,F=F,U=U,Q=Q,R=R,compliance=C,facet_coordinates=x,facet_weights=fb.dx,facet_normals=normal,traction=np.array(journals),boundary_facets=fb.find,boundary_owner=fb.tind,boundary_reference=fb.mapping.invF(x,tind=fb.tind))
 checks=dict(candidate_hash=sha(REPO/cad['part_references'][part]['path'])==cad['part_references'][part]['SHA256'],positive_volume=bool(meshvol>0),no_sampled_mapping_fold=inverted==0,volume_original1percent=bool(abs(meshvol/vol-1)<.01),positive_work=bool(np.linalg.eigvalsh((C+C.T)/2).min()>0),discrete_force1e_minus8=bool(res<1e-8),rigid_force1e_minus8=bool(rigid<1e-8),energy_identity=bool(np.max(abs(C-energy))/np.max(abs(C))<1e-8),six_gauge_motion=bool(np.max(abs(Q@U))<1e-8))
 result=dict(part=part,part_reference=cad['part_references'][part],nodes=len(p),tetra=m.nelements,DOF=N,conditional_E_MPa=E,conditional_nu=nu,material_minimum_qualified=False,fields=ref(po/'fields.npz'),checks=checks,mesh_volume_mm3=float(meshvol),CAD_volume_mm3=vol,minimum_sampled_abs_mapping_determinant=mindet,unit_force_residual_N=res,rigid_resultant_residual_N=rigid,gauge_dual_max_N=float(abs(dual).max()),compliance_mm_N=C.tolist(),geometry=geometry,free_end=traces,elapsed_s=time.monotonic()-start)
 dump(po/'summary.json',result);print(json.dumps(result),flush=True);return result

def main():
 tag,h,curv,order,*parts=sys.argv[1:];out=ROOT/'validation/integrated'/tag;out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_ycapture24/summary.json';cad=json.loads(cp.read_text());gp=ROOT/'validation/integrated/primaryP1_gamma_attachment29/pin_hole_geometry.json';geo=json.loads(gp.read_text())
 assert len(cad['part_references'])==78
 for v in cad['part_references'].values():assert sha(REPO/v['path'])==v['SHA256']
 dump(out/'inputs.json',dict(candidate=ref(cp),geometry=ref(gp),producer=ref(out/'producer.py'),dependency=ref(ROOT/'scripts/primary_finite_body34.py'),h_mm=float(h),curvature_elements=int(curv),integration_order=int(order),load_definition='NEW smooth conditional port sensitivity: cos(pi theta/.6)^2 sin(pi(x-lo)/(hi-lo))^2 inside |theta|<.3 and actual finite overlap. Unit signed Fy; actual source planar face six-resultant return. Not identical to34uniform patch; never a convergence comparison against34.',source='Actual planar trace; six-resultant test functional, NOT real clamp/stack solution.',material='Conditional E200000MPa nu.3 only; actual minima unqualified.'))
 results=[solve(out,part,cad,geo,float(h),int(curv),int(order)) for part in (parts or ['F0_ROOT_BACK','F0_ROOT_FRONT','F0_RAIL_L','F0_RAIL_R'])]
 dump(out/'summary.json',dict(status='ACTUAL_P1_CURVED_QUADRATIC_FINITE_BODY_CONDITIONAL',candidate=ref(cp),inputs=ref(out/'inputs.json'),results=results,all_local_checks=all(all(r['checks'].values()) for r in results),accepted_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,actual_CAD_change_files=[],limitations=['Quadratic CAD-projected nodal geometry is NOT exact rational cylinder; offnode radial/normal error explicitly measured.','Finite-body P2 weak Neumann solution; raw unloaded-end stress is not certified zero. No fixed Root or physical balancing load.','New smooth prescribed traction/source sensitivities are NOT contact pressure, actual fourport split, operating load, clamp, minimum material, strength, assembly or globalenergy qualification. Original34Kelvin/Ritz and all failures preserved.']))
if __name__=='__main__':main()
