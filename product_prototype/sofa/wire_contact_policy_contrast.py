"""One-variable Native Min vs Local curved-beam contact contrast."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results/current_turn_wire1614/guide';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);root=ET.parse(src/'scene.scn').getroot();original=ET.tostring(root);root.find('LocalMinDistance').tag='MinProximityIntersection';test=ET.fromstring(ET.tostring(root));test.find('MinProximityIntersection').tag='LocalMinDistance';assert ET.tostring(test)==original
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 ET.ElementTree(root).write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'preflight.json').write_text(json.dumps(dict(source_sha256=sha(Path(__file__)),source_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(out/'scene.scn'),change='ONLYNativeintersectionLocal->Min;ALLmeshfeatures/Guide/wire/BC/material/dt/buffers/friction/tolerances unchanged',memory_GiB=4,child_limit_s=120,expected_runtime_s=90,estimate_basis='actualLocal8.9s;allow10x budgetforMinredundancy,notunlimitedretry'),indent=2));proc=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','1200','--hideProgressBar',str(out/'scene.scn')],out/'process',120);rows=list(csv.DictReader((out/'states.csv').open())) if (out/'states.csv').exists() else [];logs=''.join((out/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));d=dict(status='NATIVE_CONTACT_POLICY_CONTRAST_COMPLETED_ONLY' if proc['exit_code']==0 and '[ERROR]'not in logs and len(rows)==1200 else 'FAIL_NATIVE_CONTACT_POLICY_RUN',process=proc,outputs=len(rows),source_sha256=sha(Path(__file__)),physical_validation='NOT QUALIFIED',scope='Actualdynamiconevariabletest;completiondoesNOTprovephysicalgap/contact/beamquality. No alarm/dt/force/tolerancechange. ExistingLocalnegativegapFAILpreserved.');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
