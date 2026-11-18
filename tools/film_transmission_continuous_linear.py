"""Independent continuous-time frozen linear response with COMPILED original C2."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import argparse,csv,ctypes,json,shutil,sys
from pathlib import Path
if '--worker' in sys.argv:sys.path.insert(0,str(Path(__file__).resolve().parent/'sources/tools'))
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_transmission_linear import mapping,shape
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag');p.add_argument('--rtol',type=float,choices=(1e-8,1e-10,1e-12),default=1e-10);p.add_argument('--worker');a=p.parse_args()
 if a.worker:
  from scipy.sparse import csr_matrix
  from scipy.integrate import solve_ivp
  out=__import__('pathlib').Path(a.worker);data=np.fromstring((out/'rest.linear.txt').read_text(),sep=' ');n=int(data[0]);M=data[1:1+n];B=data[1+n:1+2*n];K=csr_matrix(data[1+2*n:].reshape(n,n));library=ctypes.CDLL(str(out/'control.so'));T=library.regripTransmissionTension;T.argtypes=[ctypes.c_double];T.restype=ctypes.c_double
  def rhs(t,x):return np.r_[x[n:],(B*T(t)-K@x[:n])/M-2*x[n:]]
  result=solve_ivp(rhs,(0,.0008),np.zeros(2*n),method='DOP853',rtol=a.rtol,atol=np.r_[np.full(n,1e-32),np.full(n,1e-28)],t_eval=[.0008],max_step=.00005)
  if not result.success or result.t[-1]!=.0008:raise RuntimeError('continuous linear endpoint not reached: '+result.message)
  P=mapping();q=P@result.y[:n,-1];v=P@result.y[n:,-1]
  with (out/'endpoint.csv').open('w') as stream:
   writer=csv.writer(stream);writer.writerow(['time','q','v']);writer.writerow([.0008,' '.join(format(x,'.17g') for x in q),' '.join(format(x,'.17g') for x in v)])
  write_json(out/'worker.json',dict(status='EXPERIMENTAL',nfev=result.nfev,rtol=a.rtol,atol_q_mm=1e-32,atol_v_mm_s=1e-28,shape=shape(q),scope='double precision adaptive numerical continuous LINEAR response,not analytic/nonlinear SOFA reference'));return
 if not a.tag:raise ValueError('new experiment tag required')
 actual=ROOT/'results/autonomous_film_20261118_transmission_onset_exact1203';proof=json.loads((actual/'summary.json').read_text());provider=ROOT/'results/autonomous_film_20261118_transmission_hold50_1187';meta=json.loads((provider/'summary.json').read_text())
 for src,m in ((actual,proof),(provider,meta)):
  if m['status']!='PASS':raise ValueError('complete actual/matrix provider required')
  for name,digest in m['raw_hashes'].items():
   if sha(src/name)!=digest:raise ValueError('immutable actual/reference data changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(provider/'reference.linear.txt',out/'rest.linear.txt');archive=out/'sources';header=archive/'models/film_rail_tendon/ControlProfile.h';header.parent.mkdir(parents=True);shutil.copy2(provider/'sources/models/film_rail_tendon/ControlProfile.h',header);cpp=archive/'diagnostics/film_three_finger/TransmissionControl.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/TransmissionControl.cpp',cpp);compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-shared','-fPIC',cpp,'-o',out/'control.so'],out/'compile',120)
 helpers=archive/'tools';helpers.mkdir()
 for name in ('curve_common.py','research_common.py','birth_common.py','history_common.py','beam_common.py','verification_common.py','film_transmission_linear.py','film_guarded_process.py'):shutil.copy2(ROOT/'tools'/name,helpers/name)
 run=guarded([sys.executable,out/'runner.py','--worker',out,'--rtol',str(a.rtol)],out/'process',480) if compile['exit_code']==0 else None
 result=dict(status='FAIL',scope='independent CONTINUOUS frozen-linear C2 onset response;NOT nonlinear time/grasp certification',actual_summary_sha256=sha(actual/'summary.json'),rest_matrix_provider_sha256=sha(provider/'summary.json'),rest_matrix_sha256=sha(out/'rest.linear.txt'),rtol=a.rtol,compile=compile,process=run,control_binary_sha256=sha(out/'control.so') if (out/'control.so').exists() else None,sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},control='original archived ControlProfile::evaluate,not Python reimplementation')
 if run and run['exit_code']==0:
  result.update(json.loads((out/'worker.json').read_text()));row=list(csv.DictReader((actual/'actual.csv').open()))[-1];ref=list(csv.DictReader((out/'endpoint.csv').open()))[-1];result['actual_nonlinear_difference']={k:dict(max_abs=float(np.max(abs(np.fromstring(row[k],sep=' ')-np.fromstring(ref[k],sep=' ')))),relative_L2_percent=float(100*np.linalg.norm(np.fromstring(row[k],sep=' ')-np.fromstring(ref[k],sep=' '))/np.linalg.norm(np.fromstring(ref[k],sep=' ')))) for k in ('q','v')}
 result['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.csv','.txt')};write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('sources','compile','process','shape')}))
if __name__=='__main__':main()
