"""Read-only verification + exact-byte Supervisor request. Never stages or commits."""
import json,subprocess,shutil,hashlib
from pathlib import Path
from baseline_registry import ROOT,REPO,ref,sha,dump
from supervised_save import validate,changed,untracked
from goal_manager_policy import engineering_record
HEAD='8e2ae708ee966c991bc6afa523be230fca3e0b79'
def load(p):return json.loads(p.read_text())
def main():
 assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==HEAD;assert not subprocess.check_output(['git','diff','--cached','--name-only'],text=True).strip();assert not(ROOT/'runtime/STOP').exists()
 runtime=ROOT/'runtime/goal_authorized_20261127_7';before=load(runtime/'checkpoint_before10.json');assert before['HEAD']==HEAD;ledger=load(runtime/'ledger.json');pins={p:sha(REPO/p)==h for p,h in ledger['source_pins'].items()};assert all(pins.values())
 snapshot=load(Path('/tmp/regrip_cycle11_baseline.json'));assert set(before['preexisting_untracked'])==set(snapshot['files']);oldok=all((REPO/p).is_file() and sha(REPO/p)==h for p,h in snapshot['files'].items());assert oldok,'Original user untracked bytes changed'
 q=load(ROOT/'INTEGRATED_TASKS.json');assert not any(t['status']=='RUNNING' for t in q['tasks']);nexttask=load(ROOT/'NEXT_TASK.json')['next'];assert nexttask['id']=='goal_primary_seated_spatial_support_reclosure' and nexttask['status']=='READY'
 mainpath=ROOT/'validation/integrated/primary_cycle11_record2/summary.json';r=load(mainpath);assert r['owned_analysis_children_running']==0 and r['running_queue_tasks']==0 and r['timeouts']==0 and all(e['reaped'] for e in r['executions']);assert len(r['executions'])==22
 releasepath=ROOT/'validation/integrated/primaryP1_release16/summary.json';release=load(releasepath);assert release['status']=='INTEGRATED_NOT_QUALIFIED' and len(release['errors'])==24
 cadpath=ROOT/'cad/exports/primaryP1_seated22/summary.json';cad=load(cadpath);assert all(sha(REPO/p['path'])==p['SHA256'] for p in cad['part_references'].values());assert cad['parts']==78 and not cad['interferences'];assert load(ROOT/'CURRENT_CANDIDATE.json')['definition']==ref(cadpath);state=load(ROOT/'PRIMARY_PRODUCT.json');assert state['candidate_reference']==ref(cadpath) and state['actual_part_references']==cad['part_references'];assert nexttask['primary_state']==ref(ROOT/'PRIMARY_PRODUCT.json')
 gate=load(ROOT/'models/primary_system_gate_state14.json');assert len(gate['gates'])==22 and all(g['status']=='UNQUALIFIED' for g in gate['gates'])
 fem=load(ROOT/'validation/integrated/primaryP1_front_h5_2/summary.json');verify=load(ROOT/'validation/integrated/primaryP1_front_verify1/summary.json');feedback=load(ROOT/'validation/integrated/primaryP1_seated_front_feedback1/summary.json');foot=load(ROOT/'validation/integrated/primaryP1_front_footprint1/summary.json');geom=load(ROOT/'validation/integrated/primaryP1_seated_front_feedback_verify1/summary.json');assert all(fem['checks'].values()) and all(verify['rows'][0]['checks'].values()) and all(geom['checks'].values());assert feedback['status'].endswith('FAIL') and foot['status'].endswith('FAIL')
 # Final mutable checkpoint addendum; earlier checkpoint and all evidence remain intact.
 cp=ROOT/'CHECKPOINT.md';cp.write_text(f'''# Authoritative cycle11 closeout — same P1 seated22

Corrected actual22 coarse solve:72,216DOF/2,169contactrows/14axialconnectors,
380.546917999s/4GiB/no timeout. OSQP4000iterationlimit is preserved; separate
32stepactiveKKT closes all original constraints. Independent tetra force,
stress/energy/bolt/contact/rigidwork and corrupt-field rejection pass ONLY this
coarse static model. Framepeak4.202924943MPa is conditional/unconverged,NOTstrength.
MotorfrontFrame/Capgaps arepositive(.00888802/.00881932mm); zeroYcontactforces
andnegligiblegauges are a feasiblecoordinatewitness,NOTpositivephysicalretention.

ActualNEW22supportfeedbacknormal{feedback['normal_N']:.12g}N; its localspatialstring/
planarFinger passesindependentstring/BRepsamples, currenthelixexit{geom['exit_tangent_change_deg']:.12g}deg.
OUTERfixedpointFAIL:force{feedback['force_port_difference_N']:.12g}N andmoment
{feedback['moment_port_difference_Nm']:.12g}Nm exceed unchanged1e-8N/1e-10Nm.
ExactsamepartCADbearingareasvscoarse16edgecircles FAIL1% bymax
{foot['maximum_absolute_relative_error']*100:.12g}%; no automaticfine/gapretry orcriteriarelaxation.
All22UNQUALIFIED, trustedrelease16NOTQUALIFIED/24errors/exit2, noStage3.
Nextexactgoal_primary_seated_spatial_support_reclosure usescurrent22field/feedback
andpose-dependentfullweight/couples; no wrongload1 orunrelatedarchitecture.

22boundedchildrenreaped/{r['recorded_child_seconds_known']:.12g}knownchildseconds/0newtimeouts,
0RUNNINGqueue/0ownedanalysischildren. Original8,595useruntrackedfiles unchanged;
sourcepins unchanged; noGitadd/commit. Supervisor exactsave_request10.json pending.
Detailed authoritative evidence: validation/integrated/primary_cycle11_record2/summary.json,
models/primary_system_gate_state14.json,reports/primaryP1_seated_spatial_engineering2.md.
Recorder1 failed before summary creation by expecting absent serialization-failure
summaries; its identity8/gate13/report are preserved, superseded byidentity9/gate14/report2.

---

'''+cp.read_text())
 out=ROOT/'validation/integrated/primaryP1_cycle11_closeout';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 result=dict(status='ACTUAL_P1_SEATED22_VERIFIED_HANDOFF_NOT_RELEASE',category='DESIGN_CHANGE',task_id='goal_primary_spatial_front_contact_feedback',candidate=ref(cadpath),main_result=ref(mainpath),producer=ref(out/'producer.py'),trusted_release=ref(releasepath),actual_changed_CAD=cad['changed'],verified_conditional_coarse=ref(ROOT/'validation/integrated/primaryP1_front_verify1/summary.json'),actual_feedback_failure=ref(ROOT/'validation/integrated/primaryP1_seated_front_feedback1/summary.json'),actual_footprint_failure=ref(ROOT/'validation/integrated/primaryP1_front_footprint1/summary.json'),new22_geometry=ref(ROOT/'validation/integrated/primaryP1_seated_front_feedback_verify1/summary.json'),source_pins_unchanged=pins,original_untracked_files_preserved=len(snapshot['files']),original_untracked_hashes_unchanged=oldok,executions_reaped=22,known_child_seconds=r['recorded_child_seconds_known'],new_timeouts=0,unknown_child_times=0,running_queue_tasks=0,owned_analysis_children_running=0,coarse_DOF=fem['DOF'],conditional_Frame_peak_MPa=fem['stresses'][0]['peak_unsmoothed_vm_MPa'],new22_feedback_normal_N=feedback['normal_N'],unclosed_force_N=feedback['force_port_difference_N'],unclosed_moment_Nm=feedback['moment_port_difference_Nm'],coarse_bearing_face_error=foot['maximum_absolute_relative_error'],all22_system_gates_unqualified=True,newly_qualified_system_gate_ids=[],next_task_id=nexttask['id'],whole_system_release=False,stage3_authorized=False,hardware='HARDWARE_NOT_MEASURED',save_status='PENDING_SUPERVISOR_EXACT_LOCAL_SAVE',git_add_commit_attempted=False)
 dump(out/'summary.json',result)
 names=sorted(changed(REPO)|(untracked(REPO)-set(before['preexisting_untracked'])));records=[ref(REPO/p) for p in names]
 results=[ref(p) for p in [cadpath,mainpath,ROOT/'validation/integrated/primaryP1_seated_finger2/summary.json',ROOT/'validation/integrated/primaryP1_front_h5_2/summary.json',ROOT/'validation/integrated/primaryP1_front_verify1/summary.json',ROOT/'validation/integrated/primaryP1_seated_front_feedback1/summary.json',ROOT/'validation/integrated/primaryP1_front_footprint1/summary.json',ROOT/'validation/integrated/primaryP1_seated_front_feedback_verify1/summary.json',out/'summary.json']]
 actual=[str((ROOT/p).relative_to(REPO)) for p in ['cad/exports/primaryP1_seated22/F0_SPOOL.step','cad/exports/primaryP1_seated22/F0_SPOOL.stl','cad/exports/primaryP1_seated22/ASSEMBLY.step','cad/exports/primaryP1_seated22/BOM.json','cad/exports/primaryP1_seated22/summary.json','scripts/primary_seated_spool_v2.py','scripts/primary_seated_string.py','scripts/primary_seated_finger_v2.py','scripts/primary_front_compliance_v2.py','models/primary_system_gate_state14.json']]
 request=dict(expected_HEAD=HEAD,message='Implement P1 seated spool; verify spatial loads and coarse front contact; preserve coupled-feedback and bearing-area failures',files=records,results=results,engineering_progress=dict(category='DESIGN_CHANGE',task_id='goal_primary_spatial_front_contact_feedback',mechanism='Same78partP1 ONLYspoolfloorR11.00matchesactualnominalwire/nippletangent;77STEPrefsunchanged. ActualXYZmassivestring/planarFinger,78partloadcoverage,newfrontcontactcoarse+independentforce/energyverified. Outerfeedbackand2.55%bearingfaceFAILpreserved; all22unqualified.',system_gate_ids=load(ROOT/'INTEGRATED_TASKS.json')['tasks'][next(i for i,t in enumerate(load(ROOT/'INTEGRATED_TASKS.json')['tasks']) if t['id']=='goal_primary_spatial_front_contact_feedback')]['system_gate_ids'],actual_change_files=actual,candidate_reference=ref(cadpath),next_task_id=nexttask['id'],strategy_change=True))
 dump(runtime/'save_request10.json',request);validate(REPO,request,HEAD,before['preexisting_untracked']);engineering=engineering_record(request,REPO);assert engineering['signature'] not in ledger['seen_engineering_signatures'];assert all(sha(REPO/p)==h for p,h in ledger['source_pins'].items())
 dump(runtime/'save_preflight10.json',dict(status='READ_ONLY_SUPERVISOR_EXACT_BYTE_PREFLIGHT_PASS',expected_HEAD=HEAD,files=len(records),results=len(results),request_SHA256=sha(runtime/'save_request10.json'),engineering_record=engineering,old_untracked_hashes_preserved=oldok,source_pins_unchanged=pins,largest_file_bytes=max((REPO/p).stat().st_size for p in names),owned_analysis_children_running=0,running_queue_tasks=0,git_staged_files=0,save_executed=False));print(dict(status='SAVE_REQUEST10_READY_NOT_COMMITTED',files=len(records),results=len(results),largest_file_bytes=max((REPO/p).stat().st_size for p in names),known_child_seconds=r['recorded_child_seconds_known'],next=nexttask['id']))
if __name__=='__main__':main()
