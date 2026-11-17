"""Causal paired clock-input fix;owner trajectory purity,NOT unchanged wrong FF force."""
import argparse,csv,json,shutil
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--before',nargs=3,required=True);p.add_argument('--after',nargs=3,required=True);p.add_argument('--work',nargs=3,required=True);a=p.parse_args();pairs={};ok=True
 for before,after,work in zip(a.before,a.after,a.work):
  bp=ROOT/'results'/('autonomous_film_'+before);ap=ROOT/'results'/('autonomous_film_'+after);wp=ROOT/'results'/('autonomous_film_'+work);bm=json.loads((bp/'summary.json').read_text());am=json.loads((ap/'summary.json').read_text());wm=json.loads((wp/'summary.json').read_text())
  if bm['status']!='PASS' or am['status']!='PASS' or wm['status']!='PASS' or not am['synchronize_child_clocks'] or bm['refinement']!=am['refinement'] or wm['case']!=after:raise ValueError('completed paired same-grid fix and matching observer required')
  names=['three.states.csv','three.rows.csv','three.event.csv','three.impact_rows.csv']+['displacement_'+str(f)+'.csv' for f in range(3)];exact={n:sha(bp/n)==sha(ap/n) for n in names};observed={r['sample']:r for r in csv.DictReader((wp/'observed.csv').open())};unchanged=True;old_error=new_error=0.
  for f in range(3):
   br=list(csv.DictReader((bp/('film_'+str(f)+'.csv')).open()));ar=list(csv.DictReader((ap/('film_'+str(f)+'.csv')).open()))
   if len(br)!=len(ar) or len(ar)!=am['macro_steps']:raise ValueError('incomplete paired fields')
   for i,(b,r) in enumerate(zip(br,ar)):
    unchanged=unchanged and all(b[k]==r[k] for k in b if k not in ('U_tendon_generator','T_per_rail','tendon_work'))
    reference=float(observed['initial' if i==0 else 'end'+str(i-1)]['profile_tension']);old_error=max(old_error,abs(float(b['T_per_rail'])-reference));new_error=max(new_error,abs(float(r['T_per_rail'])-reference))
  clocks=list(csv.DictReader((ap/'clock.csv').open()));sync=all(int(r['synchronized_contexts'])==11 and float(r['minimum_next_dt'])==float(r['next_dt'])==float(r['maximum_next_dt']) for r in clocks);valid=all(exact.values()) and unchanged and sync and new_error<=1e-18 and (old_error==0 if am['refinement']==1 else old_error>1e-18);ok=ok and valid;pairs[before+'__'+after]=dict(status='PASS' if valid else 'FAIL',seven_owner_geometry_CSV_exact=exact,field_mechanical_observables_exact=unchanged,old_control_max_abs_N=old_error,new_control_max_abs_N=new_error,all11_contexts_synchronized=sync,before_summary=sha(bp/'summary.json'),after_summary=sha(ap/'summary.json'),work_summary=sha(wp/'summary.json'))
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');result=dict(status='PASS' if ok else 'FAIL',scope='causal NEXT dt child-context input correction;custom owner trajectories unchanged,previous wrong ForceField endpoint tension corrected;NOT full force/tangent/time/energy/grasp',pairs=pairs,preserved_failure='20261118_three_film_post_actual_time984',excluded_changed_field_columns=['U_tendon_generator','T_per_rail','tendon_work'],explanation='these columns MUST change when correcting old field input;never claimed equal to the old incorrect endpoint force query');write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
