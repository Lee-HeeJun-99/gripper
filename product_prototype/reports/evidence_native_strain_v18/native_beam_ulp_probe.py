"""PRIVATE +/-one-ULP force sensitivity,not a state correction or equilibrium."""
import argparse,csv,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from native_bending_coupon import BASE,ROOT,flat,sha,guarded
from observer_identity import compiled_observer

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    binary,compiled=compiled_observer('451');(out/'Observer.cpp').write_bytes(compiled.read_bytes());(out/'ldd.txt').write_text(subprocess.check_output(['ldd',str(binary)],text=True))
    (out/'CMakeLists.txt').write_bytes((BASE/'results/native_beam_accepted452/CMakeLists.txt').read_bytes());(out/'CMakeCache.txt').write_bytes((BASE/'cad/build_accepted_observer451/CMakeCache.txt').read_bytes())
    source=BASE/'results/native_beam_refined_diagnostic454';meta=json.loads((source/'summary.json').read_text());records=[]
    for item in meta['records']:
        nx=item['nx'];snapshot=np.load(source/str(nx)/'FAILED_STATE_AND_INITIAL_K_NOT_EQUILIBRIUM.npz');qfailed=snapshot['q_failed'];index=item['largest_axial_node'];free=snapshot['free'];baseline=None
        for variant in ('base','plus','minus'):
            d=out/f'{nx}_{variant}';d.mkdir();qprivate=qfailed.copy()
            if variant!='base':qprivate[index,0]=np.nextafter(qprivate[index,0],np.inf if variant=='plus' else -np.inf)
            tree=ET.parse(BASE/'results/native_rectangular_centered_refine449'/str(nx)/'scene.scn');root=tree.getroot();node=root.find('./Node');q0=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7)
            node.find('ConstantForceField').set('forces','0 0 0 0 0 0')
            root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)));ET.SubElement(node,'NativeRigidTangentObserver',dict(body='@dofs',elastic='@elastic',filename=str(d/'native'),privatePositions=flat(qprivate)))
            node.find('./Node/NativePointJournal').set('filename',str(d/'ZERO_LOAD_ACTUAL.csv'));tree.write(d/'scene.scn')
            process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','2','--hideProgressBar',d/'scene.scn'],d/'process',480)
            logs=''.join((d/'process'/f).read_text() for f in ('stdout.log','stderr.log'));r=dict(nx=nx,variant=variant,perturbed_node=index,private_delta_x_m=float(qprivate[index,0]-qfailed[index,0]),process=process,scene_sha256=sha(d/'scene.scn'),status='FAIL_QUERY')
            if process['exit_code']==0 and not any(s in logs for s in ('[ERROR]','Line search failed','failed to converge','Unused Attribute')):
                rows=list(csv.DictReader((d/'ZERO_LOAD_ACTUAL.csv').open()));state_error=max(float(np.max(abs(np.fromstring(row['q'],sep=' ').reshape(-1,3)-q0[:,:3]))) for row in rows)
                force=np.array([[float(row[k]) for k in ('fx_N','fy_N','fz_N','tx_Nm','ty_Nm','tz_Nm')] for row in csv.DictReader((d/'native.probe.csv').open())]);residual=force+snapshot['external_force']
                if variant=='base':baseline=force.copy()
                r.update(status='PRIVATE_ULP_QUERY_ONLY' if len(rows)==2 and state_error==0 else 'FAIL_STATE',actual_zero_load_position_error_m=state_error,
                    free_force_residual_N=float(np.linalg.norm(residual[free,:3])),free_axial_residual_N=float(np.linalg.norm(residual[free,0])),
                    native_force_change_N=float(np.linalg.norm((force-baseline)[free,:3])) if baseline is not None else None,
                    original_failed_force_difference_N=float(np.linalg.norm((force-snapshot['force'])[free,:3])) if variant=='base' else None,
                    scope='PRIVATE single-coordinate sensitivity,not a lower bound or permissible accepted-state adjustment')
            records.append(r)
    result=dict(scope='PRIVATE force ULP diagnostic only;NO mesh/equilibrium/PASS synthesis',producer_sha256=sha(Path(__file__)),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),binary_sha256=sha(binary),observer_source_sha256=sha(compiled),sdk='/home/ubuntu/SOFA/v26.06.00',records=records)
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
