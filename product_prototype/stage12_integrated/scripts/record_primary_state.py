"""Record this primary revision and exact follow-up without promoting system gates."""
import csv,json
from pathlib import Path
from baseline_registry import ROOT,REPO,ref,dump

def main():
 cad=ROOT/'cad/exports/primaryP1_open9/summary.json';d=json.loads(cad.read_text());v=ROOT/'validation/integrated/primaryP1_validation10/summary.json';verify=ROOT/'validation/integrated/primaryP1_verify11/summary.json';motion=ROOT/'validation/integrated/primaryP1_motion9/summary.json';fv=ROOT/'validation/transmission/primaryP1_frame_verify1/summary.json'
 loads=json.loads((v.parent/'loads.json').read_text());old=json.loads((ROOT/'CURRENT_CANDIDATE.json').read_text());assert old['revision']=='revAO_root2'
 bom=ROOT/'bom/primaryP1_identity1';bom.mkdir(exist_ok=False)
 with (bom/'CANDIDATE_BOM.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=['part_ID','STEP','STEP_SHA256','material_status','role','manufacturing_status']);w.writeheader()
  for n,r in sorted(d['part_references'].items()):w.writerow(dict(part_ID=n,STEP=r['path'],STEP_SHA256=r['SHA256'],material_status='UNQUALIFIED_MINIMUM',role='actual nominal standard interface' if 'BOLT' in n or 'NUT' in n or n in ('F0_MICRO_MOTOR','F0_STOCK_HUB','F0_SET_SCREW') else 'finite actual product part',manufacturing_status='NOT_QUALIFIED'))
 dump(bom/'summary.json',dict(status='PRIMARY_NOMINAL_BOM_IDENTITY_RECORDED_NOT_RELEASE',candidate=ref(cad),BOM=ref(bom/'CANDIDATE_BOM.csv'),parts=len(d['part_references']),source_material_contract=ref(ROOT/'models/materials/primary_material_contract1.json'),standard_source=ref(ROOT/'models/standard_drive/batch6_sources1/reviewed.json'),M2_capscrews='Historical nominal ISO4762M2x4 socket geometry reused; grade/minimum thread strength unqualified',whole_system_release=False))
 reasons={
 'cad_model_match':'69part primary identity independently reproduced; full final same-revision3Finger/Stage2 model binding absent',
 'physical_mass_inertia':'Geometric integrals only; actual materials, densities, motor/hub inertia and complete moving mass unknown',
 'tendon_force_stroke':'Correct C1 prescribed route24.067mm and .928..4.504N scenarios verified; finite loaded Finger/contact/friction equilibrium absent',
 'motor_running_torque_speed':'1101 theoretical linear screen only;45/183 rows exceed general .4A recommendation, no continuous certified curve',
 'shaft_strength':'Actual3mm D-shaft interface present; supplier shaft material/strength/radial rating absent',
 'coupling_capacity':'1996 hub actual nominal geometry with four M3 and set screw; torque/axial/material/thread minima absent',
 'pin_drum_strength':'Finite modified tangent-nipple drum and2mm mounting web; M2/M3 engagement, unused historical bores and notch/strength unresolved',
 'bearing_ratings_reactions':'Motor shaft radial demand up to conditional4.504N; actual internal bearing load/allowable absent',
 'housing_shoulder_retention':'Split rectangular cradle and front pilot shoulder exist; body vs terminals, fit, preload and reverse axial retention unresolved',
 'tendon_stiffness_strength':'Existing .5mm finished-cable geometry retained; exact construction/EA/minimum breaking and finished-end ratings absent',
 'terminal_retention':'Source-backed nominal factory nipples/pockets/caps reused; actual factory swage/pullout/pocket wall/cap loading unqualified',
 'idler_load_drag':'No Idler in primary; direct full winding physically modeled and rigid screened, but equivalent loaded guide/friction qualification absent',
 'finger_structure':'AX wide root and complete existing Finger present; actual finite Rail/PET contact/sharing/notch/strain/creep/fatigue absent',
 'root_palm_strength':'Positive root pins and relocatedRF mount into finite frame exist; frame mesh FAIL and joint/preload/material/contact unresolved',
 'continuous_load_path':'Actual69part CAD chain exists; source-backed capacities and solved joint/contact force transfer incomplete',
 'static_dynamic_consistency':'Scalar prescribed virtual-work and static linear frame reference only; no coupled dynamics/global stored-energy closure',
 'numerical_convergence':'Actual frame4/2/1.5mm compliance base-to-finest52.7693%, middle9.08318% FAIL1%; no time criterion qualification',
 'qualified_worst_case':'Unmeasured mu .2/.4/.8 and typical stiffness references; no guaranteed tolerance/material/load/physical fault maximum',
 'changed_stage1_revalidation':'81finite assembly samples/278Boolean comparisons and13motion poses pass; no continuous/tolerance/thread/full3Finger release',
 'stage3_handoff':'Blocked until actual integrated Stage1/2 release; no Stage3 operation',
 'overload_protection':'No physical certified limiter; stall/current model is not a protected peak or structural capacity',
 'motor_alignment_reactions':'Planar shaft and split mount actual CAD; finite loaded bearing/housing/alignment/reverse retention not qualified'}
 oldg=json.loads((ROOT/'validation/finger/batch6_wide_cycle1/summary.json').read_text())['remaining_system_gate_ids'];assert set(oldg)==set(reasons)
 gate=ROOT/'models/primary_system_gate_state1.json';dump(gate,dict(status='ALL22_SYSTEM_GATES_UNQUALIFIED',candidate=ref(cad),criteria_unchanged=True,newly_qualified_system_gates=[],gates=[dict(id=k,status='UNQUALIFIED',reason=reasons[k]) for k in oldg],Stage1='PARTIAL_SAMPLED_PRIMARY_ONLY',Stage3='BLOCKED',whole_system_release=False))
 state=dict(status='PRIMARY_IMPLEMENTED_PARTIAL_DIGITAL_VALIDATION_NOT_RELEASE',primary_id='P1',revision=d['revision'],candidate_reference=ref(cad),assembly=d['assembly'],BOM=d['BOM'],identity_BOM=ref(bom/'CANDIDATE_BOM.csv'),parts=d['parts'],actual_part_references=d['part_references'],material_contract=ref(ROOT/'models/materials/primary_material_contract1.json'),validation=ref(v),independent_verification=ref(verify),full_cable_motion=ref(motion),frame_refinement=ref(fv),system_gate_state=ref(gate),previous_AO_preserved=old,adopted_reference='revAA_heel_relief2 unchanged',selected_task_id='goal_primary_module',next_task_id='goal_primary_operating_window',physical_model='Motor -> stock1996 hub -> fourM3 -> finite tangent-nipple Drum -> whole factory cable -> receiver/terminal -> AX Rail/PET/root pins -> relocatedRF bolts -> finite OPEN_FRAME -> fourM5 -> finite GROUND_PLATE',load_BC='Prescribed0..60degree kinematics with conditional100g shared3Finger mu scenarios, not actual equilibrium. Separate frame unit+Z RF nut subset load with rigid/stuck fourM5 patch upper-bound supports; full joint compliance and motor counterpart unsolved.',extension=dict(three_finger='Preserve AX/AO full3Finger originals and module ground bolt interface; current F0 motor axis atorigin cannot simply be120degree-duplicated without interference. Future common-ground layout and target100mm geometry remain UNQUALIFIED, no target relaxed.',cartridge='Current Root/Front two clamp bolts, root-only pins and original distal PET sliding retained; replaceable lateral module',jamming='Original Jamming Dock/cassette solids preserved outside primary; original root interfaces retained, optional dock reinstatement requires full clearance/load revalidation'),remaining_gates=oldg,hardware_status='HARDWARE_NOT_MEASURED',powered_status='POWERED_OPERATION_NOT_AUTHORIZED',whole_system_release=False)
 dump(ROOT/'PRIMARY_PRODUCT.json',state)
 current=dict(revision=d['revision'],adopted=False,primary_product=True,definition=ref(cad),assembly=d['assembly'],BOM=d['BOM'],identity_BOM=ref(bom/'CANDIDATE_BOM.csv'),verification=ref(verify),parts=d['parts'],official_baseline_unchanged='revAA_heel_relief2',release='CANDIDATE_ONLY_INTEGRATED_NOT_QUALIFIED',hardware='HARDWARE_NOT_MEASURED',powered_operation='NOT_AUTHORIZED',primary_state=ref(ROOT/'PRIMARY_PRODUCT.json'),model_binding_status='ONE primary actual module; final same-revision3Finger/gate model binding absent')
 dump(ROOT/'CURRENT_CANDIDATE.json',current)
 qpath=ROOT/'INTEGRATED_TASKS.json';q=json.loads(qpath.read_text())
 for t in q['tasks']:
  if not t['id'].startswith('goal_primary_'):continue
  t['historical_parent_candidate']=t['parent_candidate'];t['parent_candidate']=ref(cad);t['target_candidate']=ref(cad);t['target_revision']=d['revision'];t['target_parts']=d['parts'];t['primary_state']=ref(ROOT/'PRIMARY_PRODUCT.json')
  if t['id']=='goal_primary_module':t.update(status='PARTIAL_IMPLEMENTED',result='validation/integrated/primary_cycle1/summary.json',reason='ONE primary CAD implemented and corrected through actual design failures; no system gate promotion',next='goal_primary_operating_window',consecutive_runs=1)
  if t['id']=='goal_primary_operating_window':
   t['hypothesis']='Continue P1 actual69parts: solve finite loaded AX Rail/PET + original distal sliding/contact, derive object-contact demand and root/terminal reactions; current prescribed curve demand is conditional. Reuse existing finite/extensible/contact kernels, not a new general simulator.'
   t['concrete_first_step']='Extract actual P1 Root/Terminal boundary ports and pin/slide contact from recorded STEP, reproduce corrected C1 cable virtual work, then solve a small finite-load continuation with separate Rail/PET DOFs and explicit normal contact. Retain mesh1%/time.1%; do not apply100g by calling its weight cable tension.'
   t['known_blockers']=['Actual frame mesh convergence FAIL must be retained before root strength use','1101 low-friction current recommendation FAIL; no operating acceptance or physical limiter','Material/finished cable/shaft-bearing connector minima and full3Finger layout remain absent']
  if t['id']=='goal_primary_protected_drive':t['known_blockers']=['Rated actual motor/hub/finished cable and physical overload bound absent','Do not increase motor size before actual normal demand/finite Finger response; preserve45/183 current-screen failures']
 dump(qpath,q);n=next(t for t in q['tasks'] if t['id']=='goal_primary_operating_window');dump(ROOT/'NEXT_TASK.json',dict(status='SOURCE_INTEGRITY_PASS',errors=[],revision=d['revision'],adopted_reference='revAA_heel_relief2 unchanged',next=n,running_task_records=[],warning='READY follow-up is not execution or release; continue ONE P1 actual model',resume_command='Read PRIMARY_PRODUCT.json and selected concrete_first_step; do not return to AO height scans'))
if __name__=='__main__':main()
