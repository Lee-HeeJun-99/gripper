"""Independent completed-V5 mechanical-state reference beyond the actual32ms cap."""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--steps',type=int,choices=(32,64,128,256),required=True);p.add_argument('--reuse');a=p.parse_args();src=ROOT/'results/autonomous_film_20261118_three_film_v5_next_plan1115';meta=json.loads((src/'summary.json').read_text());checkpoint=src/'three.checkpoint_216.txt'
 if meta['status']!='EXPERIMENTAL' or meta['process']['exit_code'] or sha(checkpoint)!=meta['raw_hashes'][checkpoint.name]:raise ValueError('complete actual V5 source required')
 forecast=2*meta['process']['runtime_s']*a.steps/meta['steps']+30
 previous=proof=None
 if a.reuse:
  previous=ROOT/'results'/('autonomous_film_'+a.reuse);proof=json.loads((previous/'summary.json').read_text())
  if proof['status']!='PASS' or proof['actual_checkpoint_sha256']!=sha(checkpoint) or sha(previous/'reference')!=proof['binary_sha256']:raise ValueError('qualified same-IVP source/binary profile required')
  forecast=2*proof['run']['runtime_s']*a.steps/proof['steps']+30
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py')
 if forecast>480:
  write_json(out/'summary.json',dict(status='BLOCKED',scope='reference process forecast only,NOT OS exhaustion or physical FAIL',steps=a.steps,predicted_runtime_s=forecast,limit_s=480,physics_launched=False));print('BLOCKED measured reference forecast exceeds480s');return
 shutil.copy2(checkpoint,out/'input.checkpoint');archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));cpp=archive/'diagnostics/film_three_finger/FreeRecovery.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/FreeRecovery.cpp',cpp);binary=out/'reference'
 if proof:
  for name,digest in proof['sources'].items():
   if sha(archive/name)!=digest:raise ValueError('compiled recovery reference source changed:'+name)
  shutil.copy2(previous/'reference',binary);compile={'exit_code':0,'reused_from':a.reuse,'source_closure_exact':True}
 else:compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120)
 run=guarded([binary,out/'input.checkpoint',str(a.steps),out/'recovery','common','.0064'],out/'run',480) if compile['exit_code']==0 else None;result=dict(status='PASS' if run and run['exit_code']==0 else 'FAIL',scope='independent6.4ms FREE recovery from completed actual V5;NOT actual SOFA or extended-owner qualification',steps=a.steps,duration_s=.0064,predicted_runtime_s=forecast,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},actual_checkpoint_sha256=sha(checkpoint),parent_summary_sha256=sha(src/'summary.json'),compile=compile,run=run,binary_sha256=sha(binary) if binary.exists() else None)
 if (out/'recovery.metrics.csv').exists():result['metrics']=next(csv.DictReader((out/'recovery.metrics.csv').open()))
 if run:result['failure_reason']=(out/'run/stderr.log').read_text().strip() or None
 result['raw_hashes']={f.name:sha(f) for f in out.glob('recovery.*')};write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('sources','compile','run','raw_hashes')}))
if __name__=='__main__':main()
