"""Actual Native C2 input and exact Scene single-variable contrast."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
from analyse import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);before=BASE/'results/untapered_single1504';after=BASE/'results/sequenced_single1510';trees=[];endings=[]
 for folder in (before,after):
  root=ET.parse(folder/'scene.scn').getroot();controllers=list(root.iter('NativeCableSequence'));endings.append([float(n.get('closing','.5')) for n in controllers])
  for n in controllers:n.attrib.pop('closing',None)
  for node in root.iter():
   for k,v in list(node.attrib.items()):node.set(k,v.replace(str(folder),'__OUTPUT__'))
  trees.append(ET.tostring(root))
 exact=trees[0]==trees[1];assert exact,'Unexpected physical Scene difference beyonddeclaredclosingtime'
 maximum=0.;actual_command=0.;rows=list(csv.DictReader((after/'finger0.csv').open()))
 for r in rows:
  t=float(r['time_s']);u=min(1.,max(0.,t));want=1.5*u**3*(10+u*(-15+6*u));maximum=max(maximum,abs(float(r['command_N'])-want));actual_command=max(actual_command,*[abs(float(r[f'cable{j}_force_raw'])-float(r['command_Ns'])) for j in range(2)])
 d=dict(status='PASS_NATIVE_INPUT_TIMING_CONTRACT_ONLY' if exact and maximum<=1e-12 and actual_command<=1e-12 and len(rows)==100 else 'FAIL_INPUT_CONTRACT',normalised_scene_exact_except_closing=exact,old_new_closing_s=endings,maximum_analytic_C2_command_error_N=maximum,maximum_actual_Native_impulse_command_error_Ns=actual_command,samples=len(rows),scope='ONLYinputtimingchanged,.5to1s derivedfromactualSupportwithdrawalstart;noPhysics/SDK/objectqv/tolerancechange. Not observerpurity,newgrasp or numericalPASS.',source_sha256=sha(Path(__file__)),input_hashes={str(f.relative_to(BASE)):sha(f) for f in (before/'scene.scn',after/'scene.scn',after/'finger0.csv')});(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
