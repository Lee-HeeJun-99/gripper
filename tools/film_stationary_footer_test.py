"""Archive and execute the pure stationary FREE provenance parser test."""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources'
 for f in ('tests/test_stationary_free_footer.cpp','models/film_stationary_release/FreeFooter.h'):
  dst=archive/f;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/f,dst)
 sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};compile=guarded(['g++','-O2','-std=c++17',archive/'tests/test_stationary_free_footer.cpp','-o',out/'test'],out/'compile',60);run=guarded([out/'test'],out/'process',10) if compile['exit_code']==0 else None
 r=dict(status='PASS' if run and run['exit_code']==0 else 'FAIL',scope='exact provenance roundtrip and seven malformed FREE/footer rejections ONLY;NOT dynamics',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes=sources,compile=compile,process=run,binary_sha256=sha(out/'test') if (out/'test').exists() else None);write_json(out/'summary.json',r);print(json.dumps(r))
if __name__=='__main__':main()
