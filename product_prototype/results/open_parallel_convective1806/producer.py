"""Finite initial velocity tests beyond initial J.T M J; stock Native only.
Analytic rigid-body acceleration balance is diagnostic, never a Native force.
"""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
from open_parallel_free_root import flat,mass_reference
from native_bending_coupon import guarded

def convective_load(theta,R,u):
    L=.005;H=.003;m=.001;w=.0008;omega=u[3:6];speed=u[6]
    Z=Rotation.from_rotvec([0,0,theta]).as_matrix();a=Z@np.array([L/2,0,0]);b=2*a
    normal=np.array([2*w*w,L*L+w*w,L*L+w*w])/12
    inertia=(R@Z)@np.diag(m*normal)@(R@Z).T
    bodies=[(a,a,inertia,True),(b+[0,H/2,0],b,np.eye(3)*1e-9,False),
        (a+[0,H,0],a,inertia,True)]
    h=np.zeros(7)
    for r,rotating,I,spins in bodies:
        p=R@r;jv=R@np.cross([0,0,1],rotating);jw=R@np.array([0,0,1]) if spins else np.zeros(3)
        curvature=R@(-rotating)
        linear=np.cross(omega,np.cross(omega,p))+2*np.cross(omega,jv*speed)+curvature*speed**2
        angular=np.cross(omega,jw*speed);body_omega=omega+jw*speed
        F=m*linear;torque=I@angular+np.cross(body_omega,I@body_omega)
        h[:3]+=F;h[3:6]+=np.cross(p,F)+torque;h[6]+=jv@F+jw@torque
    return h

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    src=BASE/'results/open_parallel_points1805/column6/scene.scn';root=ET.parse(src).getroot()
    base=root.find("Node[@name='base']");drive=root.find("Node[@name='drive']")
    u=np.array([0,0,0,.3,-.2,.4,1.]);theta=.4;R=Rotation.from_euler('xyz',[20,-15,30],degrees=True)
    base.find('MechanicalObject').set('velocity',flat(u[:6]));drive.find('MechanicalObject').set('velocity',str(u[6]))
    base.find('ConstantForceField').set('forces','0 0 0 0 0 0');drive.find('ConstantForceField').set('forces','0')
    for node in root.iter('NativeRigidJournal'):node.set('filename',str(out/Path(node.get('filename')).name))
    ET.ElementTree(root).write(out/'scene.scn');dt=.001;M=mass_reference(theta,R.as_matrix());h=convective_load(theta,R.as_matrix(),u)
    predicted=u-dt*np.linalg.solve(M,h)
    process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','1','--hideProgressBar',out/'scene.scn'],out/'process',60)
    logs=''.join((out/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));valid=process['exit_code']==0 and '[ERROR]'not in logs;metrics={}
    if valid:
        b=list(csv.DictReader((out/'base.csv').open()))[0];c=list(csv.DictReader((out/'body.csv').open()))[0]
        qb=np.fromstring(b['rigid_q'],sep=' ');vb=np.fromstring(b['rigid_v'],sep=' ');vc=np.fromstring(c['rigid_v'],sep=' ').reshape(-1,6)
        accepted_axis=Rotation.from_quat(qb[3:]).apply([0,0,1])
        measured=np.r_[vb,(vc[1,3:]-vb[3:])@accepted_axis]
        error=float(abs(measured-predicted).max());unchanged=float(abs(measured-u).max())
        momentum=.005*vb[:3]+.001*vc[[1,2,3],:3].sum(0)
        # Independent initial total linear momentum from Jv(q0)*u.
        initial_momentum=(M@u)[:3]
        metrics=dict(initial_velocity=u.tolist(),actual_velocity=measured.tolist(),
            independent_initial_convective_load=h.tolist(),frozen_Euler_expected_velocity=predicted.tolist(),
            maximum_frozen_velocity_error=error,maximum_native_change_from_initial=unchanged,
            total_linear_momentum_change_Ns=(momentum-initial_momentum).tolist())
        valid=bool(np.isfinite(measured).all() and error<=1e-12 and abs(momentum-initial_momentum).max()<=1e-12)
    result=dict(status='PASS_FINITE_VELOCITY_CONTRACT_ONLY' if valid else 'FAIL_FINITE_VELOCITY_CONTRACT',measurements=metrics,process=process,
        source_sha256=sha(Path(__file__)),source_scene_sha256=sha(src),scene_sha256=sha(out/'scene.scn'),
        reference_source_sha256=sha(Path(__file__).parent/'open_parallel_free_root.py'),
        scope='Initial nonzero root/joint velocities are declared free coupon initial conditions, not trajectory resets or object manipulation. Exact physical initial convective generalized load and first frozen-Euler balance tested; not a continuous-time solution or B3 model. Point mass quadrature initial matrix1805PASS does not certify missing gyro/Coriolis/centrifugal dynamics. No corrective force/ODE/SDK implementation added.')
    (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(result,indent=2))

if __name__=='__main__':main()
