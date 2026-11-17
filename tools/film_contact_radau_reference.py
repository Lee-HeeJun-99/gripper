"""Bounded independent single-row collocation reference,not SOFA certification."""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources'
 for name in ('models/film_coupled_collocation/SingleRowRadau.h','tests/test_contact_radau.cpp'):
  target=archive/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
 binary=out/'reference';compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',archive/'tests/test_contact_radau.cpp','-o',binary],out/'compile',120);run=guarded([binary],out/'run',60) if compile['exit_code']==0 else None
 result=dict(status='PASS' if run and run['exit_code']==0 else 'FAIL',scope='independent single BILATERAL persistent-row collocation with unilateral rejection;NOT actual SOFA/impact/full contact',compile=compile,run=run,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()})
 if binary.exists():result['binary_sha256']=sha(binary)
 write_json(out/'summary.json',result);print(json.dumps(dict(status=result['status'])))
if __name__=='__main__':main()
