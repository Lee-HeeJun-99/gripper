"""Short Native free-subset fixture test, NO object and NO Lift claim."""
import argparse,csv,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--end-clock',action='store_true');a=p.parse_args();src=BASE/'results/b3_alarm_window485';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 tree=ET.parse(src/'scene.scn');root=tree.getroot()
 for n in list(root):
  if (n.tag=='Node' and n.get('name') in ('object','floor')) or n.tag in ('NativeResponseRows','NativeDetectionPairs','NativeContactRows'):root.remove(n)
 for f in range(3):
  n=root.find(f"./Node[@name='free{f}']");fixed=n.find('FixedProjectiveConstraint');ids=fixed.get('indices');n.remove(fixed)
  ET.SubElement(n,'LinearMovementProjectiveConstraint',indices=ids,keyTimes='-.0025 .0075' if a.end_clock else '0 .01',movements='0 0 0 0 0 .0001')
 for n in root.iter():
  for k,v in list(n.attrib.items()):
   if str(src) in v:n.set(k,v.replace(str(src),str(out)))
 tree.write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes())
 proc=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','4','--hideProgressBar',out/'scene.scn'],out/'process',60)
 records=[]
 mesh=json.loads((src/'mesh.json').read_text());local=np.array(mesh['local_positions_mm']);cfg=json.loads((src/'config.json').read_text());indices=np.flatnonzero(local[:,0]<=cfg['finger']['clamp_length'])
 for f in range(3):
  path=out/f'finger{f}.csv'
  if not path.exists():continue
  initial=np.fromstring(root.find(f"./Node[@name='finger{f}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3)
  for r in csv.DictReader(path.open()):
   q=np.fromstring(r['q_m'],sep=' ').reshape(-1,3);t=float(r['time_s']);delta=q[indices]-initial[indices]
   expected=np.array([0,0,.0001*min(1,t/.01)])
   records.append(dict(finger=f,time_s=t,mean_root_translation_m=delta.mean(axis=0).tolist(),end_clock_error_m=float(np.max(abs(delta-expected)))))
 logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'))
 d=dict(status='NATIVE_ROOT_FIXTURE_PROBE_ONLY' if proc['exit_code']==0 and '[ERROR]' not in logs and len(records)==12 else 'FAIL_ROOT_FIXTURE_PROBE',process=proc,records=records,actual_pullpoint_API='NOT MEASURED',functional_lift='NOT RUN_NO_OBJECT',scope='Actual Native movement constraint replaces fixed Root on original free subsets; full-film/object states not prescribed. Cable controller still has liftHeight0, so this is NOT a complete moving-root/cable contract or loaded Lift.',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(f.relative_to(BASE)):sha(f) for f in [src/'scene.scn',out/'scene.scn',Path(__file__)]})
 d['clock_contract']='explicit accepted-end command,Native keyTimes shifted -dt' if a.end_clock else 'unshifted Native begin-clock command compared against end-clock'
 d['maximum_root_end_clock_error_m']=max((r['end_clock_error_m'] for r in records),default=None)
 d['root_position_API_1e12_pass']=bool(len(records)==12 and d['maximum_root_end_clock_error_m']<=1e-12)
 (out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
