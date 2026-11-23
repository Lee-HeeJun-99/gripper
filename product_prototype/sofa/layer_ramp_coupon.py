"""Single protocol change to isolate pressure-step contact tunneling hypothesis."""
import argparse,csv,json,shutil,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--mu',type=float,choices=[0,.3],default=.3);p.add_argument('--steps',type=int,choices=[50,500],default=50);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/layer_pressure_pilot1188';tree=ET.parse(src/'scene.scn');root=tree.getroot();m=json.loads((src/'mesh.json').read_text());q0=np.array(m['q0']);flat=lambda x:' '.join(format(float(v),'.17g') for v in np.array(x).ravel());root.find('CollisionResponse').set('responseParams','mu='+str(a.mu))
 for layer in (0,1):
  node=root.find(f"./Node[@name='layer{layer}']");tip=np.zeros_like(q0);tip[q0[:,0]==.04,2]=-1e-4/8;node.find('ConstantForceField').set('forces',flat(tip))
  for edge in (False,True):
   indices=[i for i,(x,y,z) in enumerate(q0) if z==(0 if layer==0 else .0002) and ((x in (0,.04))==edge)];target=(1 if layer==0 else -1)*1000*.005*.005*(.5 if edge else 1);ET.SubElement(node,'LinearForceField',template='Vec3d',points=' '.join(map(str,indices)),times='0 .01 .1',forces=flat([[0,0,0],[0,0,target],[0,0,target]]))
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 tree.write(out/'scene.scn');shutil.copy2(src/'mesh.json',out/'mesh.json');(out/'producer.py').write_bytes(Path(__file__).read_bytes());cmd=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(a.steps),'--hideProgressBar',str(out/'scene.scn')];pre=json.loads((src/'preflight.json').read_text());pre.update(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_scene_sha256=sha(src/'scene.scn'),command=cmd,steps=a.steps,friction=a.mu,pressure_protocol='Native begin-clock LinearForceField0→1000Pa over10ms,then hold. Explicit NEW physical input,not old step repair.',estimated_runtime_s=6 if a.steps==50 else 60);(out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',120);logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));counts=[len(list(csv.DictReader((out/f'layer{i}.csv').open()))) if (out/f'layer{i}.csv').exists() else 0 for i in (0,1)];d=dict(status='RAMP_LAYER_STATES_ONLY' if proc['exit_code']==0 and '[ERROR]' not in logs and counts==[a.steps]*2 else 'FAIL_RAMP_EXECUTION',process=proc,outputs=counts,physical_validation='NOT QUALIFIED',layer_jamming='NOT VALIDATED',energy_work=None);(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
