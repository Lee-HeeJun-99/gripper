"""One profiled uniform physical grid per bounded child,not a packed triplet."""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--profile',required=True);p.add_argument('--duration',type=float,default=.001);p.add_argument('--steps',type=int,choices=(128,256,512),default=128);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.profile);pm=json.loads((src/'summary.json').read_text())
 if pm['status']!='PASS' or not pm.get('sparse_stage') or not 0<a.duration<=.001 or a.duration/a.steps>1e-5:raise ValueError('completed same-kernel sparse physical profile/1ms/10us steps required')
 estimate=2*pm['run']['runtime_s']*a.steps/(7*pm['base_steps']);out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py')
 if estimate>480:write_json(out/'summary.json',dict(status='BLOCKED',scope='measured per-child runtime policy,NOT OS exhaustion',predicted_runtime_s=estimate));return
 archive=out/'sources';shutil.copytree(src/'sources/models',archive/'models')
 for name,digest in pm['sources'].items():
  if name.endswith('.h') and (sha(archive/name)!=digest or sha(ROOT/name)!=digest):raise ValueError('profiled uniform kernel changed:'+name)
 shutil.copy2(src/'input.txt',out/'input.txt');cpp=archive/'diagnostics/film_coupled_reintegrated/CombinedUniform.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_coupled_reintegrated/CombinedUniform.cpp',cpp);binary=out/'reference';compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120);run=guarded([binary,out/'input.txt',str(a.duration),str(a.steps),out/'states.csv'],out/'run',480) if compile['exit_code']==0 else None
 result=dict(status='PASS' if run and run['exit_code']==0 else 'FAIL',scope='independent nonlinear FEM from actual PRE-state,uniform sparse C2,event+Lobatto;NOT actual SOFA/global CCD/full time gate',profile=a.profile,predicted_runtime_s=estimate,duration=a.duration,steps=a.steps,compile=compile,run=run,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),input_sha256=sha(out/'input.txt'),sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()})
 if binary.exists():result['binary_sha256']=sha(binary)
 if (out/'states.csv').exists():result['completed_rows']=sum(1 for _ in csv.DictReader((out/'states.csv').open()))
 write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k in ('status','completed_rows','predicted_runtime_s')}))
if __name__=='__main__':main()
