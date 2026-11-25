"""Seven-column free-root initial mapped mass contract; no custom Native solver.
Independent J.T M J is a diagnostic, never a state/control write.
"""
import argparse
import copy
import csv
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
from native_bending_coupon import guarded

def flat(x):return ' '.join(format(float(v),'.17g') for v in np.asarray(x).ravel())
def skew(p):
    x,y,z=p
    return np.array([[0,-z,y],[z,0,-x],[-y,x,0]])

def mass_reference(theta=0.,rotation=None,world_fixed_inertia=False):
    L=.005;H=.003;m=.001;width=.0008
    R=np.eye(3) if rotation is None else rotation
    Z=Rotation.from_rotvec([0,0,theta]).as_matrix()
    matrix=np.diag([.005]*3+[.005e-6]*3+[0.])
    normal=np.array([2*width*width,L*L+width*width,L*L+width*width])/12
    a=Z@np.array([L/2,0,0]);b=Z@np.array([L,0,0])
    link_I=np.diag(m*normal) if world_fixed_inertia else (R@Z)@np.diag(m*normal)@(R@Z).T
    bodies=[(a,np.cross([0,0,1],a),[0,0,1],link_I),
        (b+[0,H/2,0],np.cross([0,0,1],b),[0,0,0],np.eye(3)*1e-9),
        (a+[0,H,0],np.cross([0,0,1],a),[0,0,1],link_I)]
    for p,jv,jw,I in bodies:
        Jv=np.column_stack([np.eye(3),-skew(R@p),R@jv])
        Jw=np.column_stack([np.zeros((3,3)),np.eye(3),R@jw])
        matrix+=m*Jv.T@Jv+Jw.T@I@Jw
    return matrix

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True)
    p.add_argument('--angle',type=float,default=0.)
    p.add_argument('--world-initial-tensors',action='store_true')
    p.add_argument('--root-euler-deg',type=float,nargs=3,default=[0.,0.,0.]);a=p.parse_args()
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    src=BASE/'results/open_parallel_unique1765/scene.scn'
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip()
    root_rotation=Rotation.from_euler('xyz',a.root_euler_deg,degrees=True)
    dt=.001;gate=1e-12;M=mass_reference(a.angle,root_rotation.as_matrix());records=[]
    assert np.linalg.eigvalsh(M).min()>0
    for k in range(7):
        case=out/f'column{k}';case.mkdir();root=ET.parse(src).getroot()
        base=ET.Element('Node',name='base')
        ET.SubElement(base,'MechanicalObject',template='Rigid3d',name='body',position=flat(np.r_[np.zeros(3),root_rotation.as_quat()]))
        ET.SubElement(base,'UniformMass',template='Rigid3d',vertexMass='.005 1e-8 1e-6 0 0 0 1e-6 0 0 0 1e-6')
        load=np.zeros(7);load[k]=1e-7 if k<3 else 1e-10
        ET.SubElement(base,'ConstantForceField',template='Rigid3d',indices='0',forces=flat(load[:6]))
        ET.SubElement(base,'NativeRigidJournal',body='@body',solver='@../constraints',filename=str(case/'base.csv'))
        drive=root.find("Node[@name='drive']");root.insert(list(root).index(drive),base)
        drive.find('MechanicalObject').set('position',str(a.angle))
        drive.find("Node[@name='angles']/MechanicalObject").set('position',flat([a.angle]*3))
        drive.find('ConstantForceField').set('forces',str(load[6]))
        mapped=drive.find("Node[@name='angles']/Node[@name='mapped']")
        if a.world_initial_tensors:
            link_mass=mapped.find("UniformMass[@name='links']")
            props=np.fromstring(link_mass.get('vertexMass'),sep=' ')
            R=root_rotation.as_matrix()@Rotation.from_rotvec([0,0,a.angle]).as_matrix()
            props[2:]=(R@props[2:].reshape(3,3)@R.T).ravel()
            link_mass.set('vertexMass',flat(props))
        mapped.find('ArticulatedSystemMapping').set('input2','@../../../base/body')
        mapped.find('NativeRigidJournal').set('filename',str(case/'body.csv'))
        ET.ElementTree(root).write(case/'scene.scn')
        process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','1','--hideProgressBar',case/'scene.scn'],case/'process',60)
        logs=''.join((case/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'))
        valid=process['exit_code']==0 and '[ERROR]'not in logs
        record=dict(column=k,load=load.tolist(),process=process,scene_sha256=sha(case/'scene.scn'),
            errors=[line for line in logs.splitlines() if '[ERROR]'in line])
        if valid:
            b=list(csv.DictReader((case/'base.csv').open()));c=list(csv.DictReader((case/'body.csv').open()))
            assert len(b)==len(c)==1
            vb=np.fromstring(b[0]['rigid_v'],sep=' ');vc=np.fromstring(c[0]['rigid_v'],sep=' ').reshape(-1,6)
            velocity=np.r_[vb,(vc[1,3:]-vb[3:])@root_rotation.apply([0,0,1])]
            reference=np.linalg.solve(M,dt*load)
            error=float(abs(velocity-reference).max())
            record.update(actual_generalized_velocity=velocity.tolist(),reference_generalized_velocity=reference.tolist(),
                maximum_velocity_error=error,mass_impulse_residual=(M@velocity-dt*load).tolist())
            valid=bool(np.isfinite(velocity).all() and error<=gate)
        record['status']='PASS_INITIAL_COLUMN_ONLY' if valid else 'FAIL_INITIAL_COLUMN'
        records.append(record)
    plugin_files=[]
    for n in ET.parse(src).getroot().findall('RequiredPlugin'):
        path=Path(n.get('pluginName',''))
        if path.is_file():plugin_files.append(dict(path=str(path),sha256=sha(path)))
    d=dict(status='PASS_FREE_ROOT_INITIAL_MASS_ONLY' if all(r['status']=='PASS_INITIAL_COLUMN_ONLY' for r in records) else 'FAIL_FREE_ROOT_INITIAL_MASS',
        records=records,independent_mass_matrix=M.tolist(),gate_absolute_generalized_velocity=gate,dt_s=dt,
        initial_joint_angle_rad=a.angle,initial_root_euler_deg=a.root_euler_deg,
        explicit_world_initial_tensors=a.world_initial_tensors,
        source_commit=commit,source_sha256=sha(Path(__file__)),source_scene_sha256=sha(src),plugin_files=plugin_files,
        sdk='/home/ubuntu/SOFA/v26.06.00',command=__import__('sys').argv,
        scope='Seven one-step small-force columns at undeformed rest, all six root coordinates FREE plus torque-driven scalar. Native mapped masses and root translation/rotation cross blocks compared with independent J transpose M J. Frozen initial tangent diagnostic only; finite amplitude/accepted-map timing can affect velocity. NO full nonlinear integration, deformed root, FEM/finite guides/wire/contact/energy/time convergence or grasp certification. No Native q/v writes or SDK modifications.')
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2))
    print(json.dumps(dict(status=d['status'],columns=[dict(column=r['column'],status=r['status'],error=r.get('maximum_velocity_error')) for r in records]),indent=2))

if __name__=='__main__':main()
