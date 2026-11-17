"""Exact rational countercheck for recorded113/334-bit ordering rejection."""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);fixture=src/'states.csv.precision.csv'
 if not fixture.exists():raise ValueError('recorded rejected comparison required')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources'
 for name in ('models/film_three_finger/PreciseDistanceOrder.h','diagnostics/film_three_finger/ExactDistance.cpp'):
  target=archive/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
 shutil.copy2(fixture,out/'coordinates.csv');binary=out/'reference';compile=guarded(['g++','-O2','-std=c++17',archive/'diagnostics/film_three_finger/ExactDistance.cpp','-o',binary],out/'compile',120);run=guarded([binary,out/'coordinates.csv'],out/'run',120) if compile['exit_code']==0 else None
 result=dict(status='PASS' if run and run['exit_code']==0 else 'FAIL',scope='independent exact rational classification of recorded binary-double geometry;NOT contact/dynamics certification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),case=a.case,fixture_sha256=sha(fixture),sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},compile=compile,run=run)
 if binary.exists():result['binary_sha256']=sha(binary)
 if run:result['reference_output']=(out/'run/stdout.log').read_text()
 write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
