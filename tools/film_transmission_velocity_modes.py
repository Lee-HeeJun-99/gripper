"""Frozen-rest modal projection of ACTUAL velocity error,not nonlinear eigenmodes."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import argparse,csv,json,shutil
import numpy as np
from scipy.linalg import eigh
from curve_common import ROOT,sha,write_json
from film_transmission_linear import mapping
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();names=('20261118_transmission_hold_coarse1189','20261118_transmission_hold50_1187','20261118_transmission_hold_fine1190');cases=[];P=mapping();pick=np.argmax(P,axis=0);weights=P[pick,np.arange(P.shape[1])]
 for name in names:
  src=ROOT/'results'/('autonomous_film_'+name);meta=json.loads((src/'summary.json').read_text())
  if meta['status']!='PASS':raise ValueError('completed actual velocity required')
  for file,digest in meta['raw_hashes'].items():
   if sha(src/file)!=digest:raise ValueError('actual data changed')
  row=list(csv.DictReader((src/'actual.csv').open()))[-1];v=np.fromstring(row['v'],sep=' ');reduced=v[pick]/weights
  if np.max(abs(P@reduced-v))>1e-12:raise ValueError('actual projected root velocity differs')
  cases.append((src,meta,row,reduced))
 if len({r[2]['time'] for r in cases})!=1 or len({r[1]['binary_sha256'] for r in cases})!=1 or len({r[1]['public_mass_sha256'] for r in cases})!=1:raise ValueError('same epoch,binary,mass required')
 data=np.fromstring((cases[1][0]/'reference.linear.txt').read_text(),sep=' ');n=int(data[0]);M=data[1:1+n];K=data[1+2*n:].reshape(n,n);inv=1/np.sqrt(M);lam,V=eigh(inv[:,None]*K*inv[None,:])
 if n!=649 or min(lam)<=0:raise ValueError('positive exact rest reference required;no regularization')
 omega=np.sqrt(lam);bounds=(0,100,1000,10000,100000,float('inf'));pairs=[];curves=[]
 for index in (0,1):
  dv=cases[index][3]-cases[2][3];modal=V.T@(np.sqrt(M)*dv);squared=modal**2;total=float(squared.sum());bands=[dict(omega_low_rad_s=lo,omega_high_rad_s=hi if np.isfinite(hi) else None,error_mass_norm_squared_fraction=float(squared[(omega>=lo)&(omega<hi)].sum()/total)) for lo,hi in zip(bounds[:-1],bounds[1:])];pairs.append(dict(cases=[names[index],names[2]],physical_velocity_L2_relative_percent=float(100*np.linalg.norm(P@dv)/np.linalg.norm(P@cases[2][3])),mass_norm_squared=float(dv@(M*dv)),modal_sum_relative_error=abs(total-float(dv@(M*dv)))/total,bands=bands,largest_error_modes=[dict(omega_rad_s=float(omega[i]),fraction=float(squared[i]/total)) for i in np.argsort(squared)[-8:][::-1]]));curves.append(squared/total)
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,ax=plt.subplots(figsize=(10,5))
 for label,squared in zip(('400us vs100us','200us vs100us'),curves):ax.semilogx(omega,np.cumsum(squared),label=label)
 ax.set_xlabel('frozen REST angular frequency [rad/s],NOT current nonlinear modes');ax.set_ylabel('cumulative mass-norm-squared ERROR fraction');ax.legend();ax.set_title('Actual50ms Hold velocity error projection;no contact\nDLL '+cases[0][1]['binary_sha256'][:12]+';Tmax=0.0001N/rail');fig.tight_layout();fig.savefig(out/'velocity_error_modes.png',dpi=150);plt.close(fig)
 result=dict(status='PASS' if max(p['modal_sum_relative_error'] for p in pairs)<1e-12 else 'FAIL',scope='diagnostic frozen-rest projection of actual endpoint velocity errors;NOT nonlinear modes/whole time certification',source_summaries={name:sha(c[0]/'summary.json') for name,c in zip(names,cases)},frozen_rest_matrix_sha256=sha(cases[1][0]/'reference.linear.txt'),pairs=pairs,contact_present=False,causal_limit='Projection identifies modal content,not sole cause;forcing excitation,phase and nonlinear coupling remain distinct hypotheses.',image_sha256=sha(out/'velocity_error_modes.png'));write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
