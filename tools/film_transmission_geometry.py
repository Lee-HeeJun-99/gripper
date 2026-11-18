"""Fixed original-layout sphere overlay ONLY; no collision forces/integration."""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'results/autonomous_film_20261118_transmission_static_hybrid1165';meta=json.loads((src/'summary.json').read_text())
 if meta['status']!='PASS':raise ValueError('complete independent static equilibria required')
 for file,digest in meta['raw_hashes'].items():
  if sha(src/file)!=digest:raise ValueError('static raw changed')
 rows=list(csv.DictReader((src/'equilibrium.states.csv').open()));out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(src/'sources/models',archive/'models');cpp=archive/'diagnostics/film_three_finger/TransmissionGeometry.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/TransmissionGeometry.cpp',cpp);binary=out/'geometry';compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120)
 (out/'samples.txt').write_text(str(len(rows))+'\n'+'\n'.join(r['T']+' '+r['q'] for r in rows)+'\n');run=guarded([binary,out/'samples.txt',out/'geometry.csv'],out/'process',480) if compile['exit_code']==0 else None
 result=dict(status='FAIL',scope='independent no-object static shapes overlaid with original fixed R30 sphere;NOT actual contact/wrapping simulation',parent_summary_sha256=sha(src/'summary.json'),compile=compile,process=run,binary_sha256=sha(binary) if binary.exists() else None,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},contact_force=None,contact_area=None,pressure=None)
 if run and run['exit_code']==0:
  values=list(csv.DictReader((out/'geometry.csv').open()));result.update(status='PASS' if len(values)==len(rows) else 'FAIL',endpoint=values[-1],unconstrained_static_shape_feasible_with_fixed_object=all(float(v['minimum_buffer_gap_mm'])>=-1e-10 for v in values),interpretation='Negative overlay gap is not an actual contact-solver failure:obstacle was absent from static equations. Constrained static/dynamic solution is required.')
 result['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.csv','.txt')};write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('sources','compile','process','raw_hashes')}))
if __name__=='__main__':main()
