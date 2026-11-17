"""Same-DLL passive instrumentation audit;inclusive timings are NOT additive."""
import argparse,csv,json,shutil,xml.etree.ElementTree as ET
from curve_common import ROOT,sha,write_json
def normalized(path):
 root=ET.parse(path).getroot()
 for node in root.iter():
  for key in ('filename','displacementFilename','costProfileFilename','ownerCostFilename','publicMassFilename','reuseJournalRows'):node.attrib.pop(key,None)
 return ET.tostring(root)
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--before',required=True);p.add_argument('--after',required=True);p.add_argument('--mode',choices=('field','owner','mass'),required=True);a=p.parse_args();before=ROOT/'results'/('autonomous_film_'+a.before);after=ROOT/'results'/('autonomous_film_'+a.after);bm=json.loads((before/'identity.json').read_text());am=json.loads((after/'identity.json').read_text());bs=json.loads((before/'summary.json').read_text());ass=json.loads((after/'summary.json').read_text())
 if bs['status']!='PASS' or ass['status']!='PASS' or bm['binary_sha256']!=am['binary_sha256'] or normalized(before/'scene.scn')!=normalized(after/'scene.scn'):raise ValueError('completed same-DLL physical input must match exactly except passive output paths')
 flag='mass_journal' if a.mode=='mass' else a.mode+'_profile'
 if bm.get(flag,False) or not am.get(flag,False):raise ValueError('explicit before-off/after-on instrumentation required')
 names=['three.states.csv','three.rows.csv','three.policy.csv']+['film_'+str(f)+'.csv' for f in range(3)]+['displacement_'+str(f)+'.csv' for f in range(3)];files={f:dict(before=sha(before/f),after=sha(after/f)) for f in names};profiles={}
 for name in ([] if a.mode=='mass' else ['field_cost_'+str(f)+'.csv' for f in range(3)] if a.mode=='field' else ['owner_cost.csv']):
  metrics={}
  for row in csv.DictReader((after/name).open()):metrics[row['metric']]=dict(count=row['count'],inclusive_seconds=row['inclusive_seconds'])
  profiles[name]=dict(metrics=metrics,sha256=sha(after/name))
 if a.mode=='mass':profiles['public_mass.txt']=dict(sha256=sha(after/'public_mass.txt'),kind='actual read-only public getElementMass journal')
 result=dict(status='PASS' if all(v['before']==v['after'] for v in files.values()) else 'FAIL',scope='same binary,nine physical CSVs exact under passive instrumentation;NOT optimization or physics certification',mode=a.mode,before=a.before,after=a.after,files=files,profiles=profiles,before_runtime_s=bs['process']['runtime_s'],after_runtime_s=ass['process']['runtime_s'],timing_note='nested inclusive times MUST NOT be summed;Field values exclude custom-owner mirror-kernel,solves,mapping,IO and startup;one pair is NOT a statistical benchmark',not_measured=['process-wide heap allocation events','unattributed owner costs in field-only mode','general cache/physics performance outside this coupon'])
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');write_json(out/'summary.json',result);print(json.dumps(dict(status=result['status'],checked=len(files),before_runtime_s=result['before_runtime_s'],after_runtime_s=result['after_runtime_s'],profiles=profiles)))
if __name__=='__main__':main()
