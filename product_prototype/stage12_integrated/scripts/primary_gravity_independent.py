"""Independent complex-analytic sinc kinematics and mass potential, no production Jacobians."""
import numpy as np
G=9.80665;L=.077;LP=.0862

def R(a):return np.array([[np.cos(a),np.sin(a)],[-np.sin(a),np.cos(a)]])
def rod(v,n,pet=False,s=None):
 length=LP if pet else L;h=length/n;a=np.r_[0.,v[:n]];e=v[n:]*1e-4;p=np.array([.05015 if pet else .0504,-.007],dtype=np.result_type(v));nodes=[p]
 for i in range(n):
  d=a[i+1]-a[i];mid=(a[i]+a[i+1])/2;p=p-h*(1+e[i])*np.sinc(d/(2*np.pi))*np.array([np.sin(mid),np.cos(mid)]);nodes.append(p)
 if s is None:return np.array(nodes),a,e
 i=min(int(s/h),n-1);u=(s-i*h)/h;d=a[i+1]-a[i];mid=a[i]+u*d/2
 return nodes[i]-h*u*(1+e[i])*np.sinc(d*u/(2*np.pi))*np.array([np.sin(mid),np.cos(mid)]),a[i]+u*d

def angle(y,x):
 z=np.arctan(y/x)
 if np.real(x)<0:z+=np.pi if np.real(y)>=0 else -np.pi
 return z

def cable(P):
 C=np.array([0.,.020]);r=.01125;D=P-C;dist=np.sqrt(D@D);u=D/dist;k=r/dist;normal=k*u+np.sqrt(1-k*k)*np.array([-u[1],u[0]]);Q=C+r*normal;distance=np.sqrt((Q-P)@(Q-P));t=(Q-P)/distance;phi=angle(normal[1],normal[0]);free=r*(np.pi/2-phi)+distance-.016
 return Q,t,phi,free
P0=np.array([.043,-.092]);_,t0,_,f0=cable(P0);b0=angle(t0[0],t0[1]);C=np.array([0.,.020]);RAD=.01125

def positions(v,n,points,beta=None):
 rail,a,e=rod(v[:2*n],n);end=rail[-1];P=end+R(a[-1])@[-.0074,-.008];E=None
 if beta is None:Q,t,phi,free=cable(P);beta=angle(t[0],t[1]);E=P+.016*t
 else:E=P+.016*np.array([np.sin(beta),np.cos(beta)]);Q,t,phi,free=cable(E);free+=.016
 eta=(free-f0)/RAD;result=[]
 for item in points:
  q=np.array(item['rest_centroid_m'])[[0,2]];mode=item['mode']
  if mode in ('rail','pet'):
   pet=mode=='pet';s=item['material_station_m'];p,th=rod(v[2*n:] if pet else v[:2*n],n,pet,s);q=p+R(th)@(q-[.05015 if pet else .0504,-.007-s])
  elif mode=='terminal':q=end+R(a[-1])@(q-[.0504,-.084])
  elif mode=='swivel':q=P+R(beta-b0)@(q-P0)
  elif mode=='rotor':q=C+R(eta)@(q-C)
  elif mode=='wire':
   start=np.pi/2-eta;arc=RAD*(start-phi);lead=np.sqrt((E-Q)@(E-Q));q=(RAD**2*np.array([np.sin(start)-np.sin(phi),np.cos(phi)-np.cos(start)])+C*arc+(Q+E)*lead/2+.006*(C+R(eta)@[-.003,RAD]))/(f0+.006)
  result.append(q)
 return np.array(result)

def potential(v,n,points,factor=1.):return sum(item['mass_kg']*G*factor*p[1] for item,p in zip(points,positions(v,n,points)))
def gradient(v,n,points,factor=1.):
 g=[]
 for i in range(len(v)):
  x=v.astype(complex);x[i]+=1e-25j;g.append(potential(x,n,points,factor).imag/1e-25)
 return np.array(g)


def potential_free(x,n,points,factor=1.):return sum(item['mass_kg']*G*factor*p[1] for item,p in zip(points,positions(x[:4*n],n,points,x[-1])))
def length_free(x,n):
 rail,a,e=rod(x[:2*n],n);P=rail[-1]+R(a[-1])@[-.0074,-.008];E=P+.016*np.array([np.sin(x[-1]),np.cos(x[-1])]);return cable(E)[3]+.016
def derivatives_free(x,n,points,factor=1.):
 gu=[];gl=[]
 for i in range(len(x)):
  z=x.astype(complex);z[i]+=1e-25j;gu.append(potential_free(z,n,points,factor).imag/1e-25);gl.append(length_free(z,n).imag/1e-25)
 return np.array(gu),np.array(gl)
