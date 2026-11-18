"""One-factor Newton tolerance probe,not a new physical model or actual SOFA."""
import argparse,csv,json,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_transmission_linear import shape
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--tolerance',choices=('1e-18','1e-20','1e-22'),required=True);a=p.parse_args();src=ROOT/'results/autonomous_film_20261118_transmission_onset_exact1203';proof=json.loads((src/'summary.json').read_text())
 if proof['status']!='PASS':raise ValueError('complete actual onset baseline required')
 for file,digest in proof['raw_hashes'].items():
  if sha(src/file)!=digest:raise ValueError('actual baseline raw changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));cpp=archive/'diagnostics/film_three_finger/Transmission.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/Transmission.cpp',cpp);binary=out/'reference';compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-DREGRIP_GAUSS_NEWTON_TOLERANCE='+a.tolerance,'-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120);run=guarded([binary,'8','.0008','.001','5',out/'probe',src/'public_mass.txt','gauss_hold'],out/'process',120) if compile['exit_code']==0 else None
 result=dict(status='FAIL',scope='independent identical100us/0.8ms input Newton residual probe;NOT actual SOFA/time certification',newton_tolerance_Ns=float(a.tolerance),production_default_Ns=1e-18,physical_inputs_unchanged=True,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),baseline_actual_summary_sha256=sha(src/'summary.json'),compile=compile,process=run,sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},binary_sha256=sha(binary) if binary.exists() else None)
 if run and run['exit_code']==0:
  rows=list(csv.DictReader((out/'probe.states.csv').open()));actual=list(csv.DictReader((src/'actual.csv').open()));errors={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for x,y in zip(rows,actual)) for k in ('q','v')};clock=len(rows)==len(actual)==8 and all(x['time']==y['time'] for x,y in zip(rows,actual));result.update(status=('EXPERIMENTAL' if a.tolerance!='1e-18' else 'PASS' if max(errors.values())<1e-12 else 'FAIL') if clock else 'FAIL',completed_steps=len(rows),accumulated_clock_exact=clock,baseline_state_difference=errors,endpoint_shape=shape(np.fromstring(rows[-1]['q'],sep=' ')))
 result['failure_reason']=(out/'process/stderr.log').read_text().strip() if run and run['exit_code'] else None;result['raw_hashes']={f.name:sha(f) for f in out.glob('probe.*')};write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('sources','compile','process','raw_hashes','endpoint_shape')}))
if __name__=='__main__':main()
