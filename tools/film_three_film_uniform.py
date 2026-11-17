"""One bounded repeated three-film reference grid,never a hidden3grid child."""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--profile',required=True);p.add_argument('--grid-profile');p.add_argument('--steps',type=int,choices=(4,8,16,32),required=True);a=p.parse_args();profile=ROOT/'results'/('autonomous_film_'+a.profile);pm=json.loads((profile/'summary.json').read_text())
 if pm['status']!='PASS' or not pm.get('precise_ties') or pm['external_force_N']!=[0,0,-.001]:raise ValueError('measured same-physics precise reference required')
 perstep=pm['run']['runtime_s'];gp=None
 if a.steps>16:
  if not a.grid_profile:raise ValueError('measured completed uniform16 grid required for32-step confirmation')
  gp=json.loads((ROOT/'results'/('autonomous_film_'+a.grid_profile)/'summary.json').read_text())
  if gp['status']!='PASS' or gp['steps']!=16 or gp['duration']!=.0001 or gp['profile']!=a.profile:raise ValueError('same physical16-grid profile required')
  perstep=max(perstep,gp['run']['runtime_s']/gp['steps'])
 estimate=2*perstep*a.steps;out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py')
 if estimate>480:write_json(out/'summary.json',dict(status='BLOCKED',scope='measured child policy,NOT OS exhaustion',predicted_runtime_s=estimate));return
 archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'))
 for name,digest in pm['sources'].items():
  if name.endswith('.h') and sha(archive/name)!=digest:raise ValueError('measured three-film kernel changed:'+name)
 if gp:
  for name,digest in gp['sources'].items():
   if name.endswith('.h') and sha(archive/name)!=digest:raise ValueError('measured uniform kernel changed:'+name)
 cpp=archive/'diagnostics/film_three_finger/UniformContact.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/UniformContact.cpp',cpp);binary=out/'reference';compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120);run=guarded([binary,str(a.steps),out/'states.csv'],out/'run',480) if compile['exit_code']==0 else None
 result=dict(status='PASS' if run and run['exit_code']==0 else 'FAIL',scope='independent repeated nonlinear3film/ONEsphere,T0,Fz=-.001N,100us;NOT actual SOFA/time/grasp certificate',steps=a.steps,duration=.0001,profile=a.profile,grid_profile=a.grid_profile,predicted_runtime_s=estimate,compile=compile,run=run,sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip())
 if binary.exists():result['binary_sha256']=sha(binary)
 if (out/'states.csv').exists():result['completed_rows']=sum(1 for _ in csv.DictReader((out/'states.csv').open()))
 write_json(out/'summary.json',result);print(json.dumps(dict(status=result['status'],completed_rows=result.get('completed_rows'),run=run)))
if __name__=='__main__':main()
