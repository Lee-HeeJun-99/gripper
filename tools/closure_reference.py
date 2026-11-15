"""Independent high-accuracy integration of the original line/sphere law."""
import json,math
import numpy as np
from scipy.integrate import quad
from closure_common import OUT,write_json
def main():
    out=OUT/'reference';out.mkdir(parents=True,exist_ok=False);rows=[]
    R=5.;skin=.1;kn=.001;kt=.001;L=10.;z=5.099;a=math.sqrt((R+skin)**2-z*z);shift=0.00001
    def density(x):
        d=math.hypot(x,z);n=np.array([x,0,z])/d;fn=kn*(R+skin-d);du=np.array([shift,0,0]);elastic=du-n*np.dot(n,du);ft=-kt*elastic;cap=.3*fn
        if np.linalg.norm(ft)>cap:ft*=cap/np.linalg.norm(ft)
        return fn*n,ft,.5*kn*(R+skin-d)**2
    reference=np.array([quad(lambda x:density(x)[0][j],-a,a,epsabs=1e-17,epsrel=1e-12)[0] for j in range(3)]+[quad(lambda x:density(x)[1][j],-a,a,epsabs=1e-17,epsrel=1e-12,limit=150)[0] for j in range(3)]+[quad(lambda x:density(x)[2],-a,a,epsabs=1e-20,epsrel=1e-12)[0]])
    for q in (8,16,32):
        nodes,weights=np.polynomial.legendre.leggauss(q);active=np.zeros(7)
        for x,w in zip(a*nodes,a*weights):
            n,t,e=density(x);active+=w*np.r_[n,t,e]
        trap=np.zeros(7)
        for i in range(q+1):
            x=-L/2+L*i/q
            if abs(x)<a:
                n,t,e=density(x);trap+=L/q*(.5 if i in (0,q) else 1)*np.r_[n,t,e]
        rows.append(dict(order=q,active_interval_length=2*a,reference=reference.tolist(),gauss=active.tolist(),gauss_max_abs_error=float(abs(active-reference).max()),trapezoid=trap.tolist(),trap_max_abs_error=float(abs(trap-reference).max()),scope='same line stiffness and skin; flat projected elastic trial / return mapping; independent SciPy reference'))
    write_json(out/'summary.json',dict(status='PASS' if all(r['gauss_max_abs_error']<1e-10 for r in rows) else 'FAIL',rows=rows,reference_method='scipy QUADPACK boundary-split epsabs1e-17/1e-20 epsrel1e-12',real_measurement=False));print([(r['order'],r['gauss_max_abs_error'],r['trap_max_abs_error']) for r in rows])
if __name__=='__main__':main()
