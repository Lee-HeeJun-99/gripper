"""Exact same arithmetic reuse,NOT a new precision or contact law."""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources'
 for name in ('tests/test_precise_query_cache.cpp','models/film_routed_contact/PreciseQueryCache.h','models/film_three_finger/PreciseDistanceOrder.h'):
  path=archive/name;path.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,path)
 sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off',archive/'tests/test_precise_query_cache.cpp','-o',out/'test'],out/'compile',120);run=guarded([out/'test'],out/'process',480) if compile['exit_code']==0 else None;r=dict(status='PASS' if run and run['exit_code']==0 else 'FAIL',scope='independent exact distance-order caching/degenerate parity ONLY;NOT adopted actual optimization',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes=sources,compile=compile,process=run,sdk='NOT used',physics_force_or_tolerance_changed=False)
 if (out/'test').exists():r['binary_sha256']=sha(out/'test')
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process')}))
if __name__=='__main__':main()
