"""Independent FEM Rayleigh trial,NOT an eigenmode or actual wrapping time."""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));cpp=archive/'diagnostics/film_three_finger/RayleighScale.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/RayleighScale.cpp',cpp);binary=out/'reference';compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120);run=guarded([binary],out/'run',120) if compile['exit_code']==0 else None;result=dict(status='PASS' if run and run['exit_code']==0 else 'FAIL',scope='independent FEM stress-free T0 contact-tangent quadratic trial;NOT computed eigenmode,dominant response,nonlinear grasp time or SOFA',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},compile=compile,run=run,assumptions='research E250MPa,film1g each,FREE sphere100g,zero external load/T0,bilateral fixed-contact tangent;not measured',interpretation='Rayleigh principle is conditional on stable linearized branch;omega is an upper bound on lowest constrained undamped frequency,NOT exact/forced/damped mode.10ms cannot by itself qualify wrap/recovery.')
 if binary.exists():result['binary_sha256']=sha(binary)
 if run and run['exit_code']==0:result['metrics']=json.loads((out/'run/stdout.log').read_text())
 write_json(out/'summary.json',result);print(json.dumps({k:result[k] for k in ('status','scope','metrics') if k in result}))
if __name__=='__main__':main()
