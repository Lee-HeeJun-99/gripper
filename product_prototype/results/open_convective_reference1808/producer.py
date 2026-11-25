"""Independent point-trajectory finite differences of the1806analytic h(q,v).
Finite difference increments are math differentiation, NOT Native dt trials.
"""
import argparse,itertools,json
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
from open_parallel_free_root import skew

def geometry(t,u):
    R=Rotation.from_rotvec(u[3:6]*t).as_matrix()@Rotation.from_euler('xyz',[20,-15,30],degrees=True).as_matrix()
    theta=.4+u[6]*t;Z=Rotation.from_rotvec([0,0,theta]).as_matrix()
    signs=np.array(list(itertools.product((-1.,1.),repeat=3)))
    iso=np.full(3,np.sqrt(.5e-6));link=np.array([.005,.0008,.0008])/(2*np.sqrt(3))
    specs=[(.005,np.zeros(3),iso,False,np.zeros(3)),
        (.001,Z@np.array([.0025,0,0]),link,True,Z@np.array([.0025,0,0])),
        (.001,Z@np.array([.005,0,0])+[0,.0015,0],iso,False,Z@np.array([.005,0,0])),
        (.001,Z@np.array([.0025,0,0])+[0,.003,0],link,True,Z@np.array([.0025,0,0]))]
    positions=[];jacobians=[];weights=[]
    for mass,p,radii,spins,rotating in specs:
        for point in signs*radii:
            offset=Z@point if spins else point
            world=R@(p+offset)
            jt=R@np.cross([0,0,1],rotating+(offset if spins else 0))
            positions.append(u[:3]*t+world);weights.append(mass/8)
            jacobians.append(np.column_stack([np.eye(3),-skew(world),jt]))
    return np.array(positions),np.array(jacobians),np.array(weights)

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/open_parallel_convective1806/summary.json'
    d=json.loads(src.read_text());u=np.array(d['measurements']['initial_velocity']);h=np.array(d['measurements']['independent_initial_convective_load'])
    assert (abs(h)>0).all() # No arbitrary denominator floor or null substitution.
    q,J,weights=geometry(0,u);records=[]
    for step in (.001,.0005):
        acc=(-geometry(2*step,u)[0]+16*geometry(step,u)[0]-30*q+16*geometry(-step,u)[0]-geometry(-2*step,u)[0])/(12*step**2)
        load=np.einsum('n,nji,nj->i',weights,J,acc)
        relative=abs(load-h)/abs(h)
        records.append(dict(math_difference_increment_s=step,point_acceleration_generalized_load=load.tolist(),componentwise_relative_error=relative.tolist()))
    worst=max(max(r['componentwise_relative_error']) for r in records)
    result=dict(status='PASS_INDEPENDENT_CONVECTIVE_REFERENCE_ONLY' if worst<=1e-5 else 'FAIL_CONVECTIVE_REFERENCE',
        records=records,maximum_componentwise_relative_error=float(worst),gate=1e-5,
        inputs=[dict(path=str(p.relative_to(BASE.parent)),sha256=sha(p)) for p in [src,Path(__file__)]],
        scope='Independent32Gaussian-point trajectory second differences reproduce analytic h of1806without reusing its rigid-body acceleration formula. This validates the diagnostic reference, not Native correction or B3 dynamics. Math FD increments are NOT Native time-step convergence; original physical0.1%gate unchanged. No new simulator or forces applied to Native.')
    (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(result,indent=2))

if __name__=='__main__':main()
