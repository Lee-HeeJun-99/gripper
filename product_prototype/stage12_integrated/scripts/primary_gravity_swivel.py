"""Same P1: independent free-swivel DOF, endpoint tangent and conservative mass pullback.
Cable still ideal taut, quasi-static and inextensible; catenary not certified.
"""
import numpy as np
from primary_gravity_pullback import Gravity,rot,drot,cable,FREE0,BETA0,P0,G,C,RADIUS
import primary_finger_tangent_v5 as kin
ARM=.016

def route(P,beta):
 e=np.array([np.sin(beta),np.cos(beta)]);E=P+ARM*e;Q,t,normal=cable(E);phi=np.arctan2(normal[1],normal[0]);length=RADIUS*(np.pi/2-phi)+np.linalg.norm(Q-E);eta=(length-FREE0)/RADIUS;start=np.pi/2-eta;arc=RADIUS*(start-phi);lead=np.linalg.norm(E-Q)
 wc=(RADIUS**2*np.array([np.sin(start)-np.sin(phi),np.cos(phi)-np.cos(start)])+C*arc+(Q+E)*lead/2+.006*(C+rot(eta)@[-.003,RADIUS]))/(FREE0+.006)
 return E,Q,t,length,eta,wc,arc+lead+.006
class FreeSwivel(Gravity):
 def evaluate(self,x,n,factor=1.,details=False):
  v=x[:4*n];beta=x[-1];rail,pet,R,dR,jr,P,JP,tip,JT,t0=kin.terminal(v,n);E,Q,t,length,eta,wc,wl=route(P,beta);de=np.array([np.cos(beta),-np.sin(beta)]);JE=np.column_stack((JP,ARM*de));dl=-t@JE;Je=dl/RADIUS;Jw=np.empty((2,2));eps=1e-7
  # Wire centroid depends on E and angle of cable payout only, hence route(E,0)
  # is evaluated through the actual P,beta pair while perturbing P.
  for j in range(2):
   d=np.eye(2)[j]*eps;Jw[:,j]=(route(P+d,beta)[5]-route(P-d,beta)[5])/(2*eps)
  # The arc/free centroid depends ONLY on E; moving P at fixed beta moves E.
  U=0.;grad=np.zeros(4*n+1);positions=[];by_mode={}
  for item in self.points:
   mode=item['mode'];c=np.array(item['rest_centroid_m']);q=c[[0,2]];J=np.zeros((2,4*n+1));m=item['mass_kg']
   if mode in ('rail','pet'):
    ispet=mode=='pet';data=pet if ispet else rail;s=item['material_station_m'];pt,j,_,_=kin.point(data,s);a,e,h,_,_=data;i=min(int(s/h),n-1);u=(s-i*h)/h;ang=(1-u)*a[i]+u*a[i+1];offset=q-np.array([.05015 if ispet else .0504,-.007-s]);q=pt+rot(ang)@offset;da=np.zeros(2*n)
    if i:da[i-1]=1-u
    da[i]=u;j+=np.outer(drot(ang)@offset,da);J[:,2*n if ispet else 0:4*n if ispet else 2*n]=j
   elif mode=='terminal':
    offset=q-[.0504,-.084];q=rail[3][-1]+R@offset;J[:,:4*n]=jr;J[:,n-1]+=dR@offset
   elif mode=='swivel':
    offset=q-P0;q=P+rot(beta-BETA0)@offset;J[:,:4*n]=JP;J[:,-1]=drot(beta-BETA0)@offset
   elif mode=='rotor':
    offset=q-C;q=C+rot(eta)@offset;J=np.outer(drot(eta)@offset,Je)
   elif mode=='wire':q=wc;J=Jw@JE
   u=m*G*factor*q[1];dg=m*G*factor*J[1];U+=u;grad+=dg;by_mode.setdefault(mode,np.zeros_like(grad));by_mode[mode]+=dg
   if details:positions.append(dict(part_ID=item['part_ID'],mode=mode,mass_kg=m,position_m=[float(q[0]),float(c[1]),float(q[1])]))
  return U,grad,positions,dict(P=P,E=E,Q=Q,t=t,length=length,eta=eta,dl=dl,JP=JP,tip=tip,Jtip=JT,by_mode=by_mode,wire_length=wl)
