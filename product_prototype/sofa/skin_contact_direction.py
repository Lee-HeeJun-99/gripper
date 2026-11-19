"""Necessary vertical Coulomb-cone direction bound from real native normal rows."""
import argparse,json
from pathlib import Path
import numpy as np
from skin_load_assess import BASE,read,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);p.add_argument('--start',type=float,default=1.6);p.add_argument('--end',type=float,default=2.);a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);meta=json.loads((src/'summary.json').read_text());cfg=json.loads((src/'config.json').read_text());mu=cfg['simulation']['friction']
 if meta['status']!='RUN_COMPLETED_NOT_QUALIFIED' or mu<=0:raise ValueError('completed three-row native Coulomb response required')
 vectors=[];norm_error=[];negative=0
 for r in read(src/'response_rows.csv'):
  if not a.start-1e-12<=float(r['time_s'])<=a.end+1e-12:continue
  if not(any('/object/' in r[k] for k in ('model0','model1')) and any('/skinCollision/' in r[k] for k in ('model0','model1'))):continue
  if (int(r['row_id'])-int(r['first_row']))%3:continue
  lam=float(r['lambda_Ns'])
  if lam<0:negative+=1
  if lam<=0:continue
  normal=np.fromstring(r['object_impulse_Ns_Nms'],sep=' ')[:3]/lam;length=np.linalg.norm(normal)
  if length==0:raise ValueError('zero normal for active object row')
  norm_error.append(abs(length-1));vectors.append(normal/length)
 n=np.array(vectors);nz=n[:,2] if len(n) else np.array([]);bound=nz+mu*np.sqrt(np.maximum(0,1-nz*nz));result=dict(status='DIAGNOSTIC_ONLY',scope='assembled active normal-row directions and necessary vertical Coulomb cone projection;NOT holding capacity,continuous contact area,6DOF closure or measured pressure',case=a.case,window_s=[a.start,a.end],active_normal_rows=len(n),negative_normal_multipliers=negative,normal_unit_error_max=max(norm_error) if norm_error else None,normal_z_range=[float(nz.min()),float(nz.max())] if len(nz) else None,upward_coefficient_range=[float(bound.min()),float(bound.max())] if len(bound) else None,all_active_cones_cannot_push_up=bool(np.all(bound<=0)) if len(bound) else None,contact_area=None,source_sha256=sha(Path(__file__)),input_hashes={f.name:sha(f) for f in (src/'summary.json',src/'response_rows.csv',src/'config.json')});(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
