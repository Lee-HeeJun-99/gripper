"""Read-only ACTUAL face-release stage work and endpoint energy inventory."""
import argparse,csv,json,math,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'results/autonomous_film_20261119_stationary_release_actual1587';m=json.loads((src/'summary.json').read_text());ref=ROOT/'results/autonomous_film_20261119_stationary_window10_64_1582'
 if m['status']!='PASS' or not m['all_RK_times_weights_masks_exact'] or m['RK_stage_max_abs']!=0:raise ValueError('qualified actual release stages required')
 for f,d in m['source_hashes'].items():
  if sha(src/'sources'/f)!=d:raise ValueError('actual model archive changed')
 for f,d in m['raw_hashes'].items():
  if sha(src/f)!=d:raise ValueError('actual release raw changed')
 if sha(ref/'summary.json')!=m['reference_summary_sha256']:raise ValueError('release reference provenance changed')
 tokens=(src/'input.checkpoint').read_text().split();n=1953;q0=np.array(tokens[5:5+n],float);v0=np.array(tokens[5+n:5+2*n],float);start=float(tokens[1]);states=list(csv.DictReader((src/'three.states.csv').open()));end=float(states[-1]['time']);samples=[('E',start,0,np.zeros(3),q0,v0)];pre=list(csv.DictReader((src/'three.release.pre.csv').open()))
 for i in range(0,len(pre),3):
  group=pre[i:i+3];row=group[0]
  if [int(x['finger']) for x in group]!=[0,1,2] or any(any(x[k]!=row[k] for k in ('time','weight_s','q','v')) for x in group):raise ValueError('shared actual pre-stage identity differs')
  samples.append(('S',float(row['time']),float(row['weight_s']),np.array([float(x['force']) for x in group]),np.fromstring(row['q'],sep=' '),np.fromstring(row['v'],sep=' ')))
 for row in csv.DictReader((src/'three.release.rk.csv').open()):
  force=np.fromstring(row['force'],sep=' ')
  if int(row['mask'])==0 and np.any(force!=0):raise ValueError('free RK stage has nonzero reaction')
  samples.append(('S',float(row['time']),float(row['weight_s']),force,np.fromstring(row['q'],sep=' '),np.fromstring(row['v'],sep=' ')))
 for row in csv.DictReader((src/'three.release.free.csv').open()):
  if float(row['weight_s'])>0:samples.append(('S',float(row['time']),float(row['weight_s']),np.zeros(3),np.fromstring(row['q'],sep=' '),np.fromstring(row['v'],sep=' ')))
 samples.append(('E',end,0,np.zeros(3),np.fromstring(states[-1]['q'],sep=' '),np.fromstring(states[-1]['v'],sep=' ')))
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(src/'sources/models',archive/'models');diag=archive/'diagnostics/film_three_finger';diag.mkdir(parents=True);shutil.copy2(ref/'sources/diagnostics/film_three_finger/RoutedCheckpoint.h',diag/'RoutedCheckpoint.h');cpp=diag/'StationaryReleasePower.cpp';shutil.copy2(ROOT/'diagnostics/film_three_finger/StationaryReleasePower.cpp',cpp);shutil.copy2(src/'input.checkpoint',out/'input.checkpoint');(out/'samples.txt').write_text(str(len(samples))+'\n'+'\n'.join(f'{kind} {t:.17g} {w:.17g} '+' '.join(format(x,'.17g') for z in (force,q,v) for x in z) for kind,t,w,force,q,v in samples)+'\n');compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'observer'],out/'compile',120);run=guarded([out/'observer',out/'input.checkpoint',out/'samples.txt',out/'power.csv'],out/'process',480) if compile['exit_code']==0 else None
 r=dict(status='FAIL',scope='actual face-release partial stage-work/endpoint inventory ONLY;NOT whole energy/time/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),actual_summary_sha256=sha(src/'summary.json'),source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},compile=compile,process=run,root_work=None,external_work_Nmm=0.,external_work_basis='actual Scene zero force/torque/gravity,source-bound zero-load system',impact_loss='no impulse in declared continuous release composition',heat='NOT assigned',work_origin='actual26.8ms IVP ONLY;prior cumulative work NOT spliced')
 if run and run['exit_code']==0:
  rows=list(csv.DictReader((out/'power.csv').open()));energies=[x for x in rows if x['kind']=='E'];stage=[x for x in rows if x['kind']=='S'];sums={key:math.fsum(float(x['weight'])*float(x[key]) for x in stage) for key in ('tendon_power','normal_power','damping_power')};U=lambda x:math.fsum(float(x[k]) for k in ('U_skin','U_rails','U_attachment'));K=lambda x:math.fsum(float(x[k]) for k in ('K_film','K_linear','K_rotation'));fields=[next(csv.DictReader((src/f'film_{f}.csv').open())) for f in range(3)];energy_error=max(abs(U(energies[-1])-math.fsum(float(f['U_shell'])+float(f['U_attachment']) for f in fields)),abs(float(energies[-1]['K_film'])-math.fsum(float(f['K']) for f in fields)));deltaU=U(energies[-1])-U(energies[0]);deltaK=K(energies[-1])-K(energies[0]);r.update(status='PASS' if len(rows)==len(samples) and len(energies)==2 and energy_error<=1e-12 else 'FAIL',actual_stored_K_field_max_abs_Nmm=energy_error,stage_count=len(stage),actual_weight_sum_s=math.fsum(float(x['weight']) for x in stage),accumulated_duration_s=end-start,tendon_work_Nmm=sums['tendon_power'],normal_constraint_work_Nmm=sums['normal_power'],Rayleigh_loss_Nmm=sums['damping_power'],delta_stored_Nmm=deltaU,delta_K_Nmm=deltaK,signed_partial_defect_Nmm=deltaU+deltaK-sums['tendon_power']-sums['normal_power']+sums['damping_power'],whole_energy='BLOCKED;unmeasured root work and global gates',binary_sha256=sha(out/'observer'))
 r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.csv','.txt')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','raw_hashes','compile','process')}))
if __name__=='__main__':main()
