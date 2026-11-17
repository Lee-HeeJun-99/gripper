"""Refine ONLY post-impact evolution from one identical saved actual state."""
import argparse,csv,json,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--steps',type=int,choices=(7,8,14,16,28,32),required=True);p.add_argument('--reuse');p.add_argument('--profile');a=p.parse_args();actual=ROOT/'results/autonomous_film_20261118_three_film_event_rows964';meta=json.loads((actual/'summary.json').read_text());source=next(csv.DictReader((actual/'three.event.csv').open()))
 if meta['status']!='PASS' or sha(actual/'three.event.csv')!=meta['raw_hashes']['three.event.csv']:raise ValueError('completed immutable actual event required')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));diag=archive/'diagnostics/film_three_finger';diag.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/PostImpact.cpp',diag/'PostImpact.cpp');sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};shutil.copy2(actual/'public_mass_reference.txt',out/'mass.txt');q=np.fromstring(source['qend'],sep=' ');(out/'initial.txt').write_text(str(len(q))+'\n'+source['qend']+'\n'+source['vend']+'\n');binary=out/'reference'
 if a.reuse:
  prior=ROOT/'results'/('autonomous_film_'+a.reuse);old=json.loads((prior/'summary.json').read_text());binary=prior/'reference';compiled=lambda d:{k:v for k,v in d.items() if k.endswith('.h') or k=='diagnostics/film_three_finger/PostImpact.cpp'}
  if old['status']!='PASS' or compiled(old['sources'])!=compiled(sources) or sha(binary)!=old['binary_sha256']:raise ValueError('post-impact same compiled headers/driver/binary required')
  compile=dict(exit_code=0,reused=a.reuse)
 else:compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',diag/'PostImpact.cpp','-o',binary],out/'compile',120)
 measured=json.loads((ROOT/'results/autonomous_film_20261118_three_film_event_sustained966/summary.json').read_text());estimate=2*measured['process']['runtime_s']*a.steps/8+30
 if a.profile:
  prior=ROOT/'results'/('autonomous_film_'+a.profile);profile=json.loads((prior/'summary.json').read_text())
  if profile['status']!='PASS' or profile['binary_sha256']!=sha(binary):raise ValueError('completed same binary profile required')
  estimate=2*profile['run']['runtime_s']*a.steps/profile['steps']+15
 result=dict(status='FAIL',scope='independent nonlinear FEM post-impact1.4ms ONLY;common saved actual200us state,NOT whole-event time/SOFA/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources=sources,steps=a.steps,start_time=.0002,duration=.0014,initial_sha256=sha(out/'initial.txt'),mass_sha256=sha(out/'mass.txt'),actual_event_sha256=sha(actual/'three.event.csv'),predicted_runtime_s=estimate,compile=compile)
 if compile['exit_code']==0:
  result['binary_sha256']=sha(binary)
  if estimate>480:result['status']='BLOCKED';result['reason']='measured child runtime policy forecast,NOT OS exhaustion'
  else:
   run=guarded([binary,out/'mass.txt',out/'initial.txt',str(a.steps),out/'states.csv'],out/'run',480);result['run']=run
   if run['exit_code']==0:
    rows=list(csv.DictReader((out/'states.csv').open()));result['completed_rows']=len(rows);result['minimum_gap_mm']=min(float(r['gap']) for r in rows);result['status']='PASS' if len(rows)==a.steps and result['minimum_gap_mm']>=-1e-10 else 'FAIL';result['states_sha256']=sha(out/'states.csv')
 write_json(out/'summary.json',result);print(json.dumps({k:result[k] for k in ('status','steps','predicted_runtime_s','run','minimum_gap_mm') if k in result}))
if __name__=='__main__':main()
