"""Alternating same-state actual SOFA A/B replay,not a synthetic AD speedup claim."""
import argparse,csv,json,statistics,subprocess,sys
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False)
 parents=['20261118_three_film_extended_actual1124','20261118_three_film_value_actual1131'];sources=[ROOT/'results'/('autonomous_film_'+n) for n in parents]
 for src in sources:
  proof=json.loads((src/'summary.json').read_text())
  if proof['status']!='EXPERIMENTAL' or proof['process']['exit_code'] or proof['sofa_errors']:raise ValueError('complete actualA/B trajectories required')
  for name,digest in proof['raw_hashes'].items():
   if sha(src/name)!=digest:raise ValueError('actualA/B raw changed')
 parity={name:(sources[0]/name).read_bytes()==(sources[1]/name).read_bytes() for name in ['three.states.csv','three.free.stages.csv']+[f'film_{i}.csv' for i in range(3)]}
 result=dict(status='FAIL',scope='actual100us four-step FREE recovery A/B replay;NOT general contact/full-cycle speedup',parent_hashes={n:sha(s/'summary.json') for n,s in zip(parents,sources)},full_eight_step_parity=parity,runs=[])
 if not all(parity.values()):write_json(out/'summary.json',result);raise ValueError('actual numerical parity failed')
 times=[[],[]]
 for repeat in range(3):
  for version in ([0,1] if repeat%2==0 else [1,0]):
   tag=a.tag+f'_r{repeat}_v{version}';command=[sys.executable,ROOT/'tools/film_three_film_v5_resume.py','--tag',tag,'--parent',parents[version],'--step','220','--steps','4','--compare']
   with (out/f'r{repeat}_v{version}.log').open('w') as log:process=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=510)
   path=ROOT/'results'/('autonomous_film_'+tag)/'summary.json'
   if process.returncode or not path.exists():write_json(out/'summary.json',result);raise RuntimeError('actualA/B process failed;log preserved')
   proof=json.loads(path.read_text());result['runs'].append(dict(tag=tag,summary_sha256=sha(path),status=proof['status'],runtime_s=proof['process']['runtime_s']));write_json(out/'summary.json',result)
   if proof['status']!='PASS':raise ValueError('strict API/stages/checkpoint replay failed')
   times[version].append(proof['process']['runtime_s'])
 med=[statistics.median(t) for t in times];result.update(status='PASS' if med[1]<med[0] else 'REJECTED',median_runtime_s=dict(AD=med[0],value=med[1]),speedup=med[0]/med[1],runtime_reduction_percent=100*(1-med[1]/med[0]),scope_only='FREE recovery with unchanged AD2 mechanical force/Hessian;contact-impact profile NOT RUN');write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
