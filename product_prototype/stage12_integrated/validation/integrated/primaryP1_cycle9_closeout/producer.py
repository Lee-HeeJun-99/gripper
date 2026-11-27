"""Exact-byte save-only closeout. Never stages/commits or launches research."""
import json,subprocess,shutil,datetime
from baseline_registry import ROOT,REPO,ref,sha,dump
HEAD='581f6de37e7937be60fc490c02f2e438b77f8188'
def load(p):return json.loads(p.read_text())
def main():
 assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==HEAD;assert not subprocess.check_output(['git','diff','--cached','--name-only'],text=True).strip();assert not(ROOT/'runtime/STOP').exists()
 before=load(ROOT/'runtime/goal_authorized_20261127_7/checkpoint_before8.json');assert before['HEAD']==HEAD
 main=ROOT/'validation/integrated/primary_cycle9/summary.json';m=load(main);src=ROOT/'cad/exports/primaryP1_framekey19/summary.json';cad=load(src);g=load(ROOT/'models/primary_system_gate_state10.json');assert len(g['gates'])==22 and all(x['status']=='UNQUALIFIED' for x in g['gates'])
 out=ROOT/'validation/integrated/primaryP1_cycle9_closeout';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');pins={p:sha(REPO/p)==h for p,h in before['source_pins'].items()} if 'source_pins' in before else {p:sha(REPO/p)==h for p,h in load(ROOT/'runtime/goal_authorized_20261127_7/ledger.json')['source_pins'].items()};assert all(pins.values())
 q=load(ROOT/'INTEGRATED_TASKS.json');assert not any(t['status']=='RUNNING' for t in q['tasks']);release=ROOT/'validation/integrated/primaryP1_release13/summary.json';rr=load(release);assert rr['status']=='INTEGRATED_NOT_QUALIFIED'
 r=dict(status='ACTUAL_P1_CYCLE9_SAVE_ONLY_EXACT_BYTE_HANDOFF_NOT_RELEASE',producer=ref(out/'producer.py'),main=ref(main),candidate=ref(src),report=ref(ROOT/'reports/primaryP1_framekey_engineering.md'),final_trusted_release=ref(release),final_trusted_release_exit_code=2,release_error_count=len(rr['errors']),system_gate_state=ref(ROOT/'models/primary_system_gate_state10.json'),source_pins_unchanged=pins,analysis_wrapper_count=m['recorded_children_wrapper_reaped'],known_child_seconds=m['recorded_child_seconds_known'],exact_child_time_unknown_count=m['exact_child_time_unknown_count'],additional_child_seconds_lower_bound=m['additional_child_seconds_lower_bound'],timeouts=m['timeouts'],owned_analysis_children_running=0,running_queue_tasks=0,STOP_present=False,limits=dict(memory_bytes=4294967296,timeout_s=420,peak_concurrent_long_analysis_children=4),newly_qualified_system_gate_ids=[],remaining_system_gate_ids=[x['id'] for x in g['gates']],actual_changed_parts=['OPEN_FRAME','GROUND_PLATE'],unchanged_part_refs=76,next_task_id=m['next_task_id'],whole_system_release=False,hardware_status='HARDWARE_NOT_MEASURED',SOFA_runs=0,git_add_commit_attempted=False,save_status='PENDING_SUPERVISOR_EXACT_SAVE',limitations=m['limitations'])
 dump(out/'summary.json',r)
 state=load(ROOT/'PRIMARY_PRODUCT.json');state.update(latest_closeout=ref(out/'summary.json'),latest_closeout_child_count=r['analysis_wrapper_count'],latest_closeout_child_seconds_known=r['known_child_seconds'],latest_closeout_child_time_unknown=r['exact_child_time_unknown_count'],latest_closeout_child_seconds_lower_bound=r['additional_child_seconds_lower_bound'],prior_outer_joint_scope='NewfiveelasticbodyRootFrameCapGroundBase/sixDOFmotor solution replacesoldouterjointonlyscope atconditionalnominaldemand. ActualphysicalBaseanchor/Fingerfeedback/threadcase/sourceallowables unresolved. No meshPASS.');dump(ROOT/'PRIMARY_PRODUCT.json',state)
 current=load(ROOT/'CURRENT_CANDIDATE.json');current.update(latest_closeout=ref(out/'summary.json'),primary_state=ref(ROOT/'PRIMARY_PRODUCT.json'),prior_outer_joint_scope=state['prior_outer_joint_scope']);dump(ROOT/'CURRENT_CANDIDATE.json',current)
 for t in q['tasks']:
  if t['id'].startswith('goal_primary_'):t['primary_state']=ref(ROOT/'PRIMARY_PRODUCT.json')
 dump(ROOT/'INTEGRATED_TASKS.json',q);nt=load(ROOT/'NEXT_TASK.json');nt['next']=next(t for t in q['tasks'] if t['id']==m['next_task_id']);dump(ROOT/'NEXT_TASK.json',nt)
 text='''# Latest actual P1 finite compliant load path — 2026-11-27, Supervisor save pending

Starting actual HEAD 581f6de37e7937be60fc490c02f2e438b77f8188.
Selected exact queue ID goal_primary_compliant_wall_cradle_frame.
SAME ONE primaryP1_framekey19,78parts; failedAO/adoptedAA and original
3Finger/cartridge/jamming extensions preserved. ONLY OPEN_FRAME/GROUND_PLATE
STEP/STL changed: integral8x6x3Framekey,R0.5root; Ground blindpocket,
R1corner toolreliefs,.6mm45degentry,.2mmroofclearance. Full78STEP/BOM and
identity6 bind76unchangedpartrefs. Source1101/1996/standardfixtureparts reused.

Newactualkey fixes missingfrictionlessFrameGroundFxpath without sharedM5fixation.
Finitekeyareas9.6mm2eachX/14.4mm2eachY; seat5059.487380938695mm2.
Necessaryfullwrenchequilibrium passes; keyomissionfails. Exactindependent
Boolean/Richardsonarea,78validsolids/191pairs/nointerference, sixFramefixture
insertionposes,81moduleposes/RFtools/independentaggregateSTL and one stored
loadedcatenary/rotor pose pass boundednominalchecks. NotCCD/tolerance/process/
actualthreadtightening/full3FingerStage1 orphysicalassembly.

New actualfiveelasticbodyRootBack/Frame/Cap/Ground/Base plus6DOFrigidmotor
conditionalcontact solution:74040DOF,14tensiononlyminorcoreaxialsprings,
finiteactualseats/walls/motorlands/newFramekey/existingGroundBasekey.
OSQP4000iterationlimit preserved; separate3iterationactiveKKT closesALL
originalconstraints. Independentdirecttetraforce/energy/stress/bolt/contact/
rigidwork andcorruptdisplacement rejection pass. NominalFramepeak3.182591MPa,
Root.108528,Cap.436393,Ground.452818,Base.493421MPa areconditionalunconverged
peaks,NOTstrengthapproval. Point/volume rigidgauge nominalstates agreephysical
strain/forces; absolute displacementgaugechanges areNOTstiffnessimprovement.

GravityfullRoot/MotorforceANDcouple includepriorloadedFinger/string/rotor;
fixedRailPET/clampmass goesRootport,hardwareweight toBaseport; finitebodies
ownweight integratedfromtetra. ExactCADconditionalmass.988823783865kg and
Basewrench[-.408610416667,0,9.697048760040,-.076674165019,-.219347805982,0]
N/Nm; nominalmeshgravityrequiresFZ9.701546171536N. Thisdifferenceisgeometric
massquadrature,notunknownforcecancellation. InchainJSONlegacyfield
external_FrameGround_port actuallyidentifiesTEST_BASE. No hiddenFramefixation.
FiniteBaseexternaltraction isNOTphysicalbenchanchor. Root/MotorfreeY and
CapfreeXY/yaw gauges carrynegligibleload,NOTpositivephysicalretention.
FrozenFingerboundaryfeedback/localhardwarebearing/thread/sourcecase/material
minima andfriction/protection/globalenergy remainunresolved.

All22systemgates UNQUALIFIED in models/primary_system_gate_state10.json;
newwhole-systemgates NONE. OldFrame52.7693%,Rail1.30247%,Ground/BasemeshFAILs
andold420sgaptimeout retained. Fine237165DOFnewtrial entered420slimitbranch,
then killgroupalreadyabsent raisedProcessLookupError. Wrapperexit1 known;
exactanalysisexitcode/timeUNKNOWN,420slowerboundonly,no field/summary,no retry.
Originalassertion/serialization/syntax/fixedmasskey errors,uncenteredfootprint
spuriousmoment,OSQPmaxiteration/CapvolumeFAILs andwrongauxdualdiagnostic are
preserved. Independentupperfieldverify correctsinterpretation withoutrewriting
originalFAIL. The already-started74040DOF .02gapcontrast alsohit420slimitbranch with
killgroupabsent/exactexitunknown/no field orsummary; NOgap/preloadPASS.
Both420slowerbounds andall executioncounts arein
primary_cycle9/summary.json and primaryP1_cycle9_closeout/summary.json.
Afterfine limit onlyexistingtasktermination/savedfieldinspection/releaseaudit/
exactbytehandoff; no newphysics/preloadcontrast/restart.

NEXT exact ID goal_primary_framekey_fit_feedback: SAMEP1 actualinternalGround
socketM5/hexnutretention,adequateprojection/tool/assemblyaccess fromexisting
ISO4762/4032sources; smoothinternalM5envelopes doNOTcertifytightening/engagement.
UpdateactualsameP1CAD/mass/footprints then existinggravityFinger/string Root/
Motorposefeedback andpairedwrenches. No automaticfine/gap timeoutretry,
blanketmeshrefinement,newarchitecture orsharedM5fixation. Physicalanchor,
case/bearings/materialminima,full3Finger/friction/protector/globalenergy blocked.

Trustedunchangedrelease13 remainsINTEGRATED_NOT_QUALIFIED,24errors,exit2.
NoP1same-revisionrelease/Stage3/SOFA/hardware claim. Sourcepins unchanged.
0RUNNINGqueue tasks/0ownedanalysischildren at finalhandoff. No Gitadd/commit/
push/historyrewrite/SDK/securitymanagerguardgatechanges/purchase/hardware/
credentials/providerselection/subagents/recursivelaunches. Originaluserfiles
preserved. ExactSupervisor save request runtime/goal_authorized_20261127_7/
save_request8.json. SavePENDING; Supervisor alone savesverifiedbytes.
Detailed CAD/numerics/failures: reports/primaryP1_framekey_engineering.md.

---

'''
 cp=ROOT/'CHECKPOINT.md';cp.write_text(text+cp.read_text())
 old=set(before['preexisting_untracked']);untracked=set(subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z']).decode().split('\0'))-{''};modified=set(subprocess.check_output(['git','diff','HEAD','--name-only','--no-renames','-z']).decode().split('\0'))-{''};paths=sorted(modified|(untracked-old));assert not(set(paths)&old)
 assert all(p.startswith('product_prototype/stage12_integrated/') and '/runtime/' not in p and (REPO/p).is_file() and (REPO/p).stat().st_size<50_000_000 for p in paths);files=[ref(REPO/p) for p in paths]
 results=[main,out/'summary.json',src,ROOT/'validation/integrated/primaryP1_framekey_witness2/summary.json',ROOT/'validation/integrated/primaryP1_framekey_assembly1/summary.json',ROOT/'validation/integrated/primaryP1_framekey_verify1/summary.json',ROOT/'validation/integrated/primaryP1_framekey_loaded1/summary.json',ROOT/'validation/integrated/primaryP1_chain0_h5_3/summary.json',ROOT/'validation/integrated/primaryP1_chain_verify1/summary.json',ROOT/'validation/integrated/primaryP1_chain_contrast1/summary.json',ROOT/'validation/integrated/primaryP1_compliant_failures1/summary.json',release]
 progress=dict(category='DESIGN_CHANGE',task_id='goal_primary_compliant_wall_cradle_frame',mechanism='Same78partP1: actual integralFrameGroundkey/relievedpocket suppliesmissingfrictionlessshear; independentfinitecontact/78solidassembly and fiveelasticbody/sixDOFmotor fullgravitywrench contact verification. All22remainunqualified; fine420slimitraceandallfailurespreserved; saveonlyafterlimit.',system_gate_ids=['continuous_load_path','motor_alignment_reactions','cad_model_match','changed_stage1_revalidation','physical_mass_inertia','numerical_convergence','root_palm_strength','qualified_worst_case'],actual_change_files=[str((ROOT/p).relative_to(REPO)) for p in ['cad/exports/primaryP1_framekey19/OPEN_FRAME.step','cad/exports/primaryP1_framekey19/OPEN_FRAME.stl','cad/exports/primaryP1_framekey19/GROUND_PLATE.step','cad/exports/primaryP1_framekey19/GROUND_PLATE.stl','cad/exports/primaryP1_framekey19/ASSEMBLY.step','cad/exports/primaryP1_framekey19/BOM.json','scripts/primary_frame_ground_key.py','scripts/primary_upper_compliance.py','scripts/verify_primary_upper.py','models/primary_system_gate_state10.json']],candidate_reference=ref(src),next_task_id=m['next_task_id'],strategy_change=True)
 request=dict(expected_HEAD=HEAD,message='Add P1 Frame-Ground key and verify actual finite compliant chain; preserve mesh, gap and timeout blockers',files=files,results=[ref(p) for p in results],engineering_progress=progress);assert len(request['message'])<=160 and '\n' not in request['message'];assert all(r in files for r in request['results']);assert all(p in paths for p in progress['actual_change_files']);target=ROOT/'runtime/goal_authorized_20261127_7/save_request8.json';assert not target.exists();dump(target,request)
 print(json.dumps(dict(request=str(target.relative_to(REPO)),files=len(files),total_bytes=sum((REPO/p).stat().st_size for p in paths),children=r['analysis_wrapper_count'] if isinstance(r,dict) and 'analysis_wrapper_count' in r else m['recorded_children_wrapper_reaped'],known_child_seconds=m['recorded_child_seconds_known'],unknown_child_times=m['exact_child_time_unknown_count'],timeouts=m['timeouts'],source_pins_unchanged=True,whole_system_release=False)))
if __name__=='__main__':main()
