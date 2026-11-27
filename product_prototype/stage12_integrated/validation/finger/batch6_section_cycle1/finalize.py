import json,hashlib,datetime,subprocess
from pathlib import Path
R=Path.cwd();root=R/'product_prototype/stage12_integrated';out=root/'validation/finger/batch6_section_cycle1'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def ref(p):return dict(path=str(p.relative_to(R)),SHA256=hashlib.sha256(p.read_bytes()).hexdigest())
head=subprocess.check_output(['git','rev-parse','HEAD']).decode().strip();assert head=='b36b26e7e006783bc1a42478d799570618ce7af1'
analysis=root/'validation/finger/batch6_section_demand1/summary.json';verify=root/'validation/finger/batch6_section_verify1/summary.json';release=root/'validation/integrated/batch6_section_release1/summary.json'
a=json.loads(analysis.read_text());v=json.loads(verify.read_text());rel=json.loads(release.read_text())
executions=[json.loads((out/(n+'_execution.json')).read_text()) for n in ['analysis','verify','release']]
assert [e['exit_code'] for e in executions]==[0,2,2] and all(e['reaped'] and not e['timeout'] for e in executions)
assert v['checks']['independent_circle_chord_and_inertia'] and not v['checks']['declared_base_to_finest_limit']
assert rel['status']=='INTEGRATED_NOT_QUALIFIED'
task='batch6_strength_worst_case_convergence';now=datetime.datetime.now(datetime.timezone.utc).isoformat()
summary=dict(status='ACTUAL_AO_SECTION_DEMAND_REPRODUCED_REFINEMENT_FAIL_STRENGTH_BLOCKED',task_id=task,starting_HEAD=head,actual_research_cycles=1,producer=ref(Path(__file__)),runner=ref(out/'runner.py'),actual_results=dict(analysis=ref(analysis),independent_verification=ref(verify),release=ref(release)),execution=executions,actual_product_evidence='16 actual AO Rail STEP slab sections at free-span/root-hole stations and four thicknesses; inertia extracted by tensor identity; conditional REST1mN stress section resultants independently integrated',quantitative=dict(free_span_root_nominal_max_MPa=a['stations'][3]['max_abs_sigma_MPa'],no_clamp_transfer_root_hole_counterfactual_MPa=a['stations'][4]['max_abs_sigma_MPa'],base_to_finest_area_relative_error=v['base_to_finest_area_relative_error'],declared_limit=v['declared_limit'],independent_chord_relative_error=v['max_chord_relative_error'],resultant_error=v['max_resultant_error']),failures_preserved=['Producer original VERIFIED label invalid for full refinement: used .001 instead of declared .0001. Archived producer/result immutable; current producer corrected to .0001 without a rerun or limit change.','Independent verifier exits2 on coarse-to-fine .055567% vs declared .01%; no adjacent-only pass.','Integrated release exits2; all22 Stage2 system criteria and same-revision full Stage1 unqualified.'],limitations=['Root-hole moment continuation assumes zero clamp transfer and is NOT actual joint stress','Nominal section stress excludes notch peak,pin contact,clamp/PET sharing,finite deformation,buckling and certified allowable','No actual demand/tolerances/rated connector chain; cannot certify qualified worst case or system convergence'],actual_capacity_qualified=False,whole_system_release=False,CAD_BOM_modified=False,changed_part_IDs=[],parts_added=0,custom_parts_removed=0,custom_processes_removed=0,new_standard_components=0,SOFA_runs=0,remaining_system_gate_ids=[x.split(':')[0] for x in rel['stage2']['errors'] if ': not qualified' in x] if 'errors' in rel['stage2'] else [],blockers=['Certified lot/minimum material and actual demand absent','Actual Root clamp/pin load split and notch/contact stress absent','Full same-revision assembly and dynamic/global energy unresolved'],next='Independent remaining product energy/handoff coverage; for strength first identify actual clamp/pin/PET load sharing and justified demand/material before notch/contact solution. No repeat of uniform linear beam or thickness sweep as system progress.',known_owned_analysis_children_running=0,save_status='PENDING_SUPERVISOR_VALIDATION_AND_LOCAL_SAVE',new_commit_SHA=None)
dump(out/'summary.json',summary)
queue=root/'INTEGRATED_TASKS.json';q=json.loads(queue.read_text());t=next(x for x in q['tasks'] if x['id']==task)
t.update(status='BLOCKED',result=str((out/'summary.json').relative_to(root)),last_run_utc=now,consecutive_runs=t.get('consecutive_runs',0)+1,reason='Actual AO sections/stress resultants reproduced, declared coarse-to-fine section convergence FAIL; no certified material/demand or actual clamp/pin sharing; nominal section arithmetic cannot qualify strength.',next=summary['next'])
assert not any(x['status']=='RUNNING' for x in q['tasks']);dump(queue,q)
p=root/'TRACK_HISTORY.json';h=json.loads(p.read_text());h['cycles'].append(dict(task=task,track='B',time_utc=now,status=summary['status'],evidence=ref(out/'summary.json'),starting_HEAD=head,execution='One actual AO net-section demand cycle; three bounded children reaped, strict convergence FAIL preserved',save='PENDING_SUPERVISOR_LOCAL_SAVE',new_commit_SHA=None));dump(p,h)
text='''# Batch6 cycle8 — actual AO section demand; refinement FAIL (2026-11-27)

Started at b36b26e7e006783bc1a42478d799570618ce7af1. Selected READY
batch6_strength_worst_case_convergence. One bounded actual analysis cycle:
validation/finger/batch6_section_cycle1/summary.json. No CAD/BOM adoption,
parts/process removal or material change. AO254 current/AA304 adopted preserved.

16 original AO Rail STEP slabs at two stations/four thicknesses extract area
and x-bending inertia by tensor identity (no constant-width z-variance guess).
Independent adaptive circle-chord integration agrees within3.80e-10 relative.
Six-point stress integration reproduces section force/moment within3.69e-17.
Perturbed stress control rejected. Actual1mN REST reference gives free-span
root maximum nominal stress0.371353MPa. Root-hole1.296269MPa is explicitly
counterfactual zero-clamp-transfer continuation,NOT actual clamped joint stress.
No notch peak/contact/allowable/demand/strength qualification or material fit.

Independent verifier exits2: base-to-finest area difference0.0555674% exceeds
predeclared0.01%. Producer incorrectly checked0.1% and emitted VERIFIED;
that full-refinement label is invalid. Original producer/result/log retained.
Current script corrected to declared0.01%; no rerun or tolerance relaxation.
Finest section reproduction does NOT override full convergence FAIL.
Release exits2, remains INTEGRATED_NOT_QUALIFIED;22Stage2 and full same-revision
Stage1 unqualified. No system strength, global energy or protection PASS.

Strength task BLOCKED on actual clamp/pin/PET sharing, justified demand,
certified minimum material and finite notch/contact solution. Do not repeat
uniform beam/slab scans as system progress. Independent remaining product
coverage selected by regenerated NEXT_TASK. Three children completed/reaped
under4GiB/420s, no timeout/live owned child or RUNNING queue task. STOP absent.
No subagents, SDK, criteria, manager/save controls, Stage3, hardware or purchase.
Unrelated untracked work and all old failures unchanged. Supervisor local save
PENDING; no git add/commit/new SHA. Exact runtime/authorized_20261127_6/
save_request8.json awaits supervisor validation/local save.

'''
for p in [root/'CHECKPOINT.md',R/'product_prototype/reports/CHECKPOINT.md',R/'product_prototype/reports/AUTONOMOUS_RESUME.md',R/'reports/INTEGRATED_CURRENT_STATUS.md',R/'reports/INTEGRATED_NEXT_TASKS.md']:
 p.write_text(text+p.read_text())
print(json.dumps(summary['quantitative']))
