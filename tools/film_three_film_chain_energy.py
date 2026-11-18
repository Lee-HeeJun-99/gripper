"""Independent energy observer over ACTUAL same-clock FREE recovery stages."""
import argparse,csv,json,math,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();names=['20261118_three_film_extended_actual1124']+[f'20261118_three_film_recovery_chain1127_plan{i}' for i in range(1,8)];records=[];hashes={}
 for name in names:
  src=ROOT/'results'/('autonomous_film_'+name);meta=json.loads((src/'summary.json').read_text())
  if meta['status']!='EXPERIMENTAL' or meta['process']['exit_code']:raise ValueError('complete actual FREE plan required')
  for f,digest in meta['raw_hashes'].items():
   if sha(src/f)!=digest:raise ValueError('actual raw changed')
  endpoint=max(src.glob('three.checkpoint_*.txt'),key=lambda f:int(f.stem.split('_')[-1])).read_text().split()
  if endpoint[0]!='REGRIP_PERSISTENT_OBSERVATION_V5' or endpoint[endpoint.index('FREE_ACTIVE_COUNT')+1]!='0':raise ValueError('explicit empty actual contact set required')
  hashes[name]=sha(src/'summary.json');records+=list(csv.DictReader((src/'three.free.stages.csv').open()))
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');old=json.loads((ROOT/'results/autonomous_film_20261118_three_film_release_inventory1096/summary.json').read_text());forecast=2*old['run']['runtime_s']*len(records)/old['sample_count']+30
 if forecast>480:write_json(out/'summary.json',dict(status='BLOCKED',scope='observer forecast only,NOT OS exhaustion',physics_launched=False,predicted_runtime_s=forecast));return
 archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));cpp=archive/'diagnostics/film_three_finger/ReleasePower.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/ReleasePower.cpp',cpp);binary=out/'reference';compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120)
 mass=ROOT/'results/autonomous_film_20261118_three_film_first_peak_actual1002/public_mass_reference.txt';shutil.copy2(mass,out/'mass.txt');(out/'samples.txt').write_text('77 73 77 73 77 73\n'+str(len(records))+'\n'+'\n'.join('s'+str(i)+' '+r['time']+' '+r['q']+' '+r['v']+' 0 0 0' for i,r in enumerate(records))+'\n')
 run=guarded([binary,out/'mass.txt',out/'samples.txt',out/'observed.csv'],out/'process',480) if compile['exit_code']==0 else None
 result=dict(status='FAIL',scope='actual31.6..38ms FREE recovery stage energy inventory;NOT full gripper energy certification',actual_summary_hashes=hashes,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),predicted_runtime_s=forecast,compile=compile,process=run,sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},root_reaction_work=None,legacy_sampled_work='NOT restored/not used',active_normal_work='analytically absent:actual FREE_ACTIVE_COUNT0,no impact/reimpact',binary_sha256=sha(binary) if binary.exists() else None)
 if run and run['exit_code']==0:
  obs=list(csv.DictReader((out/'observed.csv').open()));energies=[{k:float(v) for k,v in row.items() if k!='sample'} for row in obs];last=energies[-1];fields=[list(csv.DictReader((src/f'film_{f}.csv').open()))[-1] for f in range(3)];error=max(abs(sum(float(f['U_shell']) for f in fields)-last['U_skin']-last['U_rails']),abs(sum(float(f['U_attachment']) for f in fields)-last['U_attachment']),abs(sum(float(f['K']) for f in fields)-last['K_film']));E=lambda e:sum(e[k] for k in ('U_skin','U_rails','U_attachment','K_film','K_linear','K_rotation'));wt=we=wd=0
  if len(records)!=192 or len(obs)!=192:raise ValueError('complete64-step192-stage journal required')
  for row,e in zip(records,energies):
   w=float(row['weight_s']);v=np.fromstring(row['v'],sep=' ');wt+=w*e['profile_tension']*e['unit_tendon_power'];we+=w*(-.001)*v[-4];wd+=w*4*sum(e[k] for k in ('K_film','K_linear','K_rotation'))
  duration=math.fsum(float(r['weight_s']) for r in records);elapsed=float(records[-1]['time'])-float(records[0]['time']);change=E(last)-E(energies[0]);result.update(status='PASS' if error<1e-12 and duration==elapsed and all(e['profile_tension']==0 for e in energies) else 'FAIL',actual_field_energy_error_Nmm=error,total_quadrature_duration_s=duration,actual_elapsed_s=elapsed,stage_duration_exact=duration==elapsed,tendon_mechanical_work_Nmm=wt,external_work_Nmm=we,damping_work_Nmm=wd,stored_kinetic_change_Nmm=change,signed_inventory_defect_Nmm=change-wt-we+wd,defect_interpretation='signed quadrature/integration/roundoff/unmeasured-root defect,NOT heat',whole_energy='BLOCKED:unmeasured root work,full time/mesh/contact gates remain')
 result['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.is_file() and f.suffix in ('.txt','.csv')};write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('sources','compile','process','raw_hashes','actual_summary_hashes')}))
if __name__=='__main__':main()
