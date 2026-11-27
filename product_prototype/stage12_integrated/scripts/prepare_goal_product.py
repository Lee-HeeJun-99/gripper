"""Operator queue migration for continuous one-primary-product development."""
import json
from baseline_registry import ROOT,ref,dump
def main():
    q=json.loads((ROOT/'INTEGRATED_TASKS.json').read_text());h=json.loads((ROOT/'TRACK_HISTORY.json').read_text())
    assert not any(t['status']=='RUNNING' for t in q['tasks'])
    assert not any(t['id'].startswith('goal_primary_') for t in q['tasks']),'Do not repeat authorization migration'
    auth=ref(ROOT/'GOAL_AUTHORIZATION_20261127.json');brief=ref(ROOT/'reports/GOAL_ENGINEERING_BRIEF.md');c=json.loads((ROOT/'CURRENT_CANDIDATE.json').read_text())
    for name,track,priority,objective,gates in [
      ('module','C',-1000,'Implement one separate minimal manufacturable Motor/Drum/Tendon/Finger/Root/Ground Stage2 product with feasible operating-load contract and actual side/split assembly; then improve this primary rather than another AO micro-fix',['cad_model_match','continuous_load_path','changed_stage1_revalidation']),
      ('operating_window','B',-999,'Verify actual selected primary Finger geometry/contact/friction/deflection,normal force-stroke/torque/speed and structural response; carry evidence into the same actual module',['tendon_force_stroke','finger_structure','root_palm_strength','static_dynamic_consistency','numerical_convergence']),
      ('protected_drive','A',-998,'Complete actual minimal drive,standard connection and bounded maximum torque/energy/strain/retention through the primary product, not ideal-delay/coupon results',['motor_running_torque_speed','overload_protection','motor_alignment_reactions','coupling_capacity','housing_shoulder_retention'])]:
        q['tasks'].append(dict(id='goal_primary_'+name,track=track,priority=priority,status='READY',execution_class='PRODUCT_IMPLEMENTATION',selection_policy='goal_product_continuation',hypothesis=objective,criteria='Actual coherent primary CAD/BOM/material/load/BC and independent engineering evidence; retain all22system criteria and full same-revision final gates',system_gate_ids=gates,prerequisites=[],parent_candidate=c['definition'],product_brief=brief,followup_rule='Continue the same primary from actual failed/missing gates; create meaningful next tasks dynamically, not one-pass completion',cost='3600seconds Worker;4GiB/420seconds each analysis child',last_run_utc=None,consecutive_runs=0,system_gate_contribution=6))
    old=q.get('active_authorization');q['active_authorization']=auth;q['execution_brief']=brief
    if h.get('new_authorization'):h.setdefault('previous_authorizations',[]).append(h['new_authorization'])
    h['new_authorization']=dict(mode='GOAL_BASED',authorization=auth,total_session_limit=None,total_research_time_limit=None,usage_authority='runtime/goal_authorized_20261127_7/ledger.json',old_budget_records_preserved=True)
    dump(ROOT/'INTEGRATED_TASKS.json',q);dump(ROOT/'TRACK_HISTORY.json',h)
    print(json.dumps(dict(status='GOAL_PRODUCT_QUEUE_PREPARED_NOT_LAUNCHED',historical_authorization_preserved=bool(old))))
if __name__=='__main__':main()
