"""Resume entry: inspect real queue/evidence, never equate empty READY with release."""
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--next',action='store_true');a=p.parse_args()
q=json.loads((ROOT/'STAGE2_TASKS.json').read_text());tasks=q['tasks']
ready=sorted([t for t in tasks if t['status']=='READY'],key=lambda t:t.get('priority',999))
running=[t['id'] for t in tasks if t['status']=='RUNNING']
missing=[t['id'] for t in tasks if t.get('result') and not (ROOT/t['result']).is_file()]
print(json.dumps(dict(release=q['release'],running=running,READY=[t['id'] for t in ready],missing_evidence=missing,
 selected=(ready[0] if ready and a.next else None),note='Queue selection is not execution or qualification. Do not rerun completed tags; implement selected new hypothesis.'),indent=2))
raise SystemExit(2 if missing else 0)
