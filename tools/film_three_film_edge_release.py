"""Capture a rejected signed bilateral stage; never integrate negative reactions."""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--root',action='store_true');a=p.parse_args()
 parent=ROOT/'results/autonomous_film_20261118_three_film_edge_unload1061'
 meta=json.loads((parent/'summary.json').read_text());checkpoint=parent/'three.checkpoint_170.txt'
 if meta['status']!='FAIL' or sha(checkpoint)!=meta['raw_hashes'][checkpoint.name]:raise ValueError('preserved accepted prefix required')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(checkpoint,out/'input.checkpoint')
 archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'))
 cpp=archive/'diagnostics/film_three_finger/EdgeRelease.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/EdgeRelease.cpp',cpp)
 binary=out/'reference';compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-Werror=multichar','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120)
 run=guarded([binary,out/'input.checkpoint',out/'rejected.csv']+(['root'] if a.root else []),out/'run',480) if compile['exit_code']==0 else None
 result=dict(status='PASS' if run and run['exit_code']==0 else 'FAIL',scope='independent rejected signed-stage diagnostic;NOT actual release/accepted dynamics',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),checkpoint_sha256=sha(checkpoint),parent_summary_sha256=sha(parent/'summary.json'),compile=compile,run=run,sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()})
 if binary.exists():result['binary_sha256']=sha(binary)
 if (out/'rejected.csv').exists():
  rows=list(csv.DictReader((out/'rejected.csv').open()));result['rejected_csv_sha256']=sha(out/'rejected.csv')
  if a.root:result['root_metrics']=rows;result['scope']='independent signed reaction root/free remainder;NOT actual SOFA release or accepted unilateral event'
  else:result['signed_forces_N']=[float(r['force_N']) for r in rows];result['stage_times']=[float(r['time']) for r in rows]
 write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('sources','compile','run')}))
if __name__=='__main__':main()
