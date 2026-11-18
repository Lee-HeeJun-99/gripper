"""Actual-mass frozen-rest mode/forcing weights,not nonlinear wrap prediction."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import argparse,csv,json,shutil,subprocess,sys
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_transmission_linear import mapping
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag');p.add_argument('--worker');a=p.parse_args()
 if a.worker:
  from scipy.linalg import eigh
  from pathlib import Path
  out=Path(a.worker);matrix=np.fromstring((out/'rest.linear.txt').read_text(),sep=' ');n=int(matrix[0]);M=matrix[1:1+n];b=matrix[1+n:1+2*n];K=matrix[1+2*n:].reshape(n,n);inv=1/np.sqrt(M);w,V=eigh(inv[:,None]*K*inv[None,:])
  if M.min()<=0 or w.min()<=0:raise ValueError('strict positive actual projected mass/frozen tangent required;no clipping')
  modal=V.T@(inv*b);lift=inv[:,None]*V;P=mapping()
  if P.shape!=(693,n):raise ValueError('explicit original root projection dimensions')
  tip=P[np.arange(100,105)*3+2].mean(axis=0);contribution=(tip@lift)*modal/w;compliance=modal**2/w;omega=np.sqrt(w);records=[]
  for i in range(n):records.append(dict(mode=i,omega_rad_s=float(omega[i]),undamped_period_s=float(2*np.pi/omega[i]),cable_compliance_weight=float(compliance[i]/compliance.sum()),absolute_tip_static_weight=float(abs(contribution[i])/np.abs(contribution).sum()),tip_static_contribution_at_Tmax_mm=float(.0001*contribution[i])))
  with (out/'modes.csv').open('w') as f:writer=csv.DictWriter(f,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)
  summaries={}
  for label,weights in (('cable_compliance',compliance),('absolute_tip_static_contribution',np.abs(contribution))):
   c=np.cumsum(weights)/weights.sum();summaries[label]={str(x):records[int(np.searchsorted(c,x))] for x in (.5,.8,.95)}
  write_json(out/'worker.json',dict(status='EXPERIMENTAL',minimum_omega_rad_s=float(omega.min()),maximum_omega_rad_s=float(omega.max()),frozen_tip_linear_static_mm=float(.0001*contribution.sum()),weighted_frequency_quantiles=summaries,damping_rate_s_inverse=2.,not_a_prediction='frequencies/weights at REST,NO object/contact/prestress;NOT actual dominant nonlinear mode,response or wrap/recovery completion time'));return
 if not a.tag:raise ValueError('unique tag required')
 provider=ROOT/'results/autonomous_film_20261118_lateral_api_build1356';m=json.loads((provider/'summary.json').read_text());actual=ROOT/'results/autonomous_film_20261118_lateral_six_hold50_1363';am=json.loads((actual/'summary.json').read_text());mass=actual/'public_mass.txt'
 if m['status']!='PASS' or am['status']!='PASS' or sha(mass)!=am['raw_hashes']['public_mass.txt']:raise ValueError('qualified model and actual public mass required')
 for f,d in m['source_hashes'].items():
  if sha(provider/'sources'/f)!=d:raise ValueError('frozen physical source changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(provider/'sources/models',archive/'models');cpp=archive/'diagnostics/film_three_finger/LateralRestLinear.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/LateralRestLinear.cpp',cpp);compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'export'],out/'compile',120);export=guarded([out/'export',mass,out/'rest.linear.txt'],out/'export_process',120) if compile['exit_code']==0 else None;run=guarded([sys.executable,__file__,'--worker',out],out/'process',120) if export and export['exit_code']==0 else None;r=dict(status='FAIL',scope='independent actual-mass frozen-rest lateral spectrum/forcing scale ONLY;NOT SOFA dynamic completion/wrapping/time Gate',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),actual_mass_sha256=sha(mass),model_summary_sha256=sha(provider/'summary.json'),actual_summary_sha256=sha(actual/'summary.json'),source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},compile=compile,export_process=export,process=run)
 if run and run['exit_code']==0:r.update(json.loads((out/'worker.json').read_text()));r.update(binary_sha256=sha(out/'export'),raw_hashes={n:sha(out/n) for n in ('rest.linear.txt','modes.csv','worker.json')})
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process','export_process','weighted_frequency_quantiles')}))
if __name__=='__main__':main()
