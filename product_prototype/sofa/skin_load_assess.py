"""Actual child collision-J row ownership, not proximity/row-count contact area."""
import argparse,csv,json,hashlib
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1]
def read(p):return list(csv.DictReader(p.open()))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);meta=json.loads((src/'summary.json').read_text());cfg=json.loads((src/'config.json').read_text());threshold=cfg['study']['skin_load_bearing_minimum_fraction'];rows=read(src/'object.csv');t=np.array([float(r['time_s']) for r in rows]);index={x:k for k,x in enumerate(t)};forces={name:np.zeros((len(t),6)) for name in ('skin','rail','hardware','support','ambiguous')};dt=meta['dt_s'];masks={}
 for name in ('skin','rail'):masks[name]={(r['time_s'],r['row_id']):int(r['film_mask']) for r in read(src/f'{name}_rows.csv')}
 for row in read(src/'contact_rows.csv'):
  key=(row['time_s'],row['row_id']);skin=masks['skin'].get(key,0);rail=masks['rail'].get(key,0);film=int(row['film_mask']);name='ambiguous' if skin and rail else 'skin' if skin else 'rail' if rail else 'hardware' if int(row['hardware_only_mask']) else 'support' if not film else 'ambiguous';forces[name][index[float(row['time_s'])]]+=np.fromstring(row['object_impulse_Ns_Nms'],sep=' ')/dt
 total=np.array([np.fromstring(r['object_impulse_Ns_Nms'],sep=' ') for r in rows])/dt;err=float(np.max(abs(total-sum(forces.values()))));window=(t>=1.6-1e-12)&(t<=2.+1e-12);weight=cfg['simulation']['sphere_mass_kg']*9.81
 if not window.any():raise ValueError('hold interval NOT RUN')
 fractions={name:float(force[window,2].mean()/weight) for name,force in forces.items()};skin_min=float(np.min(forces['skin'][window,2]/weight));ambiguous=float(np.max(np.linalg.norm(forces['ambiguous'][window,:3],axis=1)));result=dict(status='PASS_SKIN_LOAD_ONLY' if skin_min>=threshold and err<=1e-12 and ambiguous==0 else 'FAIL',scope='Skin force-source qualification ONLY;requires separate unsupported holding,clearance,time convergence gates',case=a.case,predeclared_minimum_skin_weight_fraction=threshold,minimum_skin_weight_fraction=skin_min,mean_vertical_weight_fraction=fractions,force_partition_max_error_N_Nm=err,maximum_ambiguous_force_N=ambiguous,contact_area=None,pressure=None,wire_object_force=None,wire_collision='NOT IMPLEMENTED;no wire contact force claimed',source_sha256=sha(Path(__file__)),input_hashes={p.name:sha(p) for p in (src/'skin_rows.csv',src/'rail_rows.csv',src/'contact_rows.csv',src/'config.json')},surface_rule=cfg['surface_partition'],notes='signed supported load/weight,not clamped percentages;surface partition duplicates boundary features,so requires matched original-scene regression')
 result['row_load_criterion_met']=result['status']=='PASS_SKIN_LOAD_ONLY'
 result['status']='ROW_LOAD_CRITERION_MET_CONTACT_NOT_QUALIFIED' if result['row_load_criterion_met'] else 'FAIL'
 result['physical_skin_holding']='NOT QUALIFIED: requires independent accepted surface geometry,detector source ownership and time gates;child Jacobian influence alone is insufficient'
 result['scope']='JACOBIAN INFLUENCE partition only,NOT direct Skin/Rail contact-force-source certification'
 if (src/'detection_pairs.csv').exists():
  skin_pairs=[r for r in read(src/'detection_pairs.csv') if any('/object/' in r[k] for k in ('model0','model1')) and any('/skinCollision/' in r[k] for k in ('model0','model1'))];result['object_skin_detector_samples']=len(skin_pairs)
  if not skin_pairs:result['status']='FAIL_SKIN_PROVENANCE'
 with (out/'load_partition.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['time_s',*[name+'_vertical_N' for name in forces]]);w.writerows(zip(t,*[force[:,2] for force in forces.values()]))
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
