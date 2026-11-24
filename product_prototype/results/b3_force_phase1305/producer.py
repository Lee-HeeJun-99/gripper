"""Early contact force sensitivity;not full holding from a partial run."""
import argparse,json,xml.etree.ElementTree as ET
from pathlib import Path
from analyse import BASE,sha
from b3_response_cone_reference import assess
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);names=['b3_railback_grasp1001298','b3_railback_force_contact1303'];canonical=[];records=[]
 for name in names:
  src=BASE/'results'/name;run=json.loads((src/'summary.json').read_text());assert run['status']=='VALID_BOUNDED_EXPLORATION_ONLY';root=ET.parse(src/'scene.scn').getroot()
  for n in root.iter():
   if n.tag=='NativeCableSequence':n.set('maximumForceN','1.5')
   for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),'OUTPUT'))
  canonical.append(ET.tostring(root));records.append(assess(name,.1,(1.1,)))
 assert canonical[0]==canonical[1],'unexpected physical Scene difference beyond cableforce/outputpaths'
 d=dict(status='EARLY_FORCE_SENSITIVITY_ONLY',records=records,scene_one_variable_check=True,hold_window_run=False,holding='NOT ASSESSED_PARTIAL_1.2S',physical_validation='NOT QUALIFIED',scope='Actual accepted1.1s response comparison,1.5→2N only. Not motor specification,structure efficiency improvement,fullHolding orconvergence.',scene_hashes={n:sha(BASE/'results'/n/'scene.scn') for n in names});(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
