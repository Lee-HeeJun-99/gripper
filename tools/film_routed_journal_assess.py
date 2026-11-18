"""Same-binary passive cache/profile comparison;no change to physics gates."""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--baseline',required=True);p.add_argument('--candidate',required=True);a=p.parse_args();data=[]
 for case in (a.baseline,a.candidate):
  src=ROOT/'results'/('autonomous_film_'+case);m=json.loads((src/'summary.json').read_text())
  if m['status']!='PASS':raise ValueError('strict actual route replay required')
  for f,d in m['raw_hashes'].items():
   if sha(src/f)!=d:raise ValueError('physical replay changed')
  data.append((src,m))
 x,y=[m for src,m in data]
 for key in ('identity','binary_sha256','sdk_runner_sha256','input_checkpoint_sha256','start_time_s','dt_s','actual_steps'):
  if x[key]!=y[key]:raise ValueError('SAME compiled physics/input/clock required')
 names=['three.states.csv','three.rows.csv','three.policy.csv']+[f'{prefix}_{i}.csv' for prefix in ('film','displacement') for i in range(3)];names+=sorted(p.name for p in data[0][0].glob('three.checkpoint_*.txt'));same={name:sha(data[0][0]/name)==sha(data[1][0]/name) for name in names};profiles={}
 for case,(src,m) in zip((a.baseline,a.candidate),data):
  if not (src/'owner_cost.csv').exists():continue
  rows=list(csv.DictReader((src/'owner_cost.csv').open()));time=max(float(r['time']) for r in rows);profiles[case]={r['metric']:dict(count=int(r['count']),inclusive_seconds=float(r['inclusive_seconds'])) for r in rows if float(r['time'])==time}
 same_profile=x.get('owner_profile',False)==y.get('owner_profile',False);runtime=dict(baseline_s=x['process']['runtime_s'],candidate_s=y['process']['runtime_s'],change_percent=100*(y['process']['runtime_s']/x['process']['runtime_s']-1));out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');r=dict(status='PASS' if all(same.values()) else 'FAIL',scope='same-binary exact physical passivity/regression;timing is observed local branch only,NOT whole gripper speed/grasp qualification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_summaries={case:sha(src/'summary.json') for case,(src,m) in zip((a.baseline,a.candidate),data)},all_physical_csv_and_checkpoint_bytes_identical=same,runtime=runtime,speed_comparable_same_profile=same_profile,observed_runtime_improvement=same_profile and runtime['candidate_s']<runtime['baseline_s'],profiles=profiles,profile_note='CUMULATIVE inclusive/nested times;DO NOT SUM nested totals',process_heap_allocations='NOT MEASURED',speed_scope='this SAME4step active branch;NOT added to old free-recovery/value-only gains');write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k!='profiles'}))
if __name__=='__main__':main()
