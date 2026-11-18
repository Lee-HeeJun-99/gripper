"""Archived-source face/edge geometry qualification,not temporal/grasp certification."""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));source=archive/'tests/test_owned_feature_transition.cpp';source.parent.mkdir(parents=True);shutil.copy2(ROOT/'tests/test_owned_feature_transition.cpp',source);binary=out/'test';sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',source,'-o',binary],out/'compile',120);run=guarded([binary],out/'run',60) if compile['exit_code']==0 else None;result=dict(status='PASS' if run and run['exit_code']==0 else 'FAIL',scope='independent face-edge C1 gap/gradient,one-sided Hessian FD,body FD action-reaction,rotation objectivity/degenerate rejection;NOT time/SOFA/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources=sources,compile=compile,run=run)
 if binary.exists():result['binary_sha256']=sha(binary)
 write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('sources','compile','run')}))
if __name__=='__main__':main()
