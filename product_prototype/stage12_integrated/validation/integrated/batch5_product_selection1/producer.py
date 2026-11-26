"""Pure product-oriented selection; never launches sessions or renews budgets."""
import argparse,json,shutil
from pathlib import Path
from baseline_registry import ROOT,ref,dump
TRACKS={'A','B','C'}
def select(tasks,history):
    states={t['id']:t['status'] for t in tasks}
    ready=[t for t in tasks if t['status']=='READY' and all(states.get(p)=='PASS' for p in t.get('prerequisites',[]))]
    # Authorized product-policy only, not a launch/approval/security override.
    # Known diagnostic work cannot starve executable mechanical implementation.
    implementations=[t for t in ready if t.get('execution_class')=='PRODUCT_IMPLEMENTATION']
    if implementations:ready=implementations
    if any(t.get('track') not in TRACKS for t in ready):raise ValueError('READY task lacks explicit A/B/C track')
    recent=[r['track'] for r in history]
    restricted=recent[-1] if len(recent)>=2 and recent[-2]==recent[-1] else None
    alternatives=[t for t in ready if t['track']!=restricted]
    candidates=alternatives if restricted and alternatives else ready
    return min(candidates,key=lambda t:(t.get('priority',99),-t.get('system_gate_contribution',0),t.get('last_run_utc') or '',t['id'])) if candidates else None
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();q=ROOT/'INTEGRATED_TASKS.json';h=ROOT/'TRACK_HISTORY.json';tasks=json.loads(q.read_text())['tasks'];history=json.loads(h.read_text())['cycles'];choice=select(tasks,history)
    out=ROOT/'validation/integrated'/a.tag;out.mkdir(parents=True,exist_ok=False)
    shutil.copyfile(q,out/'queue_snapshot.json');shutil.copyfile(h,out/'history_snapshot.json');shutil.copyfile(__file__,out/'producer.py')
    controls=[]
    toy=[dict(id='finger',status='READY',track='B',priority=0),dict(id='drive',status='READY',track='A',priority=1)]
    assert select(toy,[{'track':'B'},{'track':'B'}])['id']=='drive';controls.append('two B cycles force executable A alternative')
    assert select([toy[0]],history)['id']=='finger';controls.append('no fake work when no alternative')
    assert select([dict(toy[1],prerequisites=['missing'])],[]) is None;controls.append('unmet prerequisite blocked')
    assert select([],[]) is None;controls.append('empty queue is not release')
    actual=dict(id='actual_CAD',track='C',priority=100,status='READY',execution_class='PRODUCT_IMPLEMENTATION')
    assert select([toy[0],actual],[])['id']=='actual_CAD';controls.append('actual executable design outranks generic diagnostic refinement')
    assert select([toy[0],dict(actual,prerequisites=['missing'])],[])['id']=='finger';controls.append('unmet design prerequisite does not block independently executable work')
    result=dict(status='PASS',scope='TRACK SELECTION CONTROLS ONLY, NOT RELEASE',next=choice,controls=controls,queue=ref(out/'queue_snapshot.json'),history=ref(out/'history_snapshot.json'),producer=ref(out/'producer.py'),automatic_sessions_launched=0,budget_renewed=False)
    dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],next_task=choice['id'] if choice else None,track=choice['track'] if choice else None,automatic_sessions_launched=0),indent=2))
if __name__=='__main__':main()
