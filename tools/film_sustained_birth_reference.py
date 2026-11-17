"""Bounded independent counterexample; not a new SOFA impact implementation."""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--persistent-work',action='store_true');a=p.parse_args()
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False)
 test='test_persistent_contact_work.cpp' if a.persistent_work else 'test_sustained_birth_phase.cpp'
 shutil.copy2(__file__,out/'runner.py');sources=[s for directory in ('film_impact','film_shell','film_rail_tendon','film_sphere_contact') for s in (ROOT/'models'/directory).glob('*.h')]+[ROOT/'tests'/test]
 for source in sources:
  target=out/'sources'/source.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
 write_json(out/'identity.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(s.relative_to(ROOT)):sha(s) for s in sources}))
 binary=out/'reference';compile=guarded(['g++','-O2','-std=c++17','-I/usr/include/eigen3',out/'sources/tests'/test,'-o',binary],out/'compile',120)
 result=dict(status='FAIL',compile=compile,scope='independent analytic counterexample;NOT actual SOFA correction')
 if compile['exit_code']==0:
  run=guarded([binary],out/'run',30);result.update(status='PASS' if run['exit_code']==0 else 'FAIL',run=run,binary_sha256=sha(binary),counterexample='persistent normal-work quadrature' if a.persistent_work else 'newborn impact velocity')
 write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
