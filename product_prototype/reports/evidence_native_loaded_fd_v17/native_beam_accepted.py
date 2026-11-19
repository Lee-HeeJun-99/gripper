"""Observe real native small-load accepted states,forces and root reactions.
No PRIVATE predictor injection; exact frozen448/450 scenes, extra observer only.
"""
import argparse,csv,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from native_bending_coupon import BASE,ROOT,sha,guarded
from observer_identity import compiled_observer

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);build=BASE/'cad/build_accepted_observer451';binary,compiled_source=compiled_observer('451')
    deps=subprocess.check_output(['ldd',str(binary)],text=True)
    if any('libSofa' in s and '=>' in s and '/home/ubuntu/SOFA/v26.06.00/' not in s for s in deps.splitlines()):raise ValueError('SDK mismatch')
    (out/'ldd.txt').write_text(deps)
    (out/'Observer.cpp').write_bytes(compiled_source.read_bytes())
    (out/'CMakeLists.txt').write_bytes((BASE/'results/native_beam_accepted452/CMakeLists.txt').read_bytes())
    (out/'CMakeCache.txt').write_bytes((build/'CMakeCache.txt').read_bytes());records=[]
    for name in ('native_rectangular_centered448','native_rectangular_centered_half450'):
        source=BASE/'results'/name;config=json.loads((source/'summary.json').read_text());force=config['force_N'];d=out/name;d.mkdir()
        tree=ET.parse(source/'21/scene.scn');root=tree.getroot();node=root.find('./Node');root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)))
        ET.SubElement(node,'NativeRigidAcceptedObserver',dict(body='@dofs',elastic='@elastic',filename=str(d/'accepted.csv')))
        node.find('./Node/NativePointJournal').set('filename',str(d/'states.csv'));tree.write(d/'scene.scn')
        process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','2','--hideProgressBar',d/'scene.scn'],d/'process',480)
        logs=''.join((d/'process'/f).read_text() for f in ('stdout.log','stderr.log'))
        r=dict(case=name,force_N=force,process=process,scene_sha256=sha(d/'scene.scn'),status='FAIL_NATIVE')
        if process['exit_code']==0 and not any(s in logs for s in ('[ERROR]','Line search failed','failed to converge','Unused Attribute')):
            actual=list(csv.DictReader((d/'states.csv').open()));control=list(csv.DictReader((source/'21/states.csv').open()));rows=list(csv.DictReader((d/'accepted.csv').open()))
            error={key:max(float(np.max(abs(np.fromstring(x[key],sep=' ')-np.fromstring(y[key],sep=' ')))) for x,y in zip(actual,control)) for key in ('q','v')}
            frames=[]
            for step in (1,2):
                rr=[row for row in rows if int(row['step'])==step]
                if len(rr)!=21:raise ValueError('missing actual native nodes')
                q=np.array([[float(row[k]) for k in ('x_m','y_m','z_m')] for row in rr]);quat=np.array([[float(row[k]) for k in ('qx','qy','qz','qw')] for row in rr])
                internal=np.array([[float(row[k]) for k in ('fx_N','fy_N','fz_N','tx_Nm','ty_Nm','tz_Nm')] for row in rr]);external=np.zeros_like(internal);external[-1,2]=-force
                residual=internal+external;reaction=-internal[:2]
                frames.append(dict(step=step,time_s=float(rr[0]['time_s']),free_force_residual_N=float(np.linalg.norm(residual[2:,:3])),free_torque_residual_Nm=float(np.linalg.norm(residual[2:,3:])),
                    root_resultant_force_N=reaction[:,:3].sum(axis=0).tolist(),
                    global_force_balance_N=(reaction[:,:3].sum(axis=0)+external[:,:3].sum(axis=0)).tolist(),
                    global_moment_balance_Nm=(np.cross(q[:2],reaction[:,:3]).sum(axis=0)+reaction[:,3:].sum(axis=0)+np.cross(q,external[:,:3]).sum(axis=0)).tolist(),
                    quaternion_norm_error=float(np.max(abs(np.linalg.norm(quat,axis=1)-1))),actual_tip_displacement_m=float(-q[-1,2])))
            qualified=len(actual)==len(control)==2 and all(v<=1e-12 for v in error.values()) and all(f['free_force_residual_N']<=1e-12 and f['free_torque_residual_Nm']<=1e-12 and f['quaternion_norm_error']<=1e-12 for f in frames)
            r.update(status='PASS_SMALL_LOAD_STATE_AND_FORCE_ONLY' if qualified else 'FAIL_FORCE_OR_API',state_errors=error,frames=frames,
                times_identical=[row['time_s'] for row in actual]==[row['time_s'] for row in control])
        records.append(r)
    result=dict(scope='Actual native21-node centered rectangular STATIC Rail only;NOT mesh/time/Skin/attachment/B3/grasp certification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),producer_sha256=sha(Path(__file__)),binary_sha256=sha(binary),observer_source_sha256=sha(out/'Observer.cpp'),sdk='/home/ubuntu/SOFA/v26.06.00',records=records)
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
