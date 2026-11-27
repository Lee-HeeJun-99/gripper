"""Exact-byte closeout and Supervisor request; never stages/commits or launches research."""
import json,subprocess,shutil,datetime
from baseline_registry import ROOT,REPO,ref,sha,dump
HEAD='a6bcbfbfa2241f9ae3f892ab98da54c43cc6e3e3'
def load(p):return json.loads(p.read_text())
def main():
 assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==HEAD;assert not subprocess.check_output(['git','diff','--cached','--name-only'],text=True).strip();assert not(ROOT/'runtime/STOP').exists()
 before=load(ROOT/'runtime/goal_authorized_20261127_7/checkpoint_before9.json');assert before['HEAD']==HEAD;ledger=load(ROOT/'runtime/goal_authorized_20261127_7/ledger.json');pins={p:sha(REPO/p)==h for p,h in ledger['source_pins'].items()};assert all(pins.values())
 root=ROOT/'validation/integrated';out=root/'primaryP1_cycle10_closeout';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');mainpath=root/'primary_cycle10/summary.json';mainresult=load(mainpath);src=ROOT/'cad/exports/primaryP1_retention20/summary.json';cad=load(src);w=load(root/'primaryP1_retention_witness4/summary.json');releasepath=root/'primaryP1_release15/summary.json';release=load(releasepath);assert release['status']=='INTEGRATED_NOT_QUALIFIED' and len(release['errors'])==24
 counts=dict(hardware_poses=len(w['assembly_poses']),tool_poses=sum(len(r['poses']) for r in w['tool_poses']),bolt_indexing_poses=sum(len(r['poses']) for r in w['tool_poses'] if 'indexing'in r['tool']),exact_comparisons=w['exact_comparisons']);assert counts==dict(hardware_poses=56,tool_poses=124,bolt_indexing_poses=52,exact_comparisons=360)
 # Preserve original recorder/gate11/report typo; authoritative correction is new evidence.
 gate=load(ROOT/'models/primary_system_gate_state11.json')
 for g in gate['gates']:
  if g['id']=='changed_stage1_revalidation':g['reason']=g['reason'].replace('108tool','124tool')
 gate['historical_parent_compliant_chain']=gate.pop('latest_compliant_chain',{});gate['count_correction']=dict(supersedes=ref(ROOT/'models/primary_system_gate_state11.json'),reason='Recorderproseunder-countedtoolposesas108. Actualimmutablewitness4enumerates124including52indexposes; noresult/criteriachanged.',actual=counts);gp=ROOT/'models/primary_system_gate_state12.json';dump(gp,gate);assert len(gate['gates'])==22 and all(g['status']=='UNQUALIFIED' for g in gate['gates'])
 report=ROOT/'reports/primaryP1_retention_feedback_closeout.md';report.write_text('''# Authoritative P1 retention20 closeout

The actual candidate is `cad/exports/primaryP1_retention20/summary.json`. Detailed engineering is `reports/primaryP1_retention_feedback_engineering.md`; all original evidence is retained.

Count correction: the initial recorder report and gate11 prose say 108 tool poses. The immutable final witness4 actually enumerates **124** tool poses:28 nut-holder,44 Lkey approach and52 bolt/Lkey indexing poses. It also checks56 internal hardware poses,360 comparisons. Gate12 supersedes only that count; all22 remain UNQUALIFIED. Base/fixture adds63 poses/91 comparisons and later module81 poses/303 comparisons. No new PASS criterion is introduced.

Scope clarification: final witness4 uses a 19mm-wide/130mm-long/**5.8mm-thick** generic nut-holding envelope and source-dimensional29/74mm Lkey. Earlier witness3's4.2mm corridor and comments are historical. Generic sharp-bend/clearance/handle/ring profiles are NOT exact purchased tools or tightening/preload certification. Bare source dimensions do not prove exact tool fit.

The one-way planar feedback's reported Root wrench is the **moving Finger subset**, with Motor/rotor/string counterparts. Fixed Root Rail/PET/clamp weights and local pin/clamp traction have not been recomputed into new20's elastic solution. The mass result is an exact CAD *contrast* under existing conditional densities; new20 has no elastic re-solve. Parent19's saved field solves its recorded incomplete contact model, and actual MotorfrontY contacts were omitted. Its gauge penetration can be relieved by freeY backshift; neither a unique physical alignment nor need for a new stop is proven. Complete actual front-contact/freeY/spatial-string feedback before strength or a new justified coarse contact solve.

Final unchanged trusted release15 is INTEGRATED_NOT_QUALIFIED,24 errors,exit2. No Stage3,hardware,global energy,mesh/time,thread/material/case or full3-Finger release. All failures and old timeout evidence remain. Exact Supervisor save only; no worker git add/commit.
''')
 executions=[]
 for ep in sorted((root/'primary_cycle10').glob('*_execution.json')):
  e=load(ep);assert e['reaped'] and not e['timeout'] and not e['STOP'];executions.append(dict(e,record=ref(ep)))
 assert len(executions)==15
 q=load(ROOT/'INTEGRATED_TASKS.json');assert not any(t['status']=='RUNNING' for t in q['tasks']);ntid=mainresult['next_task_id'];assert sum(t['id']==ntid and t['status']=='READY' for t in q['tasks'])==1
 cp=ROOT/'CHECKPOINT.md';received_checkpoint=ref(cp)
 result=dict(status='ACTUAL_P1_CYCLE10_EXACT_BYTE_HANDOFF_NOT_RELEASE',producer=ref(out/'producer.py'),main=ref(mainpath),candidate=ref(src),corrected_report=ref(report),initial_report=mainresult['report'],authoritative_system_gate_state=ref(gp),actual_retention_pose_counts=counts,final_trusted_release=ref(releasepath),final_trusted_release_exit_code=2,release_error_count=24,source_pins_unchanged=pins,received_checkpoint=received_checkpoint,received_manager_checkpoint=ref(ROOT/'runtime/goal_authorized_20261127_7/checkpoint_before9.json'),executions=executions,analysis_children_reaped=len(executions),recorded_child_seconds=sum(e['elapsed_s'] for e in executions),new_timeouts=0,new_unknown_child_times=0,historical_two420s_limit_races_preserved=True,owned_analysis_children_running=0,running_queue_tasks=0,newly_qualified_system_gate_ids=[],remaining_system_gate_ids=[g['id'] for g in gate['gates']],actual_changed_parts=[r['part_ID'] for r in cad['changed']],unchanged_STEP_refs=70,next_task_id=ntid,whole_system_release=False,hardware_status='HARDWARE_NOT_MEASURED',SOFA_runs=0,new_FEM_solves=0,git_add_commit_attempted=False,save_status='PENDING_SUPERVISOR_EXACT_SAVE',limitations=mainresult['limitations'])
 dump(out/'summary.json',result)
 state=load(ROOT/'PRIMARY_PRODUCT.json');state.update(latest_closeout=ref(out/'summary.json'),latest_retention_gate_state=ref(gp),latest_closeout_child_count=len(executions),latest_closeout_child_seconds=result['recorded_child_seconds'],latest_closeout_child_seconds_known=result['recorded_child_seconds'],latest_closeout_child_time_unknown=0,latest_closeout_child_seconds_lower_bound=0,historical_parent19_contact_scope='Verifiedsolutionofrecordedmodelonly. ExistingactualMotorfrontYcontacts omitted; savedselectedgaugegapnegative. No new20hardware/full3Dequilibrium. SeeprimaryP1_axial_gap1/summary.json.',authoritative_retention_report=ref(report));dump(ROOT/'PRIMARY_PRODUCT.json',state)
 current=load(ROOT/'CURRENT_CANDIDATE.json');current.update(latest_closeout=ref(out/'summary.json'),primary_state=ref(ROOT/'PRIMARY_PRODUCT.json'),system_gate_state=ref(gp),authoritative_retention_report=ref(report));dump(ROOT/'CURRENT_CANDIDATE.json',current)
 for t in q['tasks']:
  if t['id'].startswith('goal_primary_'):t['primary_state']=ref(ROOT/'PRIMARY_PRODUCT.json')
 dump(ROOT/'INTEGRATED_TASKS.json',q);nt=load(ROOT/'NEXT_TASK.json');nt['next']=next(t for t in q['tasks'] if t['id']==ntid);dump(ROOT/'NEXT_TASK.json',nt)
 text='''# Latest actual P1 internal retention and support feedback — 2026-11-27, Supervisor save pending

Actual starting HEAD a6bcbfbfa2241f9ae3f892ab98da54c43cc6e3e3.
Selected exact task goal_primary_framekey_fit_feedback.
SAME ONE primaryP1_retention20,78parts; failedAO/adoptedAA and original
3Finger/cartridge/jamming extension preserved. Actual CAD changes ONLY8internal
GroundM5bolt/nut STEP/STL: source-dimensional ISO4762M5x20fullthread/4AFsocket
2.5deep and ISO4032M5 8AF/4.7hexnuts.70STEPrefsunchanged. Full78assembly/BOM
and identity7 bindactualrefs. Frame/Groundkey and proven1101motor/1996hub/Finger reused.

12mmgrip/3.3mmprojection(4.125pitches),not effectiveengagement/preload/threadcapacity.
Exacthead32.986722863/nut31.667331399mm2areas matchindependentanalytic/overlap
checks within6e-12relative. Nutfootprintchangedfromold43.297115793mm2; new
conditionalminorcorelength14.35mm/k176765.277266N/mm replaces14mm. Old19field
cannotbe transferred asnew20stress/reactions. ConditionalCADmass.989532670863kg,
+.708886998gfrom19; requiredBasewrench[-.408610416667,0,9.704000566719,
-.076747158989,-.219469462599,0]N/Nm. Not measuredmass/sourcebound/physicalanchor.

78validsolids/191Booleanpairs/nointerference. 56internalhardware+124toolposes
including52Lkeyindexposes/360comparisons;63Basefixtureposes/91comparisons;
81moduleposes/303comparisons; independentaggregate/STL and one stored32element
loadedcatenary/rotorpose26comparisons clear. OrderedFrame/Ground->internalretention
beforeFinger/Base->withdrawtools->Basefixture->Finger/Drive/Cap. Source-dimensional
29/74Lkey andgeneric19wide130long5.8thickholdingcorridor only,notexacttoolCAD/
CCD/threadtightening/preload/tolerance/process/physicalassembly/full3FingerStage1.
Initial108toolcounttypo inrecorderreport/gate11 ispreserved; authoritativegate12/
closeout correctsto124actualenumeratedposes. No criteria/resultrelaxation.

PreservednewFAILs: longverticaldriverRoot-shelfcollision68.590944mm3 and Groundkey
holdingtoolcollision33.060090mm3(witness1); own-nutcollisionfromwrongrotatedhexopening
(witness2). Final lateralLkey/heldnutpath correctsgeometry; nofailuredeleted.

Actualparent19savedRootx50.5facefit328nodes/maxerror6.571e-7mm andMotor6DOF applied.
Relativeaxistilt.000145529071rad; separatelymovingoldwire splitsendpoint by
[.001454230,.013208505,.006041874]mm. Separateopposedforcerotationscreateartificial
netYforce-.000171093N. FreeYgaugeoffsets areNOTuniquephysicalretention/measurement.
ExplicitONE-WAY PLANARfeedbackkeepsglobalXobjectstop andmovedRoot/Motor/localgravity:
normal.408610416667->.408616322310N(+.001445299%); force5.77e-16N,cone/gaps/station
passreducedbranch. Zero reproducesparent;16/32Gaussnormal4.44e-16relative;
independentclosedformstringendpoint9.81e-15m andgravityvirtualwork3.43e-10relative.
ReportedRootwrench ismovingFinger subset; fixedRoot/clampweights/localtraction not
newlyrecoupled. Not3D/new20elastic/strength/mesh/time/globalenergy/graspapproval.

Crucialactualcontactcorrection: MotorfrontY=-9.5 hasFrame53.072788199/Cap51.911516624
mm2faces omittedfrom19solver. Savedselectedgauge33Frame/35Capnodespenetrateup to
.001075917/.001132415mm. FreeMotorYbackshiftcanopenthesecontacts; noautomaticnewstop
necessity/capacityfailureclaim. RootcoincidentplanarYcontactarea0. Parent19fieldis
verifiedonlyforitsrecordedincompletecontactmodel. Originalevidencenotrewritten.

All22systemgates UNQUALIFIED in models/primary_system_gate_state12.json; newlysolved
whole-systemgatesNONE. OldFrame52.7693%,Rail1.30247%,Ground/BasemeshFAILs,oldgap
TIMEOUTandtwo420slimitraces preserved. No fine/gapretry/newFEM/SOFA. Trustedunchanged
finalrelease15 INTEGRATED_NOT_QUALIFIED/24errors/exit2; noStage3/hardwareclaim.

NEXT exactID goal_primary_spatial_front_contact_feedback: SAME20,firstcomplete
actualMotorfrontunilateralcontacts/freeY/spatialstring/rotor/exitloads. Do notturn
MotorYgaugeintoaphysicalsupport orrotateopposedforcesindependently. CarryactualRoot
fit/globalXstop/movingANDfixedweights/fullcouples; update20nutfootprint14.35mmcore
andmassbeforeONEjustifiedcoarsecontactsolve. AddsameP1positiveretentiononlyifactual
existingpathrequiresit; nofine/gapretry/newarchitecture/blanketmeshstrategy.
Thread/class/minima/preload,physicalanchor/case/bearings,friction/protector/full3Finger/
globalenergy remainblocked.

15boundedanalysischildrenreaped,92.4677042381childseconds,0newtimeouts/unknowns;
4GiB/420seach,peakconcurrency2.0RUNNINGqueue tasks/0ownedanalysischildren.
STOPabsent/pinsunchanged. NoGitadd/commit/push/historyrewrite/SDK/securitymanager/
save/guard/gatesourcechanges,purchase/hardware/credentials/providerselection/
subagents/recursivelaunches. Originaluserfilespreserved. Supervisoralone savesexactbytes:
runtime/goal_authorized_20261127_7/save_request9.json. SavePENDING.
Authoritativecloseout validation/integrated/primaryP1_cycle10_closeout/summary.json;
detailed reports/primaryP1_retention_feedback_engineering.md with corrections in
reports/primaryP1_retention_feedback_closeout.md. Earliercheckpoint followsunchanged.

---

'''
 # Computed time rather than a copied estimate.
 text=text.replace('92.4677042381childseconds',f"{result['recorded_child_seconds']:.10f}childseconds")
 cp.write_text(text+cp.read_text())
 old=set(before['preexisting_untracked']);untracked=set(subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z']).decode().split('\0'))-{''};modified=set(subprocess.check_output(['git','diff','HEAD','--name-only','--no-renames','-z']).decode().split('\0'))-{''};paths=sorted(modified|(untracked-old));assert not(set(paths)&old)
 assert all(p.startswith('product_prototype/stage12_integrated/') and '/runtime/' not in p and (REPO/p).is_file() and (REPO/p).stat().st_size<50_000_000 for p in paths);assert not any(p in ledger['source_pins'] for p in paths);assert not any(p.startswith('product_prototype/stage12_integrated/cad/exports/') and '/primaryP1_retention20/' not in p for p in paths)
 files=[ref(REPO/p) for p in paths];results=[src,mainpath,out/'summary.json']+[REPO/r['path'] for r in mainresult['evidence'].values()]+[REPO/r['path'] for r in mainresult['preserved_new_failures']]+[releasepath];assert all(ref(p) in files for p in results)
 actual=[]
 for r in cad['changed']:actual.extend([r['STEP']['path'],r['STL']['path']])
 actual.extend([cad['assembly']['path'],cad['BOM']['path'],str(gp.relative_to(REPO)),str((ROOT/'scripts/primary_ground_retention.py').relative_to(REPO)),str((ROOT/'scripts/primary_support_feedback.py').relative_to(REPO))]);assert all(p in paths for p in actual)
 progress=dict(category='DESIGN_CHANGE',task_id=mainresult['task_id'],mechanism='Same78partP1actual8internalM5socket/hexSTEPSTL,3.3mmprojection/finitefootprints/orderedassembly. One-wayplanarloadfeedbackverified; omittedactualMotorfrontYcontacts/freeY/spatialloads identified. All22unqualified,failurespreserved; nooldfieldpromotion.',system_gate_ids=['cad_model_match','changed_stage1_revalidation','continuous_load_path','motor_alignment_reactions','physical_mass_inertia','numerical_convergence','root_palm_strength','qualified_worst_case'],actual_change_files=actual,candidate_reference=ref(src),next_task_id=ntid,strategy_change=True)
 request=dict(expected_HEAD=HEAD,message='Implement P1 socket/hex Ground retention and verify assembly/footprints; bound support feedback and preserve spatial-contact blockers',files=files,results=[ref(p) for p in results],engineering_progress=progress);assert len(request['message'])<=160 and '\n' not in request['message'];target=ROOT/'runtime/goal_authorized_20261127_7/save_request9.json';assert not target.exists();dump(target,request)
 print(dict(request=str(target.relative_to(REPO)),files=len(files),total_bytes=sum((REPO/p).stat().st_size for p in paths),children=len(executions),child_seconds=result['recorded_child_seconds'],source_pins_unchanged=True,whole_system_release=False))
if __name__=='__main__':main()
