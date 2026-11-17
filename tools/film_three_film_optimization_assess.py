"""Recorded before/after physical equality, not a new time-convergence claim."""
import argparse,json,shutil
from curve_common import ROOT,sha,write_json
from film_three_film_profile_assess import normalized
from film_three_film_qualified import require_completed
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--before',required=True);p.add_argument('--after',required=True);p.add_argument('--before-qualification');a=p.parse_args()
 paths=[ROOT/'results'/('autonomous_film_'+x) for x in (a.before,a.after)]
 summaries=[json.loads((x/'summary.json').read_text()) for x in paths]
 identities=[json.loads((x/'identity.json').read_text()) for x in paths]
 approval=require_completed(paths[0],a.before_qualification);require_completed(paths[1],None)
 if normalized(paths[0]/'scene.scn')!=normalized(paths[1]/'scene.scn'):
  # Absolute plugin paths necessarily differ for independently built binaries.
  import xml.etree.ElementTree as ET
  def physical(path):
   root=ET.fromstring(normalized(path/'scene.scn'))
   for node in root.iter('RequiredPlugin'):
    if 'libReGripThreeFilmContact.so' in node.get('pluginName',''):node.set('pluginName','THREE_FILM_BINARY')
   return ET.tostring(root)
  if physical(paths[0])!=physical(paths[1]):raise ValueError('completed identical physical XML required')
 names=['three.states.csv','three.rows.csv','three.policy.csv']+['film_'+str(f)+'.csv' for f in range(3)]+['displacement_'+str(f)+'.csv' for f in range(3)]
 files={name:[sha(path/name) for path in paths] for name in names};equal=all(x[0]==x[1] for x in files.values())
 times=[s['process']['runtime_s'] for s in summaries]
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py')
 result=dict(status='PASS' if equal else 'FAIL',scope='before/after exact nine physical CSVs;one runtime pair,NOT statistical speed or full regression',cases=[a.before,a.after],binary_hashes=[x['binary_sha256'] for x in identities],files=files,runtime_s=times,speedup=times[0]/times[1],runtime_improved=times[1]<times[0],source_identity=[sha(path/'identity.json') for path in paths])
 result['before_explicit_reassessment']=approval
 write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
