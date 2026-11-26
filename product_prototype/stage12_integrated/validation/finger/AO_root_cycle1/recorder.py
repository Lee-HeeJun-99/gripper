import sys,json,datetime
from pathlib import Path
sys.path.insert(0,'product_prototype/stage12_integrated/scripts')
from baseline_registry import *
now=datetime.datetime.now(datetime.timezone.utc).isoformat();head='bc8d375ace3b9bc11ef9a5deff464eb3f435885f'
source=ROOT/'cad/exports/revAO_root2/summary.json';d=json.loads(source.read_text());verification=ROOT/'validation/finger/AO_root_verify2/summary.json';out=ROOT/'validation/finger/AO_root_cycle1'
current=dict(revision=d['revision'],adopted=False,definition=ref(source),assembly=d['assembly'],BOM=d['BOM'],verification=ref(verification),parts=d['parts'],official_baseline_unchanged='revAA_heel_relief2',release='CANDIDATE_ONLY_INTEGRATED_NOT_QUALIFIED',hardware='HARDWARE_NOT_MEASURED',powered_operation='NOT_AUTHORIZED',model_binding_status='AL D-drive, AM axial and AN Palm adapter retained. AO root pins implemented; local strain/strength, normal clamp retention and full assembly path unqualified.')
dump(ROOT/'CURRENT_CANDIDATE.json',current)
# Existing Stage2 validator on the actual JSON BOM identity, not baseline/coupon evidence.
from integrated_release_gate import s2,FROZEN_CRITERIA
assert sha(S2/'models/analytical/criteria.json')==FROZEN_CRITERIA
bom=json.loads((REPO/d['BOM']['path']).read_text());assert {r['part_ID']:r['STEP'] for r in bom['parts']}==d['part_references']
assert all(sha(REPO/r['path'])==r['SHA256'] for r in d['part_references'].values())
v=s2.validate(json.loads((S2/'models/analytical/release_registry.json').read_text()),S2,dict(case=d['revision'],assembly_SHA256=d['assembly']['SHA256'],BOM_SHA256=d['BOM']['SHA256'],criteria_SHA256=FROZEN_CRITERIA))
r=dict(status='INTEGRATED_NOT_QUALIFIED',revision=d['revision'],candidate=ref(source),assembly=d['assembly'],BOM=d['BOM'],stage2=v,errors=['stage2: '+x for x in v['errors']]+['No same-revision full Stage1 release','No candidate-matched full SYSTEM_LOAD_TRANSFER evidence'],scope='Existing Stage2 gate on actual AO candidate identity; not full integrated release audit',producer=ref(S2/'scripts/stage2_release_gate.py'),criteria=ref(S2/'models/analytical/criteria.json'),current_candidate=ref(ROOT/'CURRENT_CANDIDATE.json'),whole_system_release=False)
dump(ROOT/'validation/integrated/AO_candidate_readiness1/summary.json',r);dump(ROOT/'CANDIDATE_RELEASE_STATUS.json',r)
execution=[]
for name,producer in [('build',ROOT/'cad/exports/revAO_root1/producer.py'),('verify',ROOT/'validation/finger/AO_root_verify1/producer.py'),('rail_location',None),('build2',ROOT/'cad/exports/revAO_root2/producer.py'),('verify2',ROOT/'validation/finger/AO_root_verify2/producer.py'),('release',ROOT/'scripts/integrated_release_gate.py')]:
 row=dict(name=name,exit_code=int((out/(name+'.exit')).read_text()),log=ref(out/(name+'.log')),actually_executed=True,limit_seconds=420,virtual_memory_KiB=4194304,threads=1)
 if producer:row['producer']=ref(producer)
 execution.append(row)
summary=dict(status='PARTIAL_PRODUCT_IMPLEMENTATION_NOT_QUALIFIED',starting_HEAD=head,candidate=ref(source),verification=ref(verification),release=ref(ROOT/'validation/integrated/AO_root_release1/summary.json'),candidate_readiness=ref(ROOT/'validation/integrated/AO_candidate_readiness1/summary.json'),execution=execution,failure_preservation=[ref(ROOT/'cad/exports/revAO_root1/summary.json'),ref(ROOT/'validation/finger/AO_root_verify1/summary.json'),ref(out/'environment_failures.json')],new_evidence='AN-compatible254part descendant; two integral back-clamp pins per Finger capture PET and each Rail locally. Actual STEP/BOM; independent reimport, closed STL,18signed root stops, distal shape equality and sampled root subassembly pass.',failure_detail='AO1 y=+/-7 pins pass through existing Rail empty region;12Rail stop checks fail. AO1 full installed-assembly lateral insertion also fails against terminal/cassette/bolts/nuts; preserved, NOT solved by root subassembly samples. AO1 nominal Rail area assumptions invalidated by zero removed material; corrected AO2 y=+/-10 verifies actual removed volumes and finite slice areas.',scope='Root-only rigid geometry and unit-resultant section inventory; no loaded elastic contact, local strain/strength, rated capacity or actual free sliding proof',unmet=['Rail finite slice net area0.180000016mm2 and outer ligament0.45mm require bearing/notch/strain/creep and mesh1% checks','Pin bending/shear, front socket support and back-clamp/Palm load transfer','Existing normal retaining bolts/threads and separation; no guessed preload/friction','Full ordered assembly/tool paths; AO1 installed-assembly insertion remains FAIL','Loaded distal PET sliding with actual finite geometry; no two-ended axial lock added','Same-revision Stage1/Stage2, physical mass/inertia, limiter and global energy'],save_status='PENDING_SUPERVISOR_LOCAL_SAVE',whole_system_release=False,SOFA_executed=False,known_owned_analysis_children_running=0)
dump(out/'summary.json',summary)
q=json.loads((ROOT/'INTEGRATED_TASKS.json').read_text())
for t in q['tasks']:
 if t['id'].startswith('batch5_'):
  t.update(target_candidate=ref(source),target_revision=d['revision'],target_parts=d['parts'])
 if t['id']=='batch5_positive_root_retention':
  t.update(status='READY',priority=-3,last_run_utc=now,consecutive_runs=1,result='validation/finger/AO_root_cycle1/summary.json',existing_evidence=['validation/finger/AO_root_cycle1/summary.json','validation/finger/AO_root_verify2/summary.json'],scope='PARTIAL: positive root geometry implemented, loaded strain/strength and complete assembly gates remain unqualified',hypothesis='Continue AO actual root pin bearing/notch/strain and normal retaining fasteners plus full ordered assembly; do not repeat rigid stop scans',next='Inspect small Rail net ligament, source-backed material/loaded contact mesh1%, actual clamp bolt path and full root-before-distal assembly order; preserve distal sliding')
dump(ROOT/'INTEGRATED_TASKS.json',q)
h=json.loads((ROOT/'TRACK_HISTORY.json').read_text());h['cycles'].append(dict(task='batch5_positive_root_retention',track='B',time_utc=now,result=ref(out/'summary.json'),starting_HEAD=head,status=summary['status'],save_status=summary['save_status'],execution='Bounded children build0/verify2/rail-location0/build2-0/verify2-0/release2; all completed; no Git writes'))
dump(ROOT/'TRACK_HISTORY.json',h)
print(json.dumps({'summary':ref(out/'summary.json'),'candidate_errors':len(r['errors']),'stage2_errors':len(v['errors'])}))
