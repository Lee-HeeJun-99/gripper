"""Index ALL original queue verdicts and actual evidence without rerunning them.
An index is not automated physical root-cause inference or a new PASS verdict.
"""
import argparse,collections,hashlib,json,subprocess
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--revision',default='05252d7');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 raw=subprocess.check_output(['git','show',a.revision+':product_prototype/config/research_queue.json'],cwd=BASE.parent);q=json.loads(raw);records=[]
 for task in q['tasks']:
  evidence=[]
  for case in task.get('evidence',[]):
   f=BASE/'results'/case/'summary.json';assert f.is_file();s=json.loads(f.read_text());evidence.append(dict(case=case,sha256=digest(f),actual_recorded_status=s.get('status',s.get('verdict','NOT SPECIFIED')),recorded_scope=s.get('scope','NOT SPECIFIED'),recorded_failure=s.get('failure_reason',s.get('failure_cause','NOT EXPLICIT IN SUMMARY; read original report/Raw'))))
  records.append(dict(id=task['id'],status=task['status'],hypothesis=task.get('hypothesis'),scope=task['scope'],evidence=evidence,validation_criteria=task.get('validation_criteria'),failure_criteria=task.get('failure_criteria')))
 assert len(records)==102
 d=dict(status='COMPLETE_ORIGINAL_QUEUE_EVIDENCE_INDEX_NOT_PROJECT_PASS',revision=subprocess.check_output(['git','rev-parse',a.revision],cwd=BASE.parent,text=True).strip(),original_queue_sha256=hashlib.sha256(raw).hexdigest(),task_count=len(records),states=dict(collections.Counter(t['status'] for t in records)),records=records,new_mechanisms=dict(clutch='Not in original102: actual finite-envelope sensing and next-step cable release;1715/1718 rejected for unstable approach despite zero cross-finger loads.',same_finger_yoke='Old136–158 bridge INITIALIZATION failure is NOT proof of mechanical impossibility. New1720 indexed stock UniformMass path is independently validated, enabling a finite rung and original six-foot bond. Actual1724/1730 Native mapping and initial finite geometry differ from previous width/rail/chamfer/routing sweeps.'),scope='Each original queue entry linked to its existing immutable summary hash/status. Legacy missing reason remains explicit UNKNOWN; no verdict promotion, fictional root cause or research replay. Detailed mechanism hypotheses/actual new tests are in SECTOR_CLUTCH_AND_DORSAL_YOKE_20261125.md.',source_sha256=digest(Path(__file__)))
 (out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in d.items() if k not in ('records','new_mechanisms')},indent=2))
if __name__=='__main__':main()
