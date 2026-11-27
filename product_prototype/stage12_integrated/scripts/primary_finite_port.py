"""Finite SO(3) cotangent lift of P1's specified linear area-weighted fit.
Units: input u/anchor mm, origin wrench N/Nm, output generalized force N.
This differentiates the existing pose map; it does not make that map objective.
"""
import numpy as np
from scipy.spatial.transform import Rotation

def skew(v):
 x,y,z=v;return np.array([[0.,-z,y],[z,0.,-x],[-y,x,0.]])

def left_jacobian(theta):
 t=np.linalg.norm(theta);S=skew(theta)
 if t<1e-4:
  a=.5-t*t/24+t**4/720;b=1/6-t*t/120+t**4/5040
 else:a=(1-np.cos(t))/t**2;b=(t-np.sin(t))/t**3
 return np.eye(3)+a*S+b*S@S

class RootPort:
 def __init__(self,p,w,anchor=np.array([50.4,0.,-7.])):
  self.p=np.asarray(p);self.center=self.p.mean(0);self.anchor=anchor
  A=np.concatenate([np.column_stack((np.eye(3),-skew(q-self.center))) for q in self.p]);ww=np.repeat(w,3)
  self.L=np.linalg.solve(A.T@(ww[:,None]*A),A.T*ww)
 def pose(self,u):
  z=self.L@np.asarray(u).ravel();theta=z[3:];R=Rotation.from_rotvec(theta).as_matrix();b=(self.anchor+z[:3]+np.cross(theta,self.anchor-self.center))*.001
  return z,R,b
 def positions(self,u,q):
  z,R,b=self.pose(u);return (np.asarray(q)-self.anchor*.001)@R.T+b
 def pullback(self,u,wrench):
  z,R,b=self.pose(u);F=np.asarray(wrench[:3]);tau=np.asarray(wrench[3:])-np.cross(b,F)
  g=np.r_[F,skew(self.anchor-self.center)@F+1000*left_jacobian(z[3:]).T@tau]
  return (self.L.T@g).reshape(-1,3)

def motor_positions(u,q):
 C=np.array([0.,0.,.020])+np.asarray(u[:3])*.001;R=Rotation.from_rotvec(u[3:]).as_matrix()
 return (np.asarray(q)-[0,0,.020])@R.T+C

def motor_pullback(u,wrench):
 C=np.array([0.,0.,.020])+np.asarray(u[:3])*.001;F=np.asarray(wrench[:3]);tau=np.asarray(wrench[3:])-np.cross(C,F)
 return np.r_[F,1000*left_jacobian(u[3:]).T@tau]

class ObjectiveRootPort:
 """Area weighted proper Procrustes pose, with exact polar differential.
 Reference face is planar but non-collinear; positive B eigenvalues required.
 No material constitutive law or FE contact equations are changed here.
 """
 def __init__(self,p,w):
  self.p=np.asarray(p);self.w=np.asarray(w);self.total=self.w.sum();self.center=self.w@self.p/self.total;self.relative=self.p-self.center
 def pose(self,u):
  current=self.p+u;c=self.w@current/self.total;H=(self.w[:,None]*(current-c)).T@self.relative
  U,s,Vt=np.linalg.svd(H);D=np.diag([1.,1.,np.linalg.det(U@Vt)]);R=U@D@Vt;S=H@R.T;B=np.trace(S)*np.eye(3)-S
  if np.linalg.eigvalsh((B+B.T)/2).min()<=1e-12:raise ValueError('Degenerate objective Root face')
  return R,c,B
 def positions(self,u,q):
  R,c,B=self.pose(u);return (np.asarray(q)-self.center*.001)@R.T+c*.001
 def pullback(self,u,wrench):
  R,c,B=self.pose(u);F=np.asarray(wrench[:3]);tau=1000*np.asarray(wrench[3:])-np.cross(c,F);v=np.linalg.solve(B.T,tau);r=self.relative@R.T
  return self.w[:,None]*(F/self.total+np.cross(v,r))
