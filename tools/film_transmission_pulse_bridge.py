"""Full original-pulse regression after adding a separate longer-HOLD input."""
import argparse,csv,json,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'results/autonomous_film_20261118_transmission_gauss_cycle1169';old=json.loads((src/'summary.json').read_text());new=ROOT/'results/autonomous_film_20261118_transmission_hold_profile1186';proof=json.loads((new/'summary.json').read_text())
 if old['status']!='PASS' or proof['status']!='PASS' or sha(new/'reference')!=proof['reference_binary_sha256']:raise ValueError('qualified old actual and new exact kernel required')
 for file,digest in old['raw_hashes'].items():
  if sha(src/file)!=digest:raise ValueError('old actual raw changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(new/'reference',out/'reference');run=guarded([out/'reference','250','.05','.001','5',out/'pulse',src/'public_mass.txt','gauss'],out/'process',480)
 result=dict(status='FAIL',scope='new kernel ORIGINAL pulse vs preserved actual50ms;NOT longer-hold/grasp qualification',old_actual_summary_sha256=sha(src/'summary.json'),new_profile_summary_sha256=sha(new/'summary.json'),new_reference_binary_sha256=sha(out/'reference'),process=run,api_gate=1e-12)
 if run['exit_code']==0:
  x=list(csv.DictReader((src/'actual.csv').open()));y=list(csv.DictReader((out/'pulse.states.csv').open()));errors={k:max(float(np.max(abs(np.fromstring(a[k],sep=' ')-np.fromstring(b[k],sep=' ')))) for a,b in zip(x,y)) for k in ('q','v')};clock=len(x)==len(y)==250 and all(a['time']==b['time'] for a,b in zip(x,y));stages=list(csv.DictReader((src/'actual.csv.stages.csv').open()))==list(csv.DictReader((out/'pulse.stages.csv').open()));result.update(status='PASS' if max(errors.values())<1e-12 and clock and stages else 'FAIL',state_max_abs=errors,accumulated_clock_exact=clock,force_stage_rows_exact=stages)
 result['raw_hashes']={f.name:sha(f) for f in out.glob('pulse.*')};write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('process','raw_hashes')}))
if __name__=='__main__':main()
