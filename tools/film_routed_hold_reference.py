"""Same-IVP reference after ACTUAL new-route checkpoint50;no old transplant."""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--refinement',type=int,choices=(1,2,4),default=1);p.add_argument('--reuse');p.add_argument('--parent',default='20261118_routed_to_peak1280');p.add_argument('--checkpoint-step',type=int,default=50);p.add_argument('--qualification');a=p.parse_args();parent=ROOT/'results'/('autonomous_film_'+a.parent);m=json.loads((parent/'summary.json').read_text());checkpoint=parent/f'three.checkpoint_{a.checkpoint_step}.txt';provider=ROOT/'results/autonomous_film_20261118_routed_resume1278';proof=json.loads((provider/'summary.json').read_text())
 if m['status'] not in ('PASS','EXPERIMENTAL') or sha(checkpoint)!=m['raw_hashes'][checkpoint.name] or proof['status']!='PASS':raise ValueError('qualified actual new-route checkpoint/adapter required')
 qualification=None
 if m['status']=='EXPERIMENTAL':
  if not a.qualification:raise ValueError('experimental actual parent requires separate strict API qualification')
  qualification=ROOT/'results'/('autonomous_film_'+a.qualification);qm=json.loads((qualification/'summary.json').read_text())
  if qm['status']!='PASS' or qm['actual_summary_sha256']!=sha(parent/'summary.json'):raise ValueError('strict API qualification differs from actual parent')
 for f,d in proof['source_hashes'].items():
  if sha(provider/'sources'/f)!=d:raise ValueError('qualified routed source changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(checkpoint,out/'input.checkpoint');archive=out/'sources';shutil.copytree(provider/'sources/models',archive/'models');cpp=archive/'diagnostics/film_three_finger/RoutedHoldReference.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/RoutedHoldReference.cpp',cpp);sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};binary=out/'reference';forecast=None
 if a.reuse:
  src=ROOT/'results'/('autonomous_film_'+a.reuse);old=json.loads((src/'summary.json').read_text())
  if old['status']!='PASS' or old['source_hashes']!=sources or sha(src/'reference')!=old['binary_sha256']:raise ValueError('exact same compiled reference required;current IVP separately bound')
  forecast=2*old['process']['runtime_s']*a.refinement/old['refinement']+30;shutil.copy2(src/'reference',binary);compile=dict(exit_code=0,reused_from=a.reuse)
 else:
  if a.refinement!=1:raise ValueError('initial reference must be measured baseline')
  compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120)
 r=dict(status='BLOCKED',scope='shared-kernel same-actual-IVP Hold reference;NOT actual fine SOFA/full time/energy/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes=sources,parent_summary_sha256=sha(parent/'summary.json'),qualification_summary_sha256=sha(qualification/'summary.json') if qualification else None,provider_summary_sha256=sha(provider/'summary.json'),input_checkpoint_sha256=sha(checkpoint),macro_steps=8,refinement=a.refinement,compile=compile,predicted_child_runtime_s=forecast,control='original C2 .0001N/rail,ramp10ms,release20..30ms',root_reaction_work=None,normal_work_note='computed numerical residual,NOT Coulomb heat;relative failure must remain visible')
 if forecast and forecast>480:r['failure_reason']='measured policy forecast>480s;NOT OS exhaustion';write_json(out/'summary.json',r);return
 run=guarded([binary,out/'input.checkpoint','8',str(a.refinement),out/'states.csv'],out/'process',480) if compile['exit_code']==0 else None;r.update(status='FAIL',process=run)
 if run and run['exit_code']==0:
  rows=list(csv.DictReader((out/'states.csv').open()));r.update(status='PASS' if len(rows)==8 else 'FAIL',binary_sha256=sha(binary),end_time_s=float(rows[-1]['time']),maximum_momentum_residual_Ns=max(float(x['momentum']) for x in rows),minimum_whole_stage_gap_mm=min(float(x['gap']) for x in rows),raw_hashes={'states.csv':sha(out/'states.csv')})
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process')}))
if __name__=='__main__':main()
