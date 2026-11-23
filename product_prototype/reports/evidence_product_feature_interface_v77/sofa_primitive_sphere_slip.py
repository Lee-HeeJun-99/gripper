"""Predetermined Coulomb-capacity crossing control,not parameter fitting."""
import argparse,csv,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/primitive_sphere_friction1226';tree=ET.parse(src/'scene.scn');root=tree.getroot();force=.15;fields=root.findall("./Node[@name='layer']/LinearForceField");assert len(fields)==2;fields[1].set('forces',' '.join(map(str,[0]*12+[force,0,0,0,0,0]*2)))
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 tree.write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes());pre=json.loads((src/'preflight.json').read_text());cmd=pre['command'][:-1]+[str(out/'scene.scn')];pre.update(command=cmd,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(out/'scene.scn'),tangential_force_N=force,hypothesis='0.15N exceeds assumed mu*N=0.12N;expect actual sliding and saturated impulse ratio;not jamming or grasp');(out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',60);logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));d=dict(status='SLIP_CONTROL_STATES_ONLY' if proc['exit_code']==0 and '[ERROR]' not in logs else 'FAIL_EXECUTION',process=proc,physical_validation='NOT QUALIFIED');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
