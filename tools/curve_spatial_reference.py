"""Separate interpolation error from solved Beam nodal-field error."""
import numpy as np
from scipy.integrate import quad
from curve_common import OUT,write_json
def main():
    L=100.;tip=.1;cx=47.3;R=5.;skin=.1;depth=.005;spacing=.0025
    def y(x):return tip*x*x*(3*L-x)/(2*L**3)
    def slope(x):return tip*3*x*(2*L-x)/(2*L**3)
    center=np.array([cx,R+skin+y(cx)-depth,0.]);reference,error=quad(lambda x:max(0.,R+skin-np.hypot(x-cx,y(x)-center[1])),cx-1,cx+1,epsabs=1e-13,epsrel=1e-11,limit=300)
    rows=[]
    for nodes in(11,21,41):
        X=np.linspace(0,L,nodes);ell=L/(nodes-1);n=round(ell/spacing);s=(np.arange(n)+.5)/n;h0=2*s**3-3*s*s+1;h1=1-h0;t0=s**3-2*s*s+s;t1=s**3-s*s;totals=dict(linear=0.,hermite=0.)
        for i in range(nodes-1):
            a=np.array([X[i],y(X[i]),0.]);b=np.array([X[i+1],y(X[i+1]),0.]);v0=np.array([1.,slope(X[i]),0.]);v0/=np.linalg.norm(v0);v1=np.array([1.,slope(X[i+1]),0.]);v1/=np.linalg.norm(v1)
            positions={'linear':(1-s[:,None])*a+s[:,None]*b,'hermite':h0[:,None]*a+h1[:,None]*b+ell*t0[:,None]*v0+ell*t1[:,None]*v1}
            for name,p in positions.items():totals[name]+=ell*float(np.maximum(R+skin-np.linalg.norm(p-center,axis=1),0.).mean())
        rows.append(dict(nodes=nodes,integrals=totals,relative_errors={k:abs(v-reference)/abs(reference)for k,v in totals.items()}))
    result=dict(origin='independent prescribed analytic cubic nodal positions/directors;NOT solved SOFA/FEM',reference=reference,reference_estimated_error=error,rows=rows,parameters=dict(length=L,tip=tip,center=center.tolist(),radius=R,skin=skin,penetration=depth,kn=1,spacing=spacing),scope='same fixed midpoint rule separates interpolation from unknown nodal solution error;normalized directors/reference length are explicit assumptions')
    path=OUT/'spatial_interpolation_reference.json'
    if path.exists():raise FileExistsError(path)
    write_json(path,result);print(result)
if __name__=='__main__':main()
