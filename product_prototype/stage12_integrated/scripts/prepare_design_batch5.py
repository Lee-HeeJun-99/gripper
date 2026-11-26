"""One-time authorized research queue update, not a launcher or security change."""
import json
from baseline_registry import ROOT,ref,dump
def main():
    q=json.loads((ROOT/'INTEGRATED_TASKS.json').read_text());h=json.loads((ROOT/'TRACK_HISTORY.json').read_text())
    assert not any(t['status']=='RUNNING' for t in q['tasks'])
    assert not any(t['id'].startswith('batch5_') for t in q['tasks']),'Never reset/repeat this allocation setup'
    c=json.loads((ROOT/'CURRENT_CANDIDATE.json').read_text());assert c['revision']=='revAK_integral2'
    authorization=ref(ROOT/'AUTOMATION_AUTHORIZATION_20261126_5.json');brief=ref(ROOT/'reports/DESIGN_IMPLEMENTATION_BRIEF_20261126_5.md')
    definitions=[
        ('positive_drive_retention','A',-10,'Implement positive torque and axial/thrust capture in finite new drive CAD; do not rely on guessed collet friction/motor axial bearing capacity','AH_collet_and_axial_capacity','Actual torque-bearing faces and axial capture, supplier shaft compatibility, finite parts and independent loaded reaction/capacity evidence'),
        ('grounded_palm_attachment','C',-9,'Replace compression-only support with finite side/torsion/uplift and grounded mounting interface','AI_whole_palm_support','Actual base adapter/fasteners/pins/shoulders and ground path,6DOF support and component load evidence; no unsupported FE node fixation'),
        ('positive_root_retention','B',-8,'Implement PET/Rail positive root axial retention without locking distal PET sliding','actual_finger_load_ports','Actual interlock/shoulder/capture hardware, root load/strain and distal sliding compatibility; not another pressure witness'),
        ('physical_load_limiter','A',-7,'Implement a real source-backed overload mechanism or simpler lower-load drive, not another ideal delay scan','AK_protected_maximum_load','Finite actual limiter/disconnect CAD, jam energy/input/residual-inertia paths and protected bound evidence; unknown ratings never fabricated'),
        ('idler_mechanical_retention','A',-6,'Implement actual thread load-bearing geometry/model or simpler supported axle/captive retention','AJ_idler_thread_and_load_proof','Actual flank/core/engagement or positive retention CAD, assembly, axial/radial load path and capacity evidence'),
        ('same_revision_system_revalidation','C',-5,'Accumulate compatible new hardware in one actual descendant assembly and rerun affected system gates','source_reconciliation','Single candidate assembly/BOM/hash, affected Stage1/Stage2 evidence and existing independent release audit; no mixed-revision PASS')]
    states={t['id']:t for t in q['tasks']}
    for name,track,priority,hypothesis,previous,criteria in definitions:
        predecessor=states[previous];evidence=predecessor.get('result') or predecessor.get('results',[])
        q['tasks'].append(dict(id='batch5_'+name,track=track,priority=priority,status='READY',execution_class='PRODUCT_IMPLEMENTATION',hypothesis=hypothesis,criteria=criteria,previous_diagnostic_task=previous,existing_evidence=evidence,prerequisites=[],target_candidate=c['definition'],target_revision=c['revision'],target_parts=c['parts'],product_brief=brief,expected_outputs=['Actual changed finite CAD/assembly or direct load evidence for implemented candidate','Independent verification summary, source/model/result hashes','BOM/interface invalidation and affected system gates'],cost='One3600second session, each analysis child4GiB/420s',fallback='Implement a simpler manufacturable positive mechanical alternative; preserve rejected candidate',system_gate_contribution=5,last_run_utc=None,consecutive_runs=0))
    # Assembly task follows the actual design changes; component partial PASS
    # cannot silently satisfy its independent same-revision system criteria.
    q['tasks'][-1]['prerequisites']=['batch5_'+d[0] for d in definitions[:-1]]
    q['active_authorization']=authorization;q['execution_brief']=brief
    previous=h.get('new_authorization')
    if previous:h.setdefault('previous_authorizations',[]).append(previous)
    h['new_authorization']=dict(allocation_ID='authorized_20261126_5',authorization=authorization,maximum_new_sessions=10,seconds_per_session=3600,usage_authority='runtime/authorized_20261126_5/status.json',previous_batch4_completed=10,legacy_usage_preserved=True)
    dump(ROOT/'INTEGRATED_TASKS.json',q);dump(ROOT/'TRACK_HISTORY.json',h)
    print(json.dumps(dict(status='NEW_DESIGN_BATCH_PREPARED_NOT_LAUNCHED',new_tasks=6,old_results_unchanged=True)))
if __name__=='__main__':main()
