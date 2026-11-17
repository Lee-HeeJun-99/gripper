"""C2 common-time motion/separate stored-energy gates;no small-energy exemption."""
import argparse,csv,itertools,json,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
from film_coupled_time import metric
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',required=True);p.add_argument('--energies',nargs='+',required=True);a=p.parse_args();runs=[]
 if len(a.cases)!=len(a.energies) or len(a.cases) not in (2,3):raise ValueError('two or three paired state/inventory cases required;two is NOT base-to-quarter qualification')
 for case,energy in zip(a.cases,a.energies):
  src=ROOT/'results'/('autonomous_film_'+case);s=json.loads((src/'summary.json').read_text());ep=ROOT/'results'/('autonomous_film_'+energy);e=json.loads((ep/'summary.json').read_text());rows=list(csv.DictReader((src/'states.csv').open()));inventories=list(csv.DictReader((ep/'inventory.csv').open()))
  if s['status']!='PASS' or s.get('adaptive_gap_control',False) or e['status']!='PASS' or e['case']!=case or e['raw_sha256']!=sha(src/'states.csv') or len(rows)!=s['steps'] or len(inventories)!=len(rows):raise ValueError('completed uniform independent grid/inventory required')
  if runs:
   old=runs[0][2]
   if any(s[k]!=old[k] for k in ('duration','maximum_tension_N','control','initial')):raise ValueError('physical C2 input mismatch')
   if s.get('exact_order_fallback',False)!=old.get('exact_order_fallback',False):raise ValueError('different distance-order models require separate regression,not merged refinement')
   for k in s['sources'].keys()&old['sources'].keys():
    if k.endswith('.h') and s['sources'][k]!=old['sources'][k]:raise ValueError('compiled kernel mismatch:'+k)
   missing=s['sources'].keys()^old['sources'].keys()
   if any(k.endswith('.h') and k!='models/film_coupled_collocation/GapControlledRows.h' for k in missing):raise ValueError('unreviewed missing header')
  runs.append((case,src,s,rows,inventories,ep))
 runs.sort(key=lambda r:r[2]['steps']);pairs={}
 for left,right in itertools.combinations(runs,2):
  name,_,lm,lr,le,_=left;other,_,rm,rr,re,_=right;ratio=rm['steps']//lm['steps']
  if ratio*lm['steps']!=rm['steps']:raise ValueError('nested physical grids required')
  aligned=rr[ratio-1::ratio];aligned_energy=re[ratio-1::ratio]
  if max(abs(float(x['time'])-float(y['time'])) for x,y in zip(lr,aligned))>1e-12:raise ValueError('different physical sampling times')
  errors={k:metric(np.array([float(r[k]) for r in le]),np.array([float(r[k]) for r in aligned_energy])) for k in ('U_skin','U_rails','U_attachment','K_film','K_linear','K_rotation')}
  for key in ('q','v'):
   x=np.array([np.fromstring(r[key],sep=' ') for r in lr]);y=np.array([np.fromstring(r[key],sep=' ') for r in aligned]);errors['film_'+key]=metric(x[:,:-6],y[:,:-6]);errors['body_'+key]=metric(x[:,-6:-3]-([0,0,-63.44761697652639] if key=='q' else 0),y[:,-6:-3]-([0,0,-63.44761697652639] if key=='q' else 0))
  pairs[name+'__'+other]=dict(status='PASS' if all(v['status']=='PASS' for v in errors.values()) else 'FAIL',errors=errors)
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');result=dict(status='PASS' if all(p['status']=='PASS' for p in pairs.values()) else 'FAIL',scope='independent nonlinear C2 already-touching10ms motion/separate stored-energy refinement ONLY',relative_gate=.001,pairs=pairs,full_time_gate='NOT ASSESSED:contact-force/impulse,tendon-work/fullcycle absent',inputs={name:dict(summary=sha(path/'summary.json'),states=sha(path/'states.csv'),inventory=sha(ep/'inventory.csv')) for name,path,_,_,_,ep in runs})
 write_json(out/'summary.json',result);print(json.dumps(dict(status=result['status'],pairs={k:{n:v.get('relative_error') for n,v in p['errors'].items()} for k,p in pairs.items()})))
if __name__=='__main__':main()
