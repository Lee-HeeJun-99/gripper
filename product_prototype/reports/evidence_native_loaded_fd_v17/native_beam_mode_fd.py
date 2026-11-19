"""PRIVATE native loaded bending-direction test;not a corrected equilibrium."""
import argparse,csv,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from native_bending_coupon import BASE,ROOT,sha,guarded,flat
from observer_identity import compiled_observer

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--fd-steps',nargs='+',type=float);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    binary,compiled=compiled_observer('463')
    for name in ('Observer.cpp','CMakeLists.txt'):(out/name).write_bytes((compiled.parent/name).read_bytes())
    (out/'CMakeCache.txt').write_bytes((binary.parent/'CMakeCache.txt').read_bytes());(out/'ldd.txt').write_text(subprocess.check_output(['ldd',str(binary)],text=True));records=[]
    for nx in (41,81):
        d=out/str(nx);d.mkdir();source=BASE/'results/native_beam_loaded_fd459'/str(nx)/'scene.scn';tree=ET.parse(source);root=tree.getroot();node=root.find('./Node');root.find('RequiredPlugin').set('pluginName',str(binary))
        obs=node.find('NativeRigidTangentObserver');obs.set('filename',str(d/'native'))
        q=np.fromstring(obs.get('privatePositions'),sep=' ').reshape(-1,7);q0=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7)
        if np.max(abs(q0[:,3:6]))!=0 or np.max(abs(q0[:,6]-1))!=0:raise ValueError('identity rest orientation required')
        direction=np.zeros((nx,6));direction[:,:3]=q[:,:3]-q0[:,:3]
        v=q[:,3:6];norm=np.linalg.norm(v,axis=1);active=norm>0;direction[active,3:]=v[active]*(2*np.arctan2(norm[active],q[active,6])/norm[active])[:,None]
        scale=float(np.max(np.linalg.norm(direction[:,3:],axis=1)));direction/=scale
        fixed=np.fromstring(node.find('FixedProjectiveConstraint').get('indices'),sep=' ',dtype=int);direction[fixed]=0
        obs.set('privateDirection',flat(direction))
        if a.fd_steps:obs.set('fdSteps',' '.join(format(h,'.17g') for h in a.fd_steps))
        node.find('./Node/NativePointJournal').set('filename',str(d/'ACTUAL_UNLOADED.csv'));tree.write(d/'scene.scn')
        np.savez(d/'PRIVATE_DIRECTION_NOT_STATE.npz',direction=direction,original_scale=scale)
        process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','2','--hideProgressBar',d/'scene.scn'],d/'process',480)
        logs=''.join((d/'process'/name).read_text() for name in ('stdout.log','stderr.log'))
        if process['exit_code']!=0 or any(s in logs for s in ('[ERROR]','Unused Attribute','Line search failed','failed to converge')):raise RuntimeError('native query failure;Raw preserved')
        actual=list(csv.DictReader((d/'ACTUAL_UNLOADED.csv').open()));error=max(float(np.max(abs(np.fromstring(r['q'],sep=' ').reshape(-1,3)-q0[:,:3]))) for r in actual)
        ladder=[]
        for r in csv.DictReader((d/'native').open()):
            v={k:float(x) for k,x in r.items()};v['force_relative']=v['force_error_N']/v['force_derivative_norm_N'];v['torque_relative']=v['torque_error_Nm']/v['torque_derivative_norm_Nm'];ladder.append(v)
        records.append(dict(nx=nx,process=process,scene_sha256=sha(d/'scene.scn'),source_scene_sha256=sha(source),actual_position_error_m=error,actual_frames=len(actual),ladder=ladder,best_force_row=min(ladder,key=lambda r:r['force_relative']),status='PRIVATE_BENDING_DIRECTION_ONLY' if error==0 and len(actual)==2 else 'FAIL_STATE'))
    result=dict(scope='Native directional derivative along failed-frame deformation;NOT equilibrium/full Jacobian/mesh/time/B3/grasp certification',producer_sha256=sha(Path(__file__)),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),binary_sha256=sha(binary),compiled_source_sha256=sha(out/'Observer.cpp'),sdk='/home/ubuntu/SOFA/v26.06.00',direction='failed displacement plus left quaternion logarithm,normalized to maximum1rad;fixed roots zero;translation m,rotation rad',records=records)
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
