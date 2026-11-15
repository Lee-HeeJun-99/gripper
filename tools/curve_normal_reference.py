"""Independent degree-six sphere intersections on actual curved SOFA states."""
import json,csv
import numpy as np
from scipy.integrate import quad_vec
from curve_common import OUT,write_json
from research_geometry import saved_x
def director(q):
    x,y,z,w=q;return np.array([1-2*(y*y+z*z),2*(x*y+w*z),2*(x*z-w*y)])
def check(path):
    c=json.loads((path/'config.json').read_text());initial,x=saved_x(path/'state.txt');n=c['nodes'];center=x[-1,:3];radius=c['object_radius']+.1;kn=c['normal_k'];total=np.zeros(5);estimate=0;maxRootResidual=0;midpoint=0;patches=0
    for layer in range(6):
        for i in range(n-1):
            a=layer*n+i;b=a+1;L=np.linalg.norm(initial[b,:3]-initial[a,:3]);d0=director(x[a,3:]);d1=director(x[b,3:]);delta=x[b,:3]-x[a,:3];coeff=np.array([x[a,:3]-center,L*d0,3*delta-2*L*d0-L*d1,-2*delta+L*(d0+d1)])
            polynomial=np.zeros(7)
            for j in range(3):
                term=np.polynomial.polynomial.polymul(coeff[:,j],coeff[:,j]);polynomial[:len(term)]+=term
            polynomial[0]-=radius**2
            roots=np.polynomial.polynomial.polyroots(polynomial);real=sorted(float(r.real)for r in roots if abs(r.imag)<1e-8 and 0<r.real<1)
            def position(s):return np.polynomial.polynomial.polyval(s,coeff)
            def integrand(s):
                p=position(s);norm=np.linalg.norm(p);depth=max(0.,radius-norm);return L*np.r_[kn*depth,kn*depth*p/norm,.5*kn*depth**2]
            for r in real:maxRootResidual=max(maxRootResidual,abs(np.linalg.norm(position(r))-radius))
            bounds=[0]+real+[1]
            for lo,hi in zip(bounds[:-1],bounds[1:]):
                if np.linalg.norm(position((lo+hi)/2))>=radius:continue
                value,error=quad_vec(integrand,lo,hi,epsabs=1e-14,epsrel=1e-11);total+=value;estimate+=error;patches+=1
            count=round(L/c['history_spacing']);s=(np.arange(count)+.5)/count;p=np.polynomial.polynomial.polyval(s,coeff).T;midpoint+=L*kn*float(np.maximum(radius-np.linalg.norm(p,axis=1),0).mean())
    with(path/'contact.csv').open()as f:row=min(csv.DictReader(f),key=lambda r:abs(float(r['time'])-13.99))
    actual=float(row['normal_force']);relative=abs(actual-total[0])/abs(total[0]);return dict(status='PASS'if relative<.01 and maxRootResidual<1e-9 and abs(actual-midpoint)<1e-12 else'FAIL',origin='independent polynomial sphere-boundaries/adaptive integration on actual SOFA nodal state,not re-solved dynamics',actual_time=float(row['time']),actual_cpp_normal_force=actual,reconstructed_midpoint_normal_force=midpoint,reference_normal_force=float(total[0]),reference_finger_force_vector=total[1:4].tolist(),reference_normal_energy=float(total[4]),relative_cpp_quadrature_error=float(relative),reference_estimated_absolute_error=float(estimate),maximum_geometric_root_residual_mm=float(maxRootResidual),active_patches=patches,scope='normal integration error separated from tangent/material-history error;current Sphere only,1percent unchanged')
def main():
    for p in sorted((OUT/'grasp').glob('*/metrics.json')):
        c=json.loads(p.read_text())['config'];target=OUT/('normal_reference_v2_'+p.parent.name+'.json')
        if c['profile_only']or c['shape']!=0 or target.exists():continue
        result=check(p.parent);write_json(target,result);print(p.parent.name,result['status'],result['relative_cpp_quadrature_error'])
if __name__=='__main__':main()
