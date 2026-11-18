"""Qualify factored isolated kernel before any actual SOFA adapter run."""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--reference',required=True);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.reference);meta=json.loads((src/'summary.json').read_text())
 if meta['status']!='PASS' or sha(src/'transfer.states.txt')!=meta['raw_hashes']['transfer.states.txt']:raise ValueError('immutable independent complete transfer reference required')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));cpp=archive/'diagnostics/film_three_finger/ContactTransferKernel.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/ContactTransferKernel.cpp',cpp);binary=out/'reference';compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120);run=guarded([binary,src/'input.checkpoint',src/'transfer.states.txt',out/'metrics.csv'],out/'run',180) if compile['exit_code']==0 else None;result=dict(status='PASS' if run and run['exit_code']==0 else 'FAIL',scope='independent factored transfer equivalence,owned3 equality/6-row directional derivatives/world momentum;NOT SOFA or global contact certification',reference=a.reference,reference_summary_sha256=sha(src/'summary.json'),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},compile=compile,run=run)
 if binary.exists():result['binary_sha256']=sha(binary)
 if (out/'metrics.csv').exists():result['metrics']=next(csv.DictReader((out/'metrics.csv').open()))
 if run:result['failure_reason']=(out/'run/stderr.log').read_text().strip() or None
 write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('sources','compile','run')}))
if __name__=='__main__':main()
