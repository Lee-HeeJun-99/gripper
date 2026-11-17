"""Same-binary one-factor FP input-clock test,NO actual q/v injection or rerun."""
import argparse,csv,json,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();actual=ROOT/'results/autonomous_film_20261118_three_film_first_peak_actual1002';am=json.loads((actual/'summary.json').read_text());original=ROOT/'results/autonomous_film_20261118_three_film_first_peak1000';om=json.loads((original/'summary.json').read_text())
 if am['process']['exit_code']!=0 or am['sofa_errors'] or om['completed_rows']!=50:raise ValueError('completed actual/counterfactual fixture required;original loose PASS is NOT accepted as qualification')
 for name,digest in am['raw_hashes'].items():
  if sha(actual/name)!=digest:raise ValueError('actual raw changed:'+name)
 estimate=2*om['run']['runtime_s']+30
 if estimate>480:raise ValueError('each same-input reference forecast exceeds480s')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));(archive/'tests').mkdir();shutil.copy2(ROOT/'tests/test_three_film_birth.cpp',archive/'tests/test_three_film_birth.cpp');shutil.copy2(actual/'public_mass_reference.txt',out/'mass.txt');binary=out/'reference';compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',archive/'tests/test_three_film_birth.cpp','-o',binary],out/'compile',120);result=dict(status='FAIL',scope='independent SAME-binary accumulated-vs-multiplied floating input clock;NOT new actual execution or fulltime/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},actual_summary_sha256=sha(actual/'summary.json'),actual_raw_sha256=am['raw_hashes'],predicted_each_runtime_s=estimate,absolute_api_gate=1e-12,compile=compile,modes={},state_injection=False,law='same existing C2,model,masses,solver,dt and analytic fixture;ONLY FP clock construction changes')
 if compile['exit_code']==0:
  result['binary_sha256']=sha(binary);actual_rows=list(csv.DictReader((actual/'three.states.csv').open()))
  for mode in ('accumulated','multiplied'):
   path=out/(mode+'.csv');command=[binary,out/'mass.txt',path,'50']+(['accumulated'] if mode=='accumulated' else []);run=guarded(command,out/(mode+'_run'),480);info=dict(run=run,physical_run_status='FAIL')
   if run['exit_code']==0:
    rows=list(csv.DictReader((out/(mode+'.csv.states.csv')).open()));errors={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for x,y in zip(actual_rows,rows)) for k in ('q','v')};info.update(physical_run_status='PASS' if len(rows)==50 else 'FAIL',api_status='PASS' if len(rows)==50 and max(errors.values())<1e-12 else 'FAIL',errors=errors,clock_max_abs_s=max(abs(float(x['time'])-float(y['time'])) for x,y in zip(actual_rows,rows)),states_sha256=sha(out/(mode+'.csv.states.csv')))
   result['modes'][mode]=info;write_json(out/'partial.json',result)
  left,right=result['modes'].values();result['status']='PASS' if left.get('api_status')=='PASS' and right.get('api_status')=='FAIL' and right['physical_run_status']=='PASS' else 'FAIL'
 write_json(out/'summary.json',result);print(json.dumps({k:result[k] for k in ('status','absolute_api_gate','state_injection','modes')}))
if __name__=='__main__':main()
