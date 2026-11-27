import json,hashlib,datetime
from pathlib import Path
R=Path.cwd();root=R/'product_prototype/stage12_integrated';out=root/'validation/integrated/batch6_chain_cycle1'
def ref(p):return dict(path=str(p.relative_to(R)),SHA256=hashlib.sha256(p.read_bytes()).hexdigest())
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
a=root/'validation/integrated/batch6_chain_stability2/summary.json';v=root/'validation/integrated/batch6_chain_verify2/summary.json';release=root/'validation/integrated/batch6_chain_release1/summary.json';d=json.loads(a.read_text());vd=json.loads(v.read_text())
assert all(d['checks'].values()) and all(vd['checks'].values())
executions=[json.loads((out/(n+'_execution.json')).read_text()) for n in ['analysis','verify','release','analysis2','verify2']];assert all(e['reaped'] and not e['timeout'] for e in executions)
now=datetime.datetime.now(datetime.timezone.utc).isoformat();task='batch6_system_static_dynamic_load_chain'
result=dict(status='CONDITIONAL_AO_GEOMETRIC_STIFFNESS_REFERENCE_VERIFIED_SYSTEM_CHAIN_BLOCKED',task_id=task,starting_HEAD='ca76b4047b2002afbe2128b00d9b87c1756b6f85',actual_research_cycles=1,actual_results=dict(analysis=ref(a),verification=ref(v),release=ref(release)),producer=ref(out/'finalize.py'),runner=ref(out/'runner.py'),executions=executions,actual_evidence='Same AO actual STEP-derived rail sections, envelope span and REST tendon wrench from hash-verified prior specimen; new initial-stress stiffness, consistent mass and dynamic eigenproblem at8/16/32/64elements. Not a repeat of linear force-only equilibrium.',quantitative=dict(euler_compression_N=d['euler_compression_N'],conditional_euler_tension_N=d['conditional_euler_tension_N'],unloaded_omega_rad_s=d['unloaded_omega_rad_s'],loaded_omega_rad_s=d['states'][-1]['omega_loaded_rad_s'],tip_mm=d['analytic_tip'][0],geometric_tip_change_percent=100*(d['analytic_tip'][0]/d['linear_tip'][0]-1),independent_residual_N=vd['max_residual_N']),failures_preserved=[dict(result=ref(root/'validation/integrated/batch6_chain_stability1/summary.json'),reason='Original producer density used7.93e-9kg/mm3 rather than7.93e-6kg/mm3 before kg-to-Ns2/mm conversion. Frequency overestimated sqrt1000; original VERIFIED label is invalid for dynamics. Static/buckling unchanged; original files immutable.'),dict(result=ref(root/'validation/integrated/batch6_chain_verify1/summary.json'),reason='Independent physical density catches modal mismatch .968377; exit2 retained'),dict(result=ref(release),reason='Release exit2 remains INTEGRATED_NOT_QUALIFIED')],limitations=['Typical E193GPa/density7930kg/m3 conditional; no certified lower/upper material bounds','Ideal clamped uniform projected Rail pair; fixed spatial DEAD force, not finite follower tendon or coupled PET/contact','Mass includes only Rail free span, excludes Terminal,Root,PET,drive and payload; not product resonance','Euler reference bifurcation is not installed capacity or force cap; lateral eccentric equilibrium departs linear domain earlier','Geometric potential is dead-load potential, not material stored energy or full trajectory energy closure','No justified demand, rated compatible full AO drive/connector/Palm/Ground chain, damping or full system transient'],remaining_system_gate_ids=['static_dynamic_consistency','continuous_load_path','physical_mass_inertia'],changed_part_IDs=[],CAD_BOM_modified=False,custom_parts_removed=0,custom_processes_removed=0,whole_system_release=False,actual_capacity_qualified=False,SOFA_runs=0,criteria_relaxed=False,known_owned_analysis_children_running=0,save_status='PENDING_SUPERVISOR_VALIDATION_AND_LOCAL_SAVE',new_commit_SHA=None,next='Coverage scheduler selects independent remaining READY mechanisms. This chain task requires compatible rated connectors, justified demand and actual whole-assembly mass before system static/dynamic qualification; no parameter sweep of this reference.')
write(out/'summary.json',result)
p=root/'INTEGRATED_TASKS.json';q=json.loads(p.read_text())
for t in q['tasks']:
 if t['id']==task:t.update(status='BLOCKED',last_run_utc=now,consecutive_runs=1,result='validation/integrated/batch6_chain_cycle1/summary.json',last_cycle_result=ref(out/'summary.json'),reason='Actual AO conditional compression/modal reference verified; complete same-revision chain lacks justified demand,rated connectors,whole mass and finite coupled contact.',unblock='Define rated same-revision Motor-to-Ground connectors and bounded demand/material/mass; integrate finite PET/Rail/contact dynamics. Euler reference is not installed capacity.')
assert not any(t['status']=='RUNNING' for t in q['tasks']);write(p,q)
p=root/'TRACK_HISTORY.json';h=json.loads(p.read_text());h['cycles'].append(dict(task=task,track='A',time_utc=now,status=result['status'],evidence=ref(out/'summary.json'),starting_HEAD=result['starting_HEAD'],execution='One actual AO beam-column/modal cycle; five bounded executions reaped; density failure retained',save='PENDING_SUPERVISOR_LOCAL_SAVE',new_commit_SHA=None));write(p,h)
note=f'''# Batch6 cycle6 — AO initial-stress/modal reference; system chain BLOCKED (2026-11-27)

Started at ca76b4047b2002afbe2128b00d9b87c1756b6f85. One bounded actual
analysis of selected READY {task}.
Result: product_prototype/stage12_integrated/validation/integrated/batch6_chain_cycle1/summary.json.
Actual hash-verified AO STEP-derived Rail sections,77mm envelope span and REST
wrench feed new dead-load geometric stiffness and consistent-mass eigenproblem.
8/16/32/64 refinements, Euler bifurcation, continuous beam-column solution,
independent Gauss weak form, matrix-exponential shooting, general eigenvalues
and perturbed-state rejection pass on corrected result.

1mN tip {d['analytic_tip'][0]:.9g}mm vs linear {d['linear_tip'][0]:.9g}mm;
compression changes tip by {result['quantitative']['geometric_tip_change_percent']:.6g}%.
Conditional Rail-only unloaded omega {d['unloaded_omega_rad_s']:.9g}rad/s;
Euler compression {d['euler_compression_N']:.9g}N is NOT installed capacity,
demand or protection. Typical E/density,ideal clamp,spatial dead force,no PET,
terminal inertia,connectors or full product dynamics. External geometric
potential is not material energy or whole-system closure.

Initial producer density conversion was wrong by1000; independent modal FAIL
exit2 caught it. Original VERIFIED label is invalid for dynamics; original
producer/results preserved. Corrected new tags pass without tolerance change.
Release exit2 remains INTEGRATED_NOT_QUALIFIED; unchanged system/Stage1 gates.
Five children reaped under4GiB/420s, no timeout or live owned children/RUNNING
tasks. No CAD/BOM adoption, parts/process removal, Stage3, SDK, controls edits,
subagents or SOFA runs. Historical failures/unrelated untracked data preserved.
Complete chain task BLOCKED on rated compatible connectors,justified demand,
whole mass and finite coupled PET/Rail/contact dynamics; independent remaining
READY mechanisms are selected by regenerated NEXT_TASK.
Supervisor local save PENDING; no git add/commit or new SHA claimed.
Exact runtime/authorized_20261127_6/save_request6.json awaits validation.

'''
for rel in ['product_prototype/stage12_integrated/CHECKPOINT.md','product_prototype/stage12_integrated/AUTONOMOUS_RESUME.md','product_prototype/reports/CHECKPOINT.md','product_prototype/reports/AUTONOMOUS_RESUME.md','reports/INTEGRATED_CURRENT_STATUS.md','reports/INTEGRATED_NEXT_TASKS.md']:
 p=R/rel;p.write_text(note+p.read_text())
print(result['status'])
