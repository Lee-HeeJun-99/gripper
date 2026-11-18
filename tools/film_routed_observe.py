"""Read-only physical stage work from ACTUAL new-route states,not old cable."""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);m=json.loads((src/'summary.json').read_text())
 if m['status']!='PASS':raise ValueError('completed actual routed states required')
 for f,d in m['raw_hashes'].items():
  if sha(src/f)!=d:raise ValueError('actual raw changed')
 provider=ROOT/'results/autonomous_film_20261118_routed_math_api1240'
 if sha(provider/'summary.json')!=m['source_provider_summary_sha256']:raise ValueError('routed physical provider differs')
 proof=json.loads((provider/'summary.json').read_text())
 for f,d in proof['source_hashes'].items():
  if sha(provider/'sources'/f)!=d:raise ValueError('routed physical source archive changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copytree(provider/'sources/models',out/'sources/models');cpp=out/'sources/diagnostics/film_three_finger/RoutedObserve.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/RoutedObserve.cpp',cpp);rows=list(csv.DictReader((src/'actual.csv.stages.csv').open()))
 with (out/'samples.txt').open('w') as f:
  f.write(str(len(rows))+'\n')
  for r in rows:f.write(' '.join(r[k] for k in ('time','weight','T','q','v'))+'\n')
 compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'observer'],out/'compile',120);run=guarded([out/'observer',src/'public_mass.txt',out/'samples.txt',str(m['amplitude_mm']),out/'stage_work.csv'],out/'process',480) if compile['exit_code']==0 else None;r=dict(status='FAIL',scope='read-only actual routed stage work/force norms;NOT whole energy/contact/holding',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_summary_sha256=sha(src/'summary.json'),source_hashes={str(f.relative_to(out/'sources')):sha(f) for f in (out/'sources').rglob('*') if f.is_file()},compile=compile,process=run,root_work=None,actuator_electrical_work=None)
 if run and run['exit_code']==0:
  w=list(csv.DictReader((out/'stage_work.csv').open()));endpoint=list(csv.DictReader((src/'film_0.csv').open()))[-1];W=float(w[-1]['tendon_work_Nmm']);D=float(w[-1]['damping_work_Nmm']);E=sum(float(endpoint[k]) for k in ('U_shell','U_attachment','K'));r.update(status='PASS',tendon_work_Nmm=W,damping_work_Nmm=D,stored_plus_K_Nmm=E,signed_energy_defect_Nmm=W-D-E,defect_is_heat=False,binary_sha256=sha(out/'observer'),raw_hashes={'stage_work.csv':sha(out/'stage_work.csv')})
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process')}))
if __name__=='__main__':main()
