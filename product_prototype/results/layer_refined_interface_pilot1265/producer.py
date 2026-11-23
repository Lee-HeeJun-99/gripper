"""New ideal-interface Native contrast based on independent mesh-dependent prediction."""
import argparse,csv,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--steps',type=int,choices=[10,50,500],default=10);p.add_argument('--pilot');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/layer_mesh_native1260';tree=ET.parse(src/'scene.scn');root=tree.getroot();root.insert(0,ET.Element('RequiredPlugin',pluginName='Sofa.Component.Constraint.Lagrangian.Model'));m=json.loads((src/'mesh.json').read_text());q0=np.array(m['q0']);lower=np.flatnonzero((q0[:,2]==.0002)&(q0[:,0]>0));upper=lower-1;ET.SubElement(root,'BilateralLagrangianConstraint',template='Vec3d',object1='@layer0/dofs',object2='@layer1/dofs',first_point=' '.join(map(str,lower)),second_point=' '.join(map(str,upper)),rest_vector=' '.join(['0 0 .000002']*len(lower)))
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 root.find('NativeDetectionPairs').set('filename',str(out/'detector.csv'))
 tree.write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'mesh.json').write_bytes((src/'mesh.json').read_bytes());pre=json.loads((src/'preflight.json').read_text());cmd=pre['command'].copy();cmd[cmd.index('-n')+1]=str(a.steps);cmd[-1]=str(out/'scene.scn');pre.update(command=cmd,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(out/'scene.scn'),steps=a.steps,estimated_runtime_s=3,classification='REFINED_IDEAL_INTERFACE_NOT_JAMMING',hypothesis='Independent reference predicts nx33 free/tiedratio1.09873 vs nx9 1.00694:check actual Native interface sensitivity without material/dt/force changes. Restvector tied as old1239,all collisions retained. Detector journal is untracked evidence,not physics change.',interface_lower=lower.tolist(),interface_upper=upper.tolist())
 if a.steps>10:
  if not a.pilot:raise ValueError('measured pilot required')
  pilot=BASE/'results'/a.pilot;pm=json.loads((pilot/'preflight.json').read_text());pr=json.loads((pilot/'summary.json').read_text());forecast=pr['process']['runtime_s']*a.steps/pm['steps'];pre.update(estimated_runtime_s=forecast,pilot_summary_sha256=sha(pilot/'summary.json'))
  if forecast>120:
   (out/'preflight.json').write_text(json.dumps(pre,indent=2));d=dict(status='BLOCKED_COST_FORECAST_NOT_PHYSICS_FAIL',predicted_runtime_s=forecast,physical_validation='NOT QUALIFIED');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d));return
 (out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',120);logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));counts=[len(list(csv.DictReader((out/f'layer{i}.csv').open()))) if (out/f'layer{i}.csv').exists() else 0 for i in (0,1)];d=dict(status='NATIVE_IDEAL_INTERFACE_STATES_ONLY' if proc['exit_code']==0 and '[ERROR]'not in logs and counts==[a.steps]*2 else 'FAIL_EXECUTION',process=proc,outputs=counts,physical_validation='NOT QUALIFIED');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
