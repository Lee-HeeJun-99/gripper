"""Retain legacy FAIL while qualifying the implemented stage-consistent observer."""
import argparse,csv,itertools,json,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
from film_coupled_time import metric
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--physics',required=True);p.add_argument('--observers',nargs=3,required=True);a=p.parse_args();physical=ROOT/'results'/('autonomous_film_'+a.physics);physics=json.loads((physical/'summary.json').read_text());runs=[]
 for case in a.observers:
  path=ROOT/'results'/('autonomous_film_'+case);summary=json.loads((path/'summary.json').read_text());source=ROOT/'results'/('autonomous_film_'+summary['case']);meta=json.loads((source/'identity.json').read_text())
  if summary['status']!='PASS' or len(summary['physical_csv_exact'])!=9 or any(x['before']!=x['after'] for x in summary['physical_csv_exact'].values()):raise ValueError('actual observer must preserve all nine physical CSVs exactly')
  if summary['case'] not in physics['raw'] or any(sha(source/f)!=v for f,v in physics['raw'][summary['case']].items()):raise ValueError('physical assessment and observer source do not match')
  if runs and (summary['binary_sha256']!=runs[0][2]['binary_sha256'] or meta['binary_sha256']!=runs[0][3]['binary_sha256']):raise ValueError('same actual core AND observer DLLs required')
  rows=list(csv.DictReader((path/'stage_work.csv').open()))[2::3]
  if len(rows)!=meta['steps']:raise ValueError('incomplete runtime work')
  runs.append((case,path,summary,meta,rows))
 runs.sort(key=lambda r:r[3]['steps']);pairs={}
 for left,right in itertools.combinations(runs,2):
  name,_,_,lm,lr=left;other,_,_,rm,rr=right;ratio=rm['steps']//lm['steps']
  if ratio*lm['steps']!=rm['steps']:raise ValueError('nested time grids required')
  aligned=rr[ratio-1::ratio]
  if max(abs(float(x['time'])-float(y['time'])) for x,y in zip(lr,aligned))>1e-12:raise ValueError('same physical output times required')
  pairs[name+'__'+other]=metric(np.array([float(r['cumulative_macro_work_Nmm']) for r in lr]),np.array([float(r['cumulative_macro_work_Nmm']) for r in aligned]))
 original={k:p['errors']['field_sampled_tendon_work'] for k,p in physics['pairs'].items()};physical_other={k:{n:v for n,v in p['errors'].items() if n!='field_sampled_tendon_work'} for k,p in physics['pairs'].items()};modern=all(v['status']=='PASS' for v in pairs.values()) and all(v['status']=='PASS' for p in physical_other.values() for v in p.values());legacy=all(v['status']=='PASS' for v in original.values())
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');result=dict(status='EXPERIMENTAL' if modern else 'FAIL',scope='implemented stage-consistent runtime observer10ms C2 refinement;NOT full-cycle/full-system time/energy/grasp',stage_consistent_time_gate='PASS' if modern else 'FAIL',legacy_field_work_gate='PASS' if legacy else 'FAIL',overall_legacy_inclusive_time_gate=physics['status'],relative_gate=.001,new_runtime_work_pairs=pairs,legacy_errors_preserved=original,other_physical_errors=physical_other,physics_sha256=sha(physical/'summary.json'),runtime_observers={r[0]:dict(summary=sha(r[1]/'summary.json'),work=sha(r[1]/'stage_work.csv')) for r in runs},explanation='same -integral T*dL,improved numerical quadrature;old endpoint Stieltjes sample FAIL is not removed or relabelled',not_qualified=['full closing/birth/release cycle','whole physical energy','mesh/friction/self-contact','full-thickness contact','wrap/lift/hold/grasp/12wrench/Optuna'])
 write_json(out/'summary.json',result);print(json.dumps({k:result[k] for k in ('status','stage_consistent_time_gate','legacy_field_work_gate','overall_legacy_inclusive_time_gate','new_runtime_work_pairs')}))
if __name__=='__main__':main()
