"""Compare actual public API masses with independent model reconstruction."""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);meta=json.loads((src/'identity.json').read_text())
 if json.loads((src/'summary.json').read_text())['status']!='PASS' or not meta.get('mass_journal'):raise ValueError('completed public API mass journal required')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(src/'sources/models',archive/'models');cpp=archive/'diagnostics/film_three_finger/MassIdentity.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/MassIdentity.cpp',cpp);shutil.copy2(src/'public_mass.txt',out/'mass.txt');binary=out/'reference'
 compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120);run=guarded([binary,out/'mass.txt'],out/'run',120) if compile['exit_code']==0 else None
 result=dict(status='PASS' if run and run['exit_code']==0 else 'FAIL',scope='diagnostic completed,NOT mass equality or physical-performance PASS',case=a.case,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},mass_sha256=sha(src/'public_mass.txt'),compile=compile,run=run)
 if run:result['reference_output']=(out/'run/stdout.log').read_text();result['binary_sha256']=sha(binary)
 write_json(out/'summary.json',result);print(json.dumps({k:result[k] for k in ('status','scope','reference_output') if k in result}))
if __name__=='__main__':main()
