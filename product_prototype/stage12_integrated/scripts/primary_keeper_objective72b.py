"""Actual Root keeper full3D elastic / two spinning rigid sockets conditional contact.
No physical fixed DOF. Host lateral/tilt socket BC are explicit references;
keeper gravity, pin/nut/cage compliance and system equilibrium remain UNSOLVED.
"""
import sys,json,time,shutil,resource
import numpy as np
from scipy import sparse
import osqp
from skfem import MeshTet,Basis,ElementVector,ElementTetP1,asm
from skfem.models.elasticity import linear_elasticity,lame_parameters
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
import gmsh
def meshpart(path,h,curv):
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1);gmsh.model.add('actual_keeper_coarse_contact_not_mesh_certificate');v=gmsh.model.occ.importShapes(str(path));gmsh.model.occ.synchronize();volume=sum(gmsh.model.occ.getMass(d,t) for d,t in v)
 for name,value in [('Mesh.MeshSizeMin',h),('Mesh.MeshSizeMax',h),('Mesh.MeshSizeFromPoints',0),('Mesh.MeshSizeFromCurvature',0),('Mesh.MeshSizeExtendFromBoundary',0)]:gmsh.option.setNumber(name,value)
 gmsh.model.mesh.generate(3);nt,p,_=gmsh.model.mesh.getNodes();order=np.argsort(nt);nt=np.array(nt)[order];p=np.array(p).reshape(-1,3)[order];ty,_,el=gmsh.model.mesh.getElements(3);t=np.concatenate([np.searchsorted(nt,np.array(a).reshape(-1,4)) for k,a in zip(ty,el) if k==4]);ty,_,el=gmsh.model.mesh.getElements(2);tri=np.concatenate([np.searchsorted(nt,np.array(a).reshape(-1,3)) for k,a in zip(ty,el) if k==2]);gmsh.finalize();ids=np.unique(t);return p[ids],np.searchsorted(ids,t),np.searchsorted(ids,tri),volume
from primary_keeper_coupled71 import faces,rot
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Plane

def main():
 start=time.monotonic();h=float(sys.argv[1]);out=ROOT/'validation/integrated'/sys.argv[2];out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_ground65a/summary.json';cad=json.loads(cp.read_text());refs=cad['part_references'];assert all(sha(REPO/r['path'])==r['SHA256'] for r in [*refs.values(),cad['assembly'],cad['BOM']]);step=REPO/refs['ROOT_SOCKET_KEEPER']['path'];src=ROOT/'validation/integrated/primaryP1_keepercoupled71/summary.json';d=json.loads(src.read_text());r=d['rows'][0];assert r['signs']==[1,1] and r['full18row_feasible'];T=np.array(r['conditional_bolt_torque_Nmm']);angles=np.array(r['solution'][3:]);settings=[q for q in json.loads((REPO/cad['settings']['path']).read_text())['settings'] if q['keeper']=='ROOT_SOCKET_KEEPER'];p,t,tri,Vcad=meshpart(step,h,12);N=3*len(p);E=200000.;nu=.3;la,mu=lame_parameters(E,nu);m=MeshTet(p.T,t.T);K=sparse.csr_matrix((N,N))
 print(json.dumps(dict(phase='mesh',nodes=len(p),tetra=len(t))),flush=True)
 for first in range(0,len(t),8000):
  assert not(ROOT/'runtime/STOP').exists();K+=asm(linear_elasticity(la,mu),Basis(m,ElementVector(ElementTetP1()),intorder=2,elements=np.arange(first,min(first+8000,len(t)))))
 # Unique surface edges and vertices, INCLUDING above/below moving end trims.
 walls=[];centers=[];edges=[];vertices=[]
 for i,qset in enumerate(settings):
  c=np.array([qset['x'],qset['y'],0.]);centers.append(c);ww=[]
  for f in faces(read(REPO/refs[qset['bolt']]['path'])):
   ad=BRepAdaptor_Surface(f)
   if ad.GetType()!=GeomAbs_Plane:continue
   pl=ad.Plane();o=pl.Location();axis=pl.Axis().Direction();o=np.array([o.X(),o.Y(),o.Z()]);n=np.array([axis.X(),axis.Y(),axis.Z()]);bb=bounds(f)
   if abs(n[2])<1e-7 and np.linalg.norm((np.array(bb[:3])+bb[3:])[:2]/2-c[:2])<2:
    if n@(c-o)<0:n=-n
    ww.append((o,n))
  assert len(ww)==6;walls.append(ww)
  tt=tri[np.all(np.linalg.norm(p[tri,:2]-c[:2],axis=2)<1.6,axis=1)]
  vertices.append(np.unique(tt));edges.append(np.unique(np.sort(np.concatenate([tt[:,[0,1]],tt[:,[1,2]],tt[:,[2,0]]]),axis=1),axis=0))
 centers=np.array(centers);L=.001;OBJ=.0001;pitch=.5/(2*np.pi)
 P=sparse.block_diag([K*(L*L/OBJ),sparse.csr_matrix((2,2))],format='csc');q=np.r_[np.zeros(N),-T*L/OBJ]
 def geom(x):
  pos=p+x[:N].reshape(-1,3)*L;ang=angles+x[N:]*L
  keys=[];gaps=[];rr=[];cc=[];vv=[];points=[];pull=[]
  for bi in range(2):
   lo=-1.3+pitch*ang[bi];hi=pitch*ang[bi];R=rot(ang[bi]);c=centers[bi];features=[]
   for node in vertices[bi]:
    if lo<=pos[node,2]<=hi:features.append((('v',int(node),-1),[int(node)],[1.],pos[node],None))
   for a,b in edges[bi]:
    d=pos[b]-pos[a]
    if abs(d[2])<1e-14:continue
    for end,z in enumerate([lo,hi]):
     tau=(z-pos[a,2])/d[2]
     if 0<tau<1:features.append((('e',int(a),int(b),end),[int(a),int(b)],[1-tau,tau],pos[a]+tau*d,d))
   for wi,(o0,n0) in enumerate(walls[bi]):
    n=R@n0;o=R@(o0-c)+c+np.array([0,0,pitch*ang[bi]])
    for key,nd,wt,pt,d in features:
     row=len(keys);keys.append((bi,wi,*key));gaps.append(n@(pt-o));points.append(pt)
     # Implicit derivative of material edge intersection with moving socket plane.
     g=n.copy();spin=-n@np.array([-(pt-c)[1],(pt-c)[0],0.])
     if d is not None:g[2]-=n@d/d[2];spin+=n@d/d[2]*pitch
     pull.append(g)
     for node,w in zip(nd,wt):
      for j in range(3):rr.append(row);cc.append(3*node+j);vv.append(w*g[j])
     rr.append(row);cc.append(N+bi);vv.append(spin)
  A=sparse.coo_matrix((vv,(rr,cc)),shape=(len(keys),N+2)).tocsr()
  return np.array(gaps),A,keys,np.array(points),np.array(pull)
 initial=ROOT/'validation/integrated'/sys.argv[3]/'field.npz';old=np.load(initial);assert np.array_equal(old['points_mm'],p) and np.array_equal(old['tetra'],t)
 x=np.r_[old['displacement_mm'].ravel(),old['bolt_spin_increment_rad']]/L
 gg,A,keys,pts,pull=geom(x);lookup={k:j for j,k in enumerate(keys)};active=set()
 for node,bi,wi,lm in zip(old['contact_node'],old['bolt_index'],old['wall_index'],old['normal_force_N']):
  key=(int(bi),int(wi),'v',int(node),-1)
  if lm>1e-7 and key in lookup:active.add(key)
 dump(out/'initial_guess.json',dict(source=ref(initial),all_mesh_arrays_exact=True,not_equilibrium=True));journal=[]
 # Exact directional derivative audit at deformed finite edges, topology preserved.
 rng=np.random.default_rng(72);direction=rng.normal(size=N+2);direction/=np.max(abs(direction));eps=1e-4
 gp,_,kp,_,_=geom(x+eps*direction);gm,_,km,_,_=geom(x-eps*direction);ip={k:j for j,k in enumerate(kp)};im={k:j for j,k in enumerate(km)};commonids=[j for j,k in enumerate(keys) if k in ip and k in im];fd=np.array([(gp[ip[keys[j]]]-gm[im[keys[j]]])/(2*eps*L) for j in commonids]);an=(A@direction)[commonids];fdmax=float(abs(fd-an).max());edgeids=[j for j in commonids if keys[j][2]=='e'];print(json.dumps(dict(phase='finite_features',rows=len(keys),active=len(active),fd_error=fdmax,edges=len(edgeids))),flush=True)
 from scipy.sparse.linalg import splu
 xyz=p[t];mat=np.concatenate([np.ones((*xyz.shape[:2],1)),xyz],axis=2);iv=np.linalg.inv(mat);grad=iv[:,1:,:].transpose(0,2,1);vol=abs(np.linalg.det(mat))/6
 dofs=(3*t[:,:,None]+np.arange(3)).reshape(len(t),12);ir=np.repeat(dofs,12,axis=1).ravel();ic=np.tile(dofs,(1,12)).ravel()
 def elastic(y,tangent=True):
  uu=y[:N].reshape(-1,3)*L;DG=np.einsum('tai,taj->tij',uu[t],grad);FG=DG+np.eye(3);EE=(FG.transpose(0,2,1)@FG-np.eye(3))/2;SS=2*mu*EE+la*np.trace(EE,axis1=1,axis2=2)[:,None,None]*np.eye(3);PK=FG@SS
  ef=np.einsum('tij,taj,t->tai',PK,grad,vol);ff=np.zeros((len(p),3))
  for jj in range(4):np.add.at(ff,t[:,jj],ef[:,jj])
  en=float(np.sum((mu*np.sum(EE*EE,axis=(1,2))+.5*la*np.trace(EE,axis1=1,axis2=2)**2)*vol))
  if not tangent:return ff.ravel(),en,None
  H=np.zeros((len(t),4,3,4,3));B=FG@FG.transpose(0,2,1)
  for ii in range(3):
   for kk in range(3):
    aa=(SS if ii==kk else np.zeros_like(SS))+la*FG[:,ii,:,None]*FG[:,kk,None,:]+mu*FG[:,kk,:,None]*FG[:,ii,None,:]+mu*B[:,ii,kk,None,None]*np.eye(3)
    H[:,:,ii,:,kk]=np.einsum('taj,tjl,tbl,t->tab',grad,aa,grad,vol)
  KT=sparse.coo_matrix((H.reshape(len(t),144).ravel(),(ir,ic)),shape=(N,N)).tocsc();return ff.ravel(),en,KT

 final=None
 for iteration in range(90):
  assert not(ROOT/'runtime/STOP').exists();gap,A,keys,pts,pull=geom(x);lookup={k:j for j,k in enumerate(keys)};active.intersection_update(lookup);act=np.array(sorted(lookup[k] for k in active),int)
  lower=-gap/L+A@x;C=A[act].tocsc();gauge=sparse.coo_matrix(([1.],([0],[2])),shape=(1,N+2)).tocsc();C=sparse.vstack([C,gauge],format='csc');rhs=np.r_[lower[act],0.]
  internal,en,KT=elastic(x);P=sparse.block_diag([KT*(L*L/OBJ),sparse.csr_matrix((2,2))],format='csc');nrhs=P@x-np.r_[internal*L/OBJ,np.zeros(2)]-q
  system=sparse.bmat([[P,-C.T],[C,None]],format='csc');fac=splu(system,permc_spec='COLAMD');ans=fac.solve(np.r_[nrhs,rhs]);del fac,system
  xn=ans[:N+2];du=ans[N+2:];gn,An,kn,pn,pbn=geom(xn);newlook={k:j for j,k in enumerate(kn)};lam=np.zeros(len(kn))
  for key,lm in zip([keys[j] for j in act],du[:-1]*OBJ/L):
   if key in newlook:lam[newlook[key]]=lm
  force=An.T@lam;internal,en,_=elastic(xn,False);res=internal-force[:N];tor=T+force[N:];neg=np.flatnonzero(lam<-1e-9);viol=np.flatnonzero(gn<-1e-9)
  entry=dict(iteration=iteration,rows=len(kn),active=len(act),minimum_gap_mm=float(gn.min()),minimum_lambda_N=float(lam.min()),force_residual_N=float(abs(res).max()),torque_residual_Nmm=float(abs(tor).max()),complementarity_Nmm=float(abs(lam*gn).max()),gauge_reaction_N=float(du[-1]*OBJ/L),energy_Nmm=en,delta_scaled=float(abs(xn-x).max()),negative_rows=len(neg),violating_rows=len(viol));journal.append(entry);print(json.dumps(entry),flush=True)
  np.savez_compressed(out/f'iterate_{iteration:02}.npz',scaled_unknown=xn,normal_force_N=lam,gap_mm=gn)
  x=xn;final=(gn,An,kn,pn,pbn,lam,res,tor)
  if len(neg):active.discard(kn[neg[np.argmin(lam[neg])]])
  elif len(viol):active.update(kn[j] for j in viol[np.argsort(gn[viol])[:8]])
  elif abs(res).max()<1e-10 and abs(tor).max()<1e-11 and abs(lam*gn).max()<1e-10 and abs(du[-1]*OBJ/L)<1e-11:break
 gap,A,keys,pts,pull,lam,res,tor=final;u=x[:N].reshape(-1,3)*L;force=(A.T@lam)[:N].reshape(-1,3);internal,energy,_=elastic(x,False)
 checks=dict(all83_source_hashes=True,finite_edge_derivative=fdmax<1e-6,original_elastic_force=abs(res).max()<1e-8,free_spin_torque=abs(tor).max()<1e-8,nonnegative_multipliers=lam.min()>=-1e-9,all_finite_clipped_vertices=gap.min()>=-1e-9,complementarity=abs(lam*gap).max()<1e-8,gauge_reaction_zero=abs(journal[-1]['gauge_reaction_N'])<1e-8)
 np.savez_compressed(out/'field.npz',points_mm=p,tetra=t,boundary_triangles=tri,displacement_mm=u,load_N=force,normal_force_N=lam,gap_mm=gap,bolt_spin_increment_rad=x[N:]*L,contact_points_mm=pts,pullback_direction=pull)
 dump(out/'contact_keys.json',keys)
 dump(out/'summary.json',dict(status='OBJECTIVE_STVK_FINITE_SOCKET_CONDITIONAL_REFERENCE' if all(checks.values()) else 'FINITE_SOCKET_EDGE_FAIL',candidate=ref(cp),STEP=ref(step),producer=ref(out/'producer.py'),initial=ref(initial),field=ref(out/'field.npz'),contact_keys=ref(out/'contact_keys.json'),checks={k:bool(v) for k,v in checks.items()},nodes=len(p),tetra=len(t),h_mm=h,E_ASSUMED_MPa=E,nu_ASSUMED=nu,elastic_law='SaintVenantKirchhoff_totalLagrangian_assumed',bolt_reference_spin_rad=angles.tolist(),conditional_bolt_torque_Nmm=T.tolist(),static_energy_Nmm=energy,finite_directional_derivative_error=fdmax,finite_edge_rows=len(edgeids),journal=journal,accepted83body_physical_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,physical_fixed_keeper_DOF=0,numerical_z_gauge=True,sharp_edge_normal_cone_certified=False,limitations=['Clippedfacetgap constrained; exactmaterialedge derivative includes axialcomponent. Sharpedge normalcone NOT YET independently certified; do not treat generalizededge reactions as validatedphysicalcontact.','Rigid socket lateral/tilt BC, unknownhost reactions; no actualhost/pin/nut/cage/preload operatingequilibrium.','Objective SaintVenantKirchhoff assumed200GPa/.3; smallstrainmaterial assumption not source minimum or measuredphysicalqualification; curvedSTEP spatial/time/globalenergy not certified.'],elapsed_s=time.monotonic()-start))
 return 0 if all(checks.values()) else 2
if __name__=='__main__':sys.exit(main())
