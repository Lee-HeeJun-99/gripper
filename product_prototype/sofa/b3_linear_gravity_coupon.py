"""Actual stock Native linear FEM gravity coupon, no Guide/Cable/contact.
Separate validation model, not a replacement qualified gripper.
"""
import argparse,csv,json,shutil,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
from observer_identity import compiled_observer

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--no-observer',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_rail_back_zero1127';source=ET.parse(src/'scene.scn').getroot();body=source.find("./Node[@name='finger0']");q=np.fromstring(body.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);local=np.array(json.loads((src/'mesh.json').read_text())['local_positions_mm']);root=ET.Element('Node',name='root',dt='.0025',gravity='0 0 -9.81')
    for c in source.findall('RequiredPlugin'):
        name=c.get('pluginName')
        if name.startswith('/') and not name.endswith('libReGripProductSequence.so'):continue
        root.append(c)
    binary,compiled=compiled_observer('410');ET.SubElement(root,'RequiredPlugin',pluginName=str(binary));ET.SubElement(root,'DefaultAnimationLoop');root.append(source.find('EulerImplicitSolver'));root.append(source.find('SparseLDLSolver'));node=ET.SubElement(root,'Node',name='coupon')
    for tag in ('MeshTopology','MechanicalObject','UniformMass','TetrahedronFEMForceField'):node.append(body.find(tag))
    node.find('TetrahedronFEMForceField').set('method','small');ET.SubElement(node,'FixedProjectiveConstraint',indices=' '.join(map(str,np.flatnonzero(local[:,0]<=5))))
    ET.SubElement(node,'NativePointJournal',body='@dofs',filename=str(out/'states.csv'))
    if not a.no_observer:ET.SubElement(node,'NativeElasticMatrixObserver',body='@dofs',elastic='@nativeFEM',filename=str(out/'rest'))
    ET.ElementTree(root).write(out/'scene.scn');shutil.copy2(src/'mesh.json',out/'mesh.json');(out/'producer.py').write_bytes(Path(__file__).read_bytes())
    plugins={n.get('pluginName'):sha(Path(n.get('pluginName'))) for n in root.iter('RequiredPlugin') if n.get('pluginName','').startswith('/')};cmd=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','40','--hideProgressBar',str(out/'scene.scn')];pre=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_scene_sha256=sha(src/'scene.scn'),binary_hashes=plugins,observer_compiled_source_sha256=sha(compiled),SDK='/home/ubuntu/SOFA/v26.06.00',command=cmd,estimated_runtime_s=2,child_limit_s=60,memory_GiB=4,changed='No Guide mass/mapping/Cable/contact; direct nodal fixed root; Native small linear FEM. Separate reference coupon,not B3 joint repair.')
    (out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',60);logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));rows=list(csv.DictReader((out/'states.csv').open())) if (out/'states.csv').exists() else [];d=dict(status='COUPON_STATES_ONLY' if proc['exit_code']==0 and '[ERROR]' not in logs and len(rows)==40 else 'FAIL_EXECUTION',outputs=len(rows),process=proc,physical_validation='NOT QUALIFIED',input_hashes=plugins);(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))

if __name__=='__main__':main()
