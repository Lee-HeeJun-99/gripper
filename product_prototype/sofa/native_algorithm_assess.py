"""Same-input native constraint algorithm sensitivity,not a time/convergence PASS."""
import argparse,json,csv,hashlib
import numpy as np
from native_time_assess import BASE,read,features,fingerprint
def main():
 p=argparse.ArgumentParser();p.add_argument('--cases',nargs=2,required=True);p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=[BASE/'results'/x for x in a.cases];meta=[json.loads((x/'summary.json').read_text()) for x in src]
 if any(m['status']!='RUN_COMPLETED_NOT_QUALIFIED' for m in meta) or len({m['binary_sha256'] for m in meta})!=1 or len({m['dt_s'] for m in meta})!=1 or fingerprint(src[0],True)!=fingerprint(src[1],True):raise ValueError('completed SAME physical input,binary,dt required;only native constraint solver may differ')
 data=[features(s,m) for s,m in zip(src,meta)];n=min(len(x[0]) for x in data);records=[]
 for k in range(n):
  if abs(data[0][0][k]-data[1][0][k])>1e-12:raise ValueError('clock mismatch')
  for key,x in data[0][1].items():
   u=x[k];v=data[1][1][key][k];absolute=float(np.linalg.norm(u-v));denom=max(float(np.linalg.norm(u)),float(np.linalg.norm(v)));records.append(dict(time_s=float(data[0][0][k]),quantity=key,absolute=absolute,relative=absolute/denom if denom else 0))
 stats={}
 for name,s in zip(a.cases,src):
  rows=read(s/'object.csv')[:n];stats[name]=dict(max_native_error=max(float(r['solver_error']) for r in rows),iteration_limited_frames=sum(int(r['solver_iterations'])>=1000 for r in rows),runtime_s=json.loads((s/'summary.json').read_text())['process']['runtime_s'])
 result=dict(status='ALGORITHM_SENSITIVITY_ONLY_NOT_APPROVAL',cases=a.cases,horizon_s=float(data[0][0][n-1]),stats=stats,metrics={key:max((r for r in records if r['quantity']==key),key=lambda x:x['absolute']) for key in data[0][1]},scope='same native model different numerical constraint algorithms;do NOT replace dt refinement or certify nonlinear path residual from scalar solver error',source_sha256=hashlib.sha256(__import__('pathlib').Path(__file__).read_bytes()).hexdigest())
 with (out/'errors.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=records[0]);w.writeheader();w.writerows(records)
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],horizon_s=result['horizon_s'],stats=stats)))
if __name__=='__main__':main()
