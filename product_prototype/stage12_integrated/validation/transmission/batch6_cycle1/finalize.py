"""Index one completed actual interface cycle; no launch or Git mutation."""
import datetime,hashlib,json,subprocess
from pathlib import Path
repo=Path.cwd();root=repo/'product_prototype/stage12_integrated';out=root/'validation/transmission/batch6_cycle1'
def dump(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def ref(p):return dict(path=str(p.relative_to(repo)),SHA256=hashlib.sha256(p.read_bytes()).hexdigest())
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert head=='67a9094d314e328245491c50f5d0952e61b8cd08'
assert not (root/'runtime/STOP').exists()
oper=root/'validation/transmission/batch6_operating1/summary.json';cad=root/'cad/exports/revAV_micro_interface1/summary.json';ver=root/'validation/transmission/batch6_micro_verify3/summary.json';release=root/'validation/integrated/batch6_release1/summary.json'
o=json.loads(oper.read_text());c=json.loads(cad.read_text());v=json.loads(ver.read_text());g=json.loads(release.read_text())
assert v['status']=='PASS' and g['status']=='INTEGRATED_NOT_QUALIFIED'
records=json.loads((out/'execution.json').read_text())+[json.loads((out/n).read_text()) for n in ('verify_execution.json','verify2_execution.json','verify3_execution.json','release_execution.json')]
assert all(x['reaped'] and not x['timeout'] and x['elapsed_s']<420 for x in records)
missing=[e.split(': ')[1] for e in g['errors'] if e.startswith('stage2: ')];assert len(missing)==22
contract=root/'models/standard_drive/batch6_contract1.json'
assert not contract.exists()
dump(contract,dict(status='PROVISIONAL_ARCHITECTURE_ONLY_MOTOR_OPERATING_SCREEN_FAIL',starting_product='revAO_root2',interface_revision='revAV_micro_interface1',whole_product_revision=None,
    architecture='Per-Finger standard micro metal gearmotor + stock flange hub + bolted turned spool; retained AO route reference. Optional standard protection/support still required.',
    selected_interface_components=['Pololu1101','Pololu1996','M3x5 face screws (vendor/grade unselected)','M3x8 set screw requirement (supplied hub screw length unconfirmed)'],
    normal_demand=dict(payload_kg=.1,gravity_N=.980665,contact_count_scenario=3,friction_scenarios=[.2,.4,.8],friction_certified_lower_bound=None,actual_contact_locations=None,actual_Finger_equilibrium=None,reference_peak_tension_N=max(r['conditional_tension_N'] for r in o['rows']),reference_stroke_m=o['stroke_0_to_60_m'],scope='Prescribed geometry and common-curvature elastic contrast only; NOT actual grasp demand or Stage3 execution'),
    maximum_protected_load_N=None,allowable_installed_tension_N=None,loadside_inertia_kg_m2=None,wire_EA_N=None,
    motor_general_current_screen_failures=v['recommendation_failures'],motor_operating_selection_accepted=False,
    finite_geometry=dict(axis_F0_mm=[110,0,20],wire_center_radius_mm=11.25,spool_core_radius_mm=11,wire_nominal_diameter_mm=.5,nominal_interface=ref(cad),verification=ref(ver)),
    unchanged_AO=['Finger/PET distal axial sliding','Root/Palm/Idler/Terminal/jamming interfaces remain current AO, not requalified'],
    unfinished=['Motor grounded bracket and reaction/support ratings','Spool cable anchor, actual hub thread/set-screw torque and axial retention','Duty/speed/reversing/thermal operation;1101 is rejected for conservative current scenarios','Physical maximum protection and residual energy/fault path','Actual object geometry/friction and coupled separate PET/Rail equilibrium','Full same-revision3-Finger assembly/BOM and22gate qualification'],
    manufacturing='Conventional turned spool and standard bolting are geometrically feasible; alloy, tool/process qualification and full ordered assembly unqualified. No special rivet forming.',
    adoption=False,hardware_status='HARDWARE_NOT_MEASURED',powered_status='POWERED_OPERATION_NOT_AUTHORIZED',whole_system_release=False))
summary=dict(status='PRODUCT_OPERATING_SELECTION_NOT_QUALIFIED',task_id='batch6_operating_load_and_architecture',starting_HEAD=head,save_status='PENDING_SUPERVISOR_VALIDATION_AND_LOCAL_SAVE',new_commit_SHA=None,
    actual_research_cycles=1,scope='One source-backed smaller standard-drive finite interface and actual AO route analysis; provisional architecture, NOT a completed gripper',
    actual_results=dict(operating=ref(oper),finite_interface=ref(cad),independent_verification=ref(ver),release=ref(release)),contract=ref(contract),
    numerical_local_outcomes=dict(interface_instances=24,valid_closed_positive_meshes=24,exact_context_pairs=75,intersections=0,driver_envelopes=15,driver_intersections=0,misplaced_hub_negative_control_mm3=v['misplaced_hub_control_intersection_mm3'],max_independent_derivative_relative=max(v['derivative_relative_errors']),max_independent_work_relative=max(r['relative_error'] for w in v['work'] for r in w['refinements'])),
    failed_product_screen=dict(conditional_cases=15,current_recommendation_failures=7,peak_reference_tension_N=max(r['conditional_tension_N'] for r in o['rows']),reference_stroke_m=o['stroke_0_to_60_m'],ideal_current_scenario_tension_N=o['motor_screen']['ideal_tension_at_current_scenario_N'],guaranteed_maximum_tension_N=None,material_or_capacity_certified=False),
    part_changes=dict(new_interface_instances=24,new_custom_spools=3,new_standard_component_interfaces=21,adopted_product_parts_changed=0,AO_context_replacement_candidates=c['context_replacement_IDs'],realized_product_total=None),
    structural_problem_addressed='Finite stock-hub bolt circle mates to spool, nominal shaft/pilot clears, all actual retained AO context and finite straight drivers clear. This replaces a custom D-hub/friction-stack geometric interface, not its unqualified protection/support functions.',
    proposed_custom_processes_removed=c['removed_custom_processes_proposed'],
    failures_preserved=[dict(kind='Initial import failure',exit_code=1,log=ref(out/'operating.log'),source_hash='NOT RECORDED before import failure; no output state exists; not retroactively invented'),dict(kind='Direct PDF download DNS failures',receipt=ref(root/'models/standard_drive/batch6_sources1/receipt.json')),dict(kind='Bounding-box dimension verifier1 FAIL',result=ref(root/'validation/transmission/batch6_micro_verify1/summary.json'),exit_code=2),dict(kind='SetGap verifier2 still FAIL',result=ref(root/'validation/transmission/batch6_micro_verify2/summary.json'),exit_code=2),dict(kind='Actual actuator operating screen failed',result=ref(oper),note='7/15 exceed general current recommendation; conditional route math PASS is not actuator PASS')],
    verification_repair='After two bounding-box failures, analytic imported BRep cylinder/plane inspection proves nominal17.5mm OD/5mm thickness at unchanged1e-8 dimension threshold. AddOptimal numerical1e-7 expansion remains documented; no CAD, physical tolerance or acceptance limit changed.',
    execution=records,SOFA_runs=0,remaining_gate_ids=missing,
    next='Coverage-before-repetition: standard Idler/direct routing next; use common contract but do not adopt1101 or transplant nominal interface into whole product. Independently wide Root and direct Palm remain READY. Establish actual demand/duty before selecting higher reduction or another rated actuator; no repeated100:1 parameter sweep.',
    whole_system_release=False,criteria_relaxed=False,producer=ref(Path(__file__).resolve()))
dump(out/'summary.json',summary)
q=json.loads((root/'INTEGRATED_TASKS.json').read_text());t=next(x for x in q['tasks'] if x['id']==summary['task_id']);assert t['status']=='READY'
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
t.update(status='FAIL',result='validation/transmission/batch6_cycle1/summary.json',reason='Finite1101/1996/spool interface verified, but7/15 conditional current scenarios fail. Actual normal demand, guaranteed maximum, motor support/anchor and full product remain unqualified.',last_run_utc=now,consecutive_runs=1,common_product_contract=ref(contract),followup='Independent standard Idler/direct route next; select final rated actuator after actual demand/duty. Do not repeat100:1 interface as new research.')
dump(root/'INTEGRATED_TASKS.json',q)
h=json.loads((root/'TRACK_HISTORY.json').read_text());h['cycles'].append(dict(task=t['id'],track=t['track'],time_utc=now,status='FAIL',evidence=ref(out/'summary.json'),starting_HEAD=head,execution='One bounded actual product-interface cycle; no external launch, no subagents',save='PENDING_SUPERVISOR_LOCAL_SAVE',new_commit_SHA=None));dump(root/'TRACK_HISTORY.json',h)
assert not [x for x in q['tasks'] if x['status']=='RUNNING']
note='''# Batch6 cycle0 — standard micro-drive interface; operating selection FAIL (2026-11-27)

Started at67a9094d314e328245491c50f5d0952e61b8cd08. Exact selected task:
batch6_operating_load_and_architecture. One actual finite design/analysis cycle.
No git add/commit; supervisor validation/local save PENDING, no new SHA claimed.
Result: validation/transmission/batch6_cycle1/summary.json.

Pololu1101 (100:1 HP6V) +1996 stock hub + turned spool interface implemented
at all3 actual AO axes, cable center radius11.25mm retained.24finite instances
(3custom spools,21standard component/fastener interfaces), STEP/STL/JSON BOM.
Nominal envelope models from manufacturer primary facts, NOT vendor STEP or
guaranteed maximum-stock/tolerance models. Direct PDF downloads failed DNS;
receipt preserved. Hub alloy, thread/axial/set-screw capacity are unqualified.

Independent reimport:24valid single solids, closed oriented positive meshes;
75exact changed/retained AO context pairs and15finite straight driver envelopes
clear at unchanged1e-8mm3. Misplaced hub control produces2.997776mm3 collision.
Analytic spool/motor volumes agree; independent route/tendon-work reconstruction
passes. Two failed bounding-box dimension verifiers preserved. SetGap did NOT
fix numerical1e-7mm expansion; final imported cylinder/plane measurements pass
the SAME1e-8 dimension limit. No geometry/physical tolerance relaxation.
Initial missing-trimesh import failure(exit1, initial source hash not recorded)
also preserved. It was repaired by extracting actual route algebra, not fake
imports. No failed artifact overwritten; no repeated equilibrium experiments.

Operating selection FAIL:100g static weight0.980665N is not tendon demand.
Three equal contact/friction0.2/0.4/0.8 scenarios and prescribed tip motion give
16.935839mm stroke, max7.579539N conditional tension.7/15cases exceed general
25%-stall-current recommendation. Ideal linear motor current model only;
2.963788N at0.4A is NOT continuous rated force.14.818938N extrapolated stall
is NOT a physical maximum/protection. Common-curvature separate-layer elastic
energy is a reference, not actual coupled equilibrium or object grasp proof.
Actual friction/contact locations/duty/demand and material minima remain unknown.

Finite stock bolt-circle/shaft/driver mating is solved in the bounded nominal
interface. Custom D-hub/friction stack manufacture/calibration is proposed for
removal;90old drive/support context parts are replacement candidates, NOT an
achieved product part reduction. Ground mount, rated shaft support, cable anchor
and physical protection are missing. revAV_micro_interface1 is a24part interface,
NOT a full3-Finger candidate. AO254 current and AA304 adopted remain unchanged.

Common contract: models/standard_drive/batch6_contract1.json.1101 is NOT adopted
as operating actuator. Next coverage task: standard Idler/direct route; wide
Root and simpler Palm are independent READY. Establish actual demand/duty before
final higher-reduction/different rated drive. Do not repeat this100:1 interface.

batch6_release1 remains INTEGRATED_NOT_QUALIFIED:22Stage2 gates unqualified plus
missing system evidence/coverage. No same-revision release, capacity, hardware,
Stage3, power, SDK or manager/control changes. Six bounded analysis executions
completed/reaped (operating0,CAD0,verify2/2/0,release2), each4GiB/420s;
no timeout or SOFA run. No RUNNING queue or live owned analysis children.
Historical failures and all pre-existing untracked CAD/BOM preserved.

'''
for path in [root/'CHECKPOINT.md',root/'AUTONOMOUS_RESUME.md',repo/'product_prototype/reports/CHECKPOINT.md',repo/'product_prototype/reports/AUTONOMOUS_RESUME.md',repo/'reports/INTEGRATED_CURRENT_STATUS.md',repo/'reports/INTEGRATED_NEXT_TASKS.md']:
    path.write_text(note+path.read_text())
print(json.dumps(dict(status=summary['status'],task=t['id'],running=0,save='PENDING',remaining_gates=len(missing))))
