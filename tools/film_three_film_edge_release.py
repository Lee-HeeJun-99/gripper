"""Capture a rejected signed bilateral stage; never integrate negative reactions."""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--root',action='store_true');p.add_argument('--admissible',action='store_true');p.add_argument('--rk',type=int,choices=(8,16,32,64,128));p.add_argument('--acc',type=int,choices=(8,16,32,64,128));p.add_argument('--reuse');a=p.parse_args()
 if a.admissible and not a.root:raise ValueError('admissible requires root')
 parent=ROOT/'results/autonomous_film_20261118_three_film_edge_unload1061'
 meta=json.loads((parent/'summary.json').read_text());checkpoint=parent/'three.checkpoint_170.txt'
 if meta['status']!='FAIL' or sha(checkpoint)!=meta['raw_hashes'][checkpoint.name]:raise ValueError('preserved accepted prefix required')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(checkpoint,out/'input.checkpoint')
 archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'))
 cpp=archive/'diagnostics/film_three_finger/EdgeRelease.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/EdgeRelease.cpp',cpp)
 binary=out/'reference'
 if a.reuse:
  previous=ROOT/'results'/('autonomous_film_'+a.reuse);proof=json.loads((previous/'summary.json').read_text())
  if proof['status']!='PASS' or sha(previous/'reference')!=proof['binary_sha256']:raise ValueError('verified reference binary required')
  for name,digest in proof['sources'].items():
   if sha(archive/name)!=digest:raise ValueError('compiled source closure differs:'+name)
  grid=a.acc or a.rk;old=proof.get('acc_grid') if a.acc else proof.get('rk_grid')
  if not grid or not old:raise ValueError('same profiled integrator reuse only')
  forecast=2*proof['run']['runtime_s']*(grid+32)/(old+32)+30
  if forecast>480:raise ValueError('measured RK forecast exceeds480s')
  shutil.copy2(previous/'reference',binary);compile={'exit_code':0,'reused_from':a.reuse,'source_closure_exact':True,'predicted_runtime_s':forecast}
 else:compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-Werror=multichar','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120)
 run=guarded([binary,out/'input.checkpoint',out/'rejected.csv']+(['ac'+str(a.acc)] if a.acc else ['rk'+str(a.rk)] if a.rk else ['admissible' if a.admissible else 'root'] if a.root else []),out/'run',480) if compile['exit_code']==0 else None
 result=dict(status='PASS' if run and run['exit_code']==0 else 'FAIL',scope='independent rejected signed-stage diagnostic;NOT actual release/accepted dynamics',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),checkpoint_sha256=sha(checkpoint),parent_summary_sha256=sha(parent/'summary.json'),compile=compile,run=run,sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()})
 if binary.exists():result['binary_sha256']=sha(binary)
 if (out/'rejected.csv').exists():
  rows=list(csv.DictReader((out/'rejected.csv').open()));result['rejected_csv_sha256']=sha(out/'rejected.csv')
  if a.acc:result['acc_grid']=a.acc;result['root_metrics']=[{k:v for k,v in r.items() if k not in ('q','v')} for r in rows];result['scope']='independent acceleration-complementarity release;NOT actual SOFA/time/grasp'
  elif a.rk:result['rk_grid']=a.rk;result['root_metrics']=[{k:v for k,v in r.items() if k not in ('q','v')} for r in rows];result['scope']='independent acceleration-ODE RK4 event reference;NOT actual SOFA release'
  elif a.root:result['root_metrics']=rows;result['scope']='independent signed reaction root/free remainder;NOT actual SOFA release or accepted unilateral event'
  else:result['signed_forces_N']=[float(r['force_N']) for r in rows];result['stage_times']=[float(r['time']) for r in rows]
 write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('sources','compile','run')}))
if __name__=='__main__':main()
