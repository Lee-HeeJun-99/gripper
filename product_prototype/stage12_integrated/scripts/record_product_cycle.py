"""Record one actually executed product task; never launches or saves Git."""
import argparse,json,datetime,subprocess
from baseline_registry import ROOT,REPO,dump,ref

def main():
    p=argparse.ArgumentParser();p.add_argument('--task',required=True);p.add_argument('--status',choices=['PASS','FAIL','BLOCKED'],required=True);p.add_argument('--result',required=True);p.add_argument('--reason',required=True);a=p.parse_args()
    evidence=ROOT/a.result;actual=json.loads(evidence.read_text())
    if 'status' not in actual:raise ValueError('No actual result classification')
    q=json.loads((ROOT/'INTEGRATED_TASKS.json').read_text());t=next(t for t in q['tasks'] if t['id']==a.task)
    if t['status'] not in ('READY','RUNNING'):raise ValueError('Do not overwrite a completed historical outcome')
    now=datetime.datetime.now(datetime.timezone.utc).isoformat();t.update(status=a.status,result=a.result,reason=a.reason,last_run_utc=now)
    history=json.loads((ROOT/'TRACK_HISTORY.json').read_text());history['cycles'].append(dict(task=t['id'],track=t['track'],time_utc=now,status=a.status,evidence=ref(evidence),starting_HEAD=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),execution='current interactive session; no external launch'))
    count=0
    for row in reversed(history['cycles']):
        if row['track']!=t['track']:break
        count+=1
    t['consecutive_runs']=count
    dump(ROOT/'INTEGRATED_TASKS.json',q);dump(ROOT/'TRACK_HISTORY.json',history)
    print(json.dumps(dict(task=t['id'],status=t['status'],track=t['track'],automatic_budget_remaining=history['automatic_launches_remaining'])))
if __name__=='__main__':main()
