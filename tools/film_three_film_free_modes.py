"""Actual shape projected onto an independent stress-free FREE-film spectrum."""
import argparse,json,os,shutil,subprocess,sys
from pathlib import Path
for ancestor in Path(__file__).resolve().parents:
 if (ancestor/'tools/curve_common.py').is_file():sys.path.insert(0,str(ancestor/'tools'));break
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def worker(directory):
 import numpy as np
 from scipy.linalg import eigh
 out=Path(directory)
 with (out/'film.matrix.txt').open() as stream:n=int(stream.readline());mass=np.fromstring(stream.readline(),sep=' ');K=np.loadtxt(stream)
 state=(out/'film.state.txt').read_text().splitlines();time=float(state[0]);q=np.fromstring(state[1],sep=' ').reshape(3,n);v=np.fromstring(state[2],sep=' ').reshape(3,n);current=(out/'current.flag').exists()
 if current:q=q[:1]*0;v=v[:1] # delta-q at the frozen current centre is zero,not a stored-energy estimate.
 scale=np.sqrt(mass);A=K/scale[:,None]/scale[None,:];eigen,unit=eigh(A,driver='evd');phi=unit/scale[:,None];residual=np.linalg.norm(A@unit-unit*eigen[None,:],axis=0);positive=eigen>residual;negative=eigen< -residual;uncertain=~(positive|negative);amplitude=q@(mass[:,None]*phi);speed=v@(mass[:,None]*phi);kinetic=.5*speed**2;potential=.5*eigen[None,:]*amplitude**2;energy=kinetic+potential
 omega=np.full(n,np.nan);omega[positive]=np.sqrt(eigen[positive]);records=[]
 for i in range(n):records.append(dict(mode=i,eigenvalue_per_s2=float(eigen[i]),residual_bound_per_s2=float(residual[i]),classification='positive' if positive[i] else 'negative' if negative[i] else 'unresolved_zero',omega_rad_s=float(omega[i]) if positive[i] else None,period_s=float(2*np.pi/omega[i]) if positive[i] else None,actual_linearized_modal_energy_Nmm=float(energy[:,i].sum()),actual_modal_kinetic_Nmm=float(kinetic[:,i].sum()),frozen_quadratic_potential_Nmm=float(potential[:,i].sum()) if not current else None))
 write_json(out/'modes.json',records);os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,axes=plt.subplots(1,2,figsize=(11,4));axes[0].semilogy(np.flatnonzero(positive),omega[positive]/(2*np.pi));axes[0].set_xlabel('independent FREE-film mode');axes[0].set_ylabel('frequency [Hz]');axes[1].loglog(omega[positive]/(2*np.pi),np.maximum(energy[:,positive].sum(axis=0),np.finfo(float).tiny),'.');axes[1].set_xlabel('frequency [Hz]');axes[1].set_ylabel('projected actual kinetic energy [Nmm]' if current else 'frozen quadratic metric [Nmm],NOT actual stored E');fig.suptitle(('Independent CURRENT-deformed finger0 frozen tangent' if current else 'Independent stress-free FREE-film FEM')+',actual SOFA state t='+str(time)+'s\nNOT coupled contact/nonlinear response/recovery prediction;no measured material claim');fig.tight_layout();fig.savefig(out/'free_film_spectrum.png',dpi=150);plt.close(fig)
 write_json(out/'spectrum_summary.json',dict(positive_modes=int(positive.sum()),negative_modes=int(negative.sum()),unresolved_modes=int(uncertain.sum()),mass_orthogonality_error=float(np.linalg.norm(phi.T@(mass[:,None]*phi)-np.eye(n))),minimum_positive_omega_rad_s=float(omega[positive].min()) if positive.any() else None,maximum_positive_omega_rad_s=float(omega[positive].max()) if positive.any() else None,longest_positive_undamped_period_s=float(2*np.pi/omega[positive].min()) if positive.any() else None,actual_time_s=time,actual_film_kinetic_Nmm=float(.5*np.sum(v*v*mass)),modal_kinetic_Nmm=float(kinetic.sum()),kinetic_projection_error_Nmm=float(kinetic.sum()-.5*np.sum(v*v*mass)),frozen_quadratic_potential_Nmm=None if current else float(potential.sum()),kinetic_fractions_above_omega_dt={str(limit):float(kinetic[:,positive & (omega*.0001>limit)].sum()/kinetic.sum()) for limit in (.1,1,np.pi)},scope='independent CURRENT-deformed finger0 frozen tangent,not an equilibrium/stability certificate;quadratic potential unassigned' if current else 'independent stress-free FREE single-film spectrum and frozen projection of actual three-film state;NOT constrained contact spectrum,nonlinear dominant mode,wrapping time or recovery certificate'))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag');p.add_argument('--worker');p.add_argument('--reuse-input');p.add_argument('--current',action='store_true');a=p.parse_args()
 if a.worker:return worker(a.worker)
 if not a.tag:raise ValueError('unique tag required')
 parent=ROOT/'results/autonomous_film_20261118_three_film_unload_end1083';meta=json.loads((parent/'summary.json').read_text());checkpoint=parent/'three.checkpoint_200.txt'
 if meta['status']!='EXPERIMENTAL' or meta['process']['exit_code'] or meta['sofa_errors'] or sha(checkpoint)!=meta['raw_hashes'][checkpoint.name]:raise ValueError('complete actual Unload endpoint required')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(checkpoint,out/'input.checkpoint');archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));cpp=archive/'diagnostics/film_three_finger/FreeFilmSpectrum.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/FreeFilmSpectrum.cpp',cpp);binary=out/'reference'
 if a.reuse_input:
  previous=ROOT/'results'/('autonomous_film_'+a.reuse_input);proof=json.loads((previous/'summary.json').read_text())
  previous_current=proof.get('linearization')=='current' or proof.get('metrics',{}).get('scope','').startswith('independent CURRENT-deformed')
  if a.current!=previous_current:raise ValueError('cannot relabel stress-free/current modal inputs')
  if proof['run']['exit_code'] or sha(previous/'reference')!=proof['binary_sha256'] or sha(checkpoint)!=proof['actual_checkpoint_sha256']:raise ValueError('complete unchanged actual-state FEM dump required')
  for name,digest in proof['sources'].items():
   if sha(archive/name)!=digest:raise ValueError('FEM source differs:'+name)
  for name in ('film.matrix.txt','film.state.txt'):
   if sha(previous/name)!=proof['raw_hashes'][name]:raise ValueError('immutable modal input changed')
   shutil.copy2(previous/name,out/name)
  shutil.copy2(previous/'reference',binary);compile={'exit_code':0,'reused_from':a.reuse_input,'source_closure_exact':True};run={'exit_code':0,'reused_matrix_from':a.reuse_input}
 else:
  compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120);run=guarded([binary,out/'input.checkpoint',out/'film']+(['current'] if a.current else []),out/'run',120) if compile['exit_code']==0 else None
 if a.current:write_json(out/'current.flag',{'mode':'actual-deformed frozen finger0,not equilibrium'})
 os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1';spectrum=guarded([sys.executable,out/'runner.py','--worker',out],out/'spectrum',120) if run and run['exit_code']==0 else None
 result=dict(status='PASS' if spectrum and spectrum['exit_code']==0 else 'FAIL',scope='independent FREE-film modal diagnostic;NOT actual SOFA modal or nonlinear grasp certificate',linearization='current' if a.current else 'stress-free',parent_summary_sha256=sha(parent/'summary.json'),actual_checkpoint_sha256=sha(checkpoint),actual_binary_sha256=meta['binary_sha256'],source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},compile=compile,run=run,spectrum=spectrum,binary_sha256=sha(binary) if binary.exists() else None)
 if (out/'spectrum_summary.json').exists():result['metrics']=json.loads((out/'spectrum_summary.json').read_text())
 result['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.is_file() and f.suffix in ('.txt','.json','.png') and f.name!='summary.json'};write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k in ('status','scope','metrics')}))
if __name__=='__main__':main()
