"""Independent work reconstruction from actual RK/free-stage journals."""
import argparse,csv,json,math,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);p.add_argument('--profile',action='store_true');p.add_argument('--reuse');a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);meta=json.loads((src/'summary.json').read_text())
 if meta['status']!='PASS' or meta['process']['exit_code'] or meta['sofa_errors']:raise ValueError('complete actual release required')
 for name,digest in meta['raw_hashes'].items():
  if sha(src/name)!=digest:raise ValueError('actual raw changed')
 rk=list(csv.DictReader((src/'three.release.stages.csv').open()));free=list(csv.DictReader((src/'three.release.free.csv').open()));records=[dict(name='r'+str(i),time=r['time'],weight_s=r['weight_s'],q=r['q'],v=r['v'],force=r['force']) for i,r in enumerate(rk)]+[dict(name='f'+str(i),time=r['time'],weight_s=r['weight_s'],q=r['q'],v=r['v'],force='0 0 0') for i,r in enumerate(free)]
 if a.profile:records=[records[0],records[-1]]
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));cpp=archive/'diagnostics/film_three_finger/ReleasePower.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/ReleasePower.cpp',cpp)
 for name,digest in meta['sources'].items():
  if name.endswith('.h') and sha(ROOT/name)!=digest:raise ValueError('actual/provider physics header differs:'+name)
 binary=out/'reference';forecast=None
 if a.reuse:
  prev=ROOT/'results'/('autonomous_film_'+a.reuse);proof=json.loads((prev/'summary.json').read_text())
  if proof['status']!='PASS' or not proof['profile'] or sha(prev/'reference')!=proof['binary_sha256']:raise ValueError('qualified provider profile required')
  for name,digest in proof['sources'].items():
   if sha(archive/name)!=digest:raise ValueError('provider compiled source changed:'+name)
  forecast=2*proof['run']['runtime_s']*len(records)/proof['sample_count']+30
  if forecast>480:raise ValueError('observer forecast exceeds480s')
  shutil.copy2(prev/'reference',binary);compile={'exit_code':0,'reused_from':a.reuse,'source_closure_exact':True}
 else:compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120)
 tokens=(src/'input.checkpoint').read_text().split();edge_indices=[i for i,t in enumerate(tokens) if t=='EDGE'];edges=' '.join(tokens[i+3]+' '+tokens[i+4] for i in edge_indices)
 if len(edge_indices)!=3:raise ValueError('three actual material-edge owners required')
 (out/'samples.txt').write_text(edges+'\n'+str(len(records))+'\n'+'\n'.join(r['name']+' '+r['time']+' '+r['q']+' '+r['v']+' '+r['force'] for r in records)+'\n');mass=ROOT/'results/autonomous_film_20261118_three_film_first_peak_actual1002/public_mass_reference.txt';shutil.copy2(mass,out/'mass.txt');run=guarded([binary,out/'mass.txt',out/'samples.txt',out/'observed.csv'],out/'run',480 if a.reuse else 120) if compile['exit_code']==0 else None;result=dict(status='FAIL',scope='independent reconstruction from actual stage data;NOT whole physical energy/time certificate',case=a.case,parent_summary_sha256=sha(src/'summary.json'),actual_binary_sha256=meta['binary_sha256'],profile=a.profile,sample_count=len(records),predicted_runtime_s=forecast,compile=compile,run=run,sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),root_reaction_work=None,legacy_sampled_work='NOT restored/not used')
 if binary.exists():result['binary_sha256']=sha(binary)
 if run and run['exit_code']==0:
  obs={r['sample']:{k:float(v) for k,v in r.items() if k!='sample'} for r in csv.DictReader((out/'observed.csv').open())};end=obs[records[-1]['name']];fields=[list(csv.DictReader((src/f'film_{f}.csv').open()))[-1] for f in range(3)];error=max(abs(sum(float(f['U_shell']) for f in fields)-end['U_skin']-end['U_rails']),abs(sum(float(f['U_attachment']) for f in fields)-end['U_attachment']),abs(sum(float(f['K']) for f in fields)-end['K_film']));tension_error=max(abs(float(f['T_per_rail'])-end['profile_tension']) for f in fields);result.update(status='PASS' if error<1e-12 and tension_error==0 else 'FAIL',actual_field_energy_error_Nmm=error,actual_endpoint_tension_error_N=tension_error)
  if not a.profile:
   E=lambda r:sum(r[k] for k in ('U_skin','U_rails','U_attachment','K_film','K_linear','K_rotation'));wt=we=wd=wn=0
   for r in records:
    o=obs[r['name']];w=float(r['weight_s']);velocity=np.fromstring(r['v'],sep=' ');wt+=w*o['profile_tension']*o['unit_tendon_power'];we+=w*(-.001)*velocity[-4];wd+=w*4*sum(o[k] for k in ('K_film','K_linear','K_rotation'));wn+=w*o['normal_power_Nmm_s']
   change=E(end)-E(obs[records[0]['name']]);result.update(tendon_mechanical_work_Nmm=wt,tendon_sign='positive pull coordinate=-routed cable length;power=-T*dL/dt',external_work_Nmm=we,damping_work_Nmm=wd,normal_work_independent_reconstruction_Nmm=wn,stored_kinetic_change_Nmm=change,signed_inventory_defect_Nmm=change-wt-we+wd-wn,defect_interpretation='signed quadrature/integration/roundoff/unmeasured-root defect,NOT heat',instantaneous_impact_loss='not applicable:no velocity jump/impulse applied in this release interval',total_quadrature_duration_s=math.fsum(float(r['weight_s']) for r in records),whole_energy_certification='BLOCKED:root work unmeasured/full convergence missing')
 result['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.is_file() and f.suffix in ('.txt','.csv')};write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('sources','compile','run','raw_hashes')}))
if __name__=='__main__':main()
