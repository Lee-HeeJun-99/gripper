"""Analytic derivatives for P1 separate extensible finite arc strip reduction."""
import numpy as np
from rod_point_jacobian import integrated,walls
L=.088;LP=.0862;ES=1e-4

def prepare(v,length,n,pet=False):
    a=np.r_[0.,v[:n]];e=v[n:]*ES;h=length/n
    points=[np.array([.05015 if pet else .0504,-.007])];jac=[np.zeros((2,2*n))]
    for i in range(n):
        z,g0,g1=integrated(a[i],a[i+1],h,1);J=jac[-1].copy()
        if i:J[:,i-1]+=(1+e[i])*np.array([-g0.imag,-g0.real])
        J[:,i]+=(1+e[i])*np.array([-g1.imag,-g1.real]);J[:,n+i]+=ES*np.array([-z.imag,-z.real])
        points.append(points[-1]+(1+e[i])*np.array([-z.imag,-z.real]));jac.append(J)
    return a,e,h,np.array(points),np.array(jac)

def point(data,s,side=0):
    a,e,h,p,G=data;n=len(e);i=min(int(s/h),n-1);t=(s-i*h)/h
    z,g0,g1=integrated(a[i],a[i+1],h,t);J=G[i].copy()
    if i:J[:,i-1]+=(1+e[i])*np.array([-g0.imag,-g0.real])
    J[:,i]+=(1+e[i])*np.array([-g1.imag,-g1.real]);J[:,n+i]+=ES*np.array([-z.imag,-z.real])
    th=(1-t)*a[i]+t*a[i+1];d=np.zeros(2*n)
    if i:d[i-1]=1-t
    d[i]=t
    normal=np.array([-np.cos(th),np.sin(th)]);dn=np.outer([np.sin(th),np.cos(th)],d)
    return p[i]+(1+e[i])*np.array([-z.imag,-z.real])+side*normal,J+side*dn,normal,dn

def terminal(v,n):
    r=prepare(v[:2*n],L,n);p=prepare(v[2*n:],LP,n,True)
    a=r[0][-1];c,s=np.cos(a),np.sin(a);R=np.array([[c,s],[-s,c]]);dR=np.array([[-s,c],[-c,-s]])
    jr=np.zeros((2,4*n));jr[:,:2*n]=r[4][-1]
    def port(offset):
        x=r[3][-1]+R@offset;J=jr.copy();J[:,n-1]+=dR@offset;return x,J
    P,JP=port(np.array([-.0074,.003]));tip,Jtip=port(np.array([-.0004,-.005]))
    u=(P-[0,.020])/np.linalg.norm(P-[0,.020]);k=.01125/np.linalg.norm(P-[0,.020]);normal=k*u+np.sqrt(1-k*k)*np.array([-u[1],u[0]]);Q=np.array([0,.020])+.01125*normal;t=(Q-P)/np.linalg.norm(Q-P)
    return r,p,R,dR,jr,P,JP,tip,Jtip,t

def gradient(v,n,T,E_RAIL,E_PET,width):
    r,p,R,dR,jr,P,JP,tip,Jtip,t=terminal(v,n);g=np.zeros(4*n)
    for offset,d,length,EA,EI in [(0,r,L,2*E_RAIL*.003*.0002,2*E_RAIL*.003*.0002**3/12),(2*n,p,LP,E_PET*width((np.arange(n)+.5)*LP/n)*.0003,E_PET*width((np.arange(n)+.5)*LP/n)*.0003**3/12)]:
        a,e,h,_,_=d;m=EI*np.diff(a)/h;q=m.copy();q[:-1]-=m[1:];g[offset:offset+n]=q;g[offset+n:offset+2*n]=h*EA*e*ES
    return g-T*(t@JP)

def constraints_jac(v,n,delta,dense=2):
    r,p,R,dR,jr,P,JP,tip,Jtip,t=terminal(v,n);rows=[]
    stations=np.linspace(0,LP,dense*n+1)[1:]
    for s in stations:
        pr,Jr,nr,dnr=point(r,s,.0001);ps,Jp,np_,dnp=point(p,s,-.00015)
        g=np.zeros(4*n);g[:2*n]=-nr@Jr+(ps-pr)@dnr;g[2*n:]=nr@Jp;rows.append(g)
    for s in stations:
        if s<.083:continue
        for side in (-1,1):
            ps,Jp,_,_=point(p,s,side*.00015);J=np.zeros((2,4*n));J[:,2*n:]=Jp
            local=R.T@(ps-r[3][-1])+[.0504,-.095];JL=R.T@(J-jr);JL[:,n-1]+=dR.T@(ps-r[3][-1]);_,N=walls(local,np.array([-.03363880995252074,-.095]),.08350880995252075);rows.extend(N@JL)
    if delta is not None:rows.append(Jtip[0])
    return np.array(rows)
