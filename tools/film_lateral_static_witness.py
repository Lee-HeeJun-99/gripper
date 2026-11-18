"""Fresh complete query of preserved lower-load branch,not failed-horizon PASS."""
import argparse,csv,json,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_transmission_linear import shape
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'results/autonomous_film_20261118_lateral_static1374';m=json.loads((src/'summary.json').read_text())
 if m['status']!='FAIL' or sha(src/'equilibrium.states.csv')!=m['raw_hashes']['equilibrium.states.csv']:raise ValueError('preserved failed-horizon branch required')
 for f,d in m['source_hashes'].items():
  if sha(src/'sources'/f)!=d:raise ValueError('original partial-branch model archive changed')
 selected=[x for x in csv.DictReader((src/'equilibrium.states.csv').open()) if x['stage']=='15']
 if len(selected)!=1 or float(selected[0]['T'])!=.00009375:raise ValueError('explicit lower-load branch unavailable')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(src/'sources/models',archive/'models');cpp=archive/'diagnostics/film_three_finger/LateralStaticWitness.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/LateralStaticWitness.cpp',cpp);(out/'selected.txt').write_text(selected[0]['T']+' '+selected[0]['q']+'\n');compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'query'],out/'compile',120);run=guarded([out/'query',out/'selected.txt',out/'witness.csv'],out/'process',120) if compile['exit_code']==0 else None;r=dict(status='FAIL',scope='fresh independent selected lower-load force/spectrum query ONLY;NOT failed-horizon completion/actual SOFA/contact/stability/dynamic arrival',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_horizon_status='FAIL remains;full .0001N load NOT certified',source_summary_sha256=sha(src/'summary.json'),source_branch_csv_sha256=sha(src/'equilibrium.states.csv'),selected_load_N=.00009375,compile=compile,process=run,source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},physical_change='none;standalone re-evaluation of an uncommitted partial branch,not a SOFA state commit')
 if run and run['exit_code']==0:
  values={k:float(v) for k,v in next(csv.DictReader((out/'witness.csv').open())).items()};r.update(status='EXPERIMENTAL',new_force_query_gate='PASS' if values['force_residual_N']<=1e-12 else 'FAIL',force_gate_N=1e-12,metrics=values,shape=shape(np.fromstring(selected[0]['q'],sep=' ')),stability='computed tangent spectrum only;nonlinear stability NOT certified',virtual_overlay='NOT actual object contact;negative gap invalidates using this free static state as a contact solution',binary_sha256=sha(out/'query'),raw_hashes={n:sha(out/n) for n in ('selected.txt','witness.csv')})
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process')}))
if __name__=='__main__':main()
