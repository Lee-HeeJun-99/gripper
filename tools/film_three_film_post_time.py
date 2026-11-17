"""Independent post-impact common-time gates;all pairs,unchanged0.1%."""
import argparse,csv,itertools,json,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
from film_coupled_time import metric
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs=3,required=True);p.add_argument('--energies',nargs=3,required=True);a=p.parse_args();runs=[]
 for case,energy in zip(a.cases,a.energies):
  path=ROOT/'results'/('autonomous_film_'+case);meta=json.loads((path/'summary.json').read_text());ep=ROOT/'results'/('autonomous_film_'+energy);em=json.loads((ep/'summary.json').read_text())
  if meta['status']!='PASS' or em['status']!='PASS' or em['case']!=case or em['states_sha256']!=sha(path/'states.csv') or em['observed_sha256']!=sha(ep/'observed.csv'):raise ValueError('complete identical-state inventory required')
  if runs and any(meta[k]!=runs[0][2][k] for k in ('initial_sha256','mass_sha256','binary_sha256','start_time','duration')):raise ValueError('same binary/mass/physical initial state and interval required')
  rows=list(csv.DictReader((path/'states.csv').open()));observed=list(csv.DictReader((ep/'observed.csv').open()))
  if len(rows)!=meta['steps'] or len(observed)!=meta['steps']+1:raise ValueError('incomplete run')
  initial=np.fromstring((path/'initial.txt').read_text().splitlines()[1],sep=' ');runs.append((case,path,meta,rows,observed[1:],initial))
 runs.sort(key=lambda r:r[2]['steps']);pairs={}
 for l,r in itertools.combinations(runs,2):
  ratio=r[2]['steps']//l[2]['steps'];lr,rr=l[3],r[3][ratio-1::ratio];le,re=l[4],r[4][ratio-1::ratio]
  if len(lr)!=len(rr) or max(abs(float(x['time'])-float(y['time'])) for x,y in zip(lr,rr))>1e-12:raise ValueError('unequal physical sample clocks')
  errors={k:metric(np.array([float(x[k]) for x in le]),np.array([float(x[k]) for x in re])) for k in ('U_skin','U_rails','U_attachment','K_film','K_linear','K_rotation')}
  for key in ('q','v'):
   x=np.array([np.fromstring(z[key],sep=' ') for z in lr]);y=np.array([np.fromstring(z[key],sep=' ') for z in rr]);origin=l[5] if key=='q' else np.zeros(len(l[5]));errors['film_'+key]=metric(x[:,:-6]-origin[:-6],y[:,:-6]-origin[:-6]);errors['body_'+key]=metric(x[:,-6:-3]-origin[-6:-3],y[:,-6:-3]-origin[-6:-3])
  errors['endpoint_contact_force']=metric(np.array([np.fromstring(x['force'],sep=' ') for x in lr]),np.array([np.fromstring(x['force'],sep=' ') for x in rr]));pairs[l[0]+'__'+r[0]]=dict(status='PASS' if all(e['status']=='PASS' for e in errors.values()) else 'FAIL',errors=errors)
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');result=dict(status='PASS' if all(p['status']=='PASS' for p in pairs.values()) else 'FAIL',scope='independent nonlinear post-impact1.4ms common saved actual state ONLY;NOT actual SOFA/whole-event/full energy/grasp',relative_gate=.001,pairs=pairs,missing=['stage work','whole event time/impulse refinement','actual SOFA continuation refinement','full cycle'],inputs={x[0]:dict(summary=sha(x[1]/'summary.json'),states=sha(x[1]/'states.csv')) for x in runs});write_json(out/'summary.json',result);print(json.dumps(dict(status=result['status'],pairs={k:{n:v['relative_error'] for n,v in p['errors'].items()} for k,p in pairs.items()})))
if __name__=='__main__':main()
