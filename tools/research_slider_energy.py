"""Independent variable-capacity spring/slider identity, not global energy.

e=s-p;F=k e. With end-point work F1 Delta s and associative scalar return:
W1 - Delta U - F1 Delta p = .5 k (Delta e)^2.
The RHS is DERIVED backward-step projection loss, never fitted residual/heat.
The prescribed pressure only changes the yield cap in this research model;
no chamber volume or normal pressure work exists in that scalar law.
"""
import random
from research_common import OUT,write_json
def main():
    rng=random.Random(2911);s0=p0=0.;k=3.;worst=0.;minimum=0.;sample=[]
    for i in range(10000):
        s1=s0+rng.uniform(-.02,.02);cap=rng.uniform(0,.05) if i%7 else 0.
        force=max(-cap,min(cap,k*(s1-p0)));p1=s1-force/k
        e0=s0-p0;e1=s1-p1;du=.5*k*(e1*e1-e0*e0);work=force*(s1-s0);friction=force*(p1-p0);discrete=.5*k*(e1-e0)**2;residual=work-du-friction-discrete
        worst=max(worst,abs(residual));minimum=min(minimum,friction)
        if i<20:sample.append(dict(s0=s0,s1=s1,p0=p0,p1=p1,capacity=cap,work=work,delta_U=du,associative_friction=friction,derived_backward_projection_loss=discrete,unexplained_residual=residual))
        s0,p0=s1,p1
    write_json(OUT/'slider_energy_identity.json',dict(status='PASS'if worst<1e-14 and minimum>=-1e-14 else'FAIL',origin='independent mathematical scalar pressure-cap slider',maximum_residual=worst,minimum_friction=minimum,trials=10000,samples=sample,limitations='Not actual vacuum pressure work; not proof for finite-rotation/contact transport/global SOFA integration. Do not fit unexplained residual as numerical loss.'))
    print(worst,minimum)
if __name__=='__main__':main()
