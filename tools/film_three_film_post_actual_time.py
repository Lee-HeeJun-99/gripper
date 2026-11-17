"""Actual SAME-impact post-contact refinement;retain work and tiny residual FAILs."""
import argparse,csv,itertools,json,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
from film_coupled_time import metric
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs=3,required=True);p.add_argument('--work',nargs=3,required=True);a=p.parse_args();runs=[];control_error=0.
 for case,work in zip(a.cases,a.work):
  path=ROOT/'results'/('autonomous_film_'+case);m=json.loads((path/'summary.json').read_text());wp=ROOT/'results'/('autonomous_film_'+work);wm=json.loads((wp/'summary.json').read_text())
  if m['status']!='PASS' or wm['status']!='PASS' or wm['case']!=case or wm['raw_hashes']['three.states.csv']!=sha(path/'three.states.csv') or not m['common_event_exact'] or not m['schedule_valid']:raise ValueError('completed same-impact actual/common-input work required')
  if runs and (m['binary_sha256']!=runs[0][2]['binary_sha256'] or wm['observer_binary_sha256']!=runs[0][5]['observer_binary_sha256']):raise ValueError('same actual AND observer binaries required')
  states=list(csv.DictReader((path/'three.states.csv').open()));rows=list(csv.DictReader((path/'three.rows.csv').open()));inventory=list(csv.DictReader((wp/'inventory.csv').open()));values={r['sample']:{k:float(v) for k,v in r.items() if k!='sample'} for r in csv.DictReader((wp/'observed.csv').open())};energy=[values['end'+str(i)] for i in range(len(states)-1)]
  if len(inventory)!=len(states)-1 or len(rows)!=9*(len(states)-1):raise ValueError('incomplete actual data')
  for f in range(3):
   fields=list(csv.DictReader((path/('film_'+str(f)+'.csv')).open()))
   if len(fields)!=len(states):raise ValueError('incomplete actual field input')
   control_error=max(control_error,max(abs(float(field['T_per_rail'])-value['profile_tension']) for field,value in zip(fields[1:],energy)))
  forces=[]
  for i in range(len(states)-1):
   group=rows[9*i+6:9*i+9];forces.append(-sum((float(r['force'])*np.array([float(r[k]) for k in ('nx','ny','nz')]) for r in group),np.zeros(3)))
  runs.append((case,path,m,states,wp,wm,inventory,energy,np.array(forces)))
 runs.sort(key=lambda r:r[2]['refinement']);pairs={};physical_keys=('U_skin','U_rails','U_attachment','K_film','K_linear','K_rotation');work_keys=('tendon_work_Nmm','external_work_Nmm','damping_work_Nmm','normal_contact_work_Nmm','legacy_field_work_Nmm')
 for l,r in itertools.combinations(runs,2):
  ratio=r[2]['refinement']//l[2]['refinement'];ls=l[3][1:];rs=r[3][ratio::ratio];lw=l[6];rw=r[6][ratio-1::ratio];le=l[7];re=r[7][ratio-1::ratio]
  if len(ls)!=len(rs) or max(abs(float(x['time'])-float(y['time'])) for x,y in zip(ls,rs))>1e-12:raise ValueError('unequal actual clocks;no event interpolation permitted')
  initial=np.fromstring(l[3][0]['q'],sep=' ')
  if not np.array_equal(initial,np.fromstring(r[3][0]['q'],sep=' ')):raise ValueError('different saved actual initial contact state')
  errors={k:metric(np.array([x[k] for x in le]),np.array([x[k] for x in re])) for k in physical_keys};errors.update({k:metric(np.array([float(x[k]) for x in lw]),np.array([float(x[k]) for x in rw])) for k in work_keys})
  for key in ('q','v'):
   x=np.array([np.fromstring(s[key],sep=' ') for s in ls]);y=np.array([np.fromstring(s[key],sep=' ') for s in rs]);origin=initial if key=='q' else np.zeros(len(initial));errors['film_'+key]=metric(x[:,:-6]-origin[:-6],y[:,:-6]-origin[:-6]);errors['body_'+key]=metric(x[:,-6:-3]-origin[-6:-3],y[:,-6:-3]-origin[-6:-3])
  errors['endpoint_world_contact_force']=metric(l[8],r[8][ratio-1::ratio]);impulse=lambda rr:np.array([[float(s['regular_body_impulse_'+d+'_Ns']) for d in 'xyz'] for s in rr]);li,ri=impulse(lw),impulse(rw);widths=np.diff(np.r_[.0002,[float(s['time']) for s in ls]])[:,None];errors['common_window_contact_force']=metric(np.diff(np.vstack((np.zeros((1,3)),li)),axis=0)/widths,np.diff(np.vstack((np.zeros((1,3)),ri)),axis=0)/widths)
  primary={k:v for k,v in errors.items() if k not in ('normal_contact_work_Nmm','legacy_field_work_Nmm')};pairs[l[0]+'__'+r[0]]=dict(status='PASS' if all(v['status']=='PASS' for v in errors.values()) else 'FAIL',errors=errors,stage_consistent_motion_force_stored_work_subset='PASS' if all(v['status']=='PASS' for v in primary.values()) else 'FAIL',signed_integrator_residual_diagnostic=metric(np.array([float(s['signed_residual_Nmm']) for s in lw]),np.array([float(s['signed_residual_Nmm']) for s in rw])))
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');result=dict(status='PASS' if control_error<=1e-18 and all(p['status']=='PASS' for p in pairs.values()) else 'FAIL',scope='actual COMMON fixed200us impact then post-contact200/100/50us1.4ms refinement ONLY;NOT whole-impact time/full energy/grasp',relative_gate=.001,actual_control_max_abs_N=control_error,pairs=pairs,normal_contact_work_note='finite residual lambda*Jv is reported with absolute AND relative error;no small-energy exemption or reclassification as heat',not_qualified=['event-time/impulse refinement','first interval work','birth/release/full cycle','full physical energy','mesh/friction/self-collision/full thickness','wrapping/lift/grasp/12wrench/Optuna'],inputs={r[0]:dict(summary=sha(r[1]/'summary.json'),states=sha(r[1]/'three.states.csv'),work_summary=sha(r[4]/'summary.json'),inventory=sha(r[4]/'inventory.csv')) for r in runs});write_json(out/'summary.json',result);print(json.dumps(dict(status=result['status'],control_error_N=control_error,pairs={k:{n:v['relative_error'] for n,v in p['errors'].items()} for k,p in pairs.items()})))
if __name__=='__main__':main()
