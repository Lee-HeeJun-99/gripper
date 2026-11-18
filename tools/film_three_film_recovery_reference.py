"""Same actual unloaded IVP,independent800us FREE refinement,strict CCD guard."""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--steps',type=int,choices=(8,16,32),required=True);p.add_argument('--reuse');a=p.parse_args();parent=ROOT/'results/autonomous_film_20261118_three_film_unload_end1083';meta=json.loads((parent/'summary.json').read_text());checkpoint=parent/'three.checkpoint_200.txt'
 if meta['status']!='EXPERIMENTAL' or meta['process']['exit_code'] or sha(checkpoint)!=meta['raw_hashes'][checkpoint.name]:raise ValueError('actual complete30ms checkpoint required')
 forecast=2*meta['process']['runtime_s']*a.steps/meta['steps']+30
 if forecast>480:raise ValueError('actual measured per-step forecast exceeds480s')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(checkpoint,out/'input.checkpoint');archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));cpp=archive/'diagnostics/film_three_finger/FreeRecovery.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/FreeRecovery.cpp',cpp);binary=out/'reference'
 if a.reuse:
  previous=ROOT/'results'/('autonomous_film_'+a.reuse);proof=json.loads((previous/'summary.json').read_text())
  if proof['status']!='PASS' or sha(previous/'reference')!=proof['binary_sha256']:raise ValueError('complete unchanged reference binary required')
  for name,digest in proof['sources'].items():
   if sha(archive/name)!=digest:raise ValueError('compiled reference source changed:'+name)
  shutil.copy2(previous/'reference',binary);compile={'exit_code':0,'reused_from':a.reuse,'source_closure_exact':True}
 else:compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120)
 run=guarded([binary,out/'input.checkpoint',str(a.steps),out/'recovery'],out/'run',480) if compile['exit_code']==0 else None;result=dict(status='PASS' if run and run['exit_code']==0 else 'FAIL',scope='independent800us FREE recovery refinement;NOT actual SOFA or full time/recovery certification',steps=a.steps,predicted_runtime_s=forecast,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},parent_summary_sha256=sha(parent/'summary.json'),actual_checkpoint_sha256=sha(checkpoint),compile=compile,run=run,binary_sha256=sha(binary) if binary.exists() else None)
 if (out/'recovery.metrics.csv').exists():result['metrics']=next(csv.DictReader((out/'recovery.metrics.csv').open()))
 result['raw_hashes']={f.name:sha(f) for f in out.glob('recovery.*')};write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('sources','compile','run','raw_hashes')}))
if __name__=='__main__':main()
