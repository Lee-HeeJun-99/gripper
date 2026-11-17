"""Explicit +1mN pull-away condition;not tuning force to repair a contact gate."""
import argparse,csv,json,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'results/autonomous_film_20261118_three_film_event_sustained966';meta=json.loads((src/'summary.json').read_text());rows=list(csv.DictReader((src/'three.states.csv').open()))
 if meta['status']!='PASS' or len(rows)!=8 or sha(src/'three.states.csv')!=meta['raw_hashes']['three.states.csv']:raise ValueError('complete immutable actual state required')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));cpp=archive/'diagnostics/film_three_finger/ReleaseFromState.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/ReleaseFromState.cpp',cpp);shutil.copy2(src/'public_mass_reference.txt',out/'mass.txt');last=rows[-1];(out/'initial.txt').write_text(str(len(np.fromstring(last['q'],sep=' ')))+'\n'+last['q']+'\n'+last['v']+'\n');binary=out/'reference';compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120);run=guarded([binary,out/'mass.txt',out/'initial.txt',out/'reaction.csv'],out/'run',120) if compile['exit_code']==0 else None
 result=dict(status='PASS' if run and run['exit_code']==0 else 'FAIL',scope='independent deformed ALL-row release test from saved actual1.6ms state;NOT actual release/full cycle/grasp',changed_physical_input='external Fz changes -.001N to+.001N at1.6ms;all material/damping/C2 unchanged;not numerical repair',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},actual_state_sha256=sha(src/'three.states.csv'),compile=compile,run=run,branch_note='all-row release rejects compressive/partial active sets;failure does NOT authorize zeroing velocity or reaction')
 if binary.exists():result['binary_sha256']=sha(binary)
 if (out/'reaction.csv').exists():result['reaction']=[{k:float(v) for k,v in r.items()} for r in csv.DictReader((out/'reaction.csv').open())]
 if run:result['failure_reason']=(out/'run/stderr.log').read_text().strip() or None
 write_json(out/'summary.json',result);print(json.dumps({k:result[k] for k in ('status','reaction','failure_reason','scope') if k in result}))
if __name__=='__main__':main()
