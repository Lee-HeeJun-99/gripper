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
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case');a=p.parse_args()
 if any(Path(n).name!=n for n in (a.tag,a.case) if n):p.error('local tag required')
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);spec=BASE/'config/root_service_plan_v56.json';ref=BASE/'results/product_root_disconnect1030/summary.json';cfg=json.loads(spec.read_text());audit=json.loads(ref.read_text());order=order_steps(cfg['steps']);byid={s['id']:s for s in cfg['steps']};records=[]
 for name in order:
  step=byid[name];records.append(dict(step,status='BLOCKED_NOT_PHYSICALLY_EXECUTED',blocking_reason=step['unverified'],physical_measurement=None,upstream_blocked=list(step['requires'])))
 preserved=[dict(finger=c['finger'],internal_joins=c['internal_joins'],declared_bond_cut_needed=c['needs_internal_bond_cut_for_DECLARED_partition']) for c in audit['cartridge_partitions']]
 result=dict(status='SERVICE_DEPENDENCY_PLAN_VALID_PHYSICAL_EXECUTION_BLOCKED',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(f.relative_to(BASE)):sha(f) for f in (Path(__file__),spec,ref)},ordered_steps=order,records=records,internal_joins_preserved=preserved,first_missing_mechanism='Reusable drum-side wire termination',actual_joint_cut_qualified=False,physical_steps_executed=0,physical_service_qualified=False,fabrication_ready=False,scope='Software validates uniqueIDs,known prerequisites and acyclic ordering. All physical steps remain BLOCKED/NOT RUN,no hardware IO. Current declared internal joins stay on cartridge;do not cut Skin/Rail bond for exchange. Actual completeness of physical joints,thread/drive/nutretention/wire tension and new mechanism approval still required;valid plan isNOT a valid physical sequence.')
 if a.case:
  from assembly_recipe_io import resolve_recipe
  from root_disconnect import internal_joins
  from distal_cartridge_service import classify
  src=BASE/'results'/a.case/'assembly_delta_recipe.json';parts,hashes=resolve_recipe(src);names={p['name'] for p in parts};candidates=[f'f0_c{c}_drum_{s}' for c in (0,1) for s in ('pressure_pad','adjuster_M1p6','nut_M1p6')];present=[n for n in candidates if n in names];result['candidate_mechanisms_present']=present;result['source_case']=a.case;result['assembly_part_count']=len(parts);result['internal_joins_preserved']=[]
  for finger in (0,1,2):
   moving,_,_=classify(parts,finger);joins=internal_joins(parts,moving,finger);result['internal_joins_preserved'].append(dict(finger=finger,internal_joins=joins,declared_bond_cut_needed=any(not j['all_members_move'] for j in joins)))
  if len(present)==6:
   result['first_missing_mechanism']=None
   for r in records:
    if r['id']=='release_drum':r['unverified']=r['blocking_reason']='Both finite channel candidates present;actual wire release/pullout/thread/fixture NOT MEASURED'
  result['first_unqualified_physical_prerequisite']='Actual unload and independent zero-cable-load verification'
  for f in (BASE/'cad/assembly_recipe_io.py',BASE/'cad/root_disconnect.py',BASE/'cad/distal_cartridge_service.py'):hashes[str(f.relative_to(BASE))]=sha(f)
  result['input_hashes'].update(hashes)
  result['scope']+=' Current-case mechanism presence and internal membership rebound to exact parent-hashed CAD. Presence doesNOTcomplete physical unload/thread/retention/pullout/service;all stages stillBLOCKED/NOT RUN. Original1031missing-mechanism observation remains immutable.'
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],steps=len(records),physical_steps_executed=0)))
if __name__=='__main__':main()
