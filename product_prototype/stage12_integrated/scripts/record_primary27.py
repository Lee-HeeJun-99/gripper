"""Exact-byte research handoff; read-only validation, no Git/index mutation."""
import json,copy,subprocess,datetime
from baseline_registry import ROOT,REPO,ref,sha,dump
from supervised_save import validate,changed,untracked
from goal_manager_policy import engineering_record

HEAD='1b4370cb0f302e3cc5a8cc7017b17d8f29da7e82'
TASK='goal_primary_finite_concave_face_union_fullmodel'
NEXT='goal_primary_fivebody_finite_support_transaction_coupled_loads'


def main():
    load=lambda p:json.loads(p.read_text());rt=ROOT/'runtime/goal_authorized_20261127_7';base=ROOT/'validation/integrated'
    assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==HEAD
    assert not (ROOT/'runtime/STOP').exists();ledger=load(rt/'ledger.json');assert all(sha(REPO/p)==h for p,h in ledger['source_pins'].items())
    original=load(rt/'cycle18_original_integrity.json')['originals'];assert all(sha(REPO/p)==h for p,h in original.items());old=set(load(rt/'checkpoint_before26.json')['preexisting_untracked'])
    cadpath=ROOT/'cad/exports/primaryP1_ycapture24/summary.json';cad=load(cadpath);assert len(cad['part_references'])==78 and all(sha(REPO/r['path'])==r['SHA256'] for r in cad['part_references'].values())
    names=['primaryP1_face_union27','primaryP1_face_union27audit','primaryP1_signed_boundary27v2','primaryP1_boundary_jacobian27','primaryP1_inactive_certificate27','primaryP1_inactive_certificate27bounded','primaryP1_fivebody_rebuild27','primaryP1_axial_rebuild27env','primaryP1_axial_operator27','primaryP1_frameground_boundary27','primaryP1_groundbase_boundary27','primaryP1_motorframe_boundary27','primaryP1_motorcap_boundary27','primaryP1_capframe_boundary27','primaryP1_integrated_blocks27']
    docs={n:load(base/n/'summary.json') for n in names};evidence={n:ref(base/n/'summary.json') for n in names}
    assert all(d['candidate']==ref(cadpath) and d.get('accepted_equilibria',0)==0 and not d['whole_system_release'] for d in docs.values())
    assert not docs['primaryP1_inactive_certificate27']['checks']['all_unavailable_rows_certified_exterior_inactive']
    for name,d in docs.items():
        if name!='primaryP1_inactive_certificate27':assert all(d['checks'].values()),name
    executions=[load(p) for p in sorted(base.glob('primary_cycle27*/execution.json'))]
    assert executions and all(e['reaped'] and not e['STOP'] for e in executions)
    seconds=sum(e['elapsed_s'] for e in executions);integrated=docs['primaryP1_integrated_blocks27'];assembled=integrated['results']
    assert all(not r['physical_model_solve_ready'] and not r['sourcefield_transferred'] for r in assembled)
    out=base/'primary_cycle27_record';out.mkdir(exist_ok=False)
    note=('Same78part P1_ycapture24, actual CAD unchanged. Implemented full Root material finite-face union and signed gap charts; independently verified144concave two-branch transitions,320inside/outside winding probes and physical.1/.05/0/-.001mm shoulder gap sequence. '
          'New full-row RootFrame Jacobians preserve26604/33744samples and all independent nodes; no oldsourcefield transfer. New fivebody reference meshes/material/gravity and original conditional Root/Motor ports, fresh28CADbearing footprints/14axial branches, and sixadjacent finitecontact blocks assembled. '
          'All physical acceptance gates remain blocked: no new pressure/equilibrium/fullenergy/strength/mesh/time/3Finger release. Unavailable rows remain NaN. Original.05mm bound fails inactive certification; derived stricter RootFrame-only nextstep bound succeeds, not a global transaction.')
    hypothesis=('Continue SAME78part primaryP1_ycapture24 actual Motor->stock1996hub->Drum->Tendon->Finger->Root->Frame->Ground->Base; preserve sidecartridge/distalPETslide/3Finger/jamming. '
        'Use primaryP1_integrated_blocks27 full-row sixpair matrices, primaryP1_fivebody_rebuild27 newgeometry/referenceonly and primaryP1_axial_rebuild27env fresh28CADfootprints/14finite objective branches. FIRST resolve each remaining adjacent-pair unavailable signed chart into finite face alternatives or independently exterior inactive per-proposed-step certificates, preserving every material row and rejecting grazing/distinct nearest normals. '
        'RootFrame has1317/1692unavailable derivatives but all are exterior; original.05mm perbody certificate FAIL remains. Derived b=min(.05,(minimumdistance-1e-10)/4) gives.000708247196/.000406941458mm RootFrame-only nextstep bounds; never apply them as global or time-convergence certificates. Recompute on everyaccepted geometry and include all other pairs/omitted-pair separation/continuous-surface coverage. '
        'Then finish fresh coupled Finger/string/freeY source equation and exact remaining hardware gravity with independent physical Baseanchor; original conditional ports and meshgravity are not newequilibrium. Freeze/review all source/generated identities before anysolve. '
        'Keep all physical nodes/37rigid/freeYcoordinates,14unilateral axial branches and finite owners; no oldseated22sourcefield/Pq/2208rows pressures transfer, rowdeletion/artificial spring/fixation/friction/Basecancellation. '
        'Original fullforce1e-8N/gap1e-10mm/local.05mm/rad/conesign/gauge/complementarity/Armijo unchanged. Mesh1%/time.1%/materialminimum/thread/physicalanchor/finitewire/protector/globalenergy/full3Finger/all22system gates remain. No Stage3.')
    gp=ROOT/'models/primary_system_gate_state31.json';g=load(ROOT/'models/primary_system_gate_state30.json');g.update(predecessor=ref(ROOT/'models/primary_system_gate_state30.json'),candidate=ref(cadpath),latest_same_revision_finite_blocks=evidence,newly_qualified_system_gates=[],whole_system_release=False)
    for gate in g['gates']:
        if gate['id'] in ['cad_model_match','changed_stage1_revalidation','continuous_load_path','motor_alignment_reactions','physical_mass_inertia','numerical_convergence','root_palm_strength','qualified_worst_case']:gate['reason']+=' Cycle27: '+note
    assert len(g['gates'])==22 and all(x['status']=='UNQUALIFIED' for x in g['gates']);dump(gp,g)
    pp=ROOT/'PRIMARY_PRODUCT.json';primary=load(pp);primary.update(selected_task_id=TASK,next_task_id=NEXT,system_gate_state=ref(gp),latest_same_revision_finite_blocks=evidence,CAD_this_cycle='NONE: actual product validation of unchanged78part primaryP1_ycapture24; actual new finite blocks/meshes/physical conditional load pullback, no unrelated coupon.',current_physics_status='SAME_REVISION_FINITE_BLOCKS_ASSEMBLED_NO_EQUILIBRIUM_TRANSACTION_AND_FRESH_LOADS_REQUIRED',current_physics_sourcefield=None);dump(pp,primary)
    qp=ROOT/'INTEGRATED_TASKS.json';queue=load(qp);selected=next(t for t in queue['tasks'] if t['id']==TASK);assert selected['status']=='READY';selected.update(status='PARTIAL_VALIDATED',last_run_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),consecutive_runs=selected.get('consecutive_runs',0)+1,result=evidence[names[-1]],reason=note,next=NEXT)
    new=copy.deepcopy(selected);new.update(id=NEXT,status='READY',priority=selected['priority']-10,hypothesis=hypothesis,concrete_first_step='Resolve all unavailable finite signed charts in same-revision sixpair ledger; derive per-pair next-step certificates or reject transitions before fresh coupled load solve.',known_blockers=[note,'All22system gates UNQUALIFIED; remaining pair transactions, full fresh coupled loads/physical Baseanchor/mesh/time/globalenergy/full3Finger absent.'],parent_result=evidence[names[-1]],result=None,reason=None,next=None,last_run_utc=None,consecutive_runs=0,primary_state=ref(pp));assert not any(t['id']==NEXT for t in queue['tasks']);queue['tasks'].append(new);assert not any(t['status']=='RUNNING' for t in queue['tasks']);dump(qp,queue)
    nt=load(ROOT/'NEXT_TASK.json');nt.update(status='SOURCE_INTEGRITY_PASS',errors=[],next=new,running_task_records=[],warning=note,resume_command=hypothesis);dump(ROOT/'NEXT_TASK.json',nt)
    release=load(rt/'release_before26.json');assert release['status']=='INTEGRATED_NOT_QUALIFIED'
    failures=[dict(reason='First signed-chart report JSON serialization of numpyint64 failed; generated numerical NPZ and producer retained. Newv2 changes JSON counters only, same numerical criteria.',execution=ref(base/'primary_cycle27signed/execution.json')),
        dict(reason='Original.05mm perbody trust region cannot certify7/19near nonsmooth exterior material points inactive. Failed result retained. New geometry-derived smaller bound resolves only RootFrame next local step, not wholemodel.',result=evidence['primaryP1_inactive_certificate27']),
        dict(reason='First fresh axial producer missinggmsh in defaultPython. Existing historical dependency environment read only, source/libhashes recorded, newtag succeeds; no installation or SDK edit.',execution=ref(base/'primary_cycle27axial/execution.json'))]
    dump(out/'summary.json',dict(status='ACTUAL_P1_SAME_REVISION_FINITE_UNION_SIGNED_CONTACT_FIVEBODY_BLOCKS_VALIDATED_NOT_RELEASE',candidate=ref(cadpath),selected_task_id=TASK,next_task_id=NEXT,evidence=evidence,actual_CAD_change_files=[],actual_part_count=78,
        actual_assembled_blocks=assembled,newly_qualified_system_gate_ids=[],remaining_unqualified_system_gate_ids=[x['id'] for x in g['gates']],accepted_equilibria=0,whole_system_release=False,stage3_authorized=False,
        physics_child_seconds=seconds,execution_count=len(executions),executions=[ref(p) for p in sorted(base.glob('primary_cycle27*/execution.json'))],children_reaped=True,failures_preserved=failures,
        inherited_trusted_release=dict(status=release['status'],errors=len(release['errors']),source=ref(rt/'release_before26.json'),scope='Historical supervisor audit beforethiscycle; not retagged new release.'),
        actual_operating_load_scope='Original conditional Root/Motor ports re-pulled onto actual new Root face; new fivebody mesh gravity computed. Partial external sources remain explicitly unbalanced; no Basecounterload and no equilibrium.',
        alternatives_review=[dict(alternative='A finite adjacent-face union plus oriented coplanar zero-gap charts',decision='IMPLEMENTED_AND_INDEPENDENTLY_VERIFIED',blocker='Per-pair nonsmooth transactions, continuous boundary coverage and fresh coupled forces remain.'),dict(alternative='B universal positive edge-normal hull or infinite-plane pressure',decision='REJECTED',blocker='144actualconcave probes require distinct finite face alternatives; historical hullFAIL preserved.'),dict(alternative='C retain original.05mm bound and assume all unavailable rows inactive',decision='REJECTED',blocker='7/19near rows fail. New derived tighter RootFrame-only bound is a geometric search restriction, not tolerance relaxation or physicalforce.')],
        protected_source_pins_unchanged=True,original_untracked_files_unchanged=len(original),queue_RUNNING=0,hardware_status='NOT_MEASURED',limitations=[note,hypothesis]))
    counts='; '.join(f"h{r['mesh_level']}: {r['contact_material_rows']}contact rows, {r['physical_coordinates']}coordinates, {r['remaining_unresolved_rows']}remaining unresolved" for r in assembled)
    text=f'''# P1 finite contact union and actual fivebody block rebuild — cycle27

Actual starting HEAD `{HEAD}`. Selected `{TASK}`. ONE unchanged78part `primaryP1_ycapture24`, separate from failedAO, remains primary Motor→stock1996hub→Drum→Tendon→Finger→Root→Frame→Ground→Base. Preserve sidecartridge/distalPETaxialslide/3Finger/jamming. No Stage3.

Actual changed CAD: NONE. Actual product validation uses the same78part STEP/BOM/assembly hashes. New actual numerical finite-contact/elastic/axial/load blocks were implemented; no ideal coupon or replacement candidate. Existing actual assembly/tool/tendon results remain partial, unchanged and are not rerun/retagged as new qualification.

{note}

Full Root boundary:8868/11248triangles,26604/33744degree2fixedmaterialsamples, area3267.788894434/3267.820104740mm2. All Frame boundary26074/39394triangles. Independent exhaustive-distance controls, every144concave two-face branch switch,24convex controls,168zeroedge rejections, and all finite translation inventories pass. A tied concave face is not a convex-hull edge force. Mesh crease and smooth BRep fillet remain distinct; fixed material quadrature is not moving-overlap integration or full surface CCD.

Signed local charts:320offsurface solid-angle inside/outside controls agree;160coplanarzero-gap charts have independent two-sided normal derivative tests. Actual shoulders reproduce gap.1/.05/0/-.001mm. Open.1mm gap carries no assigned pressure. Distinct nearest positions/mixed oriented signs remain unavailable; no averaged reaction. Full-row Jacobians preserve independent Root/Frame nodes, virtualwork/duality/force/moment/rigid modes. At nominal active contact RootY derivative0; no lateral tie.

Original.05mm-perbody inactive certificate FAIL:7/19near rows cannot be declared inactive, minimumdistance.002832988884/.001627765932mm. Failure retained. Whole-boundary winding confirms all1317/1692unavailable RootFrame samples exterior. Derived b=min(.05,(minimumdistance-1e-10)/4) gives.000708247196/.000406941458mm perbody; nextstep lowergap.001416494492/.000813883016mm. All retained rows are then inactive only within that NEXT RootFrame local material-point step. Perturbed vertex/point controls and oversized-step rejection pass. This is a stricter geometry search restriction, NOT changed physics/time/convergence criteria; otherpair and continuoussurface certificates are absent.

New fivebody reference: new Root/Frame tetrahedra plus three exact-CAD-identical historical geometry meshes; no old u/pressure/stress/loads/sourcefield copied. All36body/Motor rigid coordinates and independent upstreamfreeYscalar remain unfixed. Proven Support.elastic reused; zero/finitecommonrotation/affine-energy derivative tests pass. Original conditional Root/Motor operating wrenches are independently pulled back onto new Root face720/1055nodes, forces<1.3e-15N/moments<8.4e-17Nm; new meshgravity computed with explicitly conditional inherited densities. Remaining hardware masses/current Finger/string/freeY equation and physical Baseanchor are not supplied. Partial external wrench is NOT equilibrium; no Base residual cancellation.

Fresh actual CAD common faces for28head/nutfootprints,14axial branches, positive degree2area weights mapped onto both newfivebody meshes with every finiteowner present (maxdistance3.3e-14mm). Actual bolt-axis centroids preserved. Proven objective unilateral axial operator passes virtualwork/energy/actionreaction/finiteobjectivity; RootYtranslation does not stretch axialbranches. Conditional minorcore/length/E remains inherited; no thread/flank/bearing/preload/materialstrength qualification.

Six finite adjacent blocks:RootFrame,FrameGround,GroundBase,MotorFrame,MotorCap,CapFrame. Actual stock Motor surface uses rigid6DOF, no inventedcaseE. Fullsource material rows and all unavailable NaNgaps retained. {counts}. Allassembled commonrigid modes pass. This is NOT a complete force model or equilibrium; adjacent-pair transactions/certificates, omitted-pair separation, fullsurface coverage and fresh coupled sources remain mandatory before solve. No physical reaction from virtual duals and no current-pressure result.

Failures preserved: signed-chart JSON numpyint64 error; defaultPython missinggmsh; original.05mminactiveFAIL. Existing dependency environment read only, no installation/SDK/engine edits. Each execution has exact producer/log/exit record; all{len(executions)}children reaped,total{seconds:.9f}s,each4GiB/420s. No timeout/STOP/RUNNINGqueue/ownedchildren.

Newly solved SYSTEM gates:NONE. All22UNQUALIFIED in `models/primary_system_gate_state31.json`. Trusted supervisor pre-cycle audit remains INTEGRATED_NOT_QUALIFIED/{len(release['errors'])}errors, historical not a new audit. Material/source minima/thread/anchor/full3DFinger/finitewire/friction/protector/mesh1%/time.1%/globalenergy/full3Finger remain. HardwareNOTMEASURED.

Concrete next `{NEXT}`: {hypothesis}

Actual numerical cycle result `validation/integrated/primary_cycle27_record/summary.json`. All{len(original)}originaluntracked and10protectedsourcepins unchanged. Noadd/commit/push/historyrewrite/deletion/SDK/manager/security/save/guard/gate edits/subagents/recursiveagent/purchase/hardware/credentials/paidprovider. Supervisor alone saves exactbytes through `runtime/goal_authorized_20261127_7/save_request26.json`.

---

'''
    cp=ROOT/'CHECKPOINT.md';cp.write_text(text+cp.read_text());(ROOT/'reports/primaryP1_finite_blocks27.md').write_text(text)
    def request():
        files=[ref(REPO/p) for p in sorted(changed(REPO)|(untracked(REPO)-old))]
        return dict(expected_HEAD=HEAD,message='Implement P1 finite signed contact union and rebuild same-revision fivebody load and axial blocks',files=files,results=[r for r in files if r['path'].endswith('/summary.json')],engineering_progress=dict(category='ACTUAL_PRODUCT_VALIDATION',task_id=TASK,mechanism='Implement finite adjacent-face union, full signed material-boundary Jacobians, geometry-bounded inactive certificates and actual fivebody/14axial/conditional load pullback blocks.',system_gate_ids=selected['system_gate_ids'],actual_change_files=[r['path'] for r in files if '/scripts/' in r['path']],candidate_reference=ref(cadpath),next_task_id=NEXT,strategy_change=True))
    req=request();validate(REPO,req,HEAD,old);record=engineering_record(req,REPO);assert record['signature'] not in ledger['seen_engineering_signatures']
    dump(out/'preflight.json',dict(status='READ_ONLY_EXACT_SAVE_PREFLIGHT_PASS',engineering_record=record,protected_source_pins_unchanged=True,original_untracked_unchanged=len(original),queue_RUNNING=0,all_analysis_children_reaped=True))
    req=request();validate(REPO,req,HEAD,old);engineering_record(req,REPO);dump(rt/'save_request26.json',req)
    print(json.dumps(dict(files=len(req['files']),results=len(req['results']),child_seconds=seconds,request=ref(rt/'save_request26.json'))))

if __name__=='__main__':main()
