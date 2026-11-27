import json,sys,subprocess,datetime,shutil
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'product_prototype/stage12_integrated/scripts'))
from baseline_registry import ROOT,REPO,ref,sha,dump
from product_track_scheduler import select
out=ROOT/'validation/integrated/primaryP1_queue3';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'reviewer.py')
q=json.loads((ROOT/'INTEGRATED_TASKS.json').read_text());h=json.loads((ROOT/'TRACK_HISTORY.json').read_text());n=json.loads((ROOT/'NEXT_TASK.json').read_text());state=json.loads((ROOT/'PRIMARY_PRODUCT.json').read_text());current=json.loads((ROOT/'CURRENT_CANDIDATE.json').read_text());choice=select(q['tasks'],h['cycles']);running=[t['id'] for t in q['tasks'] if t['status']=='RUNNING'];assert not running;assert choice['id']==n['next']['id']==state['next_task_id']=='goal_primary_root_ground_load_path'
assert current['primary_state']==ref(ROOT/'PRIMARY_PRODUCT.json');refs=[state[k] for k in ['candidate_reference','assembly','BOM','identity_BOM','system_gate_state','latest_corner_cycle','latest_corner_equilibrium','latest_corner_verification','latest_conditional_demand','latest_conditional_demand_verification','latest_required_port_loads','latest_loaded_cable_assembly']]
for t in q['tasks']:
 if t['id'].startswith('goal_primary_'):assert t['primary_state']==ref(ROOT/'PRIMARY_PRODUCT.json')
assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs)
g=json.loads((REPO/state['system_gate_state']['path']).read_text());assert len(g['gates'])==22 and all(t['status']=='UNQUALIFIED' for t in g['gates'])
before=json.loads((ROOT/'runtime/goal_authorized_20261127_7/checkpoint_before2.json').read_text());start=json.loads((ROOT/'validation/integrated/primary_cycle3/start.json').read_text());preserved={p:sha(REPO/p)==start['initial_files'][p] for p in before['preexisting_untracked']};assert all(preserved.values())
ledger=json.loads((ROOT/'runtime/goal_authorized_20261127_7/ledger.json').read_text());pins={p:sha(REPO/p)==v for p,v in ledger['source_pins'].items()};assert all(pins.values());assert not(ROOT/'runtime/STOP').exists()
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert head=='dd8a2405a47b4b1a7eeb4d7ddce5503e91139495';assert not subprocess.check_output(['git','diff','--cached','--name-only'],text=True).strip()
log=subprocess.check_output(['git','log','-3','--format=%H %s'],text=True);(out/'actual_git_log.txt').write_text(log)
dump(out/'summary.json',dict(status='READ_ONLY_CURRENT_P1_QUEUE_AND_IDENTITY_PASS_NOT_RELEASE',candidate=state['candidate_reference'],HEAD=head,selected_task='goal_primary_terminal_feature_contact',next_task_id=choice['id'],running_task_records=running,source_pins_unchanged=pins,old_untracked_hashes_preserved=preserved,verified_primary_references=refs,remaining_system_gates=22,newly_qualified_system_gates=0,whole_system_release=False,STOP_absent=True,git_index_empty=True,automatic_launches=0,git_add_commit_attempted=False))
s=json.loads((ROOT/'validation/integrated/primary_cycle3/summary.json').read_text());m=s['actual_numerical_results'];load=m['frame_required_port_wrenches'];text=f'''# Latest actual P1 corner/load continuation — 2026-11-27, pending Supervisor save

Started at actual HEAD dd8a2405a47b4b1a7eeb4d7ddce5503e91139495.
Selected exact queue ID goal_primary_terminal_feature_contact. SAME ONE primary
primaryP1_open9,69actual parts, Motor -> stock1996 hub/fourM3 -> Drum -> whole
factory cable -> Terminal/AX Rail/PET -> Root/RF -> OPEN_FRAME -> fourM5 ->
finite GROUND_PLATE. Failed AO and3Finger/cartridge/jamming originals preserved.
Actual changed CAD this cycle: NONE. All STEP/BOM/assembly hashes unchanged.
This is ACTUAL_PRODUCT_VALIDATION with new actual finite-contact/load equations,
not DESIGN_CHANGE or an ideal coupon. Result: validation/integrated/primary_cycle3/summary.json.

Actual residual intersection was at lip Z=-90mm. Existing1N state had a true
-165.693nm max-SDF seam gap,not merely a harmless Boolean tolerance. Frozen
material witness exchange retained32/8/16 physical FAILs and one array IndexError.
A free material contact station now contacts the ACTUAL cylinder/plane corner
(X,Z)=(49.720180802444,-90)mm. Two corner-coordinate equations plus station
variation enforce zero tangential contact work. Force lies in the nonnegative
cone of actual circular face and upper planar face normals; no inequality,
physical force,material or acceptance tolerance was removed or relaxed.

Final corrected1N8/16/32states independently pass complex-step energy/force/
point-Jacobian,free-station virtual work,nonnegative cone,full inherited gaps
plus current kink roots,actual deformed PET/Rail/Terminal BRep and negative
controls. Finest normal {m['normal_at1N_finest_N']:.12f}N;8->32normal
{100*m['normal_at1N_base_to_finest_relative']:.8f}% and Rail-tip-angle
{100*m['tip_angle_at1N_base_to_finest_relative']:.8f}% pass1% locally.
Six final1N/demand reduced states total,{m['deformed_BRep_comparisons']}actual Boolean comparisons,
no final modeled BRep overlap above1e-8mm3. These remain typical-modulus,
rigid-grip,planar frictionless reductions with same-material interface and a
fixed spatial X stop20mm inward,NOT full frictional/free-grasp mechanics.

Conditional100g/3/assumedmu.8 target normal .4086104166667N is solved on all
three meshes. Required tensions8/16/32={m['conditional_target_tendon_N']}N.
Finest torque {m['conditional_target_finest_torque_Nm']:.12f}Nm and cable stroke
{m['conditional_target_finest_stroke_mm']:.9f}mm. ONE actual demand loaded wire/rotor pose,
26Boolean comparisons: valid single cable solid,constant volume,single layer,
wire/rotor clear. An inherited sentence saying Four poses is explicitly corrected
in failure_index.json; no four-pose/CCD claim. Old root-residual metadata issue
also preserved; final v2 resamples exact states and records correct row identity.

Actual demand applied Root force(X,Z)={load['frame_root_force_XZ_N']}N,
Y couple {load['frame_root_couple_about_Y_Nm']:.12f}Nm; motor cradle force
{load['motor_cradle_force_XZ_N']}N,Y couple {load['motor_cradle_couple_about_Y_Nm']:.12f}Nm.
Required Ground FX=-.408610416667N,MY=.039234099172Nm balances independently.
These are demanded port resultants,NOT solved bolt/clamp/bearing/finite Ground
reaction distributions. Free-station restricted Hessian has no negative mode
in six reduced states; this is not global stability or dynamics/energy closure.

Nominal Rail stress {m['conditional_target_finest_rail_nominal_stress_MPa']:.9f}MPa is typical E*strain,
NOT material allowable/notch/contact/fatigue/creep strength.8->32nominal stress
{100*m['nominal_stress_base_to_finest_relative']:.8f}% FAILS existing1% criterion.
Earlier frame mesh52.7693%FAIL,45/183current-screen FAIL,1N legacy penetration,
2N/4.5N branch/geometry failures and all historical immutable evidence remain.
No payload,100mm grasp,continuous motor,protector,source-minimum material or
full3Finger/Stage1 approval. ALL22system gates stay UNQUALIFIED,updated in
models/primary_system_gate_state3.json. Unchanged read-only integrated release
exits2with24errors. SOFA runs0; no dt/global-energy qualification or Stage3.

Concrete next exact ID: goal_primary_root_ground_load_path. Continue THIS P1:
map actual Root/RF,motor cradle and fourM5 bearing/thread/finite Ground surfaces;
apply BOTH required port forces AND couples and solve physical transfer before
mesh/stress qualification. Reuse actual STEP/local FEM; preserve former unit+Z
frame FAIL. Do not replace real interfaces by arbitrary fixed DOFs or silently
balance external loads. Source minima/protection and3Finger/friction remain.

{len(s['executions'])}analysis children reaped;{s['recorded_child_seconds']:.6f}child-seconds,
new timeouts{s['timeouts']}; each4GiB/420s,<=4concurrent long children. STOP absent.
No RUNNING queue records or owned analysis children. Source pins unchanged,
pre-existing user untracked hashes preserved. No manager launch/Git write,
purchase/hardware/SDK/provider/credentials/subagents. Supervisor save request:
runtime/goal_authorized_20261127_7/save_request2.json; exact local save PENDING.

'''
p=ROOT/'CHECKPOINT.md';p.write_text(text+p.read_text());print(json.dumps(dict(status='FINAL_READ_ONLY_REVIEW_PASS',next_task_id=choice['id'],old_untracked_preserved=len(preserved),running=running)))
