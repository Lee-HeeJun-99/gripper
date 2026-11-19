"""Read-only stock rectangular BeamAdapter tangent FD; no new force law.
Private perturbations use left quaternion exponential/world angular coordinates.
Actual zero-load state is checked against unobserved423; loaded states NOT used.
"""
import argparse,csv,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from native_bending_coupon import BASE,ROOT,flat,sha,guarded
from observer_identity import compiled_observer

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    binary,compiled_source=compiled_observer('428')
    deps=subprocess.check_output(['ldd',str(binary)],text=True)
    if any('libSofa' in s and '=>' in s and '/home/ubuntu/SOFA/v26.06.00/' not in s for s in deps.splitlines()):raise ValueError('SDK mismatch')
    (out/'ldd.txt').write_text(deps)
    (out/'CMakeCache.txt').write_bytes((BASE/'cad/build_rigid_observer428/CMakeCache.txt').read_bytes())
    (out/'Observer.cpp').write_bytes(compiled_source.read_bytes())
    (out/'CMakeLists.txt').write_bytes((BASE/'results/native_rigid_tangent429/CMakeLists.txt').read_bytes())
    records=[]
    for curved in (False,True):
        for amplitude in (None,0.,1e-7):
            label='control' if amplitude is None else f'{amplitude:g}'
            d=out/f'{"curved" if curved else "straight"}_{label}';d.mkdir()
            tree=ET.parse(BASE/'results/native_rectangular_rest423/21/scene.scn');root=tree.getroot();node=root.find('./Node')
            q=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7)
            if not curved:
                q[:,:3]=np.column_stack([np.linspace(0,.1,21),np.zeros(21),np.zeros(21)])
                q[:,3:]=[0,0,0,1];node.find('MechanicalObject').set('position',flat(q));node.find('BeamInterpolation').set('straight','1')
            if amplitude is not None:
                root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)))
                ET.SubElement(node,'NativeRigidTangentObserver',dict(body='@dofs',elastic='@elastic',filename=str(d/'tangent.csv'),amplitude=str(amplitude)))
            node.find('./Node/NativePointJournal').set('filename',str(d/'states.csv'))
            tree.write(d/'scene.scn')
            process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','2','--hideProgressBar',d/'scene.scn'],d/'process',480)
            logs=''.join((d/'process'/f).read_text() for f in ('stdout.log','stderr.log'))
            r=dict(curved=curved,private_amplitude=amplitude,process=process,scene_sha256=sha(d/'scene.scn'),status='FAIL_DIAGNOSTIC',state_error_m=None)
            if process['exit_code']==0 and not any(s in logs for s in ('[ERROR]','Line search failed','failed to converge')):
                rows=list(csv.DictReader((d/'states.csv').open()));error=max(float(np.max(abs(np.fromstring(row['q'],sep=' ').reshape(-1,3)-q[:,:3]))) for row in rows)
                fd=list(csv.DictReader((d/'tangent.csv').open())) if amplitude is not None else []
                r.update(state_error_m=error,status='READ_ONLY_DIAGNOSTIC' if len(rows)==2 and error<=1e-12 else 'FAIL_STATE_API',
                    force_tangent_relative=[float(x['force_error_N'])/float(x['force_derivative_norm_N']) if float(x['force_derivative_norm_N'])!=0 else None for x in fd],
                    torque_tangent_relative=[float(x['torque_error_Nm'])/float(x['torque_derivative_norm_Nm']) if float(x['torque_derivative_norm_Nm'])!=0 else None for x in fd],
                    raw_fd=fd,
                    fd_epsilon=[float(x['epsilon']) for x in fd],scope='dimensionless epsilon scales translations by .1m and rotations by1rad;force and torque separate;NOT loaded equilibrium')
            records.append(r)
    result=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_sha256=sha(Path(__file__)),
        binary_sha256=sha(binary),observer_source_sha256=sha(out/'Observer.cpp'),sdk='/home/ubuntu/SOFA/v26.06.00',records=records)
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
