"""Bounded read-only independent analysis chain for a completed full trial.
An analysis exit0 never overrides a FAIL verdict. No Native rerun.
"""
import argparse,json
from pathlib import Path
from analyse import BASE,sha
from native_bending_coupon import guarded

def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;meta=json.loads((src/'summary.json').read_text());assert meta['status']=='RUN_COMPLETED_NOT_QUALIFIED','Actual completed valid2s Native required';out=BASE/'results'/a.tag;assert not out.exists();names={key:a.tag+'_'+key for key in ['holding','balance','clearance','purity','goal']};assert all(not (BASE/'results'/n).exists() for n in names.values());out.mkdir();(out/'producer.py').write_bytes(Path(__file__).read_bytes());python='/home/ubuntu/miniconda3/envs/robot_ws/bin/python';commands=[('holding','holding_assess.py',['--case',a.case]),('balance','winch_object_balance.py',['--case',a.case]),('clearance','actual_hardware_clearance.py',['--case',a.case]),('purity','brake_prefix_compare.py',['--case',a.case]),('goal','unbraced_winch_holding_assess.py',['--case',a.case,'--holding',names['holding'],'--balance',names['balance'],'--clearance',names['clearance']])];steps=[];complete=True
 for key,script,args in commands:
  process=guarded([python,BASE/'sofa'/script,*args,'--tag',names[key]],out/(key+'_process'),120);record=dict(step=key,source_sha256=sha(BASE/'sofa'/script),process=process)
  if process['exit_code']!=0:steps.append(record);complete=False;break
  path=BASE/'results'/names[key]/'summary.json';result=json.loads(path.read_text());record.update(result=result['status'],result_summary_sha256=sha(path));steps.append(record)
 goal=json.loads((BASE/'results'/names['goal']/'summary.json').read_text()) if complete else {};purity=json.loads((BASE/'results'/names['purity']/'summary.json').read_text()) if complete else {};success=complete and goal['status']=='PASS_EXPLORATORY_UNBRACED_100G_HOLDING_ONLY' and purity['status']=='PASS_PREBRAKE_STATE_PURITY_AND_CONFIGURED_LOSS_ONLY';d=dict(status='PASS_EXPLORATORY_UNBRACED_ASSUMED_BRAKE_HOLDING_ONLY' if success else 'FAIL_OR_INCOMPLETE_BRACKETED_ASSESSMENT',case=a.case,analyses=names,steps=steps,goal=goal,source_sha256=sha(Path(__file__)),native_summary_sha256=sha(src/'summary.json'),scope='Analysis only, no new Native or force/state changes. Original161sample Holding threshold, actual hardware clearance/no-bracing/FEM/force/momentum and before-brake purity all required. Assumed actuator-loss coefficient is not actual motor/hardware/time/mesh/finitewire qualification. Process exit0 alone never passes physics.');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(dict(status=d['status'],case=a.case,analyses=names,goal=goal),indent=2))
if __name__=='__main__':main()
