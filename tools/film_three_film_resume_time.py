"""Same-start actual unload100/50us comparison;no small-residual exemption."""
import argparse,csv,json,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs=2,required=True);p.add_argument('--inventories',nargs=2,required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');data=[];provenance=[];initial=None
 for case,inventory in zip(a.cases,a.inventories):
  src=ROOT/'results'/('autonomous_film_'+case);meta=json.loads((src/'summary.json').read_text());inv=ROOT/'results'/('autonomous_film_'+inventory);im=json.loads((inv/'summary.json').read_text())
  if meta['status']!='EXPERIMENTAL' or meta['process']['exit_code'] or meta['sofa_errors'] or im['status']!='PASS' or im['provenance'][0]['case']!=case:raise ValueError('complete actual/consistent inventory required')
  for n,h in meta['raw_hashes'].items():
   if sha(src/n)!=h:raise ValueError('actual raw changed')
  if sha(inv/'observed.csv')!=im['observed_sha256'] or sha(inv/'inventory.csv')!=im['inventory_sha256']:raise ValueError('inventory raw changed')
  tokens=(src/'input.checkpoint').read_text().split();q0=np.array(list(map(float,tokens[5:1958])));v0=np.array(list(map(float,tokens[1958:3911])));iqv=np.r_[q0,v0]
  if initial is None:initial=iqv
  elif not np.array_equal(iqv,initial):raise ValueError('different physical initial states')
  states=list(csv.DictReader((src/'three.states.csv').open()));rows=list(csv.DictReader((src/'three.rows.csv').open()));q=np.fromstring(states[-1]['q'],sep=' ');v=np.fromstring(states[-1]['v'],sep=' ');observed=list(csv.DictReader((inv/'observed.csv').open()));end=next(r for r in observed if r['sample']=='end'+str(len(states)-1));values=dict(film_q_change=q[:-6]-q0[:-6],film_velocity=v[:-6],body_displacement=q[-6:-3]-q0[-6:-3],body_linear_velocity=v[-6:-3],body_angular_velocity=v[-3:],endpoint_normal_force=np.array([float(r['force']) for r in rows[-3:]]));values.update({k:float(end[k]) for k in ('U_skin','U_rails','U_attachment','K_film','K_linear','K_rotation')});values.update({k:float(im['end'][k]) for k in ('tendon_work_Nmm','external_work_Nmm','damping_work_Nmm','normal_constraint_work_Nmm')});data.append((values,float(states[-1]['time'])));provenance.append(dict(case=case,summary_sha256=sha(src/'summary.json'),inventory=inventory,inventory_summary_sha256=sha(inv/'summary.json'),dt=meta['dt']))
 metrics={}
 for k in data[0][0]:
  x,y=np.asarray(data[0][0][k]),np.asarray(data[1][0][k]);absolute=float(np.linalg.norm(x-y));reference=float(np.linalg.norm(y));relative=absolute/reference if reference else (0. if absolute==0 else None);metrics[k]=dict(absolute_error=absolute,reference_norm=reference,relative_error=relative,status='PASS' if relative is not None and relative<=.001 else 'FAIL')
 result=dict(status='PASS' if all(m['status']=='PASS' for m in metrics.values()) else 'FAIL',scope='actual common20..22ms100/50us listed pair ONLY;NOT all-pair/full-cycle time certification',provenance=provenance,relative_gate=.001,actual_end_clock_difference_s=abs(data[0][1]-data[1][1]),metrics=metrics,base200us_trial='1024 FAIL full horizon;do not reinterpret its accepted prefix as a completed convergence run',full_time_gate='FAIL remains;base-to-quarter/full-cycle not qualified',interpretation='normal constraint-work numerical residual retained under relative gate;NOT heat/physical Coulomb loss;root work remains NULL');write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
