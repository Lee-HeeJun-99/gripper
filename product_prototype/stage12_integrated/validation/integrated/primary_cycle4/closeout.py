import json,sys,subprocess,shutil
from pathlib import Path
b=Path('product_prototype/stage12_integrated').resolve();sys.path.insert(0,str(b/'scripts'))
from baseline_registry import ref,sha,dump,REPO
out=b/'validation/integrated/primaryP1_cycle4_closeout';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');cycle=b/'validation/integrated/primary_cycle4';ledger=json.loads((b/'runtime/goal_authorized_20261127_7/ledger.json').read_text());pins={p:sha(REPO/p)==h for p,h in ledger['source_pins'].items()};assert all(pins.values());assert not(b/'runtime/STOP').exists()
qpath=b/'INTEGRATED_TASKS.json';q=json.loads(qpath.read_text());primary=ref(b/'PRIMARY_PRODUCT.json')
for t in q['tasks']:
 if t['id'].startswith('goal_primary_'):t['primary_state']=primary
assert not any(t['status']=='RUNNING' for t in q['tasks']);dump(qpath,q)
# First audit failed only while serializing a relative reference. Preserve exact source and log.
f=b/'validation/integrated/primaryP1_release4';dump(f/'summary.json',dict(status='RELEASE_AUDIT_REFERENCE_SERIALIZATION_ERROR_NO_RESULT',producer=ref(f/'producer.py'),execution=ref(cycle/'release4_execution.json'),log=ref(cycle/'release4.log'),reason='Read-only gate called,but relative Path passed to absolute-repository ref() caused ValueError before result serialization. No release result claimed. release5 uses resolved base and records actual unchanged24-error audit.',whole_system_release=False))
e=[]
for p in sorted(cycle.glob('*_execution.json')):
 d=json.loads(p.read_text());assert d['reaped'];d['record']=ref(p);d['log']=ref(cycle/p.name.replace('_execution.json','.log'));e.append(d)
checks=dict(source_pins_unchanged=all(pins.values()),no_running_queue=True,STOP_absent=True,all_children_reaped=all(x['reaped'] for x in e),all_analysis_limits=all(x['memory_limit_bytes']==4294967296 and x['timeout_s']==420 and not x['timeout'] for x in e),HEAD_unchanged=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()=='6be7bb3b4011819546dbab566ad3ccbaf5de5cfd',index_empty=not subprocess.check_output(['git','diff','--cached','--name-only'],text=True).strip())
assert all(checks.values());dump(out/'summary.json',dict(status='ACTUAL_P1_CYCLE4_SAVED_BYTE_HANDOFF_READY_NOT_RELEASE',candidate=ref(b/'cad/exports/primaryP1_clamp10/summary.json'),engineering=ref(cycle/'summary.json'),actual_integrated_release=ref(b/'validation/integrated/primaryP1_release5/summary.json'),additional_audit_serialization_failure=ref(f/'summary.json'),checks=checks,source_pins=pins,executions=e,recorded_children_reaped=len(e),recorded_child_seconds=sum(x['elapsed_s'] for x in e),owned_analysis_children_running=0,timeouts=0,all22system_gates_unqualified=True,stage3_authorized=False,whole_system_release=False,producer=ref(out/'producer.py')))
print(json.dumps(dict(children=len(e),child_seconds=sum(x['elapsed_s'] for x in e),checks=checks)))
