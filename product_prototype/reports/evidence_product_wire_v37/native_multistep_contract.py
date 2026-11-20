"""Last installed Native loop candidate preflight;no custom integration or dt sweep.

MultiStepAnimationLoop is a CollisionAnimationLoop,not assumed to process
Lagrange Cable. Test at1collision/1integration substep against692same graph.
"""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
from native_loop_intervention import reference

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[];sdk=Path('/home/ubuntu/SOFA/v26.06.00');header=sdk/'include/Sofa.Component.AnimationLoop/sofa/component/animationloop/MultiStepAnimationLoop.h'
 for channel in ('external_force','cable'):
  src=BASE/'results/b3_native_loop_intervention692'/('DefaultAnimationLoop_NewmarkImplicitSolver_'+channel);d=out/channel;d.mkdir();root=ET.parse(src/'scene.scn').getroot();loop=root.find('DefaultAnimationLoop');loop.tag='MultiStepAnimationLoop';loop.attrib.update(collisionSteps='1',integrationSteps='1')
  for node in root.iter():
   if node.get('filename'):node.set('filename',str(d/Path(node.get('filename')).name))
  ET.ElementTree(root).write(d/'scene.scn');proc=guarded([sdk/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','80','--hideProgressBar',d/'scene.scn'],d/'process',480);logs=''.join((d/'process'/n).read_text(errors='replace') for n in ('stdout.log','stderr.log'));r=dict(channel=channel,process=proc,sofa_errors=logs.count('[ERROR]'),scene_sha256=sha(d/'scene.scn'),status='FAIL_NATIVE_EXECUTION')
  if proc['exit_code']==0 and not r['sofa_errors']:
   with (d/'states.csv').open() as f:rows=list(csv.DictReader(f))
   actual=np.asarray([[np.fromstring(row['q'],sep=' ').reshape(-1,3)[0,2],np.fromstring(row['v'],sep=' ').reshape(-1,3)[0,2]] for row in rows]);expected=reference('NewmarkImplicitSolver',.00025,80)
   if len(actual)!=80:raise ValueError('partial Native integration output')
   error=np.max(abs(actual-expected),axis=0);r.update(actual_steps=len(rows),maximum_position_reference_error_m=float(error[0]),maximum_velocity_reference_error_m_s=float(error[1]),actual_positions_and_velocities_identically_zero=bool(np.max(abs(actual))==0),status='PASS_FREE_ODE_SCOPE_ONLY' if max(error)<=1e-12 else 'FAIL_CABLE_INTEGRATION_CONTRACT')
  records.append(r)
 result=dict(status='NATIVE_MULTISTEP_CONTRACT_DIAGNOSTIC_NOT_B3',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),producer_sha256=sha(Path(__file__)),SDK_dependency_hashes={str(p):sha(p) for p in (header,sdk/'lib/libSofa.Component.AnimationLoop.so')},actual_configuration=dict(collisionSteps=1,integrationSteps=1,dt_s=.00025,steps=80),records=records,scope='Native installed alternative loop classification only;not constraint/contact/time/FEM/Holding qualification.No dt decrease,new solver,SDKpatch or B3change.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'MultiStepAnimationLoop.h').write_bytes(header.read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
