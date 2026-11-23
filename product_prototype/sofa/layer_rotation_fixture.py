"""Native laboratory orientation fixture;not unsupported holding or pose repair."""
import argparse,csv,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--mu',type=float,choices=[0,.3],required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results'/('layer_rigid_slip1195' if a.mu==0 else 'layer_rigid_friction1196');tree=ET.parse(src/'scene.scn');root=tree.getroot();node=root.find("./Node[@name='layer']");ET.SubElement(node,'PartialFixedProjectiveConstraint',template='Rigid3d',indices='0',fixedDirections='0 0 0 1 1 1')
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 tree.write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes());cmd=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','100','--hideProgressBar',str(out/'scene.scn')];pre=json.loads((src/'preflight.json').read_text());pre.update(command=cmd,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_scene_sha256=sha(src/'scene.scn'),rotation_fixture='Physical lab orientation constraint via Native PartialFixedProjectiveConstraint;XYZ translation free;NEW mechanism,not free grasp or postprocessed q/v');(out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',60);rows=list(csv.DictReader((out/'rigid.csv').open())) if (out/'rigid.csv').exists() else [];logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));d=dict(status='FIXTURE_STATES_ONLY' if proc['exit_code']==0 and '[ERROR]' not in logs and len(rows)==100 else 'FAIL_FIXTURE_EXECUTION',process=proc,outputs=len(rows),physical_validation='NOT QUALIFIED',holding='NOT A GRASP TEST');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
