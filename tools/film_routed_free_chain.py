"""Bounded validated released-state continuation;no background restart service."""
import argparse,csv,json,shutil,subprocess,sys
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();parent='20261118_routed_recovery_window1393';provider='20261118_routed_free_window1392';qualification=ROOT/'results/autonomous_film_20261118_routed_recovery_resume1395';qm=json.loads((qualification/'summary.json').read_text());src=ROOT/'results'/('autonomous_film_'+parent);m=json.loads((src/'summary.json').read_text())
 if qm['status']!='PASS' or qm['suffix_reference_sha256']!=sha(src/'summary.json') or not qm['all_free_stages_exact'] or not qm['full_physical_checkpoint_tokens_exact']:raise ValueError('exact new-window checkpoint replay required')
 schedule=[8]*11+[4];steps=158;time=float((src/f'three.checkpoint_{steps}.txt').read_text().split()[1]);end=time
 for i in range(sum(schedule)):end+=.0002
 if end>.05 or m['actual_steps']!=8:raise ValueError('explicit bounded fifty-ms chain')
 forecast=2*m['process']['runtime_s']*sum(schedule)/8+30;out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');records=[];result=dict(status='BLOCKED',scope='bounded actual quadratic-route FREE continuation chain ONLY;NOT recovery completed/time/energy/wrapping/holding/lift',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),start_time_s=time,expected_end_time_s=end,profile_summary_sha256=sha(src/'summary.json'),resume_qualification_sha256=sha(qualification/'summary.json'),predicted_total_runtime_s=forecast,schedule=schedule,segments=records)
 if forecast>480:write_json(out/'summary.json',result);return
 for i,count in enumerate(schedule):
  case=a.tag+'_part'+str(i);before=ROOT/'results'/('autonomous_film_'+parent);checkpoint=before/f'three.checkpoint_{steps}.txt';command=[sys.executable,ROOT/'tools/film_routed_free_continue.py','--tag',case,'--provider',provider,'--parent',parent,'--checkpoint-step',str(steps),'--steps',str(count)];run=guarded(command,out/('controller_'+str(i)),150);current=ROOT/'results'/('autonomous_film_'+case);summary=current/'summary.json'
  if not summary.exists():result.update(status='FAIL',failure_reason='segment has no completed summary');break
  cm=json.loads(summary.read_text());valid=run['exit_code']==0 and cm['status']=='PASS' and cm['input_checkpoint_sha256']==sha(checkpoint) and cm['start_time_s']==time and cm['actual_steps']==count
  applied=[]
  if valid:
   for f in range(3):
    applied.extend(float(x['T_per_rail']) for x in csv.DictReader((current/f'film_{f}.csv').open()))
   valid=bool(applied) and all(x==0 for x in applied)
  records.append(dict(case=case,summary_sha256=sha(summary),status=cm['status'],controller=run,physical_input_checkpoint_exact=cm.get('input_checkpoint_sha256')==sha(checkpoint),zero_actual_field_tension=bool(applied) and all(x==0 for x in applied),start_time_s=cm['start_time_s'],end_time_s=cm.get('end_time_s')))
  if not valid:result.update(status='FAIL',failure_reason='segment physical/clock/control gate failed;no later segment run');break
  parent=case;steps+=count;time=cm['end_time_s'];result.update(status='EXPERIMENTAL',last_completed_case=parent,last_checkpoint=f'three.checkpoint_{steps}.txt',end_time_s=time);write_json(out/'summary.json',result)
 else:result.update(status='PASS' if time==end else 'FAIL',exact_accumulated_end_time=time==end)
 write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k!='segments'}))
if __name__=='__main__':main()
