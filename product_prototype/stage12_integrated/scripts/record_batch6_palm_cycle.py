"""Record one rejected actual direct-plate design; supervisor save pending."""
import json,shutil
from datetime import datetime,timezone
from baseline_registry import ROOT,REPO,ref,dump
assert not (ROOT/'runtime/STOP').exists()
out=ROOT/'validation/transmission/batch6_palm_cycle1';shutil.copyfile(__file__,out/'recorder.py');shutil.copyfile('/tmp/regrip_palm_cycle_runner.py',out/'runner.py')
cand=ROOT/'cad/exports/revAY_direct_plate1/summary.json';ver=ROOT/'validation/transmission/AY_plate_verify2/summary.json';rd=ROOT/'validation/integrated/AY_plate_readiness2/summary.json';release=ROOT/'validation/integrated/AY_plate_release1/summary.json'
c=json.loads(cand.read_text());v=json.loads(ver.read_text());r=json.loads(rd.read_text());execs=[]
for name,expected in [('build',2),('verify',2),('release',2),('readiness',1),('verify2',2),('readiness2',2)]:
 e=json.loads((out/(name+'_execution.json')).read_text());assert e['exit_code']==expected and e['reaped'] and not e['timeout'];e.update(log=ref(out/(name+'.log')),plan=ref(out/(name+'_plan.json')));execs.append(e)
assert len(c['interferences'])==6 and v['interferences']==c['interferences'] and not v['actual_thread_retention_demonstrated']
summary=dict(status='FAIL_ACTUAL_DIRECT_PLATE_IDLER_INTERFERENCE',task='batch6_simple_palm_mount',track='C',starting_HEAD='af41aca0c845e5f199d39594a7e6c9d1a78154dd',candidate=ref(cand),verification=ref(ver),candidate_readiness=ref(rd),baseline_release_audit=ref(release),producer=ref(out/'recorder.py'),runner=ref(out/'runner.py'),execution=execs,new_product_evidence='Actual single8mm flat annular external plate replacing16mm stepped adapter, six shortened bolt/nut envelopes, full254part STEP/BOM. Six actual retained Idler fastener collisions independently reproduced. This rejects simple uniform plate without retained Idler service clearances.',structural_problem_addressed='Adapter stack simplified into declared finite direct external mating plate; actual interference prevents adoption. No structural capacity solved.',changed_part_IDs=c['changed'],part_count_before=254,part_count_after=254,custom_parts_removed=0,custom_processes_removed=0,new_standard_components=0,custom_part_profile_changes=1,fastener_envelope_changes=6,new_special_tools=0,manufacturing='Flat plate machining versus stepped adapter turning/milling; holes/slots remain. Process/tool/cost savings unqualified.',quantitative=dict(exact_intersection_pairs=v['exact_intersection_pairs'],collisions=v['interferences'],palm_contact_area_mm2=v['palm_contact_area_mm2'],geometric_volume_change_mm3=v['geometric_volume_change_mm3'],mass_change_kg=None),failures_preserved=[ref(ROOT/'validation/transmission/AY_plate_verify1/summary.json'),ref(ROOT/'validation/integrated/AY_plate_readiness1/producer.py'),ref(out/'readiness.log'),ref(cand),ref(ver),ref(rd),ref(release)],verification_corrections=['Initial readiness source path typo caused FileNotFoundError exit1; archived original producer and log preserved; new readiness2 uses actual AY candidate','First verifier used filled cylinder as socket envelope, intersecting bolt tail. Original verify1 FAIL preserved; independent hollow socket workspace verify2 clears. No actual tool/hex qualification.'],six_DOF_capacity_qualified=False,whole_system_release=False,adopted=False,hardware_status='HARDWARE_NOT_MEASURED',SOFA_executed=False,remaining_task_gate_ids=['root_palm_strength','continuous_load_path','changed_stage1_revalidation'],remaining_system_gate_ids=r['required_gate_ids'],unmet=['Six Idler bolt/nut plate collisions: no installation possible as drawn','Actual bolt thread/material/grade/engagement/preload; smooth nut escape is not retention','Actual operating wrench and Palm/plate/fastener/machine stiffness, bearing, lift/horizontal/torsion/bending','Plate lower annular machine face and four5.5mm holes declared; actual machine fasteners/support absent','Swept tendon service, installed assembly, tolerances, loaded flexible surfaces','Same revision full Stage1 and22Stage2 criteria'],followup='Coverage next: batch6_protected_standard_drive. Future Palm architecture must reserve explicit retained Idler fastener/service corridors, evaluate nonuniform three-pad or relocated mount instead of repeating uniform plate thickness scans. Real thread connectors and machine bolts remain required.',known_owned_analysis_children_running=0,save_status='PENDING_SUPERVISOR_LOCAL_SAVE',new_commit_SHA=None)
dump(out/'summary.json',summary)
qp=ROOT/'INTEGRATED_TASKS.json';q=json.loads(qp.read_text());t=next(t for t in q['tasks'] if t['id']==summary['task']);t.update(status='FAIL',last_run_utc=datetime.now(timezone.utc).isoformat(),consecutive_runs=1,result=str((out/'summary.json').relative_to(ROOT)),last_cycle_result=ref(out/'summary.json'),last_cycle_candidate=ref(cand),reason='Uniform direct plate collides with six retained Idler fasteners; no full6DOF strength/thread/machine qualification. Do not adopt. Different support topology and explicit service corridors required.',next='batch6_protected_standard_drive');assert not any(t['status']=='RUNNING' for t in q['tasks']);dump(qp,q)
hp=ROOT/'TRACK_HISTORY.json';h=json.loads(hp.read_text());h['cycles'].append(dict(task=summary['task'],track='C',time_utc=t['last_run_utc'],status=summary['status'],evidence=ref(out/'summary.json'),starting_HEAD=summary['starting_HEAD'],execution='One actual CAD design; six bounded analysis/audit executions reaped; no geometric retry, subagent or manager launch',save='PENDING_SUPERVISOR_LOCAL_SAVE',new_commit_SHA=None));dump(hp,h)
text='''# Batch6 cycle3 — direct Palm plate rejected by retained Idler fasteners (2026-11-27)

Started at af41aca0c845e5f199d39594a7e6c9d1a78154dd. Selected exact task
batch6_simple_palm_mount. One actual bounded design/analysis cycle.
Supervisor local save PENDING; no git add/commit or invented commit SHA.
Result: product_prototype/stage12_integrated/validation/transmission/batch6_palm_cycle1/summary.json.

revAY_direct_plate1 replaces AO stepped16mm adapter with one flat8mm external
mating plate (z=-20..-12, radii20/44), three shorter nominal M4 bolt/nut
pairs. Four5.5mm machine holes at radius38 and lower machine face declared.
Actual7part STEP/STL changes, full254part STEP/BOM retained. Zero parts/custom
processes actually removed; process/tool/cost advantage remains unqualified.

Actual geometry FAIL(exit2), independently reproduced on imported STEP:
six retained Idler base bolt/nut intersections,21.205750/45.908844mm3 each,
against unchanged1e-8mm3 criterion. This uniform flat-plate topology cannot be
installed as drawn. Seven valid single solids and closed oriented positive
meshes pass; finite Palm bearing footprint4341.251589mm2 and geometric volume
change -6032.084131mm3 are geometric quantities, not stiffness or mass.
Conditional head/nut stops and hollow socket workspace samples pass; actual
smooth nut/bolt axial escape remains, so no thread retention/6DOF closure.
Shank clearance means no zero-motion transverse restraint assertion. No loaded
wrench/material/strength/preload/mesh or full assembly/tendon motion PASS.

Initial readiness path typo(exit1) and filled-cylinder socket verifier FAIL
are preserved with original producer/log/results. New readiness2 and hollow
socket verify2 are separate outputs; original failures unchanged. Six bounded
executions completed/reaped under4GiB/420s/one thread; no timeout or SOFA.
Existing release and actual AY readiness remain INTEGRATED_NOT_QUALIFIED,
22Stage2 requirements missing plus same-revision Stage1/system evidence.
AA adopted/AO current unchanged; AX branch and old failures preserved.

Task marked FAIL with concrete redesign prerequisite: explicit retained Idler
fastener/service corridors and alternative nonuniform support topology; no
uniform thickness parameter sweep. Coverage next: batch6_protected_standard_drive.
No RUNNING records or owned live analysis children. No criteria/SDK/manager/
Stage3/hardware/power changes. Pre-existing untracked files preserved.
Exact runtime/authorized_20261127_6/save_request3.json pending supervisor save.

'''
for p in [ROOT/'CHECKPOINT.md',ROOT/'AUTONOMOUS_RESUME.md',REPO/'product_prototype/reports/CHECKPOINT.md',REPO/'product_prototype/reports/AUTONOMOUS_RESUME.md',REPO/'reports/INTEGRATED_CURRENT_STATUS.md',REPO/'reports/INTEGRATED_NEXT_TASKS.md']:p.write_text(text+p.read_text())
print(json.dumps(dict(status=summary['status'],result=ref(out/'summary.json'))))
