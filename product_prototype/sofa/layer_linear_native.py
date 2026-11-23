"""Same settled coupon,only Native small-vs-large strain formulation contrast."""
import argparse,csv,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/layer_free1189';tree=ET.parse(src/'scene.scn');root=tree.getroot()
 for ff in root.iter('TetrahedronFEMForceField'):assert ff.get('method')=='large';ff.set('method','small')
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 tree.write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'mesh.json').write_bytes((src/'mesh.json').read_bytes());pre=json.loads((src/'preflight.json').read_text());cmd=pre['command'][:-1]+[str(out/'scene.scn')];plugins={n.get('pluginName'):sha(Path(n.get('pluginName'))) for n in root.iter('RequiredPlugin') if n.get('pluginName','').startswith('/')};assert list(plugins.values())==[pre['binary_sha256']];pre.update(command=cmd,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),scene_sha256=sha(out/'scene.scn'),source_scene_sha256=sha(src/'scene.scn'),plugin_hashes=plugins,estimated_runtime_s=6,child_limit_s=120,classification='SMALL_VS_LARGE_NATIVE_FORMULATION_DIAGNOSTIC_ONLY',hypothesis='Small coupon displacement closely matches linear reference but reference force residual differs17%;compare actual Native small formulation before assigning cause to nonlinear tangent/arithmetic. No tolerance,material,mesh,load,dt,BC or collision changes.')
 (out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',120);logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));counts=[len(list(csv.DictReader((out/f'layer{i}.csv').open()))) if (out/f'layer{i}.csv').exists() else 0 for i in (0,1)];d=dict(status='NATIVE_FORMULATION_STATES_ONLY' if proc['exit_code']==0 and '[ERROR]'not in logs and counts==[500]*2 else 'FAIL_EXECUTION',process=proc,outputs=counts,physical_validation='NOT QUALIFIED');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
