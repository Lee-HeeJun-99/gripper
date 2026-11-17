"""Fresh independent coupled sphere kernel;immutable bounded artifacts."""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--reintegrated',action='store_true');a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);build=ROOT/'build'/('coupled_ref_'+a.tag);build.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');sources=[];test='test_coupled_reintegrated.cpp' if a.reintegrated else 'test_coupled_sphere.cpp'
    for directory in ('film_coupled_contact','film_impact','film_shell','film_rail_tendon','film_native_contact','film_sphere_contact'):sources+=list((ROOT/'models'/directory).glob('*.h'))
    sources+=[ROOT/'tests'/test]
    for s in sources:
        target=out/'sources'/s.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(s,target)
    write_json(out/'identity.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(s.relative_to(ROOT)):sha(s) for s in sources},scope='independent frictionless isotropic sphere coupled midpoint/event;NOT actual SOFA'))
    binary=build/'reference';compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',out/'sources/tests'/test,'-o',binary],out/'compile',120);result=dict(status='FAIL',compile=compile,scope='independent externally isolated coupled midpoint event bracket;NOT global earliest CCD/SOFA' if a.reintegrated else 'independent coupled kernel;NOT actual SOFA')
    if compile['exit_code']==0:
        run=guarded([binary],out/'run',60);result.update(status='PASS' if run['exit_code']==0 else 'FAIL',run=run,binary_sha256=sha(binary))
    write_json(out/'summary.json',result);print(json.dumps(dict(status=result['status'])))
if __name__=='__main__':main()
