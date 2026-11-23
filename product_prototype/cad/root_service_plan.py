"""Executable dependency validation and explicit BLOCKED service plan;no hardware IO."""
import argparse,json,subprocess
from pathlib import Path
from manufacturing_assembly import BASE,sha

def order_steps(steps):
 byid={s['id']:s for s in steps}
 if len(byid)!=len(steps):raise ValueError('duplicate step')
 done=[];active=set()
 def visit(name):
  if name in done:return
  if name not in byid:raise ValueError('unknown prerequisite:'+name)
  if name in active:raise ValueError('cyclic service dependency')
  active.add(name)
  for dep in byid[name]['requires']:visit(dep)
  active.remove(name);done.append(name)
 for name in byid:visit(name)
 return done

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
 if Path(a.tag).name!=a.tag:p.error('local tag required')
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);spec=BASE/'config/root_service_plan_v56.json';ref=BASE/'results/product_root_disconnect1030/summary.json';cfg=json.loads(spec.read_text());audit=json.loads(ref.read_text());order=order_steps(cfg['steps']);byid={s['id']:s for s in cfg['steps']};records=[]
 for name in order:
  step=byid[name];records.append(dict(step,status='BLOCKED_NOT_PHYSICALLY_EXECUTED',blocking_reason=step['unverified'],physical_measurement=None,upstream_blocked=list(step['requires'])))
 preserved=[dict(finger=c['finger'],internal_joins=c['internal_joins'],declared_bond_cut_needed=c['needs_internal_bond_cut_for_DECLARED_partition']) for c in audit['cartridge_partitions']]
 result=dict(status='SERVICE_DEPENDENCY_PLAN_VALID_PHYSICAL_EXECUTION_BLOCKED',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(f.relative_to(BASE)):sha(f) for f in (Path(__file__),spec,ref)},ordered_steps=order,records=records,internal_joins_preserved=preserved,first_missing_mechanism='Reusable drum-side wire termination',actual_joint_cut_qualified=False,physical_steps_executed=0,physical_service_qualified=False,fabrication_ready=False,scope='Software validates uniqueIDs,known prerequisites and acyclic ordering. All physical steps remain BLOCKED/NOT RUN,no hardware IO. Current declared internal joins stay on cartridge;do not cut Skin/Rail bond for exchange. Actual completeness of physical joints,thread/drive/nutretention/wire tension and new mechanism approval still required;valid plan isNOT a valid physical sequence.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],steps=len(records),physical_steps_executed=0)))
if __name__=='__main__':main()
