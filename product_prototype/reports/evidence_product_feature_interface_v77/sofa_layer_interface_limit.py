"""Ideal translation-tied interface contrast,not actual pressure/friction jamming.
Rest gap vector stays fixed in world coordinates: only small-rotation coupon
limit,not an objective finite-rotation adhesive constitutive law.
"""
import argparse,csv,json,shutil,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--steps',type=int,choices=[50,500],default=50);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/layer_free1189';tree=ET.parse(src/'scene.scn');root=tree.getroot();root.insert(0,ET.Element('RequiredPlugin',pluginName='Sofa.Component.Constraint.Lagrangian.Model'));m=json.loads((src/'mesh.json').read_text());q0=np.array(m['q0']);lower=np.flatnonzero((q0[:,2]==.0002)&(q0[:,0]>0));upper=lower-1
 ET.SubElement(root,'BilateralLagrangianConstraint',template='Vec3d',object1='@layer0/dofs',object2='@layer1/dofs',first_point=' '.join(map(str,lower)),second_point=' '.join(map(str,upper)),rest_vector=' '.join(['0 0 .000002']*len(lower)))
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 tree.write(out/'scene.scn');shutil.copy2(src/'mesh.json',out/'mesh.json');(out/'producer.py').write_bytes(Path(__file__).read_bytes());pre=json.loads((src/'preflight.json').read_text());cmd=pre['command'].copy();cmd[cmd.index('-n')+1]=str(a.steps);cmd[-1]=str(out/'scene.scn');pre.update(command=cmd,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(out/'scene.scn'),steps=a.steps,estimated_runtime_s=5 if a.steps==50 else 50,child_limit_s=120,interface_lower=lower.tolist(),interface_upper=upper.tolist(),interface_model='Native BilateralLagrangianConstraint,XYZ displacement tie,world-fixed rest gap2um,root pairs excluded redundantfixedDOFs;pressure remains0;Eunchanged;ALL collision models retained',classification='IDEAL_INTERFACE_SMALL_ROTATION_LIMIT_NOT_JAMMING_OR_ADHESIVE_CALIBRATION')
 (out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',120);logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));counts=[len(list(csv.DictReader((out/f'layer{i}.csv').open()))) if (out/f'layer{i}.csv').exists() else 0 for i in (0,1)];d=dict(status='INTERFACE_LIMIT_STATES_ONLY' if proc['exit_code']==0 and '[ERROR]' not in logs and counts==[a.steps]*2 else 'FAIL_EXECUTION',process=proc,outputs=counts,physical_validation='NOT QUALIFIED',layer_jamming='NOT IMPLEMENTED');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
