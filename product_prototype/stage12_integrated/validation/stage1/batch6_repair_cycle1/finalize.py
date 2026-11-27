import json,hashlib,subprocess
from pathlib import Path
from datetime import datetime,timezone
R=Path.cwd();root=R/'product_prototype/stage12_integrated';out=root/'validation/stage1/batch6_repair_cycle1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return dict(path=str(p.relative_to(R)),SHA256=sha(p))
def dump(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert head=='1f00595abcf73b690dbdd192e520799a49339002'
paths={'analysis':root/'validation/stage1/batch6_idler_after1/summary.json','verification':root/'validation/stage1/batch6_idler_after_verify1/summary.json','same_revision_readiness':root/'validation/integrated/batch6_repair_readiness1/summary.json','baseline_release':root/'validation/integrated/batch6_repair_release1/summary.json'}
records=[]
for name in ('analysis','verify','readiness','release'):
 p=out/(name+'_execution.json');x=json.loads(p.read_text());assert x['reaped'] and not x['timeout'];assert x['exit_code']==(0 if name=='verify' else 2);records.append(dict(execution=ref(p),log=ref(out/(name+'.log')),**x))
a=json.loads(paths['analysis'].read_text());v=json.loads(paths['verification'].read_text());assert all(v['checks'].values());assert a['collision_rows']==6 and len(a['rows'])==36
result=dict(status='ACTUAL_AO_IDLER_AFTER_SEQUENCE_REJECTED_RELEASE_BLOCKED',task_id='batch6_independent_integrated_release_and_repairs',starting_HEAD=head,actual_research_cycles=1,actual_results={k:ref(p) for k,p in paths.items()},executions=records,producer=ref(Path(__file__)),runner=ref(out/'runner.py'),findings=['254-part partition preserved: three38-part Finger modules, three7-part Idler modules and119 fixed/deferred parts','36 finite poses and248 actual Boolean comparisons: six Finger poses still intersect Palm despite deferring Idler assemblies','Largest first rejected-row Terminal-front/Palm witness213.08269300611505mm3; six rejection witnesses independently reimported and verified','18 Idler poses clear only under counterfactual prior nominal Finger installation; no continuous insertion, preassembly, tool or base-fastener access qualification','Actual AO unchanged Stage2 readiness has baseline identity mismatch and22 unqualified criteria; adopted-baseline integrated audit remains24 errors'],whole_system_release=False,adopted=False,changed_part_IDs=[],custom_parts_removed=0,custom_processes_removed=0,save='PENDING_SUPERVISOR_LOCAL_SAVE',new_commit_SHA=None,next='Reject further vertical height scans. Distinct lateral Finger insertion or independently validated split assembly/Palm architecture is needed; preserve actual Idler-after witnesses. System demand/material/load-chain/energy gates remain blocked; Stage3 not authorized.')
dump(out/'summary.json',result)
q=root/'INTEGRATED_TASKS.json';d=json.loads(q.read_text());t=next(t for t in d['tasks'] if t['id']==result['task_id']);t.update(status='BLOCKED',last_run_utc=datetime.now(timezone.utc).isoformat(),consecutive_runs=1,result=str((out/'summary.json').relative_to(root)),reason='Existing unchanged release gates reject full qualification. Actual Idler-after assembly order still collides with Palm at six Finger poses; no direct safe same-revision release repair demonstrated.',next=result['next']);assert not any(t['status']=='RUNNING' for t in d['tasks']);dump(q,d)
h=root/'TRACK_HISTORY.json';d=json.loads(h.read_text());d['cycles'].append(dict(task=result['task_id'],track='C',time_utc=t['last_run_utc'],status=result['status'],evidence=ref(out/'summary.json'),starting_HEAD=head,execution='One actual altered-order assembly cycle; four bounded children completed/reaped; no repeated height sweep',save=result['save'],new_commit_SHA=None));dump(h,d)
note='''# Batch6 cycle9 — Idler-after sequence rejected; release blocked (2026-11-27)

Started at1f00595abcf73b690dbdd192e520799a49339002. Selected READY
batch6_independent_integrated_release_and_repairs. One actual analysis cycle:
validation/stage1/batch6_repair_cycle1/summary.json. Actual AO254 STEP/BOM
identity unchanged; AA304 remains adopted. No CAD/BOM or material change.

Distinct assembly order: three38-part Finger modules followed by three7-part
Idler bracket/wheel/axle/spacer/nut/washer modules; mounting fasteners/tendons
explicitly deferred. Exact254-part partition checked.36 finite poses,248 actual
Boolean comparisons reject six Finger poses against Palm even with Idlers
absent. First largest Terminal-front/Palm witness213.08269300611505mm3.
Independent reimport/reversed-common/volume-subtraction validates6/6 rejected
rows and all input/dependency hashes. Producer exit2 preserved; verifier exit0
certifies rejection only.18 Idler samples clear under counterfactual prior
Finger installation, NOT continuous path/preassembly/tool/base-fastener PASS.

Same-AO readiness and unchanged adopted-baseline integrated release exit2.
22Stage2 criteria, full same-revision Stage1 and SYSTEM_LOAD_TRANSFER evidence
remain unqualified;24baseline audit errors retained. No release, strength,
energy or physical protection PASS. After two distinct top-entry order failures,
stop vertical height scans; investigate lateral insertion or split assembly/
Palm architecture before another actual assembly cycle. Other system gates
need justified demand/material and coupled load/energy evidence, not coupons.

All four analysis children reaped within4GiB/420s; no timeout/live owned child
or RUNNING queue task. STOP absent. Old failures and unrelated untracked work
preserved. No subagents, SDK, criteria, manager/save controls, Stage3, purchase,
hardware or power actions. Supervisor local save PENDING; no git add/commit
attempted or new SHA claimed. runtime/authorized_20261127_6/save_request9.json
contains exact cycle paths/hashes and actual result references.

'''
for rel in ('product_prototype/stage12_integrated/CHECKPOINT.md','product_prototype/stage12_integrated/AUTONOMOUS_RESUME.md','product_prototype/reports/CHECKPOINT.md','product_prototype/reports/AUTONOMOUS_RESUME.md','reports/INTEGRATED_CURRENT_STATUS.md','reports/INTEGRATED_NEXT_TASKS.md'):
 p=R/rel;p.write_text(note+p.read_text())
