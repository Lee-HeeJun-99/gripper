"""Actual-state energy-defect decomposition,not an energy-balancing force."""
import argparse,csv,json,shutil,subprocess,math
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_routed_recovery_audit import checkpoint
def rows(path):return list(csv.DictReader(path.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);p.add_argument('--profile');a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);m=json.loads((src/'summary.json').read_text());provider=ROOT/'results/autonomous_film_20261118_routed_aligned_base1405';proof=json.loads((provider/'summary.json').read_text())
 if m['status']!='PASS' or m['source_hashes']!=proof['source_hashes'] or not m['accumulated_common_clock_exact']:raise ValueError('completed same-model exact-clock actual FREE study required')
 for f,d in m['raw_hashes'].items():
  if sha(src/f)!=d:raise ValueError('actual state changed')
 for f,d in proof['source_hashes'].items():
  if sha(provider/'sources'/f)!=d:raise ValueError('compiled model source changed')
 forecast=120.
 if a.profile:
  previous=ROOT/'results'/('autonomous_film_'+a.profile);cost=json.loads((previous/'summary.json').read_text())
  if cost['status']!='EXPERIMENTAL' or cost['model_source_hashes']!=proof['source_hashes']:raise ValueError('same completed observer profile required')
  forecast=2*cost['process']['runtime_s']*m['steps']/cost['steps']+30
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(provider/'sources/models',archive/'models');cpp=archive/'diagnostics/film_three_finger/FreeEnergyDefect.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/FreeEnergyDefect.cpp',cpp);t,q0,v0,quat,D,maps=checkpoint(src/'input.checkpoint');(out/'mass.txt').write_text(str(len(D))+'\n'+' '.join(format(x,'.17g') for x in D)+'\n');accepted=rows(src/'three.states.csv');stages=rows(src/'three.free.stages.csv');fields=[rows(src/f'film_{f}.csv') for f in range(3)];initial=ROOT/'results/autonomous_film_20261118_routed_recovery_window1393';U0=math.fsum(float(rows(initial/f'film_{f}.csv')[-1][k]) for f in range(3) for k in ('U_shell','U_attachment'));lines=[str(len(accepted))]
 for n in (4,8):
  x,w=np.polynomial.legendre.leggauss(n);lines.append(str(n));lines.extend(format((xx+1)/2,'.17g')+' '+format(ww/2,'.17g') for xx,ww in zip(x,w))
 for i,row in enumerate(accepted):
  q=np.fromstring(row['q'],sep=' ');v=np.fromstring(row['v'],sep=' ');U1=math.fsum(float(fields[f][i][k]) for f in range(3) for k in ('U_shell','U_attachment'));h=float(stages[3*i+1]['weight_s']);lines.append(format(h,'.17g')+' '+format(U0,'.17g')+' '+format(U1,'.17g'));lines.extend(' '.join(format(x,'.17g') for x in a) for a in (q0,v0,q,v));q0,v0,U0=q,v,U1
 (out/'steps.txt').write_text('\n'.join(lines)+'\n');r=dict(status='BLOCKED',scope='independent actual-state force/potential/momentum energy-defect decomposition ONLY;NOT full energy/time/grasp qualification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),actual_summary_sha256=sha(src/'summary.json'),model_source_hashes=proof['source_hashes'],source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},steps=len(accepted),predicted_child_runtime_s=forecast,root_reaction_work=None,physical_law_changed=False,heat='NOT assigned',whole_energy='BLOCKED',quadrature='4/8 Gauss points along saved configuration chord for DIAGNOSTIC conservative work,not physical time substeps',kinetic='stable long-double mass*(v1-v0)*(v1+v0)/2,not difference of two large kinetic energies')
 if forecast>480:r['failure_reason']='measured observer policy forecast>480s;NOT OS exhaustion';write_json(out/'summary.json',r);return
 compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'query'],out/'compile',120);run=guarded([out/'query',out/'mass.txt',out/'steps.txt',out/'decomposition.csv'],out/'process',480) if compile['exit_code']==0 else None;r.update(status='FAIL',compile=compile,process=run)
 if run and run['exit_code']==0:
  values=rows(out/'decomposition.csv');keys=[k for k in values[0] if k.endswith('_Nmm')];r.update(status='EXPERIMENTAL' if len(values)==len(accepted) else 'FAIL',cumulative={k:math.fsum(float(x[k]) for x in values) for k in keys},maximum_absolute={k:max(abs(float(x[k])) for x in values) for k in keys},maximum_replayed_momentum_residual_Ns=max(float(x['momentum_norm_Ns']) for x in values),binary_sha256=sha(out/'query'),raw_hashes={n:sha(out/n) for n in ('mass.txt','steps.txt','decomposition.csv')})
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','model_source_hashes','compile','process')}))
if __name__=='__main__':main()
