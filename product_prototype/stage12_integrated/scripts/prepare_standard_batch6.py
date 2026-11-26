"""Operator-only one-time research queue setup. No launch, usage reset or gate change."""
import json,subprocess
from baseline_registry import ROOT,REPO,ref,dump
def main():
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()=='d39469cfd21bf9c1490d06c4830b37c353eb770d'
    q=json.loads((ROOT/'INTEGRATED_TASKS.json').read_text());h=json.loads((ROOT/'TRACK_HISTORY.json').read_text())
    assert not any(t['status']=='RUNNING' for t in q['tasks'])
    assert not any(t['id'].startswith('batch6_') for t in q['tasks']),'Do not reinitialize allocation'
    c=json.loads((ROOT/'CURRENT_CANDIDATE.json').read_text());assert c['revision']=='revAO_root2' and c['parts']==254
    auth=ref(ROOT/'AUTOMATION_AUTHORIZATION_20261127_6.json');brief=ref(ROOT/'reports/STANDARD_COMPONENT_BRIEF_20261127_6.md')
    work=[
      ('operating_load_and_architecture','C','Separate real normal demand/protected maximum/allowable; select source-backed standard simpler drive and implement actual finite interface CAD',['tendon_force_stroke','motor_running_torque_speed','overload_protection','motor_alignment_reactions']),
      ('standard_idler_or_direct_route','A','Implement standard shoulder/clevis/captive or double-supported pulley, or remove Idler with verified actual routing; no special riveting dependency',['idler_load_drag','continuous_load_path','changed_stage1_revalidation']),
      ('wide_root_cartridge','B','Move root capture stress out of flexible narrow span with wider tab/shoulder/cartridge and preserve distal PET sliding',['finger_structure','root_palm_strength','terminal_retention']),
      ('simple_palm_mount','C','Implement finite simpler mounting flange/through-bolt plate with Tendon separation and real6DOF mating interface',['root_palm_strength','continuous_load_path','changed_stage1_revalidation']),
      ('protected_standard_drive','A','Integrate appropriately sized source-backed drive/protection; actual peak torque/energy/jam paths, not a holding-torque or command-limit assumption',['overload_protection','motor_running_torque_speed','housing_shoulder_retention','motor_alignment_reactions']),
      ('actual_stage2_finger_load_specimen','B','Connect actual chosen product parts from Motor through Tendon/Finger/Root to Ground for Stage2 load verification, not Stage3 motion',['tendon_force_stroke','terminal_retention','finger_structure','continuous_load_path']),
      ('system_static_dynamic_load_chain','A','Verify selected actual full input/output force,moment,stroke and energy with bounded dynamics at justified loads',['static_dynamic_consistency','continuous_load_path','physical_mass_inertia']),
      ('same_revision_three_finger_stage1','C','Integrate one simplified3-Finger revision with actual complete CAD/BOM/wire/motion/assembly/tolerance/tools',['cad_model_match','changed_stage1_revalidation','housing_shoulder_retention']),
      ('strength_worst_case_convergence','B','Verify actual materials/standard ratings,critical sections,tolerances and numerical convergence of current design',['shaft_strength','coupling_capacity','pin_drum_strength','bearing_ratings_reactions','tendon_stiffness_strength','numerical_convergence','qualified_worst_case']),
      ('independent_integrated_release_and_repairs','C','Execute existing same-revision Stage1/Stage2/integrated gates and fix directly actionable remaining product issues',['cad_model_match','changed_stage1_revalidation','stage3_handoff'])]
    criteria=json.loads((ROOT.parent/'stage2_load_transfer/models/analytical/criteria.json').read_text())
    # Gate names are referenced, never edited; validate against the actual release registry.
    registry=json.loads((ROOT.parent/'stage2_load_transfer/models/analytical/release_registry.json').read_text())
    def keys(v):
        result=set()
        if isinstance(v,dict):
            result.update(v)
            for child in v.values():result.update(keys(child))
        elif isinstance(v,list):
            for child in v:result.update(keys(child))
        elif isinstance(v,str):result.add(v)
        return result
    known=keys(registry)|keys(criteria)
    for i,(name,track,goal,gates) in enumerate(work):
        assert all(g in known for g in gates),gates
        q['tasks'].append(dict(id='batch6_'+name,track=track,priority=-200+i,status='READY',execution_class='PRODUCT_IMPLEMENTATION',selection_policy='coverage_before_repetition',research_batch='authorized_20261127_6',recommended_session=i+1,goal=goal,hypothesis=goal,criteria='Actual source-backed component and finite same-candidate CAD/BOM/load evidence meeting the linked unchanged system gates; bounded geometry/conditional results never qualify whole capacity',system_gate_ids=gates,prerequisites=[],target_revision=c['revision'],target_parts=c['parts'],target_candidate=c['definition'],product_brief=brief,expected_outputs=['Actual implementation or direct validation of selected final-product parts','Manufacturer/model/dimensions/ratings and unknowns clearly separated','Changed/custom/standard part counts,assembly tools,source/model/result hashes','New system evidence,remaining gate IDs and concrete followup'],cost='One3600second session; each analysis child4GiB/420seconds',failure_policy='After two same-mechanism failures evaluate standard component/different architecture; do not repeat rivet or parameter scans',fallback='Independent standard-component product task from another track',system_gate_contribution=5,last_run_utc=None,consecutive_runs=0))
    q['active_authorization']=auth;q['execution_brief']=brief
    old=h.get('new_authorization')
    if old:h.setdefault('previous_authorizations',[]).append(old)
    h['new_authorization']=dict(allocation_ID='authorized_20261127_6',authorization=auth,maximum_new_sessions=10,seconds_per_session=3600,usage_authority='runtime/authorized_20261127_6/status.json',previous_batch5_completed=10,legacy_usage_preserved=True)
    dump(ROOT/'INTEGRATED_TASKS.json',q);dump(ROOT/'TRACK_HISTORY.json',h)
    print(json.dumps(dict(status='STANDARD_COMPONENT_BATCH_PREPARED_NOT_LAUNCHED',new_tasks=10,old_results_unchanged=True)))
if __name__=='__main__':main()
