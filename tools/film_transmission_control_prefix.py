"""Different C2 release schedules must have identical shared initial prefix."""
import argparse,csv,json,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();cases=('20261118_transmission_hold_profile1186','20261118_transmission_pulse_regression1188');records=[];hashes={}
 for case in cases:
  src=ROOT/'results'/('autonomous_film_'+case);proof=json.loads((src/'summary.json').read_text())
  if proof['status']!='PASS':raise ValueError('both actual controls must pass strict API')
  for file,digest in proof['raw_hashes'].items():
   if sha(src/file)!=digest:raise ValueError('actual raw changed')
  records.append((proof,list(csv.DictReader((src/'actual.csv').open())),list(csv.DictReader((src/'actual.csv.stages.csv').open()))));hashes[case]=sha(src/'summary.json')
 if records[0][0]['binary_sha256']!=records[1][0]['binary_sha256']:raise ValueError('same actual binary required')
 x,y=records[0][1],records[1][1];errors={k:max(float(np.max(abs(np.fromstring(a[k],sep=' ')-np.fromstring(b[k],sep=' ')))) for a,b in zip(x,y)) for k in ('q','v')};clock=len(x)==len(y)==8 and all(a['time']==b['time'] for a,b in zip(x,y));stages=records[0][2]==records[1][2]
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');result=dict(status='PASS' if max(errors.values())<1e-12 and clock and stages else 'FAIL',scope='same binary original pulse/new hold shared1.6ms actual prefix;NOT full-cycle/control superiority certification',source_summaries=hashes,state_max_abs=errors,accumulated_clock_exact=clock,force_stage_rows_exact=stages,api_gate=1e-12);write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
