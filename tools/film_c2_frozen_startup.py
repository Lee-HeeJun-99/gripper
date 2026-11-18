"""Independent balanced sparse exponential of SAME rest FEM;not nonlinear truth."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import argparse,csv,ctypes,json,shutil,subprocess,sys
from pathlib import Path
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_transmission_linear import mapping,shape
def worker(out):
 from scipy.sparse import bmat,csr_matrix,diags,eye
 from scipy.sparse.linalg import expm_multiply,spsolve
 d=np.fromstring((out/'rest.linear.txt').read_text(),sep=' ');n=int(d[0]);M=d[1:1+n];B=d[1+n:1+2*n];K=d[1+2*n:].reshape(n,n);P=mapping();z=(out/'actual50.checkpoint').read_text().split();offset=5+2*1953+4;mass=np.array(z[offset:offset+231],float);pairs=np.array(z[offset+693+36:offset+693+36+1386],float).reshape(693,2);actual=np.zeros(n)
 for j,(index,weight) in enumerate(pairs):
  if index>=0:actual[int(index)]+=mass[j//3]*weight*weight
 if not np.array_equal(M,actual):raise ValueError('same actual public projected mass required')
 inv=1/np.sqrt(M);Kh=inv[:,None]*K*inv[None,:];gamma=np.sqrt(np.max(np.sum(abs(Kh),axis=1)));A=bmat([[None,gamma*eye(n)],[-csr_matrix(Kh/gamma),-2*eye(n)]],format='csr');library=ctypes.CDLL(str(out/'control.so'));T=library.regripTransmissionTension;T.argtypes=[ctypes.c_double];T.restype=ctypes.c_double;answers=[];snapshots=[];r3=np.sqrt(3)/6;RK=np.array([[.25,.25-r3],[.25+r3,.25]]);nodes=np.array([.5-r3,.5+r3]);reference_ok=True
 for h in (.0002,.0001,.00005):
  coefficients=np.array([0,0,0,10*(h/.01)**3,-15*(h/.01)**4,6*(h/.01)**5]);forcing=np.zeros((2*n,6));forcing[n:,:]=(inv*B)[:,None]*.0001*coefficients;clock=np.zeros((6,6))
  for j in range(1,6):clock[j,j-1]=j
  # Exact augmentation-coordinate balancing:unit polynomial clock otherwise
  # hides tiny mechanical response from expm_multiply's normwise stopping.
  # Both the clock initial value and inverse forcing scale change together.
  clock_scale=h*.0001*(h/.01)**3*np.linalg.norm(inv*B)
  if not clock_scale>0:raise ValueError('positive forcing-coordinate scale required')
  L=bmat([[h*A,csr_matrix(h*forcing/clock_scale)],[None,csr_matrix(clock)]],format='csr');initial=np.zeros(2*n+6);initial[2*n]=clock_scale
  def flow(parts):
   state=initial.copy()
   for _ in range(parts):state=expm_multiply(L/parts,state,traceA=float(L.diagonal().sum())/parts)
   return dict(q=inv*state[:n]/gamma,v=inv*state[n:2*n])
  exact=flow(1);split=flow(4);split_error={}
  for key in ('q','v'):
   x,y=P@exact[key],P@split[key]
   for name,part in (('all',slice(None)),('Skin',slice(0,315)),('Rails',slice(315,None))):
    scale=max(np.linalg.norm(x[part]),np.linalg.norm(y[part]));rel=float(np.linalg.norm(x[part]-y[part])/scale) if scale else 0.;split_error[name+'_'+key]=rel;reference_ok=reference_ok and rel<1e-8
  sx,sy=shape(P@exact['q']),shape(P@split['q'])
  for key in sx:
   scale=max(abs(sx[key]),abs(sy[key]));rel=abs(sx[key]-sy[key])/scale if scale else 0.;split_error['observable_'+key]=rel;reference_ok=reference_ok and rel<1e-8
  # Direct linear stage solve:independent of all Newton stopping thresholds.
  block=[];rhs=[];tension=np.array([T(float(h*c)) for c in nodes]);control_error=max(abs(tension-.0001*np.polynomial.polynomial.polyval(nodes,coefficients)))
  for i in range(2):
   block.append([csr_matrix(((1 if i==k else 0)+2*h*RK[i,k])*np.diag(M)+h*h*sum(RK[i,j]*RK[j,k] for j in range(2))*K) for k in range(2)]);rhs.append(h*sum(RK[i,j]*tension[j] for j in range(2))*B)
  system=bmat(block,format='csc');right=np.concatenate(rhs);stage=spsolve(system,right).reshape(2,n);sq=h*RK@stage;forces=np.array([tension[j]*B-K@sq[j]-2*M*stage[j] for j in range(2)]);linear=dict(q=h/2*(stage[0]+stage[1]),v=h/2*(forces[0]+forces[1])/M);row=dict(h_s=h,projected_mass_EXACT=True,balancing_gamma_per_s=float(gamma),flow_split_relative=split_error,linear_stage_residual_Ns=float(np.linalg.norm(system@stage.ravel()-right)),compiled_control_polynomial_max_abs_N=float(control_error),continuous_shape=shape(P@exact['q']),direct_linear_Gauss2_shape=shape(P@linear['q']))
  actual_row=next(csv.DictReader((out/('actual_'+str(int(round(h*1e6)))+'.csv')).open()));q=np.fromstring(actual_row['q'],sep=' ');v=np.fromstring(actual_row['v'],sep=' ')
  row['actual_nonlinear_shape']=shape(q);row['differences']={}
  for key,actual_value in (('q',q),('v',v)):
   truth=P@exact[key];rk=P@linear[key];row['differences'][key]={}
   for name,part in (('all',slice(None)),('Skin',slice(0,315)),('Rails',slice(315,None))):row['differences'][key][name]=dict(linear_Gauss_vs_continuous=float(np.linalg.norm(rk[part]-truth[part])/np.linalg.norm(truth[part])),nonlinear_actual_vs_continuous=float(np.linalg.norm(actual_value[part]-truth[part])/np.linalg.norm(truth[part])),nonlinear_actual_vs_linear_Gauss=float(np.linalg.norm(actual_value[part]-rk[part])/max(np.linalg.norm(actual_value[part]),np.linalg.norm(rk[part]))))
  snapshots.extend([dict(h_s=h,kind=kind,q=' '.join(format(x,'.17g') for x in P@answer['q']),v=' '.join(format(x,'.17g') for x in P@answer['v'])) for kind,answer in (('continuous_sparse_exponential',exact),('direct_linear_Gauss2',linear))]);answers.append(row)
 with (out/'startup_states.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(snapshots[0]));w.writeheader();w.writerows(snapshots)
 write_json(out/'worker.json',dict(status='EXPERIMENTAL' if reference_ok else 'FAIL',reference_flow_split_gate='PASS' if reference_ok else 'FAIL',scope='independent frozen rest linear FEM startup and actual nonlinear differences ONLY;NOT continuous nonlinear/SOFA time certification',physical_model='same649-DOF rest M,K,unit tension gradient;C=2M;compiled C2',reference='balanced sparse augmented polynomial matrix exponential,verified1-vs4 segments at1e-8 relative INCLUDING Skin;not an analytic nonlinear trajectory',results=answers,warning='Frozen linearization differs from nonlinear film and T-dependent tendon tangent. Differences are not automatically solver errors or proof of sole cause. Root/Newton/roundoff hypotheses remain independent.'))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag');p.add_argument('--worker');a=p.parse_args()
 if a.worker:worker(Path(a.worker));return
 if not a.tag:raise ValueError('unique tag required')
 matrix=ROOT/'results/autonomous_film_20261118_lateral_modal_scale1419';mm=json.loads((matrix/'summary.json').read_text());control=ROOT/'results/autonomous_film_20261119_stationary_linear_midpoint1602';cm=json.loads((control/'summary.json').read_text());actual=ROOT/'results/autonomous_film_20261119_stationary_free_to50_chain1596_part12';am=json.loads((actual/'summary.json').read_text());cp=actual/'three.checkpoint_250.txt'
 if sha(matrix/'rest.linear.txt')!=mm['raw_hashes']['rest.linear.txt'] or sha(control/'control.so')!=cm['control_binary_sha256'] or sha(cp)!=am['raw_hashes'][cp.name]:raise ValueError('qualified frozen matrix/control/public mass changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(matrix/'rest.linear.txt',out/'rest.linear.txt');shutil.copy2(control/'control.so',out/'control.so');shutil.copy2(cp,out/'actual50.checkpoint');inputs={}
 for us,case in ((200,'20261119_rail_aspect_actual_peak1658'),(100,'20261119_rail_aspect_actual_half1659'),(50,'20261119_rail_aspect_actual_quarter1660')):
  path=ROOT/'results'/('autonomous_film_'+case);m=json.loads((path/'summary.json').read_text());source=path/'rail0.1/actual.csv'
  if m['status']!='PASS' or sha(source)!=m['trials']['0.1']['raw_hashes']['actual.csv']:raise ValueError('qualified actual baseline rail data required')
  shutil.copy2(source,out/('actual_'+str(us)+'.csv'));inputs[case]=sha(path/'summary.json')
 run=guarded([sys.executable,__file__,'--worker',out],out/'process',180);r=dict(status='FAIL',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),matrix_summary_sha256=sha(matrix/'summary.json'),matrix_sha256=sha(out/'rest.linear.txt'),control_summary_sha256=sha(control/'summary.json'),control_binary_sha256=sha(out/'control.so'),actual_summary_hashes=inputs,public_mass_checkpoint_sha256=sha(cp),process=run)
 if run['exit_code']==0:r.update(json.loads((out/'worker.json').read_text()))
 else:r['failure_reason']=(out/'process/stderr.log').read_text().strip()
 r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.txt','.csv','.checkpoint')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('process','results')}))
if __name__=='__main__':main()
