"""Independent nonlinear implicit reference; do not label these as SOFA data."""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
 if not a.tag.replace('_','').isalnum():raise ValueError('tag')
 out=ROOT/'results'/('autonomous_film_reference_'+a.tag);out.mkdir(exist_ok=False);sources=list((ROOT/'models/film_shell').glob('*.h'))+[ROOT/'diagnostics/film_shell/ImplicitReference.cpp',ROOT/'tools/film_implicit_reference.py']
 write_json(out/'identity.json',dict(source='Independent full-Newton backward Euler,not SOFA',commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(p.relative_to(ROOT)):sha(p)for p in sources}))
 for p in sources:
  q=out/'sources'/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
 binary=out/'reference';build=logged(['g++','-O2','-std=c++17','-I/usr/include/eigen3',ROOT/'diagnostics/film_shell/ImplicitReference.cpp','-o',binary],out/'build',180)
 if build['exit_code']:write_json(out/'summary.json',dict(status='FAIL',stage='build'));return
 cases={}
 for steps in (100,200,400):
  run=logged([binary,str(steps)],out/str(steps),480);case=dict(process=run)
  if run['exit_code']==0:
   rows=list(csv.DictReader((out/str(steps)/'stdout.log').open()));case.update(last=rows[-1]if rows else None,records=len(rows),status='PASS'if len(rows)==steps else'FAIL')
  else:case['status']='FAIL'
  cases[steps]=case
 write_json(out/'summary.json',dict(source='Independent numerical film dynamics,NOT actual SOFA',binary_sha256=sha(binary),cases=cases,status='PASS'if all(v['status']=='PASS'for v in cases.values())else'FAIL'));print(json.dumps(cases))
if __name__=='__main__':main()
