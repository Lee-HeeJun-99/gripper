import json,hashlib,datetime,subprocess
from pathlib import Path
R=Path.cwd();root=R/'product_prototype/stage12_integrated';out=root/'validation/stage1/batch6_stage1_cycle1'
def ref(p):return dict(path=str(p.relative_to(R)),SHA256=hashlib.sha256(p.read_bytes()).hexdigest())
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
assert not (root/'runtime/STOP').exists()
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert head=='249f05d51236ed1d7a38bdde303cead0efc49f03'
a=root/'validation/stage1/batch6_module_entry1/summary.json';v=root/'validation/stage1/batch6_module_entry_verify1/summary.json';rd=root/'validation/integrated/batch6_stage1_readiness1/summary.json';release=root/'validation/integrated/batch6_stage1_release1/summary.json'
d=json.loads(a.read_text());vd=json.loads(v.read_text());r=json.loads(rd.read_text())
assert d['status']=='ASSEMBLY_ALTERNATIVE_REJECTED' and all(vd['checks'].values()) and r['status']=='INTEGRATED_NOT_QUALIFIED'
executions=[]
for name,code in [('entry',2),('verify',0),('release',2),('readiness',2)]:
 e=json.loads((out/(name+'_execution.json')).read_text());assert e['exit_code']==code and e['reaped'] and not e['timeout'];e.update(log=ref(out/(name+'.log')),plan=ref(out/(name+'_plan.json')));executions.append(e)
now=datetime.datetime.now(datetime.timezone.utc).isoformat();task='batch6_same_revision_three_finger_stage1'
summary=dict(status='ACTUAL_AO_TOP_ENTRY_ASSEMBLY_REJECTED_STAGE1_BLOCKED',task_id=task,starting_HEAD=head,actual_research_cycles=1,actual_results=dict(analysis=ref(a),verification=ref(v),same_revision_readiness=ref(rd),baseline_release=ref(release)),producer=ref(out/'finalize.py'),runner=ref(out/'runner.py'),executions=executions,actual_evidence='New ordered preassembled38part Finger modules F0/F1/F2 top-entry alternative against full actual AO hardware. This moves pins,layers,clamp,Terminal,cassette together, unlike prior root-layer lateral insertion. RF mount fasteners and wires explicitly deferred. All254 STEP inputs hashed; inventory partition exact.',quantitative=dict(total_parts=254,module_parts=d['module_parts'],finite_poses=18,exact_boolean_comparisons=d['comparisons'],collision_rows=d['collision_rows'],independent_witnesses=len(vd['witnesses']),largest_verified_witness_mm3=max(w['reversed_common_mm3'] for w in vd['witnesses']),nominal_samples_clear=d['nominal_samples_clear']),failures_preserved=[ref(a),ref(rd),ref(release)],historical_failure_preserved=ref(root/'validation/finger/AO_root_verify1/summary.json'),structural_problem_solved='No capacity solved. Actual installed Idler/Palm hardware obstructs proposed rigid top-entry module mounting; final collision-free placement does not establish assembly feasibility.',changed_part_IDs=[],CAD_BOM_modified=False,custom_parts_removed=0,custom_processes_removed=0,whole_system_release=False,actual_capacity_qualified=False,SOFA_runs=0,known_owned_analysis_children_running=0,save_status='PENDING_SUPERVISOR_VALIDATION_AND_LOCAL_SAVE',new_commit_SHA=None,remaining_system_gate_ids=r['required_gate_ids'],limitations=d['limitations'],followup='Before another same-mechanism trial evaluate manufacturable Idler-after-Finger assembly with actual bracket/axle/tool access, or a distinct lateral module entry. Do not scan top-entry heights or combine AV/AX/AY with AO partial PASS. Independent coverage work remains READY; no exhaustion claim.')
write(out/'summary.json',summary)
p=root/'INTEGRATED_TASKS.json';q=json.loads(p.read_text());t=next(t for t in q['tasks'] if t['id']==task);t.update(status='BLOCKED',last_run_utc=now,consecutive_runs=1,result='validation/stage1/batch6_stage1_cycle1/summary.json',last_cycle_result=ref(out/'summary.json'),reason='Preassembled38part top-entry modules collide with installed Idler/Palm at12/18poses; independently verified. Final nominal clear is not assembly certification. Full same-revision Stage1 and22Stage2 gates absent.',unblock='Implement a justified distinct assembly architecture/sequence: evaluate Idler-after-Finger with actual fastener/tool/service access, or lateral complete module approach. No repeated top-entry height scan. Compatible final CAD/BOM/wire/tolerance/tools and load evidence still required.')
assert not any(t['status']=='RUNNING' for t in q['tasks']);write(p,q)
p=root/'TRACK_HISTORY.json';h=json.loads(p.read_text());h['cycles'].append(dict(task=task,track='C',time_utc=now,status=summary['status'],evidence=ref(out/'summary.json'),starting_HEAD=head,execution='One actual assembly alternative analysis; four bounded executions reaped, no retry sweep',save='PENDING_SUPERVISOR_LOCAL_SAVE',new_commit_SHA=None));write(p,h)
note='''# Batch6 cycle7 — actual AO three-module top-entry rejected (2026-11-27)

Started at249f05d51236ed1d7a38bdde303cead0efc49f03. Selected READY
batch6_same_revision_three_finger_stage1. One bounded actual assembly analysis:
validation/stage1/batch6_stage1_cycle1/summary.json. No CAD/BOM adoption or
parts/process removal. AO254 current and AA304 adopted remain unchanged.

Alternative sequence preassembles38parts per Finger (root pins/layers/clamps,
Terminal/swivel/cassette), then inserts F0,F1,F2 from +Z. RF Palm mounting
fasteners and tendon wires explicitly deferred; all254parts partitioned.
18finite poses,595actual Boolean comparisons:12poses collide with existing
Idler/bracket/Palm. Final nominal poses clear. Thus collision-free final CAD
and prior root-only subassembly samples cannot certify this assembly sequence.
Independent reimport/reversed-common/volume-subtraction verifies one actual
witness for each rejected row (12/12); input/dependency hashes pass. First
largest F0 Terminal-back/Idler witness162.4476525mm3. Original failure exit2
retained; verifier exit0 certifies rejection only. No continuous path PASS.
Later sectors are counterfactual nominal installations after earlier rejection.

Same-AO readiness and unchanged baseline release both exit2, remain
INTEGRATED_NOT_QUALIFIED. All22Stage2 criteria and full same-revision Stage1
still unqualified. No load/strength/global energy/physical protection claim.
Task BLOCKED: evaluate manufacturable Idler-after-Finger with actual bracket/
axle/tool access or a distinct lateral module path before another assembly
trial. Do not repeat top-entry height scans or merge incompatible candidate
partial PASS. Independent READY coverage work remains; consult NEXT_TASK.

Four children completed/reaped under4GiB/420s, no timeout/live owned children
or RUNNING queue records. No subagents, SDK, criteria, manager/save controls,
Stage3, purchase, hardware or power actions. Old failures and unrelated
untracked work preserved. Supervisor local save PENDING; no git add/commit
or new commit SHA. runtime/authorized_20261127_6/save_request7.json is the
exact pending save request; this checkpoint does not claim supervisor save.

'''
for p in [root/'CHECKPOINT.md',root/'AUTONOMOUS_RESUME.md',R/'product_prototype/reports/CHECKPOINT.md',R/'product_prototype/reports/AUTONOMOUS_RESUME.md',R/'reports/INTEGRATED_CURRENT_STATUS.md',R/'reports/INTEGRATED_NEXT_TASKS.md']:p.write_text(note+p.read_text())
print(json.dumps(dict(result=ref(out/'summary.json'),status=summary['status'])))
