"""Isolated energy-only reuse;normal force/Hessian code is not changed."""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);build=ROOT/'build'/('value_energy_'+a.tag);build.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py')
    shutil.copytree(ROOT/'models/film_value_energy',out/'sources/models/film_value_energy')
    for d in ('film_shell','film_rail_tendon'):
        target=out/'sources/models'/d;target.mkdir()
        for f in (ROOT/'models'/d).glob('*.h'):shutil.copy2(f,target/f.name)
    target=out/'sources/tests/test_film_value_energy.cpp';target.parent.mkdir();shutil.copy2(ROOT/'tests/test_film_value_energy.cpp',target)
    write_json(out/'identity.json',dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(f.relative_to(out/'sources')):sha(f) for f in (out/'sources').rglob('*') if f.is_file()},scope='independent value-only energies;NOT replacement of force/Jacobian'))
    stages={};stages['configure']=guarded(['cmake','-S',out/'sources/models/film_value_energy','-B',build,'-DCMAKE_BUILD_TYPE=Release'],out/'configure',120);stages['value_build']=guarded(['cmake','--build',build,'-j','1'],out/'value_build',120) if stages['configure']['exit_code']==0 else dict(exit_code=-1);binary=build/'reference'
    if stages['value_build']['exit_code']==0:
        stages['compile']=guarded(['g++','-O2','-std=c++17','-ffp-contract=off',target,build/'libReGripFilmValue.a','-o',binary],out/'compile',120)
        if stages['compile']['exit_code']==0:stages['run']=guarded([binary],out/'run',60)
    write_json(out/'summary.json',dict(status='PASS' if stages.get('run',{}).get('exit_code')==0 else 'FAIL',stages=stages,scope='independent value-energy byte-equivalence and measured evaluation cost;NOT actual whole dynamics',generated_hashes={str(f.relative_to(build)):sha(f) for f in (build/'value_models').rglob('*') if f.is_file()},binary_sha256=sha(binary) if binary.exists() else None));print(json.dumps(dict(status='PASS' if stages.get('run',{}).get('exit_code')==0 else 'FAIL')))
if __name__=='__main__':main()
