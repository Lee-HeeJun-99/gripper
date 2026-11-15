"""Independent prescribed curved contact integral,not solved dynamics."""
import math
import numpy as np
from scipy.integrate import quad_vec
from scipy.optimize import brentq
from curve_common import OUT,write_json
def main():
    L=2.;angle=.9;skin=.1;radius=1.;kn=1.;a=np.array([-1,1.3,0.]);b=np.array([1,1.3,0.]);d0=np.array([math.cos(angle),-math.sin(angle),0.]);d1=np.array([math.cos(angle),math.sin(angle),0.])
    def position(s):return(2*s**3-3*s*s+1)*a+(-2*s**3+3*s*s)*b+L*(s**3-2*s*s+s)*d0+L*(s**3-s*s)*d1
    def gap(s):return np.linalg.norm(position(s))-radius-skin
    x=np.linspace(0,1,2049);roots=[brentq(gap,l,r,xtol=1e-14)for l,r in zip(x[:-1],x[1:])if gap(l)*gap(r)<0];bounds=[0]+roots+[1];active=[(l,r)for l,r in zip(bounds[:-1],bounds[1:])if gap((l+r)/2)<0]
    def integrand(s):
        p=position(s);norm=np.linalg.norm(p);depth=max(0.,radius+skin-norm);f=kn*depth*p/norm;t=np.cross(p,-f);return L*np.r_[f,t,.5*kn*depth**2]
    reference=np.zeros(7);estimate=0
    for l,r in active:
        value,error=quad_vec(integrand,l,r,epsabs=1e-13,epsrel=1e-12);reference+=value;estimate+=error
    rows=[]
    for h in(.02,.01,.005,.0025,.00125):
        n=math.ceil(L/h);value=sum((integrand((i+.5)/n)/n for i in range(n)),np.zeros(7));error=np.linalg.norm(value[:3]-reference[:3])/np.linalg.norm(reference[:3]);rows.append(dict(spacing_mm=h,normal_force_relative_error=float(error),energy_relative_error=float(abs(value[6]-reference[6])/reference[6]),force=value[:3].tolist(),object_torque=value[3:6].tolist()))
    result=dict(status='PASS'if rows[-1]['normal_force_relative_error']<.0001 else'FAIL',origin='independent prescribed director-Hermite geometry/reference integration,no SOFA dynamics',active_intervals=active,active_reference_length=sum(r-l for l,r in active)*L,reference=reference.tolist(),reference_estimated_error=float(estimate),rows=rows,scope='normal fixed-point integration only;not friction/history/Beam convergence')
    target=OUT/'independent_reference.json'
    if target.exists():raise FileExistsError(target)
    write_json(target,result);print(result)
if __name__=='__main__':main()
