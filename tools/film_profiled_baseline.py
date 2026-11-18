"""Typed zero-design-parameter versus lateral6 actual regression,not superiority."""
import argparse,csv,json,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--profiled',required=True);p.add_argument('--design',choices=('profiled','distributed'),default='profiled');p.add_argument('--lateral',required=True);a=p.parse_args();data=[]
 for name,design,amp in ((a.profiled,a.design,0),(a.lateral,'lateral',6)):
  path=ROOT/'results'/('autonomous_film_'+name);m=json.loads((path/'summary.json').read_text())
  ramp=m.get('control_ramp_s')
  if ramp is None and m.get('source_provider_case')=='20261118_lateral_api_build1356':
   provider=ROOT/'results/autonomous_film_20261118_lateral_api_build1356'
   if sha(provider/'summary.json')!=m['source_provider_summary_sha256']:raise ValueError('original10ms provider changed')
   ramp=.01
  if m['status']!='PASS' or m['design']!=design or m.get('design_parameter_value',m.get('amplitude_mm'))!=amp or ramp!=.01:raise ValueError('typed identical physical route required')
  for f,d in m['raw_hashes'].items():
   if sha(path/f)!=d:raise ValueError('raw changed')
  data.append((path,m,list(csv.DictReader((path/'actual.csv').open()))))
 if data[0][1]['raw_hashes']['public_mass.txt']!=data[1][1]['raw_hashes']['public_mass.txt']:raise ValueError('public mass differs')
 x,y=data[0][2],data[1][2]
 if len(x)!=len(y) or [r['time'] for r in x]!=[r['time'] for r in y]:raise ValueError('exact full accepted epochs required')
 errors={k:max(np.max(abs(np.fromstring(i[k],sep=' ')-np.fromstring(j[k],sep=' '))) for i,j in zip(x,y)) for k in ('q','v')}
 stages=(data[0][0]/'actual.csv.stages.csv').read_bytes()==(data[1][0]/'actual.csv.stages.csv').read_bytes()
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');r=dict(status='PASS' if max(errors.values())<=1e-12 and stages else 'FAIL',scope='typed actual zero-profile/lateral6 physical regression ONLY',summaries=[sha(p/'summary.json') for p,_,_ in data],errors={k:float(v) for k,v in errors.items()},all_stage_rows_exact=stages,epochs=len(x));write_json(out/'summary.json',r);print(json.dumps(r))
if __name__=='__main__':main()
