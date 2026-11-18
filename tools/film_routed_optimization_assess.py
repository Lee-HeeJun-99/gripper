"""Exact physical output comparison + measured (not operation-count) cost."""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_compiled_sources import compiled_sources
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--baseline',required=True);p.add_argument('--candidate',required=True);a=p.parse_args();data=[]
 for case in (a.baseline,a.candidate):
  path=ROOT/'results'/('autonomous_film_'+case);m=json.loads((path/'summary.json').read_text())
  if m['status']!='PASS':raise ValueError('completed actual before/after required')
  for f,d in m['raw_hashes'].items():
   if sha(path/f)!=d:raise ValueError('immutable accepted output changed')
  data.append((path,m))
 x,y=[m for path,m in data]
 for k in ('amplitude_mm','steps','duration_s','physical_input','canonical_epochs','sdk_runner_sha256'):
  if x[k]!=y[k]:raise ValueError('same input/time/SDK required for optimization contrast')
 left,right=map(compiled_sources,(x['source_hashes'],y['source_hashes']));diff=sorted(k for k in set(left)|set(right) if left.get(k)!=right.get(k));allowed={'models/film_routed_tendon/Core.generated.h','models/film_routed_tendon/Route.h'}
 if set(diff)!=allowed:raise ValueError('optimization changed more than explicit generated core specialization: '+repr(diff))
 files=('actual.csv','actual.csv.stages.csv','actual.csv.clock.csv','film_0.csv','displacement_0.csv','public_mass.txt','plan.txt');identical={f:sha(data[0][0]/f)==sha(data[1][0]/f) for f in files};runtime={k:dict(baseline_s=x[k]['runtime_s'],candidate_s=y[k]['runtime_s'],change_percent=100*(y[k]['runtime_s']/x[k]['runtime_s']-1)) for k in ('reference_process','process')};faster=all(r['candidate_s']<r['baseline_s'] for r in runtime.values());exact=all(identical.values());out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');r=dict(status='PASS' if exact else 'FAIL',scope='exact numerical regression and observed wall time only;NOT statistical speed/full contact/grasp certification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_summaries={case:sha(path/'summary.json') for case,(path,m) in zip((a.baseline,a.candidate),data)},compiled_changes=diff,all_output_bytes_identical=identical,runtime=runtime,observed_both_children_faster=faster,adoption='CANDIDATE:repeat matched serial timing before robust speed claim' if exact and faster else 'NOT ADOPTED:cost benefit unproven or output changed',policy_runtime_limit_s=480);write_json(out/'summary.json',r);print(json.dumps(r))
if __name__=='__main__':main()
