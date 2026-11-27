"""Final immutable cycle handoff; no Git mutation or manager/control edits."""
import json,sys,shutil,subprocess
from pathlib import Path
b=Path('product_prototype/stage12_integrated').resolve();sys.path.insert(0,str(b/'scripts'))
from baseline_registry import ROOT,REPO,ref,sha,dump
def load(p):return json.loads(p.read_text())
assert not(b/'runtime/STOP').exists()
out=b/'validation/integrated/primaryP1_cycle5_closeout';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
cycle=b/'validation/integrated/primary_cycle5';candidate=b/'cad/exports/primaryP1_fixture13/summary.json';gpath=b/'validation/integrated/primaryP1_fixture_gravity1/summary.json';gravity=load(gpath)
ledger=load(b/'runtime/goal_authorized_20261127_7/ledger.json');pins={p:sha(REPO/p)==h for p,h in ledger['source_pins'].items()};assert all(pins.values())
e=[]
for p in sorted(cycle.glob('*_execution.json')):
 x=load(p);assert x['reaped'];x.update(record=ref(p),log=ref(cycle/p.name.replace('_execution.json','.log')));e.append(x)
q=load(b/'INTEGRATED_TASKS.json');assert not any(t['status']=='RUNNING' for t in q['tasks']);release=b/'validation/integrated/primaryP1_release7/summary.json';r=load(release);assert r['status']=='INTEGRATED_NOT_QUALIFIED' and len(r['errors'])==24
checks=dict(source_pins_unchanged=all(pins.values()),all_children_reaped=all(x['reaped'] for x in e),all_analysis_limits=all(x['memory_limit_bytes']==4294967296 and x['timeout_s']==420 for x in e),no_timeouts=all(not x['timeout'] for x in e),no_running_queue=True,STOP_absent=True,HEAD_unchanged=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()=='ca4f0b206f1e43477e17033fb1830fe7814d6119',index_empty=not subprocess.check_output(['git','diff','--cached','--name-only'],text=True).strip())
assert all(checks.values())
text='''# Latest actual P1 positive fixture continuation — 2026-11-27, Supervisor save pending

Actual starting HEAD ca4f0b206f1e43477e17033fb1830fe7814d6119.
Selected exact queue ID goal_primary_positive_ground_fixture. Same ONE P1 now
primaryP1_fixture13,78actual parts: Motor -> stock1996hub/fourM3 -> Drum ->
whole factory cable -> Terminal/AX Rail/PET -> Root/RF -> OPEN_FRAME -> original
fourM5 -> Ground -> integral shear key/separate fourM5x35/nuts -> finite TEST_BASE.
Failed AO/adopted AA/original3Finger/cartridge/jamming remain immutable.

Actual changed CAD: Ground external wings/key; separate machined bridge Base;
four real socket4AF M5x35 bolt solids and four8AF/4.7mm ISO4032 nut solids.
Final Ground uses fixture12 STEP; final Base uses fixture13 STEP with fourR1
blind corner reliefs for nominal2mm-endmill underside machining. Full78part
ASSEMBLY.step/BOM and identity3CSV bind every part/hash. Fixture11/12are preserved
within-product iterations. They are not unrelated replacement candidates.
Standard dimensions from primary Accu/PTS pages,not downloaded vendor CAD or
material certificates. No purchases/hardware. Full thread/flank/core/engagement,
preload/locking and manufacturing tolerance/process remain UNQUALIFIED.

Actual78single valid solids,190final Boolean pairs/no volume interference;
independent aggregate78part geometric identity and selected STL closure/volume
pass bounded checks. Original-module81assembly samples/296comparisons plus
fixture52samples/79comparisons and10fixture tools/RFdriver approaches clear.
One actual prior32element conditional-demand cable/rotor pose was rerun,not four.
No continuous CCD,real thread tightening/full3Finger Stage1 or physical assembly.

Key x faces30mm2 each,y18mm2 each; seat2399.542044268mm2,roof gap.2mm.
Independent actual-volume contact derivatives at.001/.002mm confirm key areas.
Pressure*finite-area integration and six rigid virtual motions reconstruct
Ground/bolt/Base action-reaction and full force/couple without hidden support.
Port-only FX=.408610416667N,MY=-.039234099172Nm is feasible without friction at
THIS outer joint. Full-face reference key pressure.0136203472MPa and bolt loads
.219697680/.231403043N are feasible demands,NOT actual compliant distribution,
capacity,preload,minimum guaranteed reactions or complete product loading.
Explicit opposite Base external wrench remains a physical grip/anchor requirement.

FAIL preserved: off-axis fixture11whole-face wrench infeasible; divided fields
required78.19/52.13N opposing key compression. Key moved y=-10->0 in fixture12.
Wrong original assertion that bolt omission must fail this load was exposed:
a snug key can transmit its planar couple. Correct independent functions:
key omission fails shear; bolt omission fails an explicit added1N separating
control. Added control is not a measured operating demand. Final port-only
1->2reaction divisions4.5041273%,2->4 2.0102069% FAIL unchanged1%criterion.
Do not continue LP-only mesh retries or call these elastic stress convergence.
A.02mm actual pocket-gap contrast loses initial shear contact; exact nominal
fit is not a guaranteed manufacturing fit. All previous failures remain.

NEW WEIGHT LIMITATION: earlier applied port demand omitted fixture selfweight.
Actual Ground volume47653.109860mm3,Base104604.490477mm3. Ground material intent
conflicts: original contract says steel candidate; producer11proposed6061-T6.
No material silently assigned. New scope model marks actual material/allowable
unknown and records both density sensitivities. At Groundrho2700/7850kg/m3,
Base2700,conditional Ground weights1.261756898/3.668441353N and Base2.769712992N.
Six actual finite-face weighted states equilibrate; total bolt bounds equal
Ground weight for these cases. Required external Base FZ4.031469890/6.438154345N,
MX=-.035184753/-.055664670Nm,MY=-.058850821/-.118049912Nm andFX=-.408610417N.
Original module/hardware weights,physical orientation/lab grip and guaranteed
density bounds remain UNKNOWN. Constant total bounds across weighted meshes
are not pressure/stress/motion convergence and do not cure port-only FAILs.

All22system gates remain UNQUALIFIED in models/primary_system_gate_state6.json.
Newly qualified whole-system gates: NONE. Bounded missing outer CAD load path,
uniform-face yaw issue and nominal pocket corner manufacturability progressed.
Read-only unchanged actual release7 is INTEGRATED_NOT_QUALIFIED,24errors(exit2).
SOFA/FEM runs0,no dt/global-energy/strength/payload/protector/Stage3 release.
Root/Motor traction mesh,Frame52.7693%FEM/Rail1.30247%stress mesh,45/183current
screens,material minima/friction/real motor-case/full3Finger failures retained.

Concrete NEXT exact ID goal_primary_keyed_joint_compliance: continue THIS P1.
First reconcile Ground material and include full product gravity/mass in load
ports. Then actual compliant Ground/key/Base/axial bolt/head/nut/thread response,
fit/gap/preload contrasts and justified thread core/flank/engagement connectors.
Carry both actual paired Root/Motor forces AND couples through finite Frame/
Ground,with actual Base external grip/anchor definition. Solve active contact,
key-root/plate deformation and stress/motion1%mesh; no major-cylinder ties or
fixation of existing sharedM5. Full3Finger/friction/protection/global energy stay
blocked. Do not qualify current LP feasibility or typical density as strength.

Main result: validation/integrated/primary_cycle5/summary.json.
Additional actual weight: validation/integrated/primaryP1_fixture_gravity1/summary.json.
Final handoff: validation/integrated/primaryP1_cycle5_closeout/summary.json.
'''
text+=f'\n{len(e)}analysis children reaped,{sum(x["elapsed_s"] for x in e):.6f}child-seconds,0timeouts;each4GiB/420s.\n'
text+='''STOP absent,no RUNNING tasks or owned analysis children. Source pins unchanged.
No Git add/commit/push/history rewrite,SDK,manager/security/save/guard/gate edits,
purchase/hardware/credentials/provider selection/subagents/recursive launches.
All earlier evidence and original user untracked data preserved. Supervisor
exact save request: runtime/goal_authorized_20261127_7/save_request4.json.
Save PENDING; no new commit claimed. Hardware NOT MEASURED,Stage3 unauthorized.
'''
for name in ('CHECKPOINT.md','AUTONOMOUS_RESUME.md','README_CURRENT.md'):
 p=b/name;p.write_text(text+'\n---\n\n'+p.read_text())
report=b/'reports/primaryP1_fixture13_engineering.md';assert not report.exists();report.write_text(text+'''

## Nominal machining and assembly definition

Ground main plate z40..46mm widens to x-54..96,y-42..23. Single integral key
x-48..-40,y-6..6,z46..49; planned source material remains unassigned.
Bridge Base roof z56..66,outer rails x-54..-34 and76..96,z46..56.
Pocket from underside46 to49.2,including fourR1reliefs centred at(-48/-40,-6/6).
Machining is underside-accessible BEFORE attachment; tool runout,corner/root
finish,burr removal,actual fit and stock/material minima need drawings/inspection.
Original drive window and RFthrough-tools continue through finite Base.

Separate fixture M5 axes(-44,-30),(-44,10),(86,-30),(86,10),clearance bores5.5.
Bolt head z35..40,major-envelope shank40..75; real4AF/2.5deep socket below.
Nut z66..70.7,8AF maximum envelope. Source minimum thread length22 places the
nominal nut region inside distal thread zone53..75; effective thread engagement
is not measured or certified by a major-bore model. No preload torque chosen.
Fit Base vertically AFTER original P1 assembly,raise bolts from below,lower nuts
from above. Socket/wrench clearance is sampled geometry,not proof of threads.
M5 clearance shanks carry no nominal shear in the model; actual key faces do.
Lab anchorage beyond Base remains an explicit unqualified boundary requirement.
''')
handoff=dict(status='ACTUAL_P1_CYCLE5_EXACT_BYTE_HANDOFF_READY_NOT_RELEASE',candidate=ref(candidate),engineering=ref(cycle/'summary.json'),actual_weight_sensitivity=ref(gpath),actual_integrated_release=ref(release),system_gate_state=ref(b/'models/primary_system_gate_state6.json'),material_scope=ref(b/'models/materials/primary_fixture13_material_scope.json'),primary_state=ref(b/'PRIMARY_PRODUCT.json'),next_task=ref(b/'NEXT_TASK.json'),checks=checks,source_pins=pins,executions=e,recorded_children_reaped=len(e),recorded_child_seconds=sum(x['elapsed_s'] for x in e),owned_analysis_children_running=0,timeouts=0,all22system_gates_unqualified=True,actual_numerical_results=dict(final_parts=78,new_solid_revisions=3,key_x_area_mm2=30,key_y_area_mm2=18,weighted_ground_rho_kg_m3=[2700,7850],weighted_coarse_bolt_N=[x['levels'][0]['result']['bolt_axial_total_N'] for x in gravity['rows']],weighted_external_Base_wrench_N_Nm=[x['levels'][-1]['required_external_base_grip_N_Nm'] for x in gravity['rows']]),stage3_authorized=False,whole_system_release=False,producer=ref(out/'producer.py'))
dump(out/'summary.json',handoff);print(json.dumps(dict(status=handoff['status'],checks=checks,children=len(e),child_seconds=handoff['recorded_child_seconds'])))
