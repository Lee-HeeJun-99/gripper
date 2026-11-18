"""Profile-bounded same-law nonlinear extension;no old checkpoint/model splice."""
import argparse,csv,json,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_transmission_linear import shape
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--startup-only',action='store_true');p.add_argument('--newton-tol',type=float,choices=(1e-22,1e-24),default=1e-24);a=p.parse_args();provider=ROOT/'results/autonomous_film_20261119_precise_gauss4_1681';m=json.loads((provider/'summary.json').read_text());qualification=ROOT/'results/autonomous_film_20261119_precise_startup_actual_time1691';qm=json.loads((qualification/'summary.json').read_text())
 if qm['status']!='PASS' or not m['FD_query_state_stages_EXACT'] or sha(provider/'reference')!=m['binary_sha256']:raise ValueError('qualified immutable startup kernel required')
 for f,d in m['source_hashes'].items():
  if sha(provider/'sources'/f)!=d:raise ValueError('compiled source changed')
 profile=max(x['process']['runtime_s'] for x in m['trials'].values());forecast=2*profile*160/8+20
 if forecast>480:raise ValueError('predicted child>480;NOT OS exhaustion')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');r=dict(status='FAIL',scope='independent SAME nonlinear FEM1ms40/80/160-step extension ONLY;NOT actual SOFA/contact/wrapping/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),provider_summary_sha256=sha(provider/'summary.json'),startup_time_summary_sha256=sha(qualification/'summary.json'),binary_sha256=m['binary_sha256'],source_hashes=m['source_hashes'],horizon_s=(.0002 if a.startup_only else .001),Newton_tolerance_Ns=a.newton_tol,relative_gate=.001,absolute_floor='NONE',predicted_max_child_runtime_s=forecast,actual_SOFA='NOT RUN',energy='NOT ASSESSED',work='NOT ASSESSED',trials={})
 r['scope']='independent SAME nonlinear FEM'+('200us8/16/32-step startup' if a.startup_only else '1ms40/80/160-step extension')+' ONLY;NOT actual SOFA/contact/wrapping/grasp'
 r['Newton_candidate']='stricter than historical1e-18;distinct1e-22/1e-24 settings,oldFAIL never relabeled'
 counts=(8,16,32) if a.startup_only else (40,80,160)
 for steps in counts:
  completed=[x for x in r['trials'].values() if x.get('status')=='PASS']
  if completed:
   prior=completed[-1];previous_steps=int(next(reversed(r['trials'])));estimate=2*prior['process']['runtime_s']*steps/previous_steps+20
   if estimate>480:r.update(status='BLOCKED',failure_reason='updated measured child forecast exceeds480s;NOT OS exhaustion',updated_predicted_child_runtime_s=estimate);break
  folder=out/str(steps);folder.mkdir();run=guarded([provider/'reference','fem',provider/'public_mass.txt',folder/'state.csv',str(r['horizon_s']),str(steps),str(a.newton_tol)],folder/'process',480);trial=dict(process=run,status='FAIL');r['trials'][str(steps)]=trial
  if run['exit_code']!=0:break
  data=next(csv.DictReader((folder/'state.csv').open()));trial.update(status='PASS',endpoint=data,shape=shape(np.fromstring(data['q'],sep=' ')))
  write_json(out/'progress.json',dict(status='INCOMPLETE',completed_steps=list(r['trials']),last_exit_code=run['exit_code'],not_a_time_PASS=True))
 if len(r['trials'])==3 and all(x['status']=='PASS' for x in r['trials'].values()):
  errors={}
  for lo,hi in ((str(counts[0]),str(counts[1])),(str(counts[1]),str(counts[2])),(str(counts[0]),str(counts[2]))):
   x,y=r['trials'][lo],r['trials'][hi];pair={}
   for key in ('q','v'):
    u,v=np.fromstring(x['endpoint'][key],sep=' '),np.fromstring(y['endpoint'][key],sep=' ')
    for label,slice_ in (('all',slice(None)),('Skin',slice(0,315)),('Rails',slice(315,None))):
     absolute=float(np.linalg.norm(u[slice_]-v[slice_]));scale=float(max(np.linalg.norm(u[slice_]),np.linalg.norm(v[slice_])));relative=absolute/scale if scale else None;pair[label+'_'+key]=dict(absolute=absolute,relative=relative,status='PASS' if relative is not None and relative<=.001 else 'FAIL')
   for key,value in x['shape'].items():
    other=y['shape'][key];absolute=abs(value-other);scale=max(abs(value),abs(other));relative=absolute/scale if scale else None;pair[key]=dict(absolute=absolute,relative=relative,status='PASS' if relative is not None and relative<=.001 else 'FAIL')
   errors[lo+'_'+hi]=pair
  r.update(status='PASS' if all(x['status']=='PASS' for pair in errors.values() for x in pair.values()) else 'FAIL',time_errors=errors,worst=max((dict(pair=p,quantity=k,**v) for p,pair in errors.items() for k,v in pair.items()),key=lambda x:x['relative'] if x['relative'] is not None else float('inf')))
 r['raw_hashes']={str(f.relative_to(out)):sha(f) for f in out.rglob('*') if f.is_file() and f.suffix=='.csv'};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','trials','raw_hashes','time_errors')}))
if __name__=='__main__':main()
