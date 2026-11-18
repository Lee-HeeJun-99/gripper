"""Foreground bounded SAME-IVP FREE chain;never a background restart service."""
import argparse,csv,json,shutil,subprocess,sys
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--parent',required=True);p.add_argument('--checkpoint-step',type=int,required=True);p.add_argument('--target-step',type=int,required=True);a=p.parse_args();provider='20261119_stationary_free_actual1590';qualification=ROOT/'results/autonomous_film_20261119_stationary_free_suffix1591';qm=json.loads((qualification/'summary.json').read_text());src=ROOT/'results'/('autonomous_film_'+a.parent);m=json.loads((src/'summary.json').read_text());cp=src/f'three.checkpoint_{a.checkpoint_step}.txt'
 if qm['status']!='PASS' or not qm['all_free_stages_exact'] or not qm['full_checkpoint_tokens_exact'] or m['status']!='PASS' or m['actual_control_error_N']!=0 or not m['ALL_independent_free_stages_exact'] or sha(cp)!=m['raw_hashes'][cp.name]:raise ValueError('actual FREE/replay qualification required')
 tokens=cp.read_text().split();time,h=float(tokens[1]),float(tokens[2]);end=time;remaining=a.target_step-a.checkpoint_step
 if tokens[0]!='REGRIP_STATIONARY_FREE_V1' or int(tokens[3])!=a.checkpoint_step or h!=.0002 or not 0<remaining<=120:raise ValueError('bounded typed physical counter required')
 for _ in range(remaining):end+=h
 if end>.05:raise ValueError('fifty-ms physical bound')
 schedule=[];left=remaining
 while left:
  count=next(n for n in (8,4,2,1) if n<=left);schedule.append(count);left-=count
 forecast=2*(m['process']['runtime_s']+m['reference_process']['runtime_s'])*remaining/m['actual_steps']+30;out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');records=[];r=dict(status='BLOCKED',scope='bounded actual stationary-origin zero-load FREE continuation ONLY;NOT completed recovery/time/energy/wrapping/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),profile_summary_sha256=sha(src/'summary.json'),replay_qualification_sha256=sha(qualification/'summary.json'),start_time_s=time,expected_end_time_s=end,predicted_total_runtime_s=forecast,schedule=schedule,segments=records)
 if forecast>480:r['failure_reason']='measured total policy forecast>480s;NOT OS exhaustion';write_json(out/'summary.json',r);return
 parent=a.parent;step=a.checkpoint_step
 for i,count in enumerate(schedule):
  case=a.tag+'_part'+str(i);before=ROOT/'results'/('autonomous_film_'+parent);checkpoint=before/f'three.checkpoint_{step}.txt';command=[sys.executable,ROOT/'tools/film_lateral_free_sofa.py','--tag',case,'--stationary','--parent',parent,'--checkpoint-step',str(step),'--steps',str(count),'--reuse-build',provider];run=guarded(command,out/('controller_'+str(i)),150);current=ROOT/'results'/('autonomous_film_'+case);summary=current/'summary.json'
  if not summary.exists():r.update(status='FAIL',failure_reason='segment has no completed summary;no later segment run');break
  cm=json.loads(summary.read_text());valid=run['exit_code']==0 and cm['status']=='PASS' and cm['source_checkpoint_sha256']==sha(checkpoint) and cm['actual_steps']==count and cm['accumulated_clock_exact'] and cm['ALL_independent_free_stages_exact'] and cm['actual_control_error_N']==0
  expected=time
  for _ in range(count):expected+=h
  saved=current/f'three.checkpoint_{step+count}.txt';actual=saved.read_text().split() if valid else [];valid=valid and cm['end_time_s']==expected and actual[0]=='REGRIP_STATIONARY_FREE_V1' and float(actual[1])==expected and int(actual[3])==step+count and sha(saved)==cm['raw_hashes'][saved.name]
  applied=[float(x['T_per_rail']) for f in range(3) for x in csv.DictReader((current/f'film_{f}.csv').open())] if valid else [];valid=valid and bool(applied) and all(x==0 for x in applied)
  records.append(dict(case=case,summary_sha256=sha(summary),controller=run,all_gates=valid,zero_actual_field_tension=bool(applied) and all(x==0 for x in applied),start_time_s=time,end_time_s=cm.get('end_time_s')))
  if not valid:r.update(status='FAIL',failure_reason='segment physical/API/clock/control gate failed;no later segment run');break
  parent=case;step+=count;time=expected;r.update(status='EXPERIMENTAL',last_completed_case=parent,last_checkpoint=f'three.checkpoint_{step}.txt',end_time_s=time);write_json(out/'summary.json',r)
 else:r.update(status='PASS' if time==end else 'FAIL',exact_accumulated_end_time=time==end)
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k!='segments'}))
if __name__=='__main__':main()
