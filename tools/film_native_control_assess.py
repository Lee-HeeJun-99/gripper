"""Compare actual default and free-motion BE before introducing contact."""
import argparse,csv,json
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--default',required=True);p.add_argument('--free',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);inputs={};data=[]
 for name in (a.default,a.free):
  directory=ROOT/'results'/('autonomous_film_'+name)
  if json.loads((directory/'summary.json').read_text())['status']!='PASS':raise RuntimeError('control execution failed')
  file=directory/'1/journal.csv';inputs[str(file.relative_to(ROOT))]=sha(file);data.append(list(csv.DictReader(file.open())))
 if len(data[0])!=len(data[1]) or any(abs(float(x['time'])-float(y['time']))>1e-12 for x,y in zip(*data)):raise RuntimeError('not same physical times')
 metrics={}
 for key in data[0][0]:
  if key in ('time','x'):continue
  x=np.array([float(r[key]) for r in data[0]]);y=np.array([float(r[key]) for r in data[1]]);absolute=float(max(abs(x-y)));scale=float(max(abs(y)));relative=absolute/scale if scale else (0 if absolute==0 else None);metrics[key]=dict(absolute=absolute,relative=relative)
 q0=np.array([[float(v) for v in r['x'].split()] for r in data[0]]);q1=np.array([[float(v) for v in r['x'].split()] for r in data[1]]);error=float(np.max(abs(q0-q1)))
 ok=error<1e-10 and all(v['relative'] is not None and v['relative']<1e-8 for v in metrics.values())
 write_json(out/'summary.json',dict(status='PASS' if ok else 'FAIL',scope='no-contact BE Default/FreeMotion consistency;not contact convergence',inputs=inputs,max_coordinate_error_mm=error,metrics=metrics));print(json.dumps(dict(status='PASS' if ok else 'FAIL',max_coordinate_error=error,metrics=metrics)))
if __name__=='__main__':main()
