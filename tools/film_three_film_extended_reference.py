"""Exact same-IVP independent800us check of the separately admitted actual Owner."""
import argparse,csv,json,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--actual',required=True);a=p.parse_args()
 src=ROOT/'results'/('autonomous_film_'+a.actual);actual=json.loads((src/'summary.json').read_text())
 if actual['status']!='EXPERIMENTAL' or not actual.get('extended_build') or actual['process']['exit_code'] or actual['steps']!=8:raise ValueError('complete first extended actual plan required')
 for name,digest in actual['raw_hashes'].items():
  if sha(src/name)!=digest:raise ValueError('actual raw changed')
 old=ROOT/'results/autonomous_film_20261118_three_film_v5_long_base1118';proof=json.loads((old/'summary.json').read_text());binary=old/'reference'
 if proof['status']!='PASS' or sha(binary)!=proof['binary_sha256']:raise ValueError('preserved reference binary required')
 if sha(src/'input.checkpoint')==actual['original_checkpoint_sha256']:raise ValueError('expected explicit new identity token')
 original=(ROOT/'results'/('autonomous_film_'+actual['parent'])/'three.checkpoint_216.txt').read_text().split();tokens=(src/'input.checkpoint').read_text().split()
 if any(x!=y for i,(x,y) in enumerate(zip(original,tokens)) if i!=4) or len(original)!=len(tokens):raise ValueError('non-identity physical payload changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(src/'input.checkpoint',out/'input.checkpoint');shutil.copy2(binary,out/'reference')
 run=guarded([out/'reference',out/'input.checkpoint','8',out/'recovery','common','.0008'],out/'process',480)
 result=dict(status='FAIL',scope='same-IVP exact-state independent800us vs actual extended SOFA;NOT full recovery/grasp',actual=a.actual,actual_summary_sha256=sha(src/'summary.json'),reference_binary_sha256=sha(binary),reference_source_summary_sha256=sha(old/'summary.json'),process=run,api_gate=1e-12)
 if run['exit_code']==0:
  expected=list(csv.DictReader((out/'recovery.states.csv').open()));rows=list(csv.DictReader((src/'three.states.csv').open()))
  if len(rows)!=8 or len(expected)!=8:raise ValueError('complete rows required')
  errors={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for x,y in zip(rows,expected)) for k in ('q','v')};clock=all(x['time']==y['time'] for x,y in zip(rows,expected));result.update(status='PASS' if max(errors.values())<1e-12 and clock else 'FAIL',reference_max_abs=errors,accumulated_clock_exact=clock)
 result['raw_hashes']={f.name:sha(f) for f in out.glob('recovery.*')};write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('process','raw_hashes')}))
if __name__=='__main__':main()
