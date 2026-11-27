"""Actual P1 finite-body Kelvin/Ritz enrichment, conditional Neumann operators.
All original elastic DOFs are retained. No halfspace compliance subtraction.
Not a contact solution: positive patch traction remains a prescribed sensitivity.
"""
import sys,json,time,shutil
import numpy as np
import gmsh
from scipy import sparse
from scipy.sparse.linalg import splu
from skfem import MeshTet,Basis,ElementTetP1,ElementVector,asm
from skfem.models.elasticity import linear_elasticity,lame_parameters
from skfem.quadrature import get_quadrature_tet
from baseline_registry import ROOT,REPO,ref,sha,dump
from primary_pin_compliance31 import clip

I=np.eye(3)
def kelvin(x,centers,directions,E,nu):
 """Full-space Navier displacement and exact gradient; singularities OUTSIDE solid."""
 r=x[...,None,:]-centers;rr=np.linalg.norm(r,axis=-1);dot=np.einsum('...mi,mi->...m',r,directions)
 c=1/(16*np.pi*(E/(2*(1+nu)))*(1-nu));a=3-4*nu
 u=c*(a*directions/rr[...,None]+dot[...,None]*r/rr[...,None]**3)
 G=c*(-a*np.einsum('mi,...mj->...mij',directions,r)/rr[...,None,None]**3+np.einsum('...mi,mj->...mij',r,directions)/rr[...,None,None]**3+dot[...,None,None]*I/rr[...,None,None]**3-3*dot[...,None,None]*np.einsum('...mi,...mj->...mij',r,r)/rr[...,None,None]**5)
 eps=(G+G.swapaxes(-1,-2))/2
 return u,eps

def stress(eps,E,nu):
 mu=E/(2*(1+nu));la=E*nu/((1+nu)*(1-2*nu))
 return 2*mu*eps+la*np.trace(eps,axis1=-2,axis2=-1)[...,None,None]*I

def wrenchmat(x):
 H=np.zeros((len(x),6,3));H[:,:3]=I
 H[:,3:,0]=np.c_[np.zeros(len(x)),x[:,2],-x[:,1]]
 H[:,3:,1]=np.c_[-x[:,2],np.zeros(len(x)),x[:,0]]
 H[:,3:,2]=np.c_[x[:,1],-x[:,0],np.zeros(len(x))]
 return H

def meshpart(path,h,curv):
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1);gmsh.model.add('actualP1finitebody');vs=gmsh.model.occ.importShapes(str(path));gmsh.model.occ.synchronize();V=sum(gmsh.model.occ.getMass(d,t) for d,t in vs)
 gmsh.option.setNumber('Mesh.MeshSizeMax',h);gmsh.option.setNumber('Mesh.MeshSizeMin',.04);gmsh.option.setNumber('Mesh.MeshSizeFromCurvature',curv);gmsh.model.mesh.generate(3)
 nt,p,_=gmsh.model.mesh.getNodes();order=np.argsort(nt);nt=np.array(nt)[order];p=np.array(p).reshape(-1,3)[order]
 ty,_,e=gmsh.model.mesh.getElements(3);t=np.concatenate([np.searchsorted(nt,np.array(a).reshape(-1,4)) for k,a in zip(ty,e) if k==4]);ty,_,e=gmsh.model.mesh.getElements(2);tri=np.concatenate([np.searchsorted(nt,np.array(a).reshape(-1,3)) for k,a in zip(ty,e) if k==2]);gmsh.finalize();ids=np.unique(t);return p[ids],np.searchsorted(ids,t),np.searchsorted(ids,tri),V

def loads(p,tri,part,geo,angle):
 """Exact-axis radial direction on clipped FACETS; surface quadrature retained."""
 root=part=='F0_ROOT_BACK';ports=list(range(4)) if root else [i for i,g in enumerate(geo) if g['part']==part];m=len(ports);N=len(p);F=np.zeros((3*N,m));journal=[];centers=[];dirs=[]
 # Explicit conditional source interface, NOT physical clamp stiffness or a fixture.
 source_x=50.5 if root or 'RAIL' in part else 50.
 source=tri[np.all(abs(p[tri,0]-source_x)<1e-7,axis=1)&np.all(p[tri,2]>=3-1e-8,axis=1)]
 assert len(source)>0,(part,'empty source interface')
 sq=[]
 for tr in source:
  pts=p[tr];ar=np.linalg.norm(np.cross(pts[1]-pts[0],pts[2]-pts[0]))/2
  for bc in [[2/3,1/6,1/6],[1/6,2/3,1/6],[1/6,1/6,2/3]]:sq.append((tr,np.array(bc),np.array(bc)@pts,ar/3))
 spos=np.array([q[2] for q in sq]);sa=np.array([q[3] for q in sq]);H=wrenchmat(spos);M=np.einsum('qai,qbi,q->ab',H,H,sa)
 for j,port in enumerate(ports):
  g=geo[port];yc,zc=g['pin']['axis_point_mm'][1:];radius=1. if root else 1.05;lo=max(g['pin']['bounds_mm'][0],g['hole']['bounds_mm'][0]);hi=min(g['pin']['bounds_mm'][3],g['hole']['bounds_mm'][3]);qs=[]
  for tr in tri:
   pts=p[tr];rad=pts[:,1:]-[yc,zc]
   if np.max(abs(np.linalg.norm(rad,axis=1)-radius))>1e-6 or np.ptp(pts[:,0])<1e-8:continue
   poly=[a.copy() for a in pts]
   for ax,value,above in [(0,lo,True),(0,hi,False),(1,yc+radius*np.cos(angle),True)]:
    if poly:poly=clip(poly,ax,value,above)
   if len(poly)<3:continue
   pinv=np.linalg.pinv(np.column_stack([pts[1]-pts[0],pts[2]-pts[0]]))
   for k in range(1,len(poly)-1):
    sub=np.array([poly[0],poly[k],poly[k+1]]);ar=np.linalg.norm(np.cross(sub[1]-sub[0],sub[2]-sub[0]))/2
    if ar<1e-15:continue
    for bcsub in [[2/3,1/6,1/6],[1/6,2/3,1/6],[1/6,1/6,2/3]]:
     q=np.array(bcsub)@sub;bc2=pinv@(q-pts[0]);bc=np.r_[1-bc2.sum(),bc2];n=np.r_[0.,q[1:]-[yc,zc]];n/=np.linalg.norm(n);qs.append((tr,bc,q,ar/3,(-1 if root else 1)*n))
  assert len(qs)>0,(part,port,'empty pressure port');normalization=abs(sum(ar*n[1] for tr,bc,q,ar,n in qs));W=np.zeros(6)
  for tr,bc,q,ar,n in qs:
   force=ar*n/normalization;W+=wrenchmat(q[None])[0]@force
   for k,node in enumerate(tr):F[3*node:3*node+3,j]+=bc[k]*force
   journal.append(dict(port=j,global_port=port,kind='conditional_contact_patch',nodes=tr.tolist(),barycentric=bc.tolist(),point_mm=q.tolist(),force_N=force.tolist(),area_mm2=ar))
  coeff=np.linalg.solve(M,-W)
  for (tr,bc,q,ar),hq in zip(sq,H):
   force=ar*(hq.T@coeff)
   for k,node in enumerate(tr):F[3*node:3*node+3,j]+=bc[k]*force
   journal.append(dict(port=j,global_port=port,kind='conditional_six_resultant_source',nodes=tr.tolist(),barycentric=bc.tolist(),point_mm=q.tolist(),force_N=force.tolist(),area_mm2=ar))
  centers.append([(lo+hi)/2,yc+radius,zc]);dirs.append([0.,-1. if root else 1.,0.])
 return F,journal,np.array(centers),np.array(dirs),dict(source_x_mm=source_x,source_z_min_mm=3.,source_area_mm2=float(sa.sum()),global_ports=ports,pressure_angle_rad=angle,source_is_actual_clamp_solution=False)

def body(out,part,cad,geo,h,curv,order,offset):
 start=time.monotonic();E=200000.;nu=.3;partout=out/part;partout.mkdir();p,t,tri,cadV=meshpart(REPO/cad['part_references'][part]['path'],h,curv);N=3*len(p);msh=MeshTet(p.T,t.T);el=ElementVector(ElementTetP1());la,mu=lame_parameters(E,nu);K=sparse.csr_matrix((N,N))
 for first in range(0,len(t),8000):
  assert not(ROOT/'runtime/STOP').exists();K+=asm(linear_elasticity(la,mu),Basis(msh,el,intorder=2,elements=np.arange(first,min(first+8000,len(t)))))
 dx=p[t[:,1:]]-p[t[:,0,None]];inv=np.linalg.inv(dx);V=abs(np.linalg.det(dx))/6;grad=np.concatenate([-inv.sum(2)[:,None,:],inv.transpose(0,2,1)],axis=1);lump=np.zeros(len(p))
 for j in range(4):np.add.at(lump,t[:,j],V/4)
 origin=np.average(p,weights=lump,axis=0);r=p-origin;wt=lump/lump.sum();length=np.sqrt(np.average(np.sum(r*r,axis=1),weights=lump));Q=[]
 for axis in I:Q.append((wt[:,None]*axis).ravel())
 for axis in I:Q.append((wt[:,None]*np.cross(axis,r)/length).ravel())
 Q=np.array(Q);R=np.zeros((N,6))
 for j,axis in enumerate(I):R[:,j]=np.broadcast_to(axis,p.shape).ravel();R[:,j+3]=np.cross(axis,r).ravel()/length
 qr=Q@R;A=sparse.bmat([[K,sparse.csr_matrix(Q.T)],[sparse.csr_matrix(Q),None]],format='csc');factor=splu(A)
 F,journal,centers,dirs,source=loads(p,tri,part,geo,.3);centers[:,1]+=(1 if part=='F0_ROOT_BACK' else -1)*offset;M=F.shape[1]
 # Independent analytic Kelvin modes outside actual pin/bore; all modes share ONE variational form.
 un,ep=kelvin(p,centers,dirs,E,nu);un=un.transpose(0,2,1).reshape(N,M);gauge=np.linalg.solve(qr,Q@un);un-=R@gauge
 # Boundary load action on enrichment integrated on same finite traction quadrature, not guessed compliance.
 L=np.zeros((M,M))
 for row in journal:
  q=np.array(row['point_mm']);uh,_=kelvin(q[None],centers,dirs,E,nu);rr=q-origin;rb=np.c_[I,-np.array([[0,-rr[2],rr[1]],[rr[2],0,-rr[0]],[-rr[1],rr[0],0]])/length];uh=uh[0].T-rb@gauge;L[:,row['port']]+=uh.T@row['force_N']
 x,w=get_quadrature_tet(order);assert w.min()>0;bc=np.vstack([1-x.sum(0),x]).T;G=np.zeros((N,M));H=np.zeros((M,M))
 for first in range(0,len(t),1200):
  assert not(ROOT/'runtime/STOP').exists();sl=slice(first,min(first+1200,len(t)));tt=t[sl];pos=np.einsum('qa,tai->tqi',bc,p[tt]);_,eps=kelvin(pos,centers,dirs,E,nu);sig=stress(eps,E,nu);weights=V[sl,None]*6*w;H+=np.einsum('tqkij,tqlij,tq->kl',eps,sig,weights);sg=np.einsum('tqmij,tq->tmij',sig,weights);ef=np.einsum('tmij,taj->taim',sg,grad[sl])
  for j in range(4):
   for axis in range(3):np.add.at(G,3*tt[:,j]+axis,ef[:,j,axis,:])
 rhs=np.column_stack([F,G]);sol=factor.solve(np.vstack([rhs,np.zeros((6,2*M))]));UF=sol[:N,:M];UG=sol[:N,M:];dual=sol[N:];S=(H-G.T@UG);S=(S+S.T)/2;d=L-G.T@UF;eig=np.linalg.eigvalsh(S);alpha=np.linalg.solve(S,d);VFE=UF-UG@alpha;C=F.T@UF+d.T@alpha;C=(C+C.T)/2
 internal=K@VFE+G@alpha;stationarity=max(abs(internal-F).max(),abs(G.T@VFE+H@alpha-L).max());energy=VFE.T@K@VFE+VFE.T@G@alpha+alpha.T@G.T@VFE+alpha.T@H@alpha
 free=tri[np.all(abs(p[tri,0]-(48.5 if part=='F0_ROOT_BACK' else (50. if part=='F0_ROOT_FRONT' else 50.3)))<1e-7,axis=1)]
 # Actual finite end raw stress trace, NOT a weak residual or pointwise certificate.
 owner={tuple(sorted(face)):i for i,tt in enumerate(t) for face in [tt[[1,2,3]],tt[[0,2,3]],tt[[0,1,3]],tt[[0,1,2]]] if tuple(sorted(face)) in set()} if False else {}
 need={tuple(sorted(tr)) for tr in free}
 for i,tt in enumerate(t):
  for face in [tt[[1,2,3]],tt[[0,2,3]],tt[[0,1,3]],tt[[0,1,2]]]:
   key=tuple(sorted(face))
   if key in need:owner[key]=i
 fv=VFE.reshape(len(p),3,M);traces=[]
 for tr in free:
  tid=owner[tuple(sorted(tr))];q=p[tr].mean(0);du=fv[t[tid,1:]]-fv[t[tid,0]];gradv=np.einsum('ij,jkm->kim',inv[tid],du).transpose(2,0,1);epsv=(gradv+gradv.swapaxes(1,2))/2;_,eh=kelvin(q[None],centers,dirs,E,nu);st=stress(epsv+np.einsum('kij,km->mij',eh[0],alpha),E,nu);traces.append(np.linalg.norm(st[:,:,0],axis=1))
 trace=np.array(traces);np.savez_compressed(partout/'fields.npz',points_mm=p,tetra=t,boundary_triangles=tri,volume_mm3=V,gradient_N=grad,F=F,G=G,H=H,L=L,UF=UF,UG=UG,VFE=VFE,alpha=alpha,S=S,Q=Q,R=R,gauge=gauge,centers_mm=centers,directions=dirs,compliance=C,dual=dual)
 dump(partout/'traction_quadrature.json',journal)
 checks=dict(nonzero_body_volume=bool(V.sum()>0),volume_original1percent=bool(abs(V.sum()/cadV-1)<.01),six_gauges_only=bool(np.linalg.matrix_rank(qr)==6),gauge_force_negligible=bool(abs(dual[:,:M]).max()<1e-8),positive_regular_mode_work=bool(eig.min()>0),positive_total_elastic_work=bool(np.linalg.eigvalsh(C).min()>0),variational_stationarity=bool(stationarity<1e-8),work_identity=bool(abs(energy-C).max()/abs(C).max()<1e-8),gauge_motion=bool(abs(Q@VFE).max()<1e-8))
 result=dict(part=part,part_reference=cad['part_references'][part],fields=ref(partout/'fields.npz'),quadrature=ref(partout/'traction_quadrature.json'),nodes=len(p),tetra=len(t),DOF=N,conditional_E_MPa=E,conditional_nu=nu,material_source_minimum_qualified=False,source=source,quadrature_order=order,source_offset_mm=offset,checks=checks,mesh_volume_mm3=float(V.sum()),CAD_volume_mm3=cadV,regular_mode_work_eigenvalues=eig.tolist(),compliance_FE_mm_N=(F.T@UF).tolist(),compliance_enriched_mm_N=C.tolist(),enrichment_compliance_relative=float(np.linalg.norm(C-F.T@UF)/np.linalg.norm(C)),unit_stationarity_N=float(stationarity),gauge_duals_max_N=float(abs(dual[:,:M]).max()),energy_identity_relative=float(abs(energy-C).max()/abs(C).max()),free_end_raw_stress_trace_samples=len(trace),free_end_raw_traction_max_MPa_per_unit_N=float(trace.max()) if len(trace) else None,free_surface_pointwise_qualified=False,elapsed_s=time.monotonic()-start)
 dump(partout/'summary.json',result);return result

def main():
 tag,h,curv,order,offset=sys.argv[1:];h=float(h);curv=int(curv);order=int(order);offset=float(offset);out=ROOT/'validation/integrated'/tag;out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');assert not(ROOT/'runtime/STOP').exists();cp=ROOT/'cad/exports/primaryP1_ycapture24/summary.json';cad=json.loads(cp.read_text());assert len(cad['part_references'])==78 and all(sha(REPO[v['path']])==v['SHA256'] for v in [])
 for v in cad['part_references'].values():assert sha(REPO/v['path'])==v['SHA256']
 gp=ROOT/'validation/integrated/primaryP1_gamma_attachment29/pin_hole_geometry.json';geo=json.loads(gp.read_text());dump(out/'inputs.json',dict(candidate=ref(cp),geometry=ref(gp),producer=ref(out/'producer.py'),dependency=ref(ROOT/'scripts/primary_pin_compliance31.py'),h_mm=h,curvature_elements=curv,quadrature_order=order,source_offset_mm=offset,conditional_material='All4bodies E200000MPa nu.3, contrast ONLY; Front/Rail minimum source not qualified.',pressure='Prescribed .3rad radial patch, NOT solved pressure; source interface six-resultant Neumann sensitivity, NOT counterload/actual clamp/support.',derivation='a(v+Ha,w+Hb)=ell(w+Hb). Eliminate FE gauges: S=H-G^T K^+G, d=L-G^T K^+F, a=S^-1 d; C=F^T K^+F+d^T S^-1 d. H here is analytic-mode energy matrix, not displacement. This is one shared variational decomposition; no guessed diagonal subtraction, no existing halfspace compliance added. Finite free surfaces enter natural weak boundary conditions; pointwise traction and quadrature remain independent checks.'))
 results=[]
 for part in ['F0_ROOT_BACK','F0_ROOT_FRONT','F0_RAIL_L','F0_RAIL_R']:
  results.append(body(out,part,cad,geo,h,curv,order,offset));print(json.dumps(results[-1]),flush=True)
 checks=dict(all_four_actual_finite_bodies=len(results)==4,all_local_variational_checks=all(all(v['checks'].values()) for v in results));dump(out/'summary.json',dict(status='ACTUAL_P1_FINITE_BODY_VARIATIONAL_OPERATOR_CONDITIONAL' if all(checks.values()) else 'ACTUAL_P1_FINITE_BODY_VARIATIONAL_OPERATOR_FAIL',candidate=ref(cp),inputs=ref(out/'inputs.json'),checks=checks,results=results,actual_CAD_change_files=[],accepted_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Conditional finite-body Neumann sensitivity, NOT pressure/contact equilibrium or full source/clamp solution. Actual open-gap patch traction never fed to product sourcefield.','All4actual solid domains retain FE DOFs and6gauges. No fixedRoot, equalquarter load split, material minimum, actual clamp/sourceQ, 100g operating load, strength or globalenergy qualification.','Finite free boundary is variational only; raw pointwise traction and independent quadrature/mesh contrasts MUST be checked. Original1percent remains. Kelvin sources outside circular boundary are analytic enrichments, not physical applied pointforces.']))
if __name__=='__main__':main()
