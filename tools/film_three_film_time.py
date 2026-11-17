"""Strict common-time independent3film refinement;small energies not exempted."""
import argparse,csv,itertools,json,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
from film_coupled_time import metric
def same_sources(left,right):
 lp,lm=left;rp,rm=right
 if lm['sources'].keys()!=rm['sources'].keys():return False
 for name,digest in lm['sources'].items():
  if digest==rm['sources'][name]:continue
  if name!='diagnostics/film_three_finger/UniformContact.cpp':return False
  def canonical(path):
   text=(path/'sources'/name).read_text();return text.replace('&&steps!=32','').replace('profiled4/8/16/32 independent grids only','profiled4/8/16 independent grids only')
  if canonical(lp)!=canonical(rp):return False
 return True
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs=3,required=True);a=p.parse_args();runs=[]
 for case in a.cases:
  path=ROOT/'results'/('autonomous_film_'+case);meta=json.loads((path/'summary.json').read_text());rows=list(csv.DictReader((path/'states.csv').open()))
  if meta['status']!='PASS' or len(rows)!=meta['steps']:raise ValueError('completed independent grid required')
  if runs and (any(meta[k]!=runs[0][2][k] for k in ('duration','profile')) or not same_sources((runs[0][1],runs[0][2]),(path,meta))):raise ValueError('physical/source/profile mismatch')
  runs.append((case,path,meta,rows))
 runs.sort(key=lambda r:r[2]['steps']);pairs={}
 for left,right in itertools.combinations(runs,2):
  name,_,lm,lr=left;other,_,rm,rr=right;ratio=rm['steps']//lm['steps']
  if ratio*lm['steps']!=rm['steps']:raise ValueError('nested physical grids required')
  aligned=rr[ratio-1::ratio]
  if max(abs(float(x['time'])-float(y['time'])) for x,y in zip(lr,aligned))>1e-12:raise ValueError('different physical times')
  errors={}
  for key in ('U_skin','U_rails','U_attachment','K_total','external_work','damping_work'):
   errors[key]=metric(np.array([float(r[key]) for r in lr]),np.array([float(r[key]) for r in aligned]))
  for key in ('q','v','normal_force'):
   x=np.array([np.fromstring(r[key],sep=' ') for r in lr]);y=np.array([np.fromstring(r[key],sep=' ') for r in aligned]);errors[key]=metric(x,y)
   if key=='q':
    center=np.array([0,0,-63.44761697652639]);errors['body_displacement']=metric(x[:,-6:-3]-center,y[:,-6:-3]-center);errors['film_displacement']=metric(x[:,:-6],y[:,:-6])
  coarse=np.array([np.fromstring(r['body_impulse'],sep=' ') for r in lr]);fine=np.array([np.fromstring(r['body_impulse'],sep=' ') for r in rr]);summed=fine.reshape(len(lr),ratio,3).sum(axis=1);errors['common_window_contact_force']=metric(coarse/(lm['duration']/lm['steps']),summed/(lm['duration']/lm['steps']))
  diagnostics={key:metric(np.array([float(r[key]) for r in lr]),np.array([float(r[key]) for r in aligned])) for key in ('contact_work','signed_energy_residual')}
  pairs[name+'__'+other]=dict(status='PASS' if all(e['status']=='PASS' for e in errors.values()) else 'FAIL',errors=errors,integration_defect_observations=diagnostics,defect_note='raw absolute/relative values retained;not constitutive dissipation or full energy certificate')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');result=dict(status='PASS' if all(v['status']=='PASS' for v in pairs.values()) else 'FAIL',scope='independent nonlinear3film100us common-time refinement;NOT actual SOFA/fullcycle/energy/grasp',relative_gate=.001,pairs=pairs,inputs={name:dict(summary=sha(path/'summary.json'),states=sha(path/'states.csv')) for name,path,_,_ in runs});write_json(out/'summary.json',result);print(json.dumps(dict(status=result['status'],pairs={k:{n:v['relative_error'] for n,v in value['errors'].items()} for k,value in pairs.items()})))
if __name__=='__main__':main()
