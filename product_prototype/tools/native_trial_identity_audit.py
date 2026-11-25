"""Verify explicit completed trial producers/scenes/recorded binary identities.
Audit-time stock SDK hashes are not misrepresented as historical measurements.
"""
import argparse,json,hashlib
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',required=True);a=p.parse_args();records=[];bad=[]
 for case in a.cases:
  folder=BASE/'results'/case;d=json.loads((folder/'preflight.json').read_text());result=json.loads((folder/'summary.json').read_text());checks={}
  for key,name in [('source_sha256','producer.py'),('scene_sha256','scene.scn')]:
   assert key in d;checks[name]=sha(folder/name)==d[key]
  binary_checks={}
  for key in ['binary_sha256','binary_hashes']:
   for path,h in d.get(key,{}).items():binary_checks[path]=sha(Path(path))==h
  schedule=d.get('schedule')
  if schedule:binary_checks[schedule['binary']]=sha(Path(schedule['binary']))==schedule['binary_sha256'];binary_checks['controller_source']=sha(BASE/'sofa/native_brake_schedule/Controller.cpp')==schedule['controller_source_sha256']
  if 'journal_binary_sha256'in d:binary_checks['point_journal']=sha(BASE/'cad/build_default_control332/libReGripProductSequence.so')==d['journal_binary_sha256']
  if 'softrobots_binary_sha256'in d:binary_checks['SoftRobots']=sha(Path('/home/ubuntu/SOFA/v26.06.00/plugins/SoftRobots/lib/libSoftRobots.so'))==d['softrobots_binary_sha256']
  record=dict(case=case,result_status=result['status'],file_checks=checks,recorded_binary_checks=binary_checks)
  if not all(checks.values()) or not all(binary_checks.values()):bad.append(record)
  records.append(record)
 sdk=Path('/home/ubuntu/SOFA/v26.06.00');stock=[sdk/'bin/runSofa-26.06.00']+[sdk/'lib'/n for n in ['libSofa.Component.Mass.so','libSofa.Component.Mapping.Linear.so','libSofa.Component.Mapping.NonLinear.so','libSofa.Component.SolidMechanics.FEM.Elastic.so','libSofa.Component.ODESolver.Backward.so','libSofa.Component.Constraint.Lagrangian.Solver.so','libSofa.Component.MechanicalLoad.so']];d=dict(status='PASS_RECORDED_TRIAL_IDENTITIES_ONLY' if not bad else 'FAIL_TRIAL_IDENTITIES',records=records,failures=bad,audit_time_stock_SDK_sha256={str(f):sha(f) for f in stock},source_sha256=sha(Path(__file__)),scope='Read-only current identity versus actual frozen producer/preflight/Scene and recorded custom/plugin hashes for explicit completed trials. Retains physics FAIL/factory/errors. Audit-time extra stock hashes are NOT retroactive execution-time capture and not an external backup. Whole Raw preservation is checked by separate immutable manifests; no physics rerun or SDK edit.');out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(dict(status=d['status'],cases=len(records),failures=bad),indent=2))
if __name__=='__main__':main()
