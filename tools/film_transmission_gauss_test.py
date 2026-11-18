"""Guarded independent fourth-order/tangent reference before actual SOFA."""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));cpp=archive/'tests/test_transmission_gauss.cpp';cpp.parent.mkdir();shutil.copy2(ROOT/'tests/test_transmission_gauss.cpp',cpp);binary=out/'test';compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120);run=guarded([binary],out/'process',120) if compile['exit_code']==0 else None;result=dict(status='FAIL',scope='independent damped oscillator analytic order4 and nonlinear stage tangent;NOT SOFA/full time gate',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},compile=compile,process=run,binary_sha256=sha(binary) if binary.exists() else None)
 if run and run['exit_code']==0:result.update(json.loads((out/'process/stdout.log').read_text()))
 write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('sources','compile','process')}))
if __name__=='__main__':main()
