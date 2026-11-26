"""Record one finite actual-root pressure analysis, no system promotion."""
import json,datetime,shutil
from baseline_registry import ROOT,REPO,ref,dump
from integrated_release_gate import audit

def main():
    assert not (ROOT/'runtime/STOP').exists()
    out=ROOT/'validation/finger/AK_root_pressure_cycle1';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    a=ROOT/'validation/finger/AK_root_pressure1/summary.json';v=ROOT/'validation/finger/AK_root_pressure_verify1/summary.json'
    assert all(json.loads(a.read_text())['checks'].values()) and all(json.loads(v.read_text())['checks'].values())
    release=audit(json.loads((ROOT/'CURRENT_BASELINE.json').read_text()),json.loads((ROOT/'models/integrated_contract.json').read_text()));dump(out/'release_summary.json',release)
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    execution=dict(SOFA_runs=0,children=[dict(script='ak_root_pressure_witness.py',exit_code=0,observed_tool_wall_s=.701098),dict(script='verify_ak_root_pressure.py',exit_code=0,observed_tool_wall_s=.760857515)],bounds=dict(virtual_memory_KiB=4194304,timeout_s=420,threads=1),stdout='Tool session captured; no separate raw log. Metrics retained in actual summaries.',owned_live_analysis_children=0)
    dump(out/'execution.json',execution)
    status='FINITE_ROOT_PRESSURE_WITNESS_VERIFIED_LOADED_CONTACT_BLOCKED'
    report=ROOT/'reports/AK_ROOT_PRESSURE_WITNESS_20261126.md'
    report.write_text('''# Actual AK root finite pressure witness

Fixed hypothesis: nonuniform positive normal pressure may balance the actual
bolt height without requiring the previously tested full-area uniform pressure.
This is one finite geometry analysis, not a parameter scan or a FEM solution.
All235 actual AK part hashes were checked before analysis. For each Rail,
three actual FRONT/SKIN, SKIN/RAIL, RAIL/BACK contact faces were intersected
in their common yz projection within a predeclared z4..6mm band. Their
common finite patches have area6mm² each, centroid y=-10/+10mm and z=5mm.
Each carries a hypothetical0.5N, pressure0.083333MPa per total1N compression.
Total normal force and rigid-body moment match two equal bolt loads at z5mm.
No preload value is assigned physically. Original uniform-area3.455241199
Nmm/N residual is preserved: that distribution differs from this witness.

Independent .001/.002mm interior-volume slices on BOTH actual solids at
all6interfaces reproduce the6mm² areas (24 solid tests). Independent direct
moment and virtual-work checks pass. A0.1mm pressure-height corruption is
rejected. Two analysis/verifier children exit0 under4GiB/420s, one thread;
actual outputs, source snapshots, hashes and bounded execution metadata saved.
No this-cycle failed child; all historical failures and CAD/BOM preserved.

This is only an existence witness for necessary normal rigid-body equilibrium.
The separated bolts at y±16mm still require plate load spreading to y±10mm.
Actual elastic pressure, preload, bending/stress, contact opening, tolerance,
friction and full Finger behavior remain unqualified. A positive witness
cannot imply compliance/strength, grasp or whole-system energy PASS.
No adopted design, actual geometry, criteria, SDK or manager control changed.
Read-only release audit remains INTEGRATED_NOT_QUALIFIED. Next B work requires
bolt/plate/contact elasticity and source-backed preload/material evidence,
or separately analyzed positive retention; do not repeat patch scans.
Independent C six-DOF/ground attachment and A protection gates remain open.
Supervisor local save is PENDING; no Git writes or commit SHA claimed.
''')
    summary=dict(status=status,starting_HEAD='4c68ae3e7f9d0f7eb5ab6fc2c3e7d347708e8293',task='actual_finger_load_ports',track='B',time_utc=now,analysis=ref(a),verification=ref(v),execution=ref(out/'execution.json'),producer=ref(out/'producer.py'),dependencies=[ref(ROOT/'scripts/baseline_registry.py'),ref(ROOT/'scripts/integrated_release_gate.py')],report=ref(report),release=ref(out/'release_summary.json'),release_status=release['status'],release_errors=len(release['errors']),whole_system_release=False,physical_preload_N=None,save_status='PENDING_SUPERVISOR_LOCAL_SAVE',owned_live_analysis_children=0)
    dump(out/'summary.json',summary)
    q=json.loads((ROOT/'INTEGRATED_TASKS.json').read_text());assert not any(t['status']=='RUNNING' for t in q['tasks'])
    t=next(t for t in q['tasks'] if t['id']=='actual_finger_load_ports');t.update(last_run_utc=now,consecutive_runs=t.get('consecutive_runs',0)+1,last_result=ref(out/'summary.json'),last_verification=ref(v),last_cycle_status=status,selection_note='Independent B cycle8 completed after C cycles; no adoption or release promotion.',followup_hypothesis='Finite common pressure patches can match bolt normal resultant, but actual plate spreading from y±16 to±10, preload, elastic pressure and friction require evidence. Solve loaded bolt/plate/contact with material/preload basis or positive retention, not more patch scans.')
    dump(ROOT/'INTEGRATED_TASKS.json',q)
    h=json.loads((ROOT/'TRACK_HISTORY.json').read_text());h['cycles'].append(dict(task=t['id'],track='B',time_utc=now,status=status,evidence=ref(out/'summary.json'),starting_HEAD=summary['starting_HEAD'],save_status='PENDING_SUPERVISOR_LOCAL_SAVE',execution='authorized_20261126_4 cycle8; two bounded analysis children completed; no Git writes'));dump(ROOT/'TRACK_HISTORY.json',h)
    text='''# Bounded B cycle — finite actual-root pressure witness (2026-11-26)

Started at4c68ae3e7f9d0f7eb5ab6fc2c3e7d347708e8293. Supervisor local save PENDING;
no git add/commit attempted. Actual result: product_prototype/stage12_integrated/validation/finger/AK_root_pressure_cycle1/summary.json.

Two actual common6mm² pressure patches across FRONT/PET/RAIL/BACK at y±10,z5mm
provide a positive unit-normal rigid-body equilibrium witness against equal
bolt loads. Independent24solid slices, moment and virtual-work checks pass;
0.1mm height corruption rejected. All235AK source hashes verified. Old uniform
pressure3.455241199Nmm/N residual remains valid and unchanged. This is no
elastic-pressure/preload/strength/full Finger PASS; plate load spreading from
bolt y±16mm is unresolved. All historical failures and CAD/BOM preserved.

Read-only release remains INTEGRATED_NOT_QUALIFIED. Next B needs supported
bolt/plate/contact elasticity, actual preload/material/friction or positive
retention; no repeated patch scans. Independent C six-DOF grounding and A
protection remain READY. Two analysis children exit0 within4GiB/420s; no SOFA.
No RUNNING queue record or owned live analysis child. No Stage3, SDK, criteria,
manager or save-control change, external manager launch or Git write.
Manifest runtime/authorized_20261126_4/save_request8.json awaits supervisor save.

'''
    for p in [ROOT/'CHECKPOINT.md',ROOT/'AUTONOMOUS_RESUME.md',REPO/'reports/INTEGRATED_CURRENT_STATUS.md',REPO/'reports/INTEGRATED_NEXT_TASKS.md']:p.write_text(text+p.read_text())
    print(json.dumps(summary))
if __name__=='__main__':main()
