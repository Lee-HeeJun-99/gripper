"""Native XYZ ideal interface on section-refined free coupon;not jamming."""
import argparse,csv,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--steps',type=int,choices=[50,500],default=50);p.add_argument('--pilot');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/layer_section_native1288';m=json.loads((src/'mesh.json').read_text());q=np.array(m['q0']);lo=np.flatnonzero((q[:,2]==.0002)&(q[:,0]>0));up=lo-2;assert np.all(q[up,2]==0);tree=ET.parse(src/'scene.scn');root=tree.getroot();root.insert(0,ET.Element('RequiredPlugin',pluginName='Sofa.Component.Constraint.Lagrangian.Model'));root.find('BlockGaussSeidelConstraintSolver').set('scaleTolerance','0');ET.SubElement(root,'BilateralLagrangianConstraint',template='Vec3d',object1='@layer0/dofs',object2='@layer1/dofs',first_point=' '.join(map(str,lo)),second_point=' '.join(map(str,up)),rest_vector=' '.join(['0 0 .000002']*len(lo)))
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 tree.write(out/'scene.scn');(out/'mesh.json').write_bytes((src/'mesh.json').read_bytes());(out/'producer.py').write_bytes(Path(__file__).read_bytes());pre=json.loads((src/'preflight.json').read_text());cmd=pre['command'].copy();cmd[cmd.index('-n')+1]=str(a.steps);cmd[-1]=str(out/'scene.scn');forecast=10.
 if a.steps>50:
  if not a.pilot:raise ValueError('matching pilot required')
  pr=json.loads((BASE/'results'/a.pilot/'summary.json').read_text());assert pr['status']=='PASS_IDEAL_TIE_EXECUTION_ONLY' and pr['outputs']==[50]*2;forecast=pr['process']['runtime_s']*10
  if forecast>120:raise ValueError('forecast over budget')
 plugins={n.get('pluginName'):sha(Path(n.get('pluginName'))) for n in root.iter('RequiredPlugin') if n.get('pluginName','').startswith('/')};assert list(plugins.values())==[pre['binary_sha256']]
 pre.update(command=cmd,steps=a.steps,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),scene_sha256=sha(out/'scene.scn'),source_scene_sha256=sha(src/'scene.scn'),estimated_runtime_s=forecast,plugin_hashes=plugins,scope='Ideal XYZ world-displacement tie plus previously validated stricter unscaled termination,numeric tolerance1e-10 unchanged. Free source has no constraint force;not actual vacuum/friction.',interface_lower=lo.tolist(),interface_upper=up.tolist());(out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',120);logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));counts=[len(list(csv.DictReader((out/f'layer{i}.csv').open()))) if (out/f'layer{i}.csv').exists() else 0 for i in (0,1)];d=dict(status='PASS_IDEAL_TIE_EXECUTION_ONLY' if proc['exit_code']==0 and '[ERROR]'not in logs and 'Unused Attribute'not in logs and counts==[a.steps]*2 else 'FAIL_EXECUTION',process=proc,outputs=counts,physical_validation='NOT QUALIFIED');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
