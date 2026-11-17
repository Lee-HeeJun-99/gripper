"""Common-time motion checks for completed independent uniform FEM grids only."""
import argparse,csv,json,itertools
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs=3,required=True);a=p.parse_args();runs=[]
 for case in a.cases:
  path=ROOT/'results'/('autonomous_film_'+case);meta=json.loads((path/'summary.json').read_text());rows=list(csv.DictReader((path/'states.csv').open()))
  if meta['status']!='PASS' or len(rows)!=meta['steps']:raise ValueError('incomplete independent uniform run')
  runs.append((case,path,meta,rows))
 runs.sort(key=lambda r:r[2]['steps']);base=runs[0][2]
 for _,_,m,_ in runs:
  if any(m[k]!=base[k] for k in ('input_sha256','duration','sources')):raise ValueError('different physics/source/window')
 comparisons=[]
 for left,right in itertools.combinations(runs,2):
  lc,lp,lm,lr=left;rc,rp,rm,rr=right;ratio=rm['steps']//lm['steps']
  if ratio*lm['steps']!=rm['steps']:raise ValueError('non-nested grid')
  aligned=rr[ratio-1::ratio];time_error=max(abs(float(x['time'])-float(y['time'])) for x,y in zip(lr,aligned))
  if time_error>1e-12:raise ValueError('physical time misalignment')
  metrics={}
  for key in ('local_displacement','local_velocity','body_center','body_velocity'):
   x=np.array([np.fromstring(r[key],sep=' ') for r in lr]);y=np.array([np.fromstring(r[key],sep=' ') for r in aligned]);absolute=float(np.max(np.linalg.norm(x-y,axis=1)));scale=float(np.max(np.linalg.norm(y,axis=1)));relative=absolute/scale if scale else (0 if absolute==0 else None)
   metrics[key]=dict(absolute_error=absolute,reference_max_norm=scale,relative_error=relative,status='PASS' if relative is not None and relative<=.001 else 'FAIL')
  comparisons.append(dict(left=lc,right=rc,time_alignment_error_s=time_error,metrics=metrics))
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False)
 result=dict(status='PASS' if all(v['status']=='PASS' for c in comparisons for v in c['metrics'].values()) else 'FAIL',scope='independent FEM common-time motion ONLY;NOT actual SOFA/full time/energy/force convergence',gate=.001,comparisons=comparisons,inputs={case:dict(summary=sha(path/'summary.json'),states=sha(path/'states.csv')) for case,path,_,_ in runs},not_measured=['contact force','attachment/shell/kinetic energy','work','continuous event-time convergence','actual SOFA 1ms'])
 write_json(out/'summary.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
