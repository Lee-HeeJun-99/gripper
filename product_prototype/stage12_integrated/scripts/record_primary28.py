"""Cycle28 exact-byte handoff preparation; no index writes or Git mutations."""
import sys,json,copy,subprocess,datetime
from baseline_registry import ROOT,REPO,ref,sha,dump
from supervised_save import validate,changed,untracked
from goal_manager_policy import engineering_record
HEAD='623fe07360e068ba846e6313bc08b498455eae84'
TASK='goal_primary_fivebody_finite_support_transaction_coupled_loads'
NEXT='goal_primary_hardware_ports_gamma_compatibility_surface_transaction'


def main():
 load=lambda p:json.loads(p.read_text());base=ROOT/'validation/integrated';rt=ROOT/'runtime/goal_authorized_20261127_7'
 assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==HEAD
 assert not(ROOT/'runtime/STOP').exists();ledger=load(rt/'ledger.json');assert all(sha(REPO/p)==h for p,h in ledger['source_pins'].items())
 originals=load(rt/'cycle27_start_integrity.json')['untracked'];assert all(sha(REPO/p)==h for p,h in originals.items());old=set(load(rt/'checkpoint_before27.json')['preexisting_untracked']);assert set(originals)==old
 cp=ROOT/'cad/exports/primaryP1_ycapture24/summary.json';cad=load(cp);assert len(cad['part_references'])==78 and all(sha(REPO/r['path'])==r['SHA256'] for r in cad['part_references'].values())
 names=[f'primaryP1_{p}_transaction28' for p in ['frameground','groundbase','motorframe','motorcap','capframe']]+['primaryP1_omitted_separation28','primaryP1_transaction_audit28','primaryP1_fresh_sources28','primaryP1_hardware_gravity28','primaryP1_root_trial28']
 docs={n:load(base/n/'summary.json') for n in names};evidence={n:ref(base/n/'summary.json') for n in names}
 assert all(d['candidate']==ref(cp) and d['accepted_equilibria']==0 and not d['whole_system_release'] for d in docs.values())
 executions=[load(p) for p in sorted(base.glob('primary_cycle28*/execution.json'))];assert len(executions)==10 and all(e['reaped'] and not e['STOP'] for e in executions)
 assert all(not e['timeout'] and e['elapsed_s']<420 for e in executions)
 # Preserve physical FAIL outputs, never turn process exit alone into PASS.
 failures=[dict(result=evidence[n],failed_checks=[k for k,v in d['checks'].items() if not v]) for n,d in docs.items() if not all(d['checks'].values())]
 audit=docs['primaryP1_transaction_audit28'];sources=docs['primaryP1_fresh_sources28'];hardware=docs['primaryP1_hardware_gravity28'];trial=docs['primaryP1_root_trial28'];seconds=sum(e['elapsed_s'] for e in executions)
 note=('Same78part primaryP1_ycapture24 actual CAD unchanged. Five remaining pair unavailable-row guards implemented; independent ray-parity and exhaustive-distance audit now covers all sixpairs and all19395/23985unavailable samples. '
 'Original.05mm-perbody inactive bound FAIL170/252rows preserved. Common actual-vertex nextstep bounds .000038916833875/.000036776069447mm certify exterior inactivity only. All150102/197202material rows and originalNaNgaps retained; no physicalpressure. '
 'Nine omitted pairs among sixsupport bodies have whole-polyhedral-solid AABB separation. Fresh conditional planarFinger/spatialTendon solves retain supplied upstreamgamma and return its generalizedforce; newRoot720/1055node pullbacks verified, no oldsupportsourcefield. '
 'Fresh28hardware CAD gravity/inertia gives disjoint78part accounting; own free hardware wrench, no arbitraryBase lump/counterload. RootFrame fullrow lateraltrial requery is separately recorded. No actual supportequilibrium/adjacentcontinuoussurface/gammaattachment/hardwaretransfer/physicalBaseanchor/strength/energy/release.')
 hypothesis=('Continue SAME78part primaryP1_ycapture24 Motor->stock1996hub->Drum->Tendon->Finger->Root->Frame->Ground->Base; preserve sidecartridge/distalPETslide/3Finger/jamming. '
 'FIRST derive physical compatibility of upstreamgamma with actualRoot attachment: primaryP1_fresh_sources28 retains it and returns Qgamma, but nominal reference solves do not authorize a second hidden relative translation of clampedFinger/fixedRootparts. Keep allphysicalRoot/Motor modes and explicitgamma until compatibility is physically justified; no arbitraryfix/spring/rowdeletion. '
 'Use fresh28hardware gravity/inertia and actual28bearing footprints to construct physical same-revision hardware-to-adjacent-body load transfer with thread/core/flank/shear/tilt/material assumptions explicit; never relocate allhardware mass toBase. '
 'Then implement accepted finite-chart continuation and continuous adjacent source/owner boundary coverage, using primaryP1_transaction_audit28 common actualvertex bounds, primaryP1_root_trial28 all-row trialrequery, sixpairfullJ/14unilateralaxialbranches and nineomitted-support-pair solidseparation. Recompute allguards/owners at everytrial and reject stale/grazing/negativegap/unresolved chart; materialpointguard is not fullsurfaceCCD. '
 'Fresh conditional source pullbacks are reference evaluations, not oldseated22Pq/pressure/2208row/sourcefield transfer or a supportequilibrium. Hardware ownwrenches and necessaryanchorresultant are not appliedBasecounterloads; specify actualfinitephysicalanchor before solve. '
 'Freeze/review complete source/generated identities before coupled solve; originalforce1e-8N/gap1e-10mm/local.05mm/rad/conesign/gauge/complementarity/Armijo/mesh1%/time.1% unchanged. Source-backedminima/thread/finitewire/protector/friction/full3DFinger/globalenergy/fullsame-revision3Finger/all22gates remain. NoStage3.')
 gp=ROOT/'models/primary_system_gate_state32.json';g=load(ROOT/'models/primary_system_gate_state31.json');g.update(predecessor=ref(ROOT/'models/primary_system_gate_state31.json'),candidate=ref(cp),latest_same_revision_transaction_and_sources=evidence,newly_qualified_system_gates=[],whole_system_release=False)
 affected=['cad_model_match','changed_stage1_revalidation','continuous_load_path','motor_alignment_reactions','physical_mass_inertia','numerical_convergence','root_palm_strength','qualified_worst_case']
 for gate in g['gates']:
  if gate['id'] in affected:gate['reason']+=' Cycle28: '+note
 assert len(g['gates'])==22 and all(x['status']=='UNQUALIFIED' for x in g['gates']);dump(gp,g)
 pp=ROOT/'PRIMARY_PRODUCT.json';primary=load(pp);primary.update(selected_task_id=TASK,next_task_id=NEXT,system_gate_state=ref(gp),latest_same_revision_transaction_and_sources=evidence,CAD_this_cycle='NONE: actual product validation of unchanged78part primaryP1_ycapture24; new pair guards, independent audit, source/gamma block,28hardware CAD gravity and lateraltrial requery.',current_physics_status='SIXPAIR_SAMPLE_GUARDS_AND_FRESH_CONDITIONAL_SOURCES_NO_SUPPORT_EQUILIBRIUM',current_physics_sourcefield=None);dump(pp,primary)
 qp=ROOT/'INTEGRATED_TASKS.json';queue=load(qp);selected=next(t for t in queue['tasks'] if t['id']==TASK);assert selected['status']=='READY';selected.update(status='PARTIAL_VALIDATED',last_run_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),consecutive_runs=selected.get('consecutive_runs',0)+1,result=evidence['primaryP1_transaction_audit28'],reason=note,next=NEXT)
 new=copy.deepcopy(selected);new.update(id=NEXT,status='READY',priority=selected['priority']-10,hypothesis=hypothesis,concrete_first_step='Derive and audit actualRoot/upstreamgamma compatibility before coupling freshsource block; then physical28hardware finitefootprint load transfer and full adjacent-surface transaction.',known_blockers=[note,'All22system gates UNQUALIFIED. Hardware gravity accounted but physicaltransmission absent; source gamma physicalcompatibility and physicalBaseanchor absent.'],parent_result=evidence['primaryP1_hardware_gravity28'],result=None,reason=None,next=None,last_run_utc=None,consecutive_runs=0,primary_state=ref(pp));assert not any(t['id']==NEXT for t in queue['tasks']);queue['tasks'].append(new);assert not any(t['status']=='RUNNING' for t in queue['tasks']);dump(qp,queue)
 nt=load(ROOT/'NEXT_TASK.json');nt.update(status='SOURCE_INTEGRITY_PASS',errors=[],next=new,running_task_records=[],warning=note,resume_command=hypothesis);dump(ROOT/'NEXT_TASK.json',nt)
 out=base/'primary_cycle28_record';out.mkdir(exist_ok=False)
 dump(out/'summary.json',dict(status='ACTUAL_P1_SAMPLE_TRANSACTION_FRESH_COUPLED_SOURCE_AND_78PART_GRAVITY_VALIDATED_NOT_RELEASE',candidate=ref(cp),selected_task_id=TASK,next_task_id=NEXT,evidence=evidence,actual_CAD_change_files=[],actual_part_count=78,
  sixpair_material_guard_results=audit['results'],conditional_source_results=sources['results'],conditional_78part_gravity_results=hardware['results'],lateral_trial_checks=trial['checks'],lateral_trial_results=trial['results'],newly_qualified_system_gate_ids=[],remaining_unqualified_system_gate_ids=[x['id'] for x in g['gates']],accepted_equilibria=0,whole_system_release=False,stage3_authorized=False,
  physics_child_seconds=seconds,execution_count=len(executions),executions=[ref(p) for p in sorted(base.glob('primary_cycle28*/execution.json'))],children_reaped=True,failures_preserved=failures,
  original_05mm_inactive_certificate_failure_rows=[r['original_05_bound_FAILED_rows'] for r in audit['results']],prior_failures='Allhistorical immutable outputs remain; original.05mm boundFAIL not overwritten, accepted as a failed proposal, no criterion relaxed.',
  necessary_anchor_wrench_is_applied=False,protected_source_pins_unchanged=True,original_untracked_files_unchanged=len(originals),queue_RUNNING=0,hardware_status='NOT_MEASURED',
  alternatives_review=[dict(alternative='A Reuse proven massive string/planarFinger with explicit upstreamgamma',decision='IMPLEMENTED_CONDITIONAL_SOURCE_BLOCK',blocker='Physicalgamma attachment/full3DFinger/same-revision supportequilibrium notcertified.'),dict(alternative='B Own28hardware rigidgravity and finiteactualbearing ports',decision='GRAVITY_AND_CAD_ACCOUNTING_IMPLEMENTED_TRANSFER_PENDING',blocker='Thread/shear/tilt/preload/physicalanchor/material minima required; do not lump toBase.'),dict(alternative='C Ignore unavailablecharts at original.05mm bound or substituteBasecounterload',decision='REJECTED',blocker='170/252unavailable points fail original localinactive test, hardware loadpath and anchor cannot be fabricated.')],limitations=[note,hypothesis]))
 rows='; '.join(f"h{r['mesh_level']}: {r['all_material_rows']}rows, {r['all_original_unavailable_rows']}unavailable, original.05FAIL{r['original_05_bound_FAILED_rows']}, b={r['common_actual_vertex_bound_mm_per_body']:.12g}mm, remaininglocalunavailable={r['remaining_unavailable_rows_within_common_bound']}" for r in audit['results'])
 tr='; '.join(f"h{r['mesh_level']} Y={r['RootY_trial_mm']:+g}mm: remaining{r['remaining_unresolved_rows']}, negativegap{r['negative_gap_rows']}" for r in trial['results'])
 text=f'''# P1 sample transaction, fresh coupled sources and 78part gravity — cycle28

Actual starting HEAD `{HEAD}`. Exact selected queue ID `{TASK}`. ONE unchanged78part `primaryP1_ycapture24`, separate from failed AO, remains primary Motor→stock1996hub→Drum→Tendon→Finger→Root→Frame→Ground→Base. Preserve replaceable sidecartridge/distalPETaxialslide/3Finger/jamming. No Stage3.

Actual changed CAD: NONE. Actual product validation binds all78actual STEP parts/BOM/assembly hashes. No replacement ideal coupon or candidate. Prior actual assembly/tool/tendon checks remain partial historical evidence, not a new assembly release.

{note}

Independent triangle-ray parity audits EVERY unavailable sample, with12inside tetra-centroid controls per pair/mesh and exhaustive point-to-alltriangle distances. {rows}. All original NaNgaps remain; unavailable derivatives are not set tozero. Common bound is maximum ACTUAL vertex motion, including Motor rotation-induced displacement, not a radian/mm interchange. Stalehash/negativebound/oversized-step rejection and finite owner perturbation controls pass. This guards nextstep sampled exterior inactivity only, not accepted-chart/fullsurface transaction or convergence.

All9omittedpairs among sixsupportbodies have complete linear-tetra-solid AABB separation for.05mm maximum actualvertex motion perbody. This covers surface interiors through solid envelopes, but not exact curvedBRep approximation error or all78part CCD. Adjacent continuoussurface coverage remains incomplete.

Fresh conditional sources: identityreference Root/Motor, no inherited supportu/pressure/portloads. Supplied gamma0,+/-.00001mm retained;5internal string equations solved, Qgamma returned instead of imposingFeY=0. Fresh coupled planarFinger/spatialTendon normal={sources['results'][0]['normal_N']:.12g}N at inherited conditionalT={sources['results'][0]['T_N']:.12g}N. Qgamma slope={sources['gamma_force_derivative_N_per_mm']:.12g}N/mm; order16→32 normaldifference={sources['order16_32_normal_force_difference_N']:.12g}N. Every conditional source check passes; Root720/1055nodes independently recover force/moment. This is NOT operating-demand recertification or fullsupportequilibrium. Physical compatibility of upstreamgamma versus actualRoot attachment must be reviewed, not silently fixed/eliminated/duplicated.

Fresh CAD28fastener volume/centroid/inertia plus45upstreamparts+5elasticparts gives disjoint78part accounting. Conditional fastener nominal-envelope mass={hardware['results'][0]['conditional_hardware_total_mass_kg']:.12g}kg, gravity={hardware['results'][0]['hardware_gravity_wrench_N_Nm']}. Each remains its own free rigid wrench; actual28bearingbranch/side/adjacentbody references recorded, physical loadtransfer unimplemented. Smoothenvelope density7900kg/m3 is conditional, not actual threadmass/allowable. Necessary external anchor wrench h2={hardware['results'][0]['necessary_external_anchor_resultant_N_Nm']} is a design demand ONLY, NEVER applied balancingload or anchorcertificate. No arbitraryBase lump/cancellation.

Actual fullRoot-row finite lateral trial requery: {tr}. Checks={trial['checks']}. Each trial rebuilds accepted finiteowners/J and guards unavailable exterior points; no oldJacobian/pressure/sourcefield transfer. Trial geometry only, not physicalacceptedstep/forceequilibrium/continuoussurfacecertificate.

Failures preserved: original.05mm perbody inactive proposal FAIL170/252rows; all prior failed immutable trials untouched. New result failedchecks={failures}. All{len(executions)}analysischildren reaped, total{seconds:.9f}s, each4GiB/420s; no timeout/STOP/RUNNINGqueue/ownedchildren. No exit0-only success: summaries/logs/checks/physical limitations reviewed.

Newly solved SYSTEM gates: NONE. All22remainUNQUALIFIED in `models/primary_system_gate_state32.json`. Hardware NOTMEASURED. Existing source/minimum/thread/bearing/preload/anchor/finitewire/protector/friction/full3DFinger/mesh1%/time.1%/globalenergy/fullsame-revision3Finger remain. Actualunchanged physical criteria and protectedgate/security/manager/save/guard sources preserved.

Concrete next `{NEXT}`: {hypothesis}

New cycle numerical result `validation/integrated/primary_cycle28_record/summary.json`. All{len(originals)}originaluntracked and10protectedsourcepins unchanged. Noadd/commit/push/historyrewrite/deletion/SDK/subagent/recursiveagent/purchase/hardware/credentials/paidprovider. Exact save request `runtime/goal_authorized_20261127_7/save_request27.json`; only Supervisor saves verified bytes.

---

'''
 checkpoint=ROOT/'CHECKPOINT.md';checkpoint.write_text(text+checkpoint.read_text());(ROOT/'reports/primaryP1_transaction_sources28.md').write_text(text)
 def request():
  files=[ref(REPO/p) for p in sorted(changed(REPO)|(untracked(REPO)-old))]
  return dict(expected_HEAD=HEAD,message='Verify P1 finite sample guards and fresh coupled source loads with complete conditional78part gravity accounting',files=files,results=[r for r in files if r['path'].endswith('/summary.json')],engineering_progress=dict(category='ACTUAL_PRODUCT_VALIDATION',task_id=TASK,mechanism='Implement sixpair bounded inactive transaction guards, independent ray-parity audit, explicit-gamma coupled Finger/string source pullbacks, fresh28hardware CAD gravity and fullrow lateraltrial finite requery.',system_gate_ids=affected,actual_change_files=[r['path'] for r in files if '/scripts/' in r['path']],candidate_reference=ref(cp),next_task_id=NEXT,strategy_change=True))
 req=request();validate(REPO,req,HEAD,old);record=engineering_record(req,REPO);assert record['signature'] not in ledger['seen_engineering_signatures']
 dump(out/'preflight.json',dict(status='READ_ONLY_EXACT_SAVE_PREFLIGHT_PASS',engineering_record=record,original_untracked_files_unchanged=len(originals),source_pins_unchanged=True,queue_RUNNING=0,all_analysis_children_reaped=True))
 req=request();validate(REPO,req,HEAD,old);engineering_record(req,REPO);dump(rt/'save_request27.json',req)
 print(json.dumps(dict(files=len(req['files']),results=len(req['results']),child_seconds=seconds,request=ref(rt/'save_request27.json'))))

if __name__=='__main__':main()
