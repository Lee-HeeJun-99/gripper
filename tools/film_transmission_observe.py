"""Read-only actual SOFA force-path/energy reconstruction;no dynamics changes."""
import argparse,csv,json,math,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_transmission_linear import shape
from film_compiled_sources import identical_compiled_sources
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);p.add_argument('--reuse');a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);proof=json.loads((src/'summary.json').read_text())
 if proof['status']!='PASS' or proof['process']['exit_code']:raise ValueError('complete actual single coupon required')
 if proof.get('scheme','midpoint')!='midpoint':raise ValueError('midpoint work observer must not be used for Gauss stage work')
 for name,digest in proof['raw_hashes'].items():
  if sha(src/name)!=digest:raise ValueError('actual raw changed')
 rows=list(csv.DictReader((src/'actual.csv').open()));out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));cpp=archive/'diagnostics/film_three_finger/TransmissionObserve.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/TransmissionObserve.cpp',cpp);sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};binary=out/'observer';forecast=None
 if a.reuse:
  prev=ROOT/'results'/('autonomous_film_'+a.reuse);old=json.loads((prev/'summary.json').read_text())
  if old['status']!='PASS' or not identical_compiled_sources(old['sources'],sources) or sha(prev/'observer')!=old['binary_sha256']:raise ValueError('same exact observer code/build/input/profile required')
  forecast=2*old['process']['runtime_s']*len(rows)/old['samples']+30
  if forecast>480:raise ValueError('profiled observer exceeds480s')
  shutil.copy2(prev/'observer',binary);compile={'exit_code':0,'reused_from':a.reuse}
 else:compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120)
 (out/'samples.txt').write_text(str(len(rows))+'\n'+'\n'.join(r['time']+' '+r['dt']+' '+r['T_mid']+' '+r['T_end']+' '+r['q']+' '+r['v'] for r in rows)+'\n');run=guarded([binary,str(proof['bond_stiffness_N_mm']),str(proof['guide_offset_mm']),src/'public_mass.txt',out/'samples.txt',out/'observed.csv'],out/'process',480) if compile['exit_code']==0 else None;result=dict(status='FAIL',scope='actual single-film transmission force-path and stage-work inventory;NOT full energy/grasp',case=a.case,parent_summary_sha256=sha(src/'summary.json'),actual_binary_sha256=proof['binary_sha256'],source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources=sources,compile=compile,process=run,samples=len(rows),predicted_runtime_s=forecast,binary_sha256=sha(binary) if binary.exists() else None,root_reaction_work=None,contact_force=None,contact_area=None,pressure=None)
 if run and run['exit_code']==0:
  obs=list(csv.DictReader((out/'observed.csv').open()));fields=list(csv.DictReader((src/'film_0.csv').open()));error=max(max(abs(float(f['U_shell'])-float(o['U_skin'])-float(o['U_rails'])),abs(float(f['U_attachment'])-float(o['U_attachment'])),abs(float(f['K'])-float(o['K']))) for f,o in zip(fields,obs));endpoint={k:float(v) for k,v in obs[-1].items()};change=sum(endpoint[k] for k in ('U_skin','U_rails','U_attachment','K'));duration=math.fsum(float(r['dt']) for r in rows);result.update(status='PASS' if len(obs)==len(rows) and error<1e-12 else 'FAIL',actual_field_energy_error_Nmm=error,endpoint=endpoint,endpoint_shape=shape(np.fromstring(rows[-1]['q'],sep=' ')),stage_weight_duration_s=duration,actual_elapsed_s=float(rows[-1]['time']),signed_energy_defect_Nmm=change-endpoint['midpoint_tendon_work_Nmm']+endpoint['midpoint_damping_work_Nmm'],defect='signed discretization/quadrature/unmeasured-root inventory,NOT heat;whole energy BLOCKED')
 result['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.is_file() and f.suffix in ('.txt','.csv')};write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('sources','compile','process','raw_hashes','endpoint_shape')}))
if __name__=='__main__':main()
