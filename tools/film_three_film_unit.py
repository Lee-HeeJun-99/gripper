"""Bounded,archived standalone regression;never substitutes for actual SOFA."""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 allowed=('test_routed_cable_power.cpp','test_gap_controlled_rows.cpp','test_three_film_row_snapshot.cpp','test_precise_distance_order.cpp','test_three_film_free_block.cpp','test_three_film_birth.cpp')
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--test',choices=allowed,required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));(archive/'tests').mkdir();shutil.copy2(ROOT/'tests'/a.test,archive/'tests'/a.test);helper=archive/'diagnostics/film_three_finger/RoutedCablePower.h';helper.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/RoutedCablePower.h',helper);binary=out/'reference'
 compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',archive/'tests'/a.test,'-o',binary],out/'compile',120);run=guarded([binary],out/'run',120) if compile['exit_code']==0 else None
 result=dict(status='PASS' if run and run['exit_code']==0 else 'FAIL',scope='independent standalone mathematical/controller regression,NOT actual SOFA or full physics certification',test=a.test,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},compile=compile,run=run)
 if binary.exists():result['binary_sha256']=sha(binary)
 if run:result['reference_output']=(out/'run/stdout.log').read_text()
 write_json(out/'summary.json',result);print(json.dumps({k:result[k] for k in ('status','scope','reference_output') if k in result}))
if __name__=='__main__':main()
