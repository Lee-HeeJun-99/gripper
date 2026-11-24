"""Native small-strain coupon with explicit uniform face traction."""
import argparse,csv,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
from layer_face_load import tip_load

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--steps',type=int,choices=[50,500],default=50);p.add_argument('--pilot');a=p.parse_args()
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/layer_linear_native1261';m=json.loads((src/'mesh.json').read_text());q=np.array(m['q0']);t=np.array(m['tetrahedra']);F,area,_=tip_load(q,t,[0,0,-5e-5]);tree=ET.parse(src/'scene.scn');root=tree.getroot()
 cc=root.find('GenericConstraintCorrection');cc.attrib.pop('solverName',None);cc.set('linearSolver','@globalLinear')
 for i in (0,1):
  field=root.find(f"./Node[@name='layer{i}']/ConstantForceField");field.set('indices',' '.join(map(str,range(len(q)))));field.set('forces',' '.join(format(v,'.17g') for v in F.ravel()))
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)).replace('layer_pairs.csv','detector.csv'))
 tree.write(out/'scene.scn');(out/'mesh.json').write_bytes((src/'mesh.json').read_bytes());(out/'producer.py').write_bytes(Path(__file__).read_bytes())
 pre=json.loads((src/'preflight.json').read_text());cmd=pre['command'].copy();cmd[cmd.index('-n')+1]=str(a.steps);cmd[-1]=str(out/'scene.scn')
 forecast=6.
 if a.steps==500:
  if not a.pilot:raise ValueError('pilot required')
  pilot=BASE/'results'/a.pilot;pr=json.loads((pilot/'summary.json').read_text());assert pr['status']=='PASS_NATIVE_TRACTION_EXECUTION_ONLY' and pr['outputs']==[50,50];forecast=pr['process']['runtime_s']*10
  if forecast>120:raise ValueError('forecast exceeds budget')
 plugins={n.get('pluginName'):sha(Path(n.get('pluginName'))) for n in root.iter('RequiredPlugin') if n.get('pluginName','').startswith('/')};assert list(plugins.values())==[pre['binary_sha256']]
 pre.update(command=cmd,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),scene_sha256=sha(out/'scene.scn'),source_scene_sha256=sha(src/'scene.scn'),plugin_hashes=plugins,steps=a.steps,estimated_runtime_s=forecast,load_area_m2=area,scope='New face-traction load distribution plus canonical correction link. Not an unchanged old-load mesh comparison. Same small FEM, material, mass, geometry, dt and collision.')
 (out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',120);logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));counts=[];quality=[];tips=[]
 for i in (0,1):
  rows=list(csv.DictReader((out/f'layer{i}.csv').open())) if (out/f'layer{i}.csv').exists() else [];counts.append(len(rows))
  if rows:
   states=np.array([np.fromstring(r['q'],sep=' ').reshape(-1,3) for r in rows]);initial=q+[0,0,i*.000202];tips.append(float((states[-1,q[:,0]==.04,2]-initial[q[:,0]==.04,2]).mean()));D=(states[:,t[:,1:]]-states[:,t[:,0,None]]).transpose(0,1,3,2);D0=(q[t[:,1:]]-q[t[:,0,None]]).transpose(0,2,1);quality.append(float((np.linalg.det(D)/np.linalg.det(D0)).min()))
 clean=proc['exit_code']==0 and '[ERROR]'not in logs and 'Unused Attribute'not in logs and counts==[a.steps]*2 and len(quality)==2 and min(quality)>0
 d=dict(status='PASS_NATIVE_TRACTION_EXECUTION_ONLY' if clean else 'FAIL_EXECUTION_OR_INVERSION',process=proc,outputs=counts,tip_displacement_m=tips,minimum_volume_ratio=quality,physical_validation='NOT QUALIFIED');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
