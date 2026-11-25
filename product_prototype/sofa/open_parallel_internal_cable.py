"""Actual Native two-ended C2 impulse through a free-root open mechanism.
One-step small coupon only; no finite-wire/contact or whole-grasp claim.
"""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
from open_parallel_free_root import mass_reference,flat

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    src=BASE/'results/open_parallel_root1784/column6/scene.scn';root=ET.parse(src).getroot()
    drive=root.find("Node[@name='drive']");drive.find('ConstantForceField').set('forces','0')
    for n in root.iter('NativeRigidJournal'):
        n.set('filename',str(out/Path(n.get('filename')).name))
    mapped=drive.find("Node[@name='angles']/Node[@name='mapped']")
    cable=ET.SubElement(mapped,'Node',name='cable')
    points=np.array([[0,0,0],[.005,.0015,0]])
    ET.SubElement(cable,'MechanicalObject',template='Vec3d',name='points',position=flat(points))
    ET.SubElement(cable,'RigidMapping',input='@../frames',output='@points',rigidIndexPerPoint='0 2',globalToLocalCoords='1',mapMatrices='1')
    tension=1e-7;dt=.001
    ET.SubElement(cable,'CableConstraint',template='Vec3d',name='actuator',indices='0 1',hasPullPoint='0',valueType='force',value=str(tension*dt))
    ET.SubElement(cable,'NativeCableAudit',body='@points',cable='@actuator',filename=str(out/'cable.csv'))
    ET.SubElement(root,'NativeConstraintJournal',solver='@constraints',filename=str(out/'constraints.csv'))
    ET.ElementTree(root).write(out/'scene.scn')
    # Equal/opposite endpoint forces produce zero external root wrench.
    direction=points[1]/np.linalg.norm(points[1]);g=np.zeros(7)
    g[6]=-tension*(direction@np.array([0,.005,0]))
    reference=np.linalg.solve(mass_reference(),dt*g)
    process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','1','--hideProgressBar',out/'scene.scn'],out/'process',60)
    logs=''.join((out/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'))
    valid=process['exit_code']==0 and '[ERROR]'not in logs;metrics={}
    if valid:
        b=list(csv.DictReader((out/'base.csv').open()));c=list(csv.DictReader((out/'body.csv').open()))
        rows=list(csv.DictReader((out/'constraints.csv').open()));audit=list(csv.DictReader((out/'cable.csv').open()))
        assert len(b)==len(c)==len(rows)==len(audit)==1
        vb=np.fromstring(b[0]['rigid_v'],sep=' ');vc=np.fromstring(c[0]['rigid_v'],sep=' ').reshape(-1,6)
        v=np.r_[vb,vc[1,5]-vb[5]];error=float(abs(v-reference).max())
        impulse=np.fromstring(rows[0]['impulses_Ns'],sep=' ');assert len(impulse)==1
        force_error=float(abs(impulse[0]/dt-tension))
        momentum=.005*vb[:3]+.001*vc[[1,2,3],:3].sum(0)
        metrics=dict(velocity_error=error,actual_velocity=v.tolist(),reference_velocity=reference.tolist(),
            tension_N=tension,actual_impulse_Ns=float(impulse[0]),force_error_N=force_error,
            linear_momentum_Ns=momentum.tolist(),native_linear_residual=rows[0]['error'],native_iterations=rows[0]['iterations'])
        valid=bool(np.isfinite(v).all() and error<=1e-12 and force_error<=1e-12 and abs(momentum).max()<=1e-12)
    d=dict(status='PASS_INTERNAL_CABLE_INITIAL_CONTRACT_ONLY' if valid else 'FAIL_INTERNAL_CABLE_INITIAL_CONTRACT',
        measurements=metrics,process=process,scene_sha256=sha(out/'scene.scn'),source_sha256=sha(Path(__file__)),
        reference_source_sha256=sha(Path(__file__).parent/'open_parallel_free_root.py'),source_scene_sha256=sha(src),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),
        errors=[line for line in logs.splitlines() if '[ERROR]'in line],
        sdk='/home/ubuntu/SOFA/v26.06.00',
        scope='Actual stock C2 with hasPullPoint=false and different physical root/coupler owners; no external cable anchor or active fixed root. Small1step force impulse/mass contract ONLY. Not continuous anisotropic inertia, physical motor/cable friction, finite wire, joint/contact/FEM dynamics, energy/time convergence or grasp PASS.')
    d['plugin_files']=[dict(path=n.get('pluginName'),sha256=sha(Path(n.get('pluginName')))) for n in root.findall('RequiredPlugin') if Path(n.get('pluginName')).is_file()]
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps({k:v for k,v in d.items() if k!='plugin_files'},indent=2))

if __name__=='__main__':main()
