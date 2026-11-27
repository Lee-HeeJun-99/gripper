"""Conservative actual CAD mass-centroid pullback on existing P1 finite rod model.
Planar ideal taut cable with its own gravitational potential, not cable catenary.
"""
import numpy as np
import primary_finger_tangent_v5 as kin
G=9.80665;RADIUS=.01125;C=np.array([0.,.020]);ROOT_POINT=np.array([.0504,-.007]);ANCHOR=np.array([.0504,-.084])
def rot(a):return np.array([[np.cos(a),np.sin(a)],[-np.sin(a),np.cos(a)]])
def drot(a):return np.array([[-np.sin(a),np.cos(a)],[-np.cos(a),-np.sin(a)]])
def cable(P):
 D=P-C;dist=np.sqrt(np.sum(D*D));u=D/dist;k=RADIUS/dist;normal=k*u+np.sqrt(1-k*k)*np.array([-u[1],u[0]]);Q=C+RADIUS*normal;t=(Q-P)/np.sqrt(np.sum((Q-P)**2));return Q,t,normal
P0=np.array([.043,-.092]);Q0,T0,N0=cable(P0)
def free(P):
 Q,t,n=cable(P);return RADIUS*(np.pi/2-np.arctan2(n[1],n[0]))+np.linalg.norm(P-Q)-.016
FREE0=free(P0);BETA0=np.arctan2(T0[0],T0[1])
def wire_centroid(P):
 Q,t,normal=cable(P);eta=(free(P)-FREE0)/RADIUS;start=np.pi/2-eta;phi=np.arctan2(normal[1],normal[0]);arc=RADIUS*(start-phi);end=P+.016*t;lead=np.linalg.norm(end-Q)
 moment=RADIUS**2*np.array([np.sin(start)-np.sin(phi),np.cos(phi)-np.cos(start)])+C*arc+(Q+end)*lead/2+.006*(C+rot(eta)@[-.003,RADIUS])
 return moment/(FREE0+.006),arc+lead+.006
class Gravity:
 def __init__(self,points):self.points=points
 def evaluate(self,v,n,factor=1.,details=False):
  rail,pet,R,dR,jr,P,JP,tip,JT,t=kin.terminal(v,n);a=rail[0][-1];eta=(free(P)-FREE0)/RADIUS;Je=-t@JP/RADIUS
  dt=np.empty((2,2))
  for j in range(2):
   z=P.astype(complex);z[j]+=1e-25j;dt[:,j]=cable(z)[1].imag/1e-25
  beta=np.arctan2(t[0],t[1]);Jb=(t[1]*dt[0]-t[0]*dt[1])@JP
  wc,wl=wire_centroid(P);Jw=np.empty((2,2));eps=1e-7
  for j in range(2):
   d=np.eye(2)[j]*eps;Jw[:,j]=(wire_centroid(P+d)[0]-wire_centroid(P-d)[0])/(2*eps)
  U=0.;grad=np.zeros(4*n);rows=[]
  for item in self.points:
   mode=item['mode'];c=np.array(item['rest_centroid_m']);q=c[[0,2]];J=np.zeros((2,4*n));m=item['mass_kg']
   if mode in ('rail','pet'):
    petmode=mode=='pet';data=pet if petmode else rail;s=item['material_station_m'];pt,j,_,_=kin.point(data,s);th=data[0];h=data[2];i=min(int(s/h),n-1);u=(s-i*h)/h;ang=(1-u)*th[i]+u*th[i+1];offset=q-np.array([.05015 if petmode else .0504,-.007-s]);q=pt+rot(ang)@offset;da=np.zeros(2*n)
    if i:da[i-1]=1-u
    da[i]=u;j+=np.outer(drot(ang)@offset,da);J[:,2*n if petmode else 0:4*n if petmode else 2*n]=j
   elif mode=='terminal':
    offset=q-ANCHOR;q=rail[3][-1]+R@offset;J=jr.copy();J[:,n-1]+=dR@offset
   elif mode=='swivel':
    offset=q-P0;q=P+rot(beta-BETA0)@offset;J=JP+np.outer(drot(beta-BETA0)@offset,Jb)
   elif mode=='rotor':
    offset=q-C;q=C+rot(eta)@offset;J=np.outer(drot(eta)@offset,Je)
   elif mode=='wire':q=wc;J=Jw@JP
   U+=m*G*factor*q[1];grad+=m*G*factor*J[1]
   if details:rows.append(dict(part_ID=item['part_ID'],mode=mode,mass_kg=m,position_m=[float(q[0]),float(c[1]),float(q[1])]))
  return U,grad,rows
