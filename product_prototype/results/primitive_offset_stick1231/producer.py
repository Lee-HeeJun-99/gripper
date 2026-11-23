"""Laboratory planar-translation invariance contrast;all collision models retained."""
import argparse,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--source',required=True,choices=['primitive_sphere_slip1225','primitive_sphere_friction1226','primitive_sphere_slip1228']);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results'/a.source;tree=ET.parse(src/'scene.scn');root=tree.getroot();state=root.find("./Node[@name='layer']/MechanicalObject");q=state.get('position').split();q[0]='.005';state.set('position',' '.join(q))
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 tree.write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes());pre=json.loads((src/'preflight.json').read_text());cmd=pre['command'][:-1]+[str(out/'scene.scn')];pre.update(command=cmd,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(out/'scene.scn'),initial_x_m=.005,hypothesis='Flat interior contact is translation-invariant physically;initial center shifted away from internal triangulation diagonal. ALL collision models retained. Diagnostic only,not moving held object or repairing grasp. Boundary clearance assessed from actual trajectory.')
 (out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',60);logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));d=dict(status='TRANSLATION_CONTROL_STATES_ONLY' if proc['exit_code']==0 and '[ERROR]' not in logs else 'FAIL_EXECUTION',process=proc,physical_validation='NOT QUALIFIED');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
