"""Preserved exact numerical-plan reference against ALL actual38..44.4ms states."""
import argparse,csv,json,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();names=['20261118_three_film_after38_actual1174']+[f'20261118_three_film_after38_chain1178_plan{i}' for i in range(1,8)];rows=[];hashes={}
 for name in names:
  src=ROOT/'results'/('autonomous_film_'+name);meta=json.loads((src/'summary.json').read_text())
  if meta['status']!='EXPERIMENTAL' or meta['process']['exit_code'] or not meta['after38_owner']:raise ValueError('complete new-scope actual plans required')
  for file,digest in meta['raw_hashes'].items():
   if sha(src/file)!=digest:raise ValueError('actual raw changed')
  hashes[name]=sha(src/'summary.json');rows+=list(csv.DictReader((src/'three.states.csv').open()))
 old=ROOT/'results/autonomous_film_20261118_three_film_chain_reference1134';proof=json.loads((old/'summary.json').read_text());binary=old/'reference';checkpoint=ROOT/'results/autonomous_film_20261118_three_film_recovery_chain1127_plan7/three.checkpoint_280.txt';ledger=json.loads((ROOT/'reports/FILM_CONTACT_EVIDENCE_20261118_three_film_recovery_v12.json').read_text())
 for file in (binary,checkpoint,old/'summary.json'):
  if sha(file)!=ledger['files'][str(file.relative_to(ROOT))]:raise ValueError('preserved exact reference/IVP identity differs')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(binary,out/'reference');shutil.copy2(checkpoint,out/'input.checkpoint');run=guarded([out/'reference',out/'input.checkpoint','64',out/'reference','plans','.0064'],out/'process',480)
 result=dict(status='FAIL',scope='independent same-plan64step reference vs actual3finger38..44.4ms;NOT wrapping/full recovery/grasp',actual_summary_hashes=hashes,reference_binary_sha256=sha(binary),historical_compiled_source_commit=proof['source_commit'],reference_source_summary_sha256=sha(old/'summary.json'),actual_initial_checkpoint_sha256=sha(checkpoint),process=run,api_gate=1e-12)
 if run['exit_code']==0:
  expected=list(csv.DictReader((out/'reference.states.csv').open()));errors={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for x,y in zip(rows,expected)) for k in ('q','v')};clock=len(rows)==len(expected)==64 and all(x['time']==y['time'] for x,y in zip(rows,expected));result.update(status='PASS' if max(errors.values())<1e-12 and clock else 'FAIL',reference_max_abs=errors,accumulated_clock_exact=clock)
 result['raw_hashes']={f.name:sha(f) for f in out.glob('reference.*') if f.is_file()};write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('process','raw_hashes','actual_summary_hashes')}))
if __name__=='__main__':main()
