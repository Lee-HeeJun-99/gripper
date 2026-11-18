"""REST-basis projection of cumulative nonlinear time-discretization errors."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import argparse,csv,json,shutil,subprocess,sys
from pathlib import Path
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag');p.add_argument('--worker');a=p.parse_args()
 if a.worker:
  from scipy.linalg import eigh
  out=Path(a.worker);data=np.fromstring((out/'rest.linear.txt').read_text(),sep=' ');n=int(data[0]);M=data[1:1+n];K=data[1+2*n:].reshape(n,n);e,V=eigh(K/np.sqrt(M[:,None]*M[None,:]));
  if e.min()<=0:raise ValueError('positive frozen REST basis required;no clipping')
  rows={(x['substeps'],x['macro']):x for x in csv.DictReader((out/'states.csv').open())};omega=np.sqrt(e);records=[];summaries={}
  for left,right in (('1','4'),('2','4')):
   x=np.fromstring(rows[(left,'8')]['v'],sep=' ')[:3*n].reshape(3,n);y=np.fromstring(rows[(right,'8')]['v'],sep=' ')[:3*n].reshape(3,n);delta=x-y;coordinates=(delta*np.sqrt(M))@V;power=np.sum(coordinates**2,axis=0);direct=float(np.sum(delta*delta*M));closure=abs(power.sum()-direct)/direct
   if closure>1e-10:raise ValueError('mass-weighted modal completeness failed')
   cumulative=np.cumsum(power)/power.sum();summaries[left+'_'+right]=dict(REST_basis_completeness_relative=closure,error_mass_norm_squared_Nmm=direct,omega_error_quantiles_rad_s={str(q):float(omega[np.searchsorted(cumulative,q)]) for q in (.5,.9,.99)},warning='REST eigenbasis only;not actual deformed modes or a causal proof')
   for i in range(n):records.append(dict(pair=left+'_'+right,mode=i,REST_omega_rad_s=float(omega[i]),error_mass_fraction=float(power[i]/power.sum()),omega_h_coarse=float(omega[i]*(.0008 if left=='1' else .0004))))
  with (out/'error_modes.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
  write_json(out/'worker.json',dict(status='EXPERIMENTAL',scope='projection of independent nonlinear time error into existing REST basis ONLY;NOT actual modal/grasp certification',pairs=summaries));return
 if not a.tag:raise ValueError('unique tag required')
 src=ROOT/'results/autonomous_film_20261119_stationary_gauss_window_both1624';m=json.loads((src/'summary.json').read_text());basis=ROOT/'results/autonomous_film_20261118_lateral_modal_scale1419';bm=json.loads((basis/'summary.json').read_text())
 if m['process']['exit_code']!=0 or sha(src/'states.csv')!=m['raw_hashes']['states.csv'] or sha(basis/'rest.linear.txt')!=bm['raw_hashes']['rest.linear.txt']:raise ValueError('completed cumulative error/reference basis required')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(src/'states.csv',out/'states.csv');shutil.copy2(basis/'rest.linear.txt',out/'rest.linear.txt');run=guarded([sys.executable,__file__,'--worker',out],out/'process',180);r=dict(status='FAIL',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),time_reference_summary_sha256=sha(src/'summary.json'),REST_basis_summary_sha256=sha(basis/'summary.json'),process=run)
 if run['exit_code']==0:r.update(json.loads((out/'worker.json').read_text()))
 r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.csv','.txt')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k!='process'}))
if __name__=='__main__':main()
