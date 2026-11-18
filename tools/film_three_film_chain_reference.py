"""Independent numerical-plan clock reference;not a clock or state correction."""
import argparse,csv,json,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();names=['20261118_three_film_extended_actual1124']+[f'20261118_three_film_recovery_chain1127_plan{i}' for i in range(1,8)];rows=[];hashes={}
 for name in names:
  src=ROOT/'results'/('autonomous_film_'+name);meta=json.loads((src/'summary.json').read_text())
  if meta['status']!='EXPERIMENTAL' or meta['process']['exit_code'] or meta['steps']!=8:raise ValueError('complete actual plans required')
  for f,digest in meta['raw_hashes'].items():
   if sha(src/f)!=digest:raise ValueError('actual raw changed')
  hashes[name]=sha(src/'summary.json');rows+=list(csv.DictReader((src/'three.states.csv').open()))
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));cpp=archive/'diagnostics/film_three_finger/FreeRecovery.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/FreeRecovery.cpp',cpp);binary=out/'reference';checkpoint=ROOT/'results/autonomous_film_20261118_three_film_v5_next_plan1115/three.checkpoint_216.txt';shutil.copy2(checkpoint,out/'input.checkpoint')
 compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120);run=guarded([binary,out/'input.checkpoint','64',out/'reference','plans','.0064'],out/'process',480) if compile['exit_code']==0 else None
 result=dict(status='FAIL',scope='same-plan independent64-step reference vs actual SOFA31.6..38ms;NOT full physical recovery/time/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),actual_summary_hashes=hashes,source_checkpoint_sha256=sha(checkpoint),compile=compile,process=run,sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},api_gate=1e-12)
 if run and run['exit_code']==0:
  expected=list(csv.DictReader((out/'reference.states.csv').open()));errors={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for x,y in zip(rows,expected)) for k in ('q','v')};clock=len(rows)==len(expected)==64 and all(x['time']==y['time'] for x,y in zip(rows,expected));result.update(status='PASS' if max(errors.values())<1e-12 and clock else 'FAIL',reference_max_abs=errors,accumulated_api_clock_exact=clock,binary_sha256=sha(binary))
 result['raw_hashes']={f.name:sha(f) for f in out.glob('reference.*')};write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('sources','process','compile','raw_hashes','actual_summary_hashes')}))
if __name__=='__main__':main()
