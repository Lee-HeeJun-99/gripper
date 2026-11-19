"""Actual Contact pair -> response Constraint -> row -> object J^T lambda."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from skin_load_assess import BASE,read,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);m=json.loads((src/'summary.json').read_text())
 if m['status']!='RUN_COMPLETED_NOT_QUALIFIED':raise ValueError('complete run required')
 objects=read(src/'object.csv');t=np.array([float(r['time_s']) for r in objects]);index={x:k for k,x in enumerate(t)};names=('skin','rail','guide','support','other');impulses={name:np.zeros((len(t),6)) for name in names};seen=set();rows=read(src/'response_rows.csv');first={}
 for r in rows:
  paths=(r['model0'],r['model1']);v=np.fromstring(r['object_impulse_Ns_Nms'],sep=' ')
  if not any('/object/' in x for x in paths):
   if np.max(abs(v))>1e-12:raise ValueError('non-object collision assigned object impulse')
   continue
  time=float(r['time_s']);key=(time,int(r['row_id']))
  if key in seen:raise ValueError('duplicate response object row')
  seen.add(key);other=paths[1] if '/object/' in paths[0] else paths[0];label='skin' if '/skinCollision/' in other else 'rail' if '/railCollision/' in other else 'guide' if '/guides' in other else 'support' if '/floor/' in other else 'other';impulses[label][index[time]]+=v
  if np.linalg.norm(v)>0:first.setdefault(label,time)
 total=np.array([np.fromstring(r['object_impulse_Ns_Nms'],sep=' ') for r in objects]);error=float(np.max(abs(total-sum(impulses.values()))));dt=m['dt_s'];cfg=json.loads((src/'config.json').read_text());weight=cfg['simulation']['sphere_mass_kg']*9.81;window=(t>=1.6-1e-12)&(t<=2.+1e-12);hold=None
 if window.any():hold={name:dict(mean_force_N=(v[window,:3]/dt).mean(axis=0).tolist(),mean_moment_Nm=(v[window,3:]/dt).mean(axis=0).tolist(),minimum_vertical_weight_fraction=float((v[window,2]/dt/weight).min()),mean_vertical_weight_fraction=float((v[window,2]/dt/weight).mean())) for name,v in impulses.items()}
 result=dict(status='PASS_RESPONSE_PARTITION_ONLY' if error<=1e-12 else 'FAIL',scope='direct native Contact pair + uniquely matched constraint/context/mapped state ancestry + bilateral local row intersection;NOT grasp/time/energy certification',case=a.case,maximum_partition_error_Ns_Nms=error,object_rows=len(seen),first_nonzero_impulse_s=first,hold=hold,normal_tangential_split=None,contact_area=None,pressure=None,skin_holding='NOT QUALIFIED;independent unsupported motion and accepted geometry/time gates required',input_hashes={f.name:sha(f) for f in (src/'summary.json',src/'response_rows.csv',src/'object.csv')},source_sha256=sha(Path(__file__)))
 implementation=(src/'source/Controller.cpp').read_text();result['scope']='Direct Contact pair + unique constraint name/context/mapped-state ancestry + public ConstraintBlockInfo Row IDs;NOT grasp/time/energy certification' if 'owner->getConstraintInfo(nullptr' in implementation else result['scope']
 result['metadata_side_effect']='public getConstraintInfo sets yetIntegrated;internal-history purity NOT claimed;actual q/v equivalence tested separately' if 'owner->getConstraintInfo(nullptr' in implementation else None
 with (out/'response_forces.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['time_s',*[name+'_vertical_N' for name in names]]);w.writerows(zip(t,*[impulses[name][:,2]/dt for name in names]))
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
