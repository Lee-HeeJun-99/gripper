"""Read-only task selection;never silently promotes a physical gate."""
import json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
def main():
 queue=json.loads((BASE/'config/research_queue.json').read_text());allowed={'READY','RUNNING','PASS','FAIL','BLOCKED','NOT MEASURED'}
 for task in queue['tasks']:
  assert task['status'] in allowed and task['scope']
  for case in task.get('evidence',[]):assert (BASE/'results'/case/'summary.json').exists()
 ready=sorted([t for t in queue['tasks'] if t['status']=='READY'],key=lambda t:t['priority']);print(json.dumps(dict(next=ready[0] if ready else None,qualified_product=False,blocked=[t['id'] for t in queue['tasks'] if t['status']=='BLOCKED']),indent=2))
if __name__=='__main__':main()
