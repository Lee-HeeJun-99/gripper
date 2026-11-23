"""Actual no-object,zero-tendon Native gravity reference;not measured hardware."""
import argparse,csv,json,shutil,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results/b3_alarm_window485';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);tree=ET.parse(src/'scene.scn');root=tree.getroot()
 for n in list(root):
  if (n.tag=='Node' and n.get('name') in ('object','floor')) or n.tag in ('NativeResponseRows','NativeDetectionPairs','NativeContactRows'):root.remove(n)
 for n in root.iter():
  for k,v in list(n.attrib.items()):
   if str(src) in v:n.set(k,v.replace(str(src),str(out)))
 for n in root.iter('NativeCableSequence'):n.set('maximumForceN','0')
 for name in ('config.json','mesh.json'):shutil.copy2(src/name,out/name)
 tree.write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes())
 pre=dict(scope='Independent zero-tendon,no-object Native gravity reference with original fixed Root. Same full Film/Rail/Guide mass/materials,not an empty scene. Candidate equilibrium and Recovery comparison only;time/mesh/material gates remain open.',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),SDK='/home/ubuntu/SOFA/v26.06.00',binary_hashes={n.get('pluginName'):sha(Path(n.get('pluginName'))) for n in root.iter('RequiredPlugin') if n.get('pluginName','').startswith('/')},steps=100,dt_s=.0025,estimate_s=101.108/8,child_limit_s=120,memory_GiB=4,reference_stability_max_node_speed_mm_s=.001,comparison_relative_displacement_limit=.001,note='Relative displacement compared without floor;Native numerical reference,NOT true hardware stress-free shape or material certification.')
 (out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','100','--hideProgressBar',out/'scene.scn'],out/'process',120);logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));counts=[len(list(csv.DictReader((out/f'finger{f}.csv').open()))) if (out/f'finger{f}.csv').exists() else 0 for f in range(3)]
 d=dict(status='NATIVE_GRAVITY_REFERENCE_RUN_NOT_EQUILIBRIUM_CERTIFIED' if proc['exit_code']==0 and '[ERROR]' not in logs and counts==[100]*3 else 'FAIL_GRAVITY_REFERENCE_EXECUTION',process=proc,counts=counts,preflight_sha256=sha(out/'preflight.json'),scene_sha256=sha(out/'scene.scn'),physical_validation='NOT QUALIFIED')
 (out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
