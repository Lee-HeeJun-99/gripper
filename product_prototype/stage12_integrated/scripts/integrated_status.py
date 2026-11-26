"""Selection/integrity CLI only. Does not pretend to execute research."""
import argparse,json,os
from pathlib import Path
from baseline_registry import ROOT,integrity,dump
def next_task():
    queue=json.loads((ROOT/'INTEGRATED_TASKS.json').read_text())['tasks'];states={x['id']:x['status'] for x in queue}
    history=ROOT/'TRACK_HISTORY.json'
    if history.is_file():
        from product_track_scheduler import select
        return select(queue,json.loads(history.read_text())['cycles'])
    ready=[x for x in queue if x['status']=='READY' and all(states.get(p)=='PASS' for p in x.get('prerequisites',[]))]
    return min(ready,key=lambda x:x.get('priority',999)) if ready else None
def main():
    p=argparse.ArgumentParser();p.add_argument('--next',action='store_true');p.add_argument('--save-next',action='store_true');a=p.parse_args()
    baseline=json.loads((ROOT/'CURRENT_BASELINE.json').read_text());errors=integrity(baseline);task=next_task()
    lock=ROOT/'runtime/manager.lock';running=[]
    queue=json.loads((ROOT/'INTEGRATED_TASKS.json').read_text())['tasks']
    for x in queue:
        if x['status']=='RUNNING':running.append(x['id'])
    result=dict(status='SOURCE_INTEGRITY_PASS' if not errors else 'SOURCE_INTEGRITY_FAIL',errors=errors,
        revision=baseline['revision'],next=task,running_task_records=running,
        warning='Selection is not execution. Manager lock file existence alone does not establish a live process.',
        resume_command='python product_prototype/stage12_integrated/scripts/integrated_status.py --next')
    if a.save_next:dump(ROOT/'NEXT_TASK.json',result)
    print(json.dumps(task if a.next else result,indent=2));raise SystemExit(2 if errors else 0)
if __name__=='__main__':main()
