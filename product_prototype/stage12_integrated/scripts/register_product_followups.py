"""Register evidence-supported actual product followups, no automatic launch."""
import json
from baseline_registry import ROOT,dump
def main():
    p=ROOT/'INTEGRATED_TASKS.json';q=json.loads(p.read_text());ids={t['id'] for t in q['tasks']}
    tasks=[
      dict(id='AF_protection_topology',track='A',priority=0,hypothesis='Actual input-supported bearing creates a parallel torque path even with ideal friction cap',criteria='Actual part-linked graph; ideal-only, bypass and grounded-support controls; do not certify measured seizure force',cost='read-only stored geometry and algebra'),
      dict(id='AF_calibration_stand',track='A',priority=1,hypothesis='A split keyed bench stand reacts hub torque without depending on motor holding torque',criteria='Finite actual fixture STEP/STL, actual cartridge interference and independent mesh audit; not proof capacity',cost='4GiB/420s'),
      dict(id='AG_ground_support',track='C',priority=0,hypothesis='Ground-supported hollow spindle removes the input/output bearing bypass, with actual finite axial retention and input shaft clearance',criteria='Actual three-sector finite CAD, shaft passage, independent geometry audit and full-turn geometric check; no certified friction/strength promotion',cost='4GiB/420s',fallback='separate_rated_upstream_disconnect'),
      dict(id='AF_full_wire_motion',track='C',priority=3,hypothesis='Changed radial layout must retain finite wire clearance and terminal compatibility over prescribed Finger motion',criteria='Actual wire at distinct poses, actual retained parts, no fixed-wire collision exemption promoted to PASS; max stock/tolerance remain separate',cost='4GiB/420s',prerequisites=['candidate_system_integration']),
      dict(id='root_retention_load_contract',track='B',priority=2,hypothesis='Actual root positive capture/clamp contact determines preload and axial load capability, not an assumed fixed rod boundary',criteria='Actual finite root geometry/load ports, preload/retention model with conditional or certified properties, force/moment equilibrium',cost='bounded read-only CAD and independent structural calculation')]
    if any(t['id'] in ids for t in tasks):raise ValueError('Do not duplicate product tasks')
    for t in tasks:
        t.update(status='READY',system_gate_contribution=3,last_run_utc=None,consecutive_runs=0)
        t.setdefault('prerequisites',[]);t.setdefault('fallback','review_independent_product_track');q['tasks'].append(t)
    dump(p,q)
if __name__=='__main__':main()
