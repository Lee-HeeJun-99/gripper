"""P1 saved tetra/row/axial-branch objective contrast, N/mm.
No remesh, solve, stress certification or general simulator. Biot strain reuses
original isotropic constants. Owner-volume polar normals and axial directions
are a testable approximation; deformed local facet bounds must qualify them.
"""
import numpy as np
from scipy.sparse import csr_matrix
from scipy.spatial.transform import Rotation
from primary_finite_port import ObjectiveRootPort,left_jacobian

CONTACTS={
 'root_seat':('F0_ROOT_BACK','OPEN_FRAME',[0,0,1]),'root_wall':('F0_ROOT_BACK','OPEN_FRAME',[-1,0,0]),
 'motor_bottom':('Motor','OPEN_FRAME',[0,0,1]),'motor_xmin':('Motor','OPEN_FRAME',[1,0,0]),'motor_xmax':('Motor','OPEN_FRAME',[-1,0,0]),
 'motor_top':('Motor','MOTOR_CAP',[0,0,-1]),'motor_front_frame':('Motor','OPEN_FRAME',[0,-1,0]),'motor_front_cap':('Motor','MOTOR_CAP',[0,-1,0]),
 'frame_seat':('OPEN_FRAME','GROUND_PLATE',[0,0,-1]),'frame_key_xmin':('OPEN_FRAME','GROUND_PLATE',[1,0,0]),'frame_key_xmax':('OPEN_FRAME','GROUND_PLATE',[-1,0,0]),'frame_key_ymin':('OPEN_FRAME','GROUND_PLATE',[0,1,0]),'frame_key_ymax':('OPEN_FRAME','GROUND_PLATE',[0,-1,0]),
 'ground_seat':('GROUND_PLATE','TEST_BASE',[0,0,-1]),'ground_key_xmin':('GROUND_PLATE','TEST_BASE',[1,0,0]),'ground_key_xmax':('GROUND_PLATE','TEST_BASE',[-1,0,0]),'ground_key_ymin':('GROUND_PLATE','TEST_BASE',[0,1,0]),'ground_key_ymax':('GROUND_PLATE','TEST_BASE',[0,-1,0])}
class Support:
 def __init__(self,a,names):
  self.a=a;self.names=names;self.N=len(a['u_mm']);self.mo=int(a['motor_offset']);self.bodies={}
  for name in names:
   X=a[name+'_points_mm'];t=a[name+'_tetra'];dx=X[t[:,1:]]-X[t[:,0,None]];inv=np.linalg.inv(dx);V=abs(np.linalg.det(dx))/6;gr=np.concatenate([-inv.sum(2)[:,None,:],inv.transpose(0,2,1)],axis=1);w=np.zeros(len(X))
   for j in range(4):np.add.at(w,t[:,j],V/4)
   E=float(a[name+'_E_MPa']);nu=float(a[name+'_nu']);self.bodies[name]=dict(X=X,t=t,inv=inv,V=V,gr=gr,w=w,offset=int(a[name+'_offset']),lam=E*nu/((1+nu)*(1-2*nu)),mu=E/(2*(1+nu)),port=ObjectiveRootPort(X,w),rho=float(a[name+'_rho_kg_m3']))
  self.groups=[]
  for label in np.unique(a['contact_label']):
   ids=np.flatnonzero(a['contact_label']==label);first,second,n=CONTACTS[str(label)];q=a['contact_points_mm'][ids];group=dict(label=str(label),ids=ids,first=first,second=second,n=np.array(n),q=q)
   for side,name in [('a',first),('b',second)]:
    if name!='Motor':
     pp=self.bodies[name]['X'];lookup={tuple(np.round(p,7)):i for i,p in enumerate(pp)};ii=np.array([lookup[tuple(np.round(p,7))] for p in q]);assert np.max(abs(pp[ii]-q))<1e-6;group[side]=ii
   self.groups.append(group)
  D=a['bolt_D'];self.bolts=[]
  for row in D:
   pieces=[]
   for n,b in self.bodies.items():
    o=b['offset'];weights=row[o:o+3*len(b['X'])].reshape(-1,3);assert np.max(abs(weights[:,:2]))==0
    if np.max(abs(weights))>0:pieces.append((n,weights[:,2]))
   assert len(pieces)==2
   first,wa=next(x for x in pieces if x[1].sum()>0);second,wb=next(x for x in pieces if x[1].sum()<0);wb=-wb
   assert abs(wa.sum()-1)<1e-12 and abs(wb.sum()-1)<1e-12
   ca=wa@self.bodies[first]['X'];cb=wb@self.bodies[second]['X'];self.bolts.append(dict(first=first,second=second,wa=wa,wb=wb,length=ca[2]-cb[2]))
 def body_u(self,u,name):
  b=self.bodies[name];o=b['offset'];return u[o:o+3*len(b['X'])].reshape(-1,3)
 def scatter(self,g,name,f):
  b=self.bodies[name];o=b['offset'];g[o:o+3*len(b['X'])]+=f.ravel()
 def poses(self,u):return {n:b['port'].pose(self.body_u(u,n)) for n,b in self.bodies.items()}
 def point(self,u,name,q,ids=None):
  if name=='Motor':
   z=u[self.mo:self.mo+6];R=Rotation.from_rotvec(z[3:]).as_matrix();return (q-[0,0,20])@R.T+[0,0,20]+z[:3]
  return self.bodies[name]['X'][ids]+self.body_u(u,name)[ids]
 def add_points(self,g,u,name,ids,q,f):
  if name=='Motor':
   z=u[self.mo:self.mo+6];C=np.array([0,0,20])+z[:3];x=self.point(u,name,q);tau=np.cross(x-C,f).sum(0);g[self.mo:self.mo+3]+=f.sum(0);g[self.mo+3:self.mo+6]+=left_jacobian(z[3:]).T@tau
  else:
   b=self.bodies[name];ff=np.zeros_like(b['X']);np.add.at(ff,ids,f);self.scatter(g,name,ff)
 def owner_torque(self,g,u,torques):
  for n,tau in torques.items():self.scatter(g,n,self.bodies[n]['port'].pullback(self.body_u(u,n),np.r_[np.zeros(3),tau*.001]))
 def elastic(self,u,corotated=True):
  total=0.;g=np.zeros(self.N);rows=[]
  for n,b in self.bodies.items():
   X,t,inv,V,gr=(b[k] for k in ('X','t','inv','V','gr'));uu=self.body_u(u,n);du=uu[t[:,1:]]-uu[t[:,0,None]];grad=np.einsum('tij,tjk->tik',inv,du).transpose(0,2,1);F=grad+np.eye(3)
   if corotated:
    l,s,r=np.linalg.svd(F);R=l@r;assert np.min(np.linalg.det(R))>0;eps=np.einsum('tji,tj,tjk->tik',r,s-1,r)
   else:eps=(grad+grad.transpose(0,2,1))/2
   stress=2*b['mu']*eps+b['lam']*np.trace(eps,axis1=1,axis2=2)[:,None,None]*np.eye(3);energy=.5*np.sum(V*np.sum(eps*stress,axis=(1,2)));P=np.einsum('tij,tj,tjk->tik',l,2*b['mu']*(s-1)+b['lam']*np.sum(s-1,axis=1)[:,None],r) if corotated else stress;ff=np.einsum('tij,tnj,t->tni',P,gr,V);nodal=np.zeros_like(X)
   for j in range(4):np.add.at(nodal,t[:,j],ff[:,j])
   self.scatter(g,n,nodal);total+=energy;rows.append(dict(part=n,energy_Nmm=float(energy),force_N=nodal.sum(0).tolist(),current_moment_Nm=np.cross((X+uu)*.001,nodal).sum(0).tolist(),min_detF=float(np.linalg.det(F).min()),max_grad=float(np.linalg.norm(grad,axis=(1,2)).max())))
  return float(total),g,rows
 def contacts(self,u,pressure):
  poses=self.poses(u);gaps=np.zeros(len(pressure));g=np.zeros(self.N);torques={n:np.zeros(3) for n in self.names};details=[]
  for row in self.groups:
   ids=row['ids'];first,second=row['first'],row['second'];xa=self.point(u,first,row['q'],row.get('a'));xb=self.point(u,second,row['q'],row['b']);n=poses[second][0]@row['n'];d=xa-xb;gaps[ids]=d@n+self.a['initial_gaps_mm'][ids];ff=pressure[ids,None]*n;self.add_points(g,u,first,row.get('a'),row['q'],ff);self.add_points(g,u,second,row['b'],row['q'],-ff);torques[second]+=np.cross(n,d*pressure[ids,None]).sum(0);details.append(dict(label=row['label'],normal=n.tolist(),owner=second,maximum_pair_separation_mm=float(np.linalg.norm(d,axis=1).max())))
  self.owner_torque(g,u,torques);return gaps,g,details
 def connectors(self,u,forces=None):
  poses=self.poses(u);ext=[];g=np.zeros(self.N);torques={n:np.zeros(3) for n in self.names}
  for i,row in enumerate(self.bolts):
   first,second=row['first'],row['second'];ba,bb=self.bodies[first],self.bodies[second];xa=ba['X']+self.body_u(u,first);xb=bb['X']+self.body_u(u,second);d=row['wa']@xa-row['wb']@xb;n=poses[second][0][:,2];e=float(n@d-row['length']);ext.append(e);force=forces[i] if forces is not None else max(0,self.a['bolt_k_N_mm'][i]*e);self.scatter(g,first,row['wa'][:,None]*n*force);self.scatter(g,second,-row['wb'][:,None]*n*force);torques[second]+=np.cross(n,d)*force
  self.owner_torque(g,u,torques);return np.array(ext),g
 def wrench(self,u,g):
  W=np.zeros(6)
  for n,b in self.bodies.items():
   o=b['offset'];f=g[o:o+3*len(b['X'])].reshape(-1,3);W+=np.r_[f.sum(0),np.cross((b['X']+self.body_u(u,n))*.001,f).sum(0)]
  z=u[self.mo:self.mo+6];f=g[self.mo:self.mo+3];tau=np.linalg.solve(left_jacobian(z[3:]).T,g[self.mo+3:self.mo+6]);W+=np.r_[f,tau*.001+np.cross((np.array([0,0,20])+z[:3])*.001,f)];return W
 def rigid(self,u,R,t):
  z=u.copy()
  for n,b in self.bodies.items():
   o=b['offset'];z[o:o+3*len(b['X'])]=((b['X']+self.body_u(u,n))@R.T+t-b['X']).ravel()
  mo=self.mo;um=u[mo:mo+6];z[mo:mo+3]=R@(np.array([0,0,20])+um[:3])+t-[0,0,20];z[mo+3:mo+6]=Rotation.from_matrix(R@Rotation.from_rotvec(um[3:]).as_matrix()).as_rotvec();return z
