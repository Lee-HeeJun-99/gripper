"""Coupled event plus Lobatto remainder on real saved PRE-impact input."""
import argparse,csv,json,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--residual',required=True);p.add_argument('--duration',type=float,default=.0000390625);p.add_argument('--base-steps',type=int,choices=(4,8,16),default=4);p.add_argument('--profile');p.add_argument('--sparse-stage',action='store_true');a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.residual);summary=json.loads((src/'summary.json').read_text())
 if summary['status']!='PASS' or not 0<a.duration<=.000125 or a.duration/a.base_steps>1e-5:raise ValueError('completed actual pre-state provenance/profile-bounded125us/10us steps required')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources'
 for directory in ('film_coupled_contact','film_coupled_collocation','film_combined_contact','film_impact','film_shell','film_rail_tendon','film_native_contact','film_sphere_contact'):
  target=archive/'models'/directory;target.mkdir(parents=True)
  for f in (ROOT/'models'/directory).glob('*.h'):shutil.copy2(f,target/f.name)
 # No silent material/control change relative to the ACTUAL original source.
 actual=json.loads((ROOT/'results'/('autonomous_film_'+summary['case'])/'identity.json').read_text())
 for name,digest in actual['sources'].items():
  if name.startswith(('models/film_shell/','models/film_rail_tendon/','models/film_sphere_contact/')) and name.endswith('.h') and sha(archive/name)!=digest:raise ValueError('actual physical header changed:'+name)
 estimate=None;limit=120
 if a.base_steps>4:
  if not a.profile:raise ValueError('measured same-kernel reference profile required')
  pm=json.loads((ROOT/'results'/('autonomous_film_'+a.profile)/'summary.json').read_text())
  if pm['status']!='PASS' or pm['residual_source']!=a.residual or pm.get('sparse_stage',False)!=a.sparse_stage:raise ValueError('profile actual initial state/backend differs')
  for name,digest in pm['sources'].items():
   if name.endswith('.h') and sha(archive/name)!=digest:raise ValueError('profiled combined kernel changed:'+name)
  estimate=2*pm['run']['runtime_s']*a.base_steps/pm.get('base_steps',4);limit=480
  if estimate>480:write_json(out/'summary.json',dict(status='BLOCKED',scope='measured reference runtime policy,NOT OS exhaustion',predicted_runtime_s=estimate));return
 shutil.copy2(src/'input.txt',out/'input.txt');cpp=archive/'diagnostics/film_coupled_reintegrated/CombinedActualState.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_coupled_reintegrated/CombinedActualState.cpp',cpp);binary=out/'reference';compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120);run=guarded([binary,out/'input.txt',str(a.duration),out/'states.csv',str(a.base_steps),str(int(a.sparse_stage))],out/'run',limit) if compile['exit_code']==0 else None
 result=dict(status='PASS' if run and run['exit_code']==0 else 'FAIL',scope='independent coupled actual PRE-state event+Lobatto glue;NOT global CCD/SOFA/full time certification',compile=compile,run=run,duration=a.duration,actual_pre_source=summary['case'],residual_source=a.residual,input_sha256=sha(out/'input.txt'),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()})
 result.update(base_steps=a.base_steps,profile=a.profile,predicted_runtime_s=estimate,child_limit_s=limit,sparse_stage=a.sparse_stage,clock_protocol='independent start+=dt;matches SOFA finite-precision clock;NOT copied actual states')
 if binary.exists():result['binary_sha256']=sha(binary)
 if result['status']=='PASS':result['events']=[{k:r[k] for k in ('steps','event_time','impulse','gap','normal_after')} for r in csv.DictReader((out/'states.csv').open())]
 write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k in ('status','events')}))
if __name__=='__main__':main()
