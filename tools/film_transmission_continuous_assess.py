"""All-pair adaptive-reference tolerance check;linear model only."""
import argparse,csv,itertools,json,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
from film_transmission_linear import shape
from film_transmission_time import relative
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();names=('20261118_transmission_continuous_linear_coarse1215','20261118_transmission_continuous_linear1214','20261118_transmission_continuous_linear_fine1219');cases=[]
 for name in names:
  src=ROOT/'results'/('autonomous_film_'+name);meta=json.loads((src/'summary.json').read_text())
  if meta['status']!='EXPERIMENTAL' or meta['process']['exit_code']:raise ValueError('completed independent continuous linear references required')
  for file,digest in meta['raw_hashes'].items():
   if sha(src/file)!=digest:raise ValueError('reference data changed')
  row=next(csv.DictReader((src/'endpoint.csv').open()));q=np.fromstring(row['q'],sep=' ');v=np.fromstring(row['v'],sep=' ');cases.append((src,meta,row,dict(q=q,v=v,**shape(q))))
 for key in ('rest_matrix_sha256','control_binary_sha256'):
  if len({c[1][key] for c in cases})!=1:raise ValueError('reference input/control differs')
 if len({c[2]['time'] for c in cases})!=1:raise ValueError('reference epochs differ')
 pairs=[]
 for i,j in itertools.combinations(range(3),2):
  errors={k:relative(cases[i][3][k],cases[j][3][k]) for k in cases[i][3]};pairs.append(dict(cases=[names[i],names[j]],metrics=errors,status='PASS' if all(e['pass_0p1'] for e in errors.values()) else 'FAIL'))
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');result=dict(status='PASS' if all(p['status']=='PASS' for p in pairs) else 'FAIL',scope='independent continuous LINEAR reference rtol1e-8/10/12 convergence;NOT nonlinear actual time certification',source_summaries={n:sha(c[0]/'summary.json') for n,c in zip(names,cases)},pairs=pairs);write_json(out/'summary.json',result);print(json.dumps(dict(status=result['status'],maximum_percent=max(e['relative_percent'] for p in pairs for e in p['metrics'].values() if e['relative_percent'] is not None))))
if __name__=='__main__':main()
