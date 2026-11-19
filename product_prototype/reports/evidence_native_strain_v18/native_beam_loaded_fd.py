"""Root-consistent PRIVATE loaded native tangent ladder;never commits query poses."""
import argparse,csv,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from native_bending_coupon import BASE,ROOT,sha,guarded
from observer_identity import compiled_observer

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--legacy-regression',action='store_true');a=p.parse_args()
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    binary,compiled=compiled_observer('458')
    for name in ('Observer.cpp','CMakeLists.txt'):(out/name).write_bytes((compiled.parent/name).read_bytes())
    (out/'CMakeCache.txt').write_bytes((binary.parent/'CMakeCache.txt').read_bytes())
    (out/'ldd.txt').write_text(subprocess.check_output(['ldd',str(binary)],text=True))
    records=[]
    for nx in (41,81):
        d=out/str(nx);d.mkdir();source=BASE/'results/native_beam_ulp_probe455'/f'{nx}_base/scene.scn'
        tree=ET.parse(source);root=tree.getroot();node=root.find('./Node')
        plugin=root.find('RequiredPlugin');plugin.set('pluginName',str(binary))
        obs=node.find('NativeRigidTangentObserver');obs.set('filename',str(d/'native'))
        fixed=np.fromstring(node.find('FixedProjectiveConstraint').get('indices'),sep=' ',dtype=int)
        if not np.array_equal(fixed,np.arange(len(fixed))):raise ValueError('contiguous root required')
        if not a.legacy_regression:
            obs.set('directionStart',str(len(fixed)));obs.set('fdSteps','1e-5 3e-6 1e-6 3e-7 1e-7 3e-8 1e-8 3e-9 1e-9')
        node.find('./Node/NativePointJournal').set('filename',str(d/'ACTUAL_UNLOADED.csv'))
        tree.write(d/'scene.scn')
        process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','2','--hideProgressBar',d/'scene.scn'],d/'process',480)
        logs=''.join((d/'process'/name).read_text() for name in ('stdout.log','stderr.log'))
        if process['exit_code']!=0 or any(s in logs for s in ('[ERROR]','Unused Attribute','Line search failed','failed to converge')):raise RuntimeError('native query failed;Raw retained')
        q0=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7)[:,:3]
        actual=list(csv.DictReader((d/'ACTUAL_UNLOADED.csv').open()))
        error=max(float(np.max(abs(np.fromstring(r['q'],sep=' ').reshape(-1,3)-q0))) for r in actual)
        ladder=[]
        for r in csv.DictReader((d/'native').open()):
            v={k:float(x) for k,x in r.items()};v['force_relative']=v['force_error_N']/v['force_derivative_norm_N'];v['torque_relative']=v['torque_error_Nm']/v['torque_derivative_norm_Nm'];ladder.append(v)
        best=min(ladder,key=lambda r:r['force_relative'])
        regression=(d/'native').read_bytes()==(source.parent/'native').read_bytes() if a.legacy_regression else None
        records.append(dict(nx=nx,root_nodes=fixed.tolist(),legacy_default_FD_bytes_identical=regression,process=process,source_scene_sha256=sha(source),scene_sha256=sha(d/'scene.scn'),actual_position_error_m=error,actual_frames=len(actual),ladder=ladder,best_force_row=best,
            status='PRIVATE_DIRECTIONAL_DIAGNOSTIC_ONLY' if error==0 and len(actual)==2 else 'FAIL_STATE',
            warning='Best FD step is diagnostic selection,not a physical solver tolerance or full Jacobian certificate'))
    result=dict(scope='Loaded PRIVATE directional derivative,not equilibrium,mesh/time or grasp PASS',legacy_regression=a.legacy_regression,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),producer_sha256=sha(Path(__file__)),binary_sha256=sha(binary),compiled_source_sha256=sha(out/'Observer.cpp'),sdk='/home/ubuntu/SOFA/v26.06.00',direction='translation .1m*sin(index),left rotation 1rad*sin(index);legacy mode excludes only first2 nodes,otherwise all fixed roots excluded',records=records)
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
