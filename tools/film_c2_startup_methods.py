"""Frozen-FEM startup method screening against qualified sparse exponential."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import argparse,csv,ctypes,importlib.util,json,shutil,subprocess,sys,time
from pathlib import Path
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_transmission_linear import mapping,shape
def worker(out):
 from scipy.sparse import bmat,csr_matrix,diags
 from scipy.sparse.linalg import splu
 import mpmath as mp
 mp.mp.dps=80;spec=importlib.util.spec_from_file_location('frozen_tableau',out/'tableau.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 d=np.fromstring((out/'rest.linear.txt').read_text(),sep=' ');n=int(d[0]);M=d[1:1+n];B=d[1+n:1+2*n];K=d[1+2*n:].reshape(n,n);P=mapping();pick=np.argmax(P==1,axis=0)
 if not np.all(P[pick,np.arange(n)]==1):raise ValueError('exact root coordinate lift required')
 library=ctypes.CDLL(str(out/'control.so'));T=library.regripTransmissionTension;T.argtypes=[ctypes.c_double];T.restype=ctypes.c_double;refs=list(csv.DictReader((out/'reference_states.csv').open()));records=[];errors=[]
 for horizon in (.0002,.0001):
  reference=next(x for x in refs if float(x['h_s'])==horizon and x['kind']=='continuous_sparse_exponential');truth={k:np.fromstring(reference[k],sep=' ') for k in ('q','v')};qref,vref=truth['q'][pick],truth['v'][pick];Eref=dict(U=float(.5*qref@K@qref),K=float(.5*np.dot(M*vref,vref)));sr=shape(truth['q'])
  for stages,substeps in [(2,k) for k in (1,2,4,8,16,32,64)]+[(3,k) for k in (1,2,4,8)]+[(4,k) for k in (1,2,4,8)]:
   if stages==2:r=np.sqrt(3)/6;A=np.array([[.25,.25-r],[.25+r,.25]]);b=np.array([.5,.5]);c=np.array([.5-r,.5+r])
   else:
    aa,bb,cc=module.tableau(stages);A=np.array(aa.tolist(),float);b=np.array(list(bb),float);c=np.array(list(cc),float)
   if np.max(abs(A.sum(axis=1)-c))>1e-14 or abs(b.sum()-1)>1e-14:raise ValueError('collocation tableau consistency fails')
   q=np.zeros(n);v=np.zeros(n);clock=0.;cache={};momentum=0.;work=np.longdouble(0);loss=np.longdouble(0);start=time.perf_counter()
   for micro in range(substeps):
    h=horizon/substeps if micro+1<substeps else horizon-clock
    if h not in cache:
     blocks=[[csr_matrix(((1 if i==k else 0)+2*h*A[i,k])*np.diag(M)+h*h*sum(A[i,j]*A[j,k] for j in range(stages))*K) for k in range(stages)] for i in range(stages)];cache[h]=splu(bmat(blocks,format='csc'))
    tension=np.array([T(float(clock+h*x)) for x in c]);elastic=K@q;rhs=np.array([M*v+h*sum(A[i,j]*(tension[j]*B-elastic) for j in range(stages)) for i in range(stages)]);sv=cache[h].solve(rhs.ravel()).reshape(stages,n);sq=q[None,:]+h*A@sv;force=np.array([tension[j]*B-K@sq[j]-2*M*sv[j] for j in range(stages)]);nq=q+h*(b@sv);nv=v+h*(b@force)/M;momentum+=np.linalg.norm(M*(nv-v)-h*(b@force))
    for j in range(stages):work+=np.longdouble(h*b[j])*np.longdouble(tension[j])*np.longdouble(B@sv[j]);loss+=2*np.longdouble(h*b[j])*np.longdouble(np.dot(M*sv[j],sv[j]))
    q,v=nq,nv;clock+=h
   if clock!=horizon or momentum>1e-17:raise ValueError('unchanged clock/momentum gate fails')
   elapsed=time.perf_counter()-start;E=dict(U=float(.5*q@K@q),K=float(.5*np.dot(M*v,v)));s=shape(P@q);quantities={key:(np.array([E[key]]),np.array([Eref[key]])) for key in E}
   for key,value in (('q',P@q),('v',P@v)):
    for name,part in (('all',slice(None)),('Skin',slice(0,315)),('Rails',slice(315,None))):quantities[name+'_'+key]=(value[part],truth[key][part])
   for key in s:quantities[key]=(np.array([s[key]]),np.array([sr[key]]))
   relative=[]
   for key,(u,w) in quantities.items():
    absolute=float(np.linalg.norm(u-w));scale=float(max(np.linalg.norm(u),np.linalg.norm(w)));error=absolute/scale if scale else 0.;relative.append(error);errors.append(dict(horizon_s=horizon,stages=stages,substeps=substeps,quantity=key,absolute=absolute,relative=error,status='PASS' if error<=.001 else 'FAIL'))
   records.append(dict(horizon_s=horizon,stages=stages,substeps=substeps,linear_core_gate='PASS' if max(relative)<=.001 else 'FAIL',maximum_relative=max(relative),worst_quantity=max(quantities,key=lambda key:next(x['relative'] for x in reversed(errors) if x['quantity']==key and x['horizon_s']==horizon and x['stages']==stages and x['substeps']==substeps)),linear_runtime_s=elapsed,factorizations=len(cache),momentum_sum_bound_Ns=float(momentum),stage_work_Nmm=float(work),damping_loss_Nmm=float(loss),work_reference=None))
 with (out/'methods.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
 with (out/'errors.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(errors[0]));w.writeheader();w.writerows(errors)
 write_json(out/'worker.json',dict(status='EXPERIMENTAL',scope='independent frozen rest FEM method screening ONLY;NOT actual nonlinear/SOFA startup/time/grasp certification',relative_gate=.001,absolute_floor='NONE',methods=records,nonlinear_AD_runtime='NOT MEASURED;linear sparse solve timings are NOT actual SOFA cost forecasts',work_time_gate='NOT RUN;continuous work reference absent,not filled0',selected_nonlinear_method=None))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag');p.add_argument('--worker');a=p.parse_args()
 if a.worker:worker(Path(a.worker));return
 if not a.tag:raise ValueError('unique tag required')
 provider=ROOT/'results/autonomous_film_20261119_c2_frozen_startup1666';pm=json.loads((provider/'summary.json').read_text());table=ROOT/'results/autonomous_film_20261119_c2_transmission_startup1663';tm=json.loads((table/'summary.json').read_text())
 if pm['reference_flow_split_gate']!='PASS' or tm['status']!='PASS' or sha(provider/'startup_states.csv')!=pm['raw_hashes']['startup_states.csv'] or sha(provider/'rest.linear.txt')!=pm['matrix_sha256'] or sha(provider/'control.so')!=pm['control_binary_sha256']:raise ValueError('qualified same frozen model/reference/tableau required')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py')
 for old,new in (('rest.linear.txt','rest.linear.txt'),('control.so','control.so'),('startup_states.csv','reference_states.csv')):shutil.copy2(provider/old,out/new)
 shutil.copy2(table/'runner.py',out/'tableau.py');run=guarded([sys.executable,__file__,'--worker',out],out/'process',180);r=dict(status='FAIL',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),reference_summary_sha256=sha(provider/'summary.json'),tableau_summary_sha256=sha(table/'summary.json'),tableau_source_sha256=sha(out/'tableau.py'),matrix_sha256=sha(out/'rest.linear.txt'),control_binary_sha256=sha(out/'control.so'),process=run)
 if run['exit_code']==0:r.update(json.loads((out/'worker.json').read_text()))
 else:r['failure_reason']=(out/'process/stderr.log').read_text().strip()
 r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.txt','.csv')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('methods','process')}))
if __name__=='__main__':main()
