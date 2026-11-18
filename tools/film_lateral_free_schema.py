"""Independent typed footer unit test; no physical dynamics PASS inference."""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources'
 for name in ('tests/test_lateral_free_footer.cpp','models/film_lateral_release/FreeFooter.h'):
  target=archive/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
 compile=guarded(['g++','-O2','-std=c++17',archive/'tests/test_lateral_free_footer.cpp','-o',out/'test'],out/'compile',60);run=guarded([out/'test'],out/'process',30) if compile['exit_code']==0 else None;r=dict(status='PASS' if run and run['exit_code']==0 else 'FAIL',scope='typed FREE footer/schema ONLY;NOT SOFA or physical convergence',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},compile=compile,process=run)
 if (out/'test').exists():r['binary_sha256']=sha(out/'test')
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process')}))
if __name__=='__main__':main()
