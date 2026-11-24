"""Read-only task selection;never silently promotes a physical gate."""
import argparse,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
def enrich(queue):
 for t in queue['tasks']:
  defaults=dict(goal=t['scope'],prerequisites=[],expected_outputs=[],validation_criteria=[t['scope']],failure_alternatives=[],successors=[],impact=1,estimated_cost=1,metadata_scope='Legacy scope retained;unspecified outputs/cost are not measured estimates')
  for key,value in defaults.items():t.setdefault(key,value)
 return queue
def select(queue):
 queue=enrich(queue);allowed={'READY','RUNNING','PASS','FAIL','BLOCKED','REJECTED','NOT MEASURED'};byid={t['id']:t for t in queue['tasks']};assert len(byid)==len(queue['tasks'])
 for task in queue['tasks']:
  assert task['status'] in allowed and task['scope']
  assert all(dep in byid for dep in task['prerequisites'])
  for case in task.get('evidence',[]):assert (BASE/'results'/case/'summary.json').exists()
 ready=sorted([t for t in queue['tasks'] if t['status']=='READY' and all(byid[d]['status'] in t.get('prerequisite_states',{}).get(d,['PASS']) for d in t['prerequisites'])],key=lambda t:(t['priority'],-t['impact']/max(t['estimated_cost'],1),t['id']))
 running=[t['id'] for t in queue['tasks'] if t['status']=='RUNNING']
 return dict(next=ready[0] if ready else None,qualified_product=False,running=running,blocked=[t['id'] for t in queue['tasks'] if t['status']=='BLOCKED'],requires_project_reevaluation=not ready and not running)
def main():
 p=argparse.ArgumentParser();p.add_argument('--refresh-metadata',action='store_true',help='Add explicit metadata defaults,never change verdicts or execute tasks');a=p.parse_args();path=BASE/'config/research_queue.json';queue=enrich(json.loads(path.read_text()));result=select(queue)
 if a.refresh_metadata:path.write_text(json.dumps(queue,indent=2)+'\n')
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
