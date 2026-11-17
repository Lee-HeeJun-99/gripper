"""Bounded independent event-to-first-C2-peak continuation;stop on branch failure."""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--clock',choices=('accumulated','multiplied'),default='accumulated');a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));(archive/'tests').mkdir();shutil.copy2(ROOT/'tests/test_three_film_birth.cpp',archive/'tests/test_three_film_birth.cpp');actual=ROOT/'results/autonomous_film_20261118_three_film_event_rows964';shutil.copy2(actual/'public_mass_reference.txt',out/'mass.txt');profile=ROOT/'results/autonomous_film_20261118_three_film_post7_975';pm=json.loads((profile/'summary.json').read_text());estimate=2*pm['run']['runtime_s']*49/7+30
 if pm['status']!='PASS' or estimate>480:raise ValueError('measured persistent per-step forecast exceeds480s policy')
 binary=out/'reference';compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',archive/'tests/test_three_film_birth.cpp','-o',binary],out/'compile',120);run=guarded([binary,out/'mass.txt',out/'reference.csv','50']+(['accumulated'] if a.clock=='accumulated' else []),out/'run',480) if compile['exit_code']==0 else None;rows=list(csv.DictReader((out/'reference.csv.states.csv').open())) if (out/'reference.csv.states.csv').exists() else []
 result=dict(status='PASS' if run and run['exit_code']==0 and len(rows)==50 else 'FAIL',scope='independent nonlinear three-film shared event to FIRST C2 peak10ms;NOT actual SOFA/fulltime/energy/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},steps=50,dt=.0002,duration=.01,maximum_tension_N=.0001,control='existing C2 ramp.01s release.02-.03s;NO input change',predicted_runtime_s=estimate,profile_summary_sha256=sha(profile/'summary.json'),compile=compile,run=run,completed_rows=len(rows),last_completed_time=float(rows[-1]['time']) if rows else None,physical_gates_unchanged=True)
 if binary.exists():result['binary_sha256']=sha(binary)
 result['input_clock']=a.clock
 if run:result['failure_reason']=(out/'run/stderr.log').read_text().strip() or None
 if rows:result['minimum_gap_mm']=min(float(r['gap']) for r in rows);result['states_sha256']=sha(out/'reference.csv.states.csv')
 write_json(out/'summary.json',result);print(json.dumps({k:result[k] for k in ('status','completed_rows','last_completed_time','failure_reason','predicted_runtime_s','run') if k in result}))
if __name__=='__main__':main()
