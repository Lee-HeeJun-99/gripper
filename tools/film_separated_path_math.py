"""Strict supporting-plane interval exclusion unit evidence."""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('__pycache__'));cpp=archive/'tests/test_separated_numerical_path.cpp';cpp.parent.mkdir();shutil.copy2(ROOT/'tests/test_separated_numerical_path.cpp',cpp)
 compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'test'],out/'compile',120);run=guarded([out/'test'],out/'process',60) if compile['exit_code']==0 else None;r=dict(status='PASS' if run and run['exit_code']==0 else 'FAIL',scope='independent strict numerical-path exclusion only;NOT actual CCD/grasp/time certification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},compile=compile,process=run,sdk='NOT used')
 if (out/'test').exists():r['binary_sha256']=sha(out/'test')
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process')}))
if __name__=='__main__':main()
