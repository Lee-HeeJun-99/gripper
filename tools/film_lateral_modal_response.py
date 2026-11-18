"""Frozen REST linear response to the actual C2 polynomial;NOT contact dynamics."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import argparse,csv,ctypes,json,shutil,subprocess,sys
from pathlib import Path
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_transmission_linear import mapping,shape
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag');p.add_argument('--worker');a=p.parse_args()
 if a.worker:
  from scipy.linalg import eigh,expm
  import scipy
  out=Path(a.worker);data=np.fromstring((out/'rest.linear.txt').read_text(),sep=' ');n=int(data[0]);M=data[1:1+n];B=data[1+n:1+2*n];K=data[1+2*n:].reshape(n,n);tokens=(out/'actual10.checkpoint').read_text().split();mass=np.array(tokens[3915:3915+231],float);pairs=np.array(tokens[3915+693+36:3915+693+36+1386],float).reshape(693,2);actualM=np.zeros(n)
  for j,(index,weight) in enumerate(pairs):
   if index>=0:actualM[int(index)]+=float(mass[j//3])*float(weight)*float(weight)
  if not np.array_equal(M,actualM):raise ValueError('frozen matrix/actual public projected mass not EXACT;no mass substitution')
  inv=1/np.sqrt(M);A=inv[:,None]*K*inv[None,:];eigen,V=eigh(A)
  if eigen.min()<=0:raise ValueError('nonpositive frozen mode;no clipping')
  omega=np.sqrt(eigen);modal=V.T@(inv*B);lift=inv[:,None]*V;P=mapping();library=ctypes.CDLL(str(out/'control.so'));T=library.regripTransmissionTension;T.argtypes=[ctypes.c_double];T.restype=ctypes.c_double
  pieces=[(0.,.01,[0,0,0,10,-15,6]),(.01,.02,[1]),(.02,.03,[1,0,0,-10,15,-6]),(.03,.05,[0])];control_error=0.
  for left,right,c in pieces:
   for u in np.linspace(0,1,501):control_error=max(control_error,abs(.0001*np.polynomial.polynomial.polyval(u,c)-T(left+(right-left)*u)))
  if control_error>512*np.finfo(float).eps*.0001:raise ValueError('compiled original C2/polynomial relation exceeds operation bound')
  def advance(state,h,c):
   answer=np.empty_like(state)
   for i,w in enumerate(omega):
    matrix=np.zeros((8,8));matrix[0,1]=h*w;matrix[1,0]=-h*w;matrix[1,1]=-2*h
    for k,coefficient in enumerate(c):matrix[1,2+k]=h*modal[i]*.0001*coefficient
    for k in range(1,6):matrix[2+k,1+k]=k
    initial=np.zeros(8);initial[:2]=state[i];initial[2]=1;answer[i]=(expm(matrix)@initial)[:2]
   return answer
  state=np.zeros((n,2));records=[];semigroup=0.
  for left,right,c in pieces:
   polynomial=np.polynomial.Polynomial(c);first=polynomial(np.polynomial.Polynomial([0,.5])).coef;second=polynomial(np.polynomial.Polynomial([.5,.5])).coef;full=advance(state,right-left,c);split=advance(advance(state,(right-left)/2,first),(right-left)/2,second);semigroup=max(semigroup,float(np.max(abs(full-split))));state=full;q=lift@(state[:,0]/omega);v=lift@state[:,1];records.append(dict(time=right,q=q,v=v,shape=shape(P@q)))
  # SAME frozen linear ODE, actual accumulated-clock implicit midpoint.
  # Separates linear time-discretization error from the nonlinear/contact
  # difference without pretending the frozen model is actual SOFA dynamics.
  discrete={};state=np.zeros((n,2));clock=0.;work=np.longdouble(0);damping=np.longdouble(0)
  for step in range(1,251):
   h=.0002;d=h*omega/2;rhs0=state[:,0]+d*state[:,1];rhs1=-d*state[:,0]+(1-h)*state[:,1]+h*modal*T(clock+h/2);velocity=(rhs1-d*rhs0)/(1+h+d*d);position=rhs0+d*velocity;midv=((state[:,1]+velocity)/2).astype(np.longdouble);work+=np.longdouble(h)*sum(modal.astype(np.longdouble)*np.longdouble(T(clock+h/2))*midv);damping+=2*np.longdouble(h)*sum(midv*midv);state=np.c_[position,velocity];clock+=h
   if step in (50,100,150,250):discrete[step]=dict(time=clock,q=lift@(state[:,0]/omega),v=lift@state[:,1])
  linear_time={}
  for step,index in ((50,0),(100,1),(150,2),(250,3)):linear_time[str(step)]={key:dict(max_abs=float(np.max(abs(discrete[step][key]-records[index][key]))),relative_L2=float(np.linalg.norm(discrete[step][key]-records[index][key])/np.linalg.norm(records[index][key]))) for key in ('q','v')}
  with (out/'linear.csv').open('w') as f:
   writer=csv.writer(f);writer.writerow(['time','q','v','width_mean_tip_z_mm','centre_tip_z_mm']);
   for r in records:writer.writerow([r['time'],' '.join(format(x,'.17g') for x in r['q']),' '.join(format(x,'.17g') for x in r['v']),r['shape']['skin_tip_z'],r['shape']['skin_centre_tip_z']])
  comparison={}
  for label,index,filename in (('precontact10ms',0,'actual10.checkpoint'),('postcontact50ms',3,'actual50.checkpoint')):
   t=(out/filename).read_text().split();q=np.array(t[5:5+n],float);v=np.array(t[5+1953:5+1953+n],float);step=50 if index==0 else 250
   if float(t[1])!=discrete[step]['time']:raise ValueError('actual/frozen discrete accumulated clocks differ')
   comparison[label]={key:dict(max_abs_vs_continuous=float(np.max(abs(actual-records[index][key]))),relative_L2_vs_continuous=float(np.linalg.norm(actual-records[index][key])/np.linalg.norm(records[index][key])),relative_L2_vs_frozen_midpoint=float(np.linalg.norm(actual-discrete[step][key])/np.linalg.norm(discrete[step][key]))) for key,actual in (('q',q),('v',v))}
  modal_energy=sum(state.astype(np.longdouble).ravel()**2)/2
  write_json(out/'worker.json',dict(status='EXPERIMENTAL',scope='independent double-precision frozen REST linear polynomial-forcing response ONLY;NOT analytic/nonlinear/contact/time/grasp certification',numpy=np.__version__,scipy=scipy.__version__,actual_projected_mass_EXACT=True,compiled_C2_polynomial_max_abs_N=control_error,matrix_exponential_split_max_abs_modal=semigroup,frozen_eigen_residual_relative=float(np.linalg.norm(A@V-V*eigen)/np.linalg.norm(A)),response=[dict(time=r['time'],shape=r['shape']) for r in records],frozen_midpoint_discretization_difference=linear_time,frozen_midpoint_signed_energy_defect_Nmm=float(modal_energy-work+damping),actual_nonlinear_difference=comparison,warning='nonlinear force/tangent changes,contact and numerical errors differ;postcontact impacts/constraints absent from frozen model;differences are NOT automatically solver errors or isolated physical effects'));return
 if not a.tag:raise ValueError('unique tag required')
 provider=ROOT/'results/autonomous_film_20261118_lateral_modal_scale1419';m=json.loads((provider/'summary.json').read_text());actual10=ROOT/'results/autonomous_film_20261119_stationary_peak_actual1541';actual50=ROOT/'results/autonomous_film_20261119_stationary_free_to50_chain1596_part12'
 # Resolve the first peak by its unique completed campaign suffix if the human
 # readable prefix differs;never select a failed or partial result.
 if not actual10.exists():
  candidates=[d for d in (ROOT/'results').glob('autonomous_film_*1541') if (d/'summary.json').exists()];
  if len(candidates)!=1:raise ValueError('unique actual1541 required')
  actual10=candidates[0]
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py')
 if sha(provider/'rest.linear.txt')!=m['raw_hashes']['rest.linear.txt']:raise ValueError('frozen matrix changed')
 for f,d in m['source_hashes'].items():
  if sha(provider/'sources'/f)!=d:raise ValueError('frozen provider source changed')
 shutil.copy2(provider/'rest.linear.txt',out/'rest.linear.txt');actuals={}
 for label,path,step in (('10',actual10,50),('50',actual50,250)):
  am=json.loads((path/'summary.json').read_text());cp=path/f'three.checkpoint_{step}.txt'
  if am['status']!='PASS' or sha(cp)!=am['raw_hashes'][cp.name]:raise ValueError('completed strict actual checkpoint required')
  for f,d in am['source_hashes'].items():
   if sha(path/'sources'/f)!=d:raise ValueError('actual compiled source changed')
  shutil.copy2(cp,out/f'actual{label}.checkpoint');actuals[label]=sha(path/'summary.json')
 archive=out/'sources';header=archive/'models/film_rail_tendon/ControlProfile.h';header.parent.mkdir(parents=True);shutil.copy2(actual50/'sources/models/film_rail_tendon/ControlProfile.h',header);cpp=archive/'diagnostics/film_three_finger/TransmissionControl.cpp';cpp.parent.mkdir(parents=True);text=(ROOT/'diagnostics/film_three_finger/TransmissionControl.cpp').read_text();
 if text.count('.01,.05,.06,true')!=1:raise ValueError('compiled existing control binding anchor differs')
 cpp.write_text(text.replace('.01,.05,.06,true','.01,.02,.03,true'));compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-shared','-fPIC',cpp,'-o',out/'control.so'],out/'compile',60);run=guarded([sys.executable,__file__,'--worker',out],out/'process',180) if compile['exit_code']==0 else None;r=dict(status='FAIL',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),matrix_summary_sha256=sha(provider/'summary.json'),matrix_sha256=sha(out/'rest.linear.txt'),actual_summaries=actuals,compile=compile,process=run,source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()})
 if run and run['exit_code']==0:r.update(json.loads((out/'worker.json').read_text()))
 elif run:r['failure_reason']=(out/'process/stderr.log').read_text().strip()
 r['control_binary_sha256']=sha(out/'control.so') if (out/'control.so').exists() else None;r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.txt','.csv','.checkpoint')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process','response')}))
if __name__=='__main__':main()
