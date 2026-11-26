"""Exact finite circular-arc rod point Jacobians for STATIC material contacts."""
import math
import numpy as np
def sinc_derivative(x):
    if abs(x)<1e-4:return -x/3+x**3/30-x**5/840
    return (x*math.cos(x)-math.sin(x))/(x*x)
def integrated(theta0,theta1,h,t):
    d=theta1-theta0;z=d*t/2;v=np.sinc(z/np.pi);phase=np.exp(1j*(theta0+d*t/2));pref=h*t*phase
    return pref*v,pref*(-t/2*sinc_derivative(z)+1j*(1-t/2)*v),pref*(t/2*sinc_derivative(z)+1j*t/2*v)
def prepare(q,L):
    n=len(q);h=L/n;a=np.r_[0.,q];u=np.zeros(n+1,dtype=complex);u[0]=1j*.00025;G=np.zeros((n+1,n),dtype=complex)
    for i in range(n):
        v,g0,g1=integrated(a[i],a[i+1],h,1.);u[i+1]=u[i]+v;G[i+1]=G[i]
        if i:G[i+1,i-1]+=g0
        G[i+1,i]+=g1
    return a,u,G,h
def point(prepared,i,t,side,M,shift,local=True):
    a,u,G,h=prepared;n=G.shape[1];v,g0,g1=integrated(a[i],a[i+1],h,t);p=u[i]+v;g=G[i].copy()
    if i:g[i-1]+=g0
    g[i]+=g1;phi=(1-t)*a[i]+t*a[i+1];dq=np.zeros(n)
    if i:dq[i-1]=1-t
    dq[i]=t
    world=np.array([.0504-p.imag,-.007-p.real])+side*.00015*np.array([-math.cos(phi),math.sin(phi)])
    J=np.vstack((-g.imag,-g.real))+side*.00015*np.outer([math.sin(phi),math.cos(phi)],dq)
    return (M.T@(world-shift),M.T@J) if local else (world,J)
def rectangle(p,lo,hi):
    lo,hi=np.array(lo),np.array(hi);z=p-(lo+hi)/2;d=np.abs(z)-(hi-lo)/2;v=np.maximum(d,0);length=np.linalg.norm(v)
    if length:return float(length+min(float(d.max()),0.)),np.sign(z)*v/length
    i=int(np.argmax(d));normal=np.zeros(2);normal[i]=1 if z[i]>=0 else -1
    return float(d[i]),normal
def walls(p,fc,fr):
    a,na=rectangle(p,[.040,-.095],[.049,-.084]);b,nb=rectangle(p,[.040,-.100],[.050,-.095]);c,nc=rectangle(p,[.04898,-.095],[.04990,-.090]);radius=np.linalg.norm(p-fc);circle=radius-fr
    return np.array([a,b,max(c,circle)]),np.vstack((na,nb,(p-fc)/radius if circle>=c else nc))
