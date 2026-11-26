"""One-time metadata/queue migration; historical outcomes and evidence unchanged."""
import json
from baseline_registry import ROOT,dump
def main():
    path=ROOT/'INTEGRATED_TASKS.json';q=json.loads(path.read_text())
    for t in q['tasks']:
        name=t['id'];t['track']='A' if any(s in name for s in ('jam','limiter','alignment','protected','torque')) else 'B' if any(s in name for s in ('contact','pet','rail','static','jacobian','cone','rank','terminal')) else 'C'
        t.setdefault('system_gate_contribution',1);t.setdefault('last_run_utc',None);t.setdefault('consecutive_runs',0)
        if name=='flexible_rail_contact':t.update(priority=6,consecutive_runs=6,last_run_utc='2026-11-26T07:37:14Z',selection_note='Stop generic rod refinement. Next B task is actual CAD boundary/load-port identification.')
    additions=[dict(id='direct_clutch_cartridge',track='A',priority=0,status='READY',system_gate_contribution=4,hypothesis='Direct motor-supported friction drum removes rigid two-shaft coupling and reduces downstream inertia; actual slip/bearing drag and speed bound still require qualification',difference='New physical transmission topology, not HPMC dimensional retry',criteria='Finite CAD/shaft connection/retention, actual retained-hardware collisions, explicit force window and dynamic assumptions. No certified cap from assumed friction.',prerequisites=[],cost='4GiB/420s CAD and independent bounded analysis',fallback='manufacturer_complete_clutch'),dict(id='actual_finger_boundary_map',track='B',priority=1,status='READY',system_gate_contribution=3,hypothesis='Actual terminal and root surfaces determine axial travel and load ports; independent rods are references only',criteria='Actual STEP identity, finite terminal stops, clamp/capture graph, load input/output coordinates; no manufactured friction/strength values',prerequisites=[],cost='Actual CAD section/translation checks, no new generic rod solve',fallback='simpler_free_sliding_terminal'),dict(id='candidate_system_integration',track='C',priority=2,status='READY',system_gate_contribution=5,hypothesis='New drive candidate must be checked against all retained three-finger hardware and wiring, not a stand-alone coupon',criteria='Actual assembly STEP, explicit replacement cut-set, dimensional BOM, exact nominal interference and sampled motion; no adoption with failed mounting',prerequisites=[],cost='4GiB/420s',fallback='motor_plate_revision')]
    ids={t['id'] for t in q['tasks']}
    if any(t['id'] in ids for t in additions):raise RuntimeError('Migration already performed; do not duplicate')
    q['tasks'].extend(additions);q['policy']=dict(max_consecutive_same_track=2,goal='Actual same-revision product release; no coupon promotion',automatic_budget_remaining_runs=0,automatic_budget_renewal=False,current_session_work_authorized=True)
    dump(path,q)
    commits=['f5225df','1afffcb','a46536d','0570ac4','0e10955','d01db2b']
    dump(ROOT/'TRACK_HISTORY.json',dict(scope='Six actually completed external research cycles; no fabricated timestamps',cycles=[dict(commit=c,track='B',task='flexible_rail_contact',time_utc=None) for c in commits],automatic_launches_used=6,automatic_launches_remaining=0))
if __name__=='__main__':main()
