"""Same actual integral55e support, P2 displacement with unchanged Neumann functional.
Boundary polynomial integrals via oriented CAD edge Green quadrature, independently
checked against exact CAD area/centroid/covariance and P1 restriction. No host tie.
"""
import sys,json,time,shutil
import numpy as np
from scipy import sparse
from scipy.linalg import qr
from scipy.sparse.linalg import cg
from skfem import MeshTet,Basis,ElementVector,ElementTetP2,LinearForm,asm
from skfem.models.elasticity import linear_elasticity,lame_parameters
from skfem.quadrature import get_quadrature_tet
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
from primary_anchor_contact38 import common_faces,planar_triangles,tri_shape,surface_moment,bary
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE,TopAbs_FACE,TopAbs_REVERSED
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.gp import gp_Pnt,gp_Vec
import pyamg

def moments(cs,pts,order):
 inv=np.linalg.pinv((pts[1:]-pts[0]).T);jac=np.linalg.norm(np.cross(pts[1]-pts[0],pts[2]-pts[0]));xx,ww=np.polynomial.legendre.leggauss(order);M=np.zeros((4,4));ex=TopExp_Explorer(cs,TopAbs_FACE)
 while ex.More():
  face=TopoDS.Face_s(ex.Current());ex.Next();ee=TopExp_Explorer(face,TopAbs_EDGE)
  while ee.More():
   edge=TopoDS.Edge_s(ee.Current());ee.Next();c=BRepAdaptor_Curve(edge);lo,hi=c.FirstParameter(),c.LastParameter();sign=-1 if edge.Orientation()==TopAbs_REVERSED else 1
   for t,w in zip((xx+1)*(hi-lo)/2+lo,ww*(hi-lo)/2):
    p=gp_Pnt();d=gp_Vec();c.D1(float(t),p,d);uv=inv@(np.array([p.X(),p.Y(),p.Z()])-pts[0]);duv=inv@np.array([d.X(),d.Y(),d.Z()])
    for a in range(4):
     for b in range(4-a):M[a,b]+=sign*w*uv[0]**(a+1)*uv[1]**b*duv[1]/(a+1)*jac
 if M[0,0]<0:M=-M
 return M

def mul(a,b):
 c=np.zeros((4,4))
 for i,j in zip(*np.nonzero(a)):
  for k,l in zip(*np.nonzero(b)):
   if i+j+k+l<=3:c[i+k,j+l]+=a[i,j]*b[k,l]
 return c

def main():
 start=time.monotonic();h=sys.argv[1];tag=sys.argv[2];out=ROOT/'validation/integrated'/tag;out.mkdir();shutil.copyfile(__file__,out/'producer.py');oldp=ROOT/f'validation/integrated/primaryP1_integral55e_h{h}/summary.json';old=json.loads(oldp.read_text());data=np.load(REPO/old['field']['path']);p=data['points_mm'];t=data['tetra'];cadp=ROOT/'cad/exports/primaryP1_integral55e/summary.json';cad=json.loads(cadp.read_text());step=REPO/cad['part_references']['BENCH_SUPPORT']['path'];assert sha(step)==cad['part_references']['BENCH_SUPPORT']['SHA256'];assert not(ROOT/'runtime/STOP').exists()
 dump(out/'inputs.json',dict(candidate=ref(cadp),STEP=ref(step),mesh_source=ref(oldp),source=ref(out/'producer.py'),h_mm=float(h),element='affine_geometry_TetP2',predeclared_contrast='Same h8/5/3 meshes,P2 versus historical P1. Original1percent all-pair energy/compliance/objectiveRootmotion;never transfer P1 stiffness.',load='EXACT SAME Rootuniform .980665N downward vertical test + distributed ownweight + given positive affine foot traction;not actual grasp',physical_fixed_DOF=0,original_criteria=dict(mesh_fraction=.01,force_N=1e-8,moment_Nm=1e-10,residual_N=1e-8,energy_fraction=1e-8),boundary_method='CAD oriented edge Green moments degree3,16vs32Gauss;exact CAD moments and inheritedP1 restriction independent checks'))
 m=MeshTet(p.T,t.T);sb=Basis(m,ElementTetP2(),intorder=4);el=ElementVector(ElementTetP2());pos=sb.doflocs.T;N=int(3*sb.N);la,mu=lame_parameters(68900,.33);K=sparse.csr_matrix((N,N));print(json.dumps(dict(stage='mesh',h=h,vertices=len(p),scalar_nodes=int(sb.N),tetra=len(t),DOF=N)),flush=True)
 @LinearForm
 def gravity(v,w):return -2700e-9*9.80665*v[2]
 F=np.zeros(N)
 for first in range(0,len(t),1200):
  assert not(ROOT/'runtime/STOP').exists();bs=Basis(m,el,intorder=4,elements=np.arange(first,min(first+1200,len(t))));K+=asm(linear_elasticity(la,mu),bs);F+=asm(gravity,bs)
 own=F.copy();center=np.array(old['conditional_mesh_COM_mm']);edges={tuple(x):int(sb.dofs.edge_dofs[0,i]) for i,x in enumerate(m.edges.T)};body=dict(p=p,tri=m.facets[:,m.boundary_facets()].T);support=read(step);journal=[];rootF=np.zeros(N);footF=np.zeros(N);maxmom=0.;maxquad=0.
 L=np.zeros((3,4,4));L[0,0,0]=1;L[0,1,0]=L[0,0,1]=-1;L[1,1,0]=1;L[2,0,1]=1;one=np.zeros((4,4));one[0,0]=1;shapes=[2*mul(a,a)-a for a in L]+[4*mul(L[i],L[j]) for i,j in [(0,1),(1,2),(0,2)]]
 def trace(face,z,coeff,target,label):
  nonlocal maxmom,maxquad
  bb=np.array(bounds(face));area=0.;jcount=0
  for nodes,pts in planar_triangles(body,2,z):
   if any(pts[:,k].max()<bb[k]-1e-8 or pts[:,k].min()>bb[k+3]+1e-8 for k in [0,1]):continue
   cs=BRepAlgoAPI_Common(face,tri_shape(pts)).Shape();ar,q,cov=surface_moment(cs)
   if ar<1e-10:continue
   M=moments(cs,pts,16);M2=moments(cs,pts,32);maxquad=max(maxquad,float(abs(M-M2).max()/ar));inv=np.linalg.pinv((pts[1:]-pts[0]).T);uv=inv@(q-pts[0]);raw=inv@cov@inv.T/ar+np.outer(uv,uv);expect=[ar,ar*uv[0],ar*uv[1],ar*raw[0,0],ar*raw[0,1],ar*raw[1,1]];actual=[M[0,0],M[1,0],M[0,1],M[2,0],M[1,1],M[0,2]];maxmom=max(maxmom,float(np.max(abs(np.array(actual)-expect))/ar));pressure=one*(coeff@np.r_[1,pts[0,:2]]);pressure[1,0]=coeff[1:]@(pts[1,:2]-pts[0,:2]);pressure[0,1]=coeff[1:]@(pts[2,:2]-pts[0,:2]);ids=list(nodes)+[edges[tuple(sorted((int(nodes[i]),int(nodes[j]))))] for i,j in [(0,1),(1,2),(0,2)]]
   values=[float(np.sum(mul(sh,pressure)*M)) for sh in shapes]
   for node,value in zip(ids,values):target[3*node+2]+=value
   area+=ar;jcount+=1
  ca,_,_=surface_moment(face);journal.append(dict(label=label,area_mm2=area,CAD_area_mm2=ca,relative_area_error=abs(area/ca-1),clipped_triangles=jcount))
 root=read(REPO/cad['part_references']['F0_ROOT_BACK']['path']);feet=read(REPO/cad['part_references']['EXTERNAL_BENCH_PLATE']['path']);faces=common_faces(support,root,2,-7);rootarea=sum(surface_moment(f)[0] for f in faces)
 for i,face in enumerate(faces):trace(face,-7,np.array([-.980665/rootarea,0,0]),rootF,f'Root{i}')
 coeff=np.array(old['bottom_affine_pressure_coefficients_MPa'])
 for face in common_faces(support,feet,2,-130):trace(face,-130,coeff,footF,'foot')
 F+=rootF+footF;F3=F.reshape(-1,3);R=np.zeros((N,6))
 for j,e in enumerate(np.eye(3)):R[:,j]=np.broadcast_to(e,pos.shape).ravel();R[:,j+3]=(np.cross(e,pos-center)/100).ravel()
 # Positive vertex-volume gauge, extended with zero edge weights; no physical restraints.
 dx=p[t[:,1:]]-p[t[:,0,None]];vol=abs(np.linalg.det(dx))/6;lump=np.zeros(sb.N)
 for j in range(4):np.add.at(lump,t[:,j],vol/4)
 Q=np.array([(R[:,j].reshape(-1,3)*(lump/lump.sum())[:,None]).ravel() for j in range(6)]);_,_,pivot=qr(R.T,mode='economic',pivoting=True);anchor=np.sort(pivot[:6]);free=np.setdiff1d(np.arange(N),anchor);kf=(K[free][:,free]/68900).tocsr();ml=pyamg.smoothed_aggregation_solver(kf,B=R[free],symmetry='symmetric',max_coarse=60);hist=[]
 def cb(x):
  assert not(ROOT/'runtime/STOP').exists();hist.append(float(np.linalg.norm(kf@x-F[free]/68900)))
  if len(hist)%50==0:print(json.dumps(dict(stage='CG',iteration=len(hist),residual=hist[-1])),flush=True)
 sol,info=cg(kf,F[free]/68900,M=ml.aspreconditioner(),rtol=1e-11,atol=1e-15,maxiter=3000,callback=cb);dump(out/'iterations.json',dict(info=int(info),history=hist));assert info==0;u=np.zeros(N);u[free]=sol;u-=R@np.linalg.solve(Q@R,Q@u);u3=u.reshape(-1,3);res=K@u-F;energy=.5*float(u@K@u);independent=0.;internal=np.zeros(N);peak=0.
 # Independent explicit P2 gradients at exact degree2 tetra quadrature, no skfem form.
 x,w=get_quadrature_tet(2);bc=np.vstack([1-x.sum(0),x]).T;inv=np.linalg.inv(dx);gl=np.concatenate([-inv.sum(2)[:,None,:],inv.transpose(0,2,1)],axis=1);ed=sb.element_dofs.T;loc_edges=[(0,1),(1,2),(0,2),(0,3),(1,3),(2,3)]
 for first in range(0,len(t),2000):
  sl=slice(first,min(first+2000,len(t)));g=gl[sl];gg=np.stack([(4*bc[:,i,None,None]-1)*g[None,:,i,:] for i in range(4)]+[4*(bc[:,i,None,None]*g[None,:,j,:]+bc[:,j,None,None]*g[None,:,i,:]) for i,j in loc_edges],axis=2);G=np.einsum('qtai,taj->qtji',gg,u3[ed[sl]]);eps=(G+G.swapaxes(-1,-2))/2;sig=2*mu*eps+la*np.trace(eps,axis1=-2,axis2=-1)[...,None,None]*np.eye(3);weights=6*w[:,None]*vol[sl];independent+=float(np.einsum('qtij,qtij,qt->',eps,sig,weights)/2);ef=np.einsum('qtij,qtaj,qt->tai',sig,gg,weights)
  for a in range(10):np.add.at(internal.reshape(-1,3),ed[sl,a],ef[:,a,:])
  dev=sig-np.trace(sig,axis1=-2,axis2=-1)[...,None,None]*np.eye(3)/3;peak=max(peak,float(np.sqrt(1.5*np.sum(dev*dev,axis=(-1,-2))).max()))
 # Restrict to old P1 virtual fields: midpoint displacement is endpoint average.
 restricted=F3[:len(p)].copy()
 for i,(a,b) in enumerate(m.edges.T):restricted[a]+=F3[sb.dofs.edge_dofs[0,i]]/2;restricted[b]+=F3[sb.dofs.edge_dofs[0,i]]/2
 restrict_error=float(abs(restricted-data['load_N']).max());force=F3.sum(0);moment=np.cross(pos-center,F3).sum(0)*.001;rootmotion=-float(rootF@u)/.980665;checks=dict(same_actual_CAD=sha(step)==cad['part_references']['BENCH_SUPPORT']['SHA256'],CAD_moments=maxmom<1e-8,Green16vs32=maxquad<1e-8,P1_load_restriction=restrict_error<1e-8,force=np.linalg.norm(force)<1e-8,moment=np.linalg.norm(moment)<1e-10,original_all_DOF_residual=abs(res).max()<1e-8,independent_internal_force=abs(internal-F).max()<1e-8,independent_energy=abs(independent/energy-1)<1e-8,halfwork=abs(.5*F@u/energy-1)<1e-8,actual_trace_area=max(a['relative_area_error'] for a in journal)<.01,finite=bool(np.isfinite(u).all()))
 np.savez_compressed(out/'field.npz',points_mm=p,tetra=t,P2_points_mm=pos,P2_element_nodes=ed,displacement_mm=u3,load_N=F3,ownweight_N=own.reshape(-1,3),root_load_N=rootF.reshape(-1,3),foot_load_N=footF.reshape(-1,3),residual_N=res,independent_internal_force_N=internal)
 dump(out/'summary.json',dict(status='ACTUAL_PRODUCT_P2_NEUMANN_LOCAL_CHECKS_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_PRODUCT_P2_NEUMANN_FAIL',candidate=ref(cadp),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),field=ref(out/'field.npz'),checks={k:bool(v) for k,v in checks.items()},h_mm=float(h),order=2,nodes=int(sb.N),tetra=len(t),physical_fixed_DOF=0,static_strain_energy_Nmm=energy,independent_energy_Nmm=independent,root_objective_relative_displacement_mm=rootmotion,maximum_displacement_mm=float(np.linalg.norm(u3,axis=1).max()),raw_peak_VM_MPa=peak,CAD_moment_error=maxmom,Green_quadrature_error=maxquad,P1_load_restriction_error_N=restrict_error,force_balance_N=force.tolist(),moment_balance_Nm=moment.tolist(),residual_N=float(abs(res).max()),independent_internal_force_error_N=float(abs(internal-F).max()),ports=journal,elapsed_s=time.monotonic()-start,accepted_physical_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,actual_100g_operating_field=None,limitations=['Same prescribed normal100g/ownweight/positiveaffinefoot reference,NOT grasp/hostcontact','P2 changes displacement order only;CAD,typicalmaterial,allphysicalcriteria unchanged','Raw stress at sharp geometry notstrengthcertificate;all22unqualified']))
 print((out/'summary.json').read_text(),flush=True);raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
