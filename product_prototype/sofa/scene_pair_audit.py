"""Strict saved state comparison; repeatability is not numerical accuracy."""
import argparse,json
import numpy as np
from skin_load_assess import BASE,read,sha
from pathlib import Path
def main():
 p=argparse.ArgumentParser();p.add_argument('--cases',nargs=2,required=True);p.add_argument('--tag',required=True);p.add_argument('--prefix',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);sources=[BASE/'results'/x for x in a.cases];records=[]
 counts=[json.loads((s/'summary.json').read_text()).get('fingers',3) for s in sources]
 if len(set(counts))!=1:raise ValueError('same finger count required')
 for file,fields in [('object.csv',('rigid_q','rigid_v')),*[(f'finger{k}.csv',('q_m','v_m_s')) for k in range(counts[0])]]:
  x,y=[read(s/file) for s in sources]
  if len(x)!=len(y) and not a.prefix:raise ValueError('complete equal-length comparison required')
  n=min(len(x),len(y));x=x[:n];y=y[:n]
  clock=max(abs(float(r['time_s'])-float(t['time_s'])) for r,t in zip(x,y))
  for field in fields:
   error=max(float(np.max(abs(np.fromstring(r[field],sep=' ')-np.fromstring(t[field],sep=' ')))) for r,t in zip(x,y));records.append(dict(file=file,field=field,maximum_component_difference=error,clock_difference_s=clock,status='PASS' if max(error,clock)<=1e-12 else 'FAIL'))
 result=dict(status='PASS' if all(r['status']=='PASS' for r in records) else 'FAIL',scope='STRICT1e-12 saved-state API comparison only',cases=a.cases,records=records,source_sha256=sha(Path(__file__)),input_hashes={str(s/'summary.json'):sha(s/'summary.json') for s in sources});(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
