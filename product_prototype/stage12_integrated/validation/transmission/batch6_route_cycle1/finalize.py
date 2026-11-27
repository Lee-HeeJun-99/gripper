"""Record one completed actual route-removal analysis; no Git mutation."""
import datetime,hashlib,json,subprocess
from pathlib import Path
repo=Path.cwd();root=repo/'product_prototype/stage12_integrated';out=root/'validation/transmission/batch6_route_cycle1'
def dump(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def ref(p):return dict(path=str(p.relative_to(repo)),SHA256=hashlib.sha256(p.read_bytes()).hexdigest())
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert head=='c3e3d56ff626d7b3a39507f180007bd7f5e6fda0'
assert not (root/'runtime/STOP').exists()
cad=root/'cad/exports/revAW_direct_route2/summary.json';ver=root/'validation/transmission/batch6_route_verify1/summary.json';work=root/'validation/transmission/batch6_route_work1/summary.json';release=root/'validation/integrated/batch6_route_release1/summary.json';failure=root/'cad/exports/revAW_direct_route1/summary.json'
c,v,w,g=[json.loads(p.read_text()) for p in (cad,ver,work,release)]
assert c['status']=='DIRECT_ROUTE_INTERFERENCE_FAIL' and v['status']=='PASS' and w['status']=='DIRECT_ROUTE_CLOSING_ACTUATION_FAIL' and g['status']=='INTEGRATED_NOT_QUALIFIED'
records=[json.loads((out/(n+'_execution.json')).read_text()) for n in ('route','route2','verify','release','work')]
assert [r['exit_code'] for r in records]==[1,2,0,2,2]
assert all(r['reaped'] and not r['timeout'] and r['elapsed_s']<420 for r in records)
remaining=[e.split(': ')[1] for e in g['errors'] if e.startswith('stage2: ')];assert len(remaining)==22
summary=dict(status='ACTUAL_DIRECT_ROUTE_REJECTED',task_id='batch6_standard_idler_or_direct_route',starting_HEAD=head,save_status='PENDING_SUPERVISOR_VALIDATION_AND_LOCAL_SAVE',new_commit_SHA=None,actual_research_cycles=1,
    scope='Actual finite nominal0.5mm direct route specimen at AO Finger/AV drive positions, proposed removal of27 Idler instances; NOT whole candidate assembly or powered operation',
    actual_results=dict(route_geometry=ref(cad),independent_verification=ref(ver),virtual_work=ref(work),release=ref(release),initial_execution_failure=ref(failure)),
    structural_problem_addressed='Tested whether direct drum-to-terminal routing can remove all Idler bracket/pulley/spacer/axle/nut/base/clamp-washer instances and special axle forming. Exact actual Palm interference and adverse initial pull direction reject this route. No Idler hardware is qualified by this result.',
    changed_part_IDs=[f'F{i}_TENDON_WIRE' for i in range(3)],new_route_specimens=15,proposed_removed_parts=27,realized_product_reduction=0,custom_processes_removed=0,adoption=False,
    proposed_process_removal_if_feasible=['Special Idler crosspin/rivet forming and opposing tool access','Idler axle retention assembly and replacement'],
    geometry=dict(exact_context_pairs=c['exact_pairs'],intersections=len(c['hits']),min_palm_intersection_mm3=min(h['common_mm3'] for h in c['hits']),max_palm_intersection_mm3=max(h['common_mm3'] for h in c['hits']),unchanged_intersection_limit_mm3=1e-8,valid_single_solids=15,closed_oriented_positive_meshes=15,independent_constant_length_range_mm=v['constant_length_range_mm'],rest_palm_midheight_crossing_F0_mm=v['checks'][0]['palm_midheight_crossing_F0_mm']),
    actuation=dict(rest_closing_torque_Nm_per_N=w['rows'][0]['closing_torque_Nm_per_N'],dead_point_deg=w['dead_point_deg'],stroke_0_to_60_mm=w['stroke_0_to_60_mm'],meaning='Prescribed virtual-work sign, not actual loaded equilibrium. Direct length increases initially; reversal of motor winding cannot make a tension-only tendon push.'),
    verification=dict(input_hashes=True,exact_STEP_intersections=True,analytic_tangency_and_constant_wire_length=True,finite_difference_work_derivative=True,disjoint_and_corrupt_tangent_controls=True,mesh_vertex_key_rounding_mm=1e-9,mesh_comment_erratum='Archived verifier parenthetical1nm is a unit typo: rounding to9 decimal places in mm is1e-9mm. This is numerical vertex identity only, never collision/physical tolerance.'),
    limitations=['No flexible PET/Rail deformed geometry; no actual load equilibrium','No CCD or continuous clearance, tolerances, termination fatigue or maximum cable stock','Redirected swivel seating/rotation limits/full assembly and installation path unqualified','AV1101 remains rejected as operating motor; ground support, anchor, thread capacity and physical protection unresolved','No physical material/rating/strength/energy or same-revision full product certificate'],
    execution=records,SOFA_runs=0,failures_preserved=[dict(result=ref(failure),log=ref(out/'route.log'),reason='Path-join TypeError before CAD; archived producer and pre-run SHA preserved'),dict(result=ref(cad),exit_code=2),dict(result=ref(work),exit_code=2),dict(result=ref(release),exit_code=2)],
    remaining_gate_ids=remaining,directly_informed_gates=['idler_load_drag','continuous_load_path','changed_stage1_revalidation','tendon_force_stroke'],
    next='Coverage before repetition: wide Root cartridge then simpler Palm mounting. For Idler use stock shoulder/clevis axle with double support and preload-bypass spacer; current AO/AV direct route is rejected. A Palm port alone cannot repair adverse pull direction. Revisit routing only with a materially different drive/attachment architecture, not small parameter scans.',
    whole_system_release=False,criteria_relaxed=False,producer=ref(Path(__file__).resolve()))
dump(out/'summary.json',summary)
q=json.loads((root/'INTEGRATED_TASKS.json').read_text());t=next(x for x in q['tasks'] if x['id']==summary['task_id']);assert t['status']=='READY'
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
t.update(status='FAIL',result='validation/transmission/batch6_route_cycle1/summary.json',reason='Actual direct-route removal branch rejected:15/15 Palm intersections and adverse initial tension torque. Standard double-supported Idler alternative remains untested/unqualified.',last_run_utc=now,consecutive_runs=1,followup=summary['next'])
dump(root/'INTEGRATED_TASKS.json',q)
h=json.loads((root/'TRACK_HISTORY.json').read_text());h['cycles'].append(dict(task=t['id'],track=t['track'],time_utc=now,status='FAIL',evidence=ref(out/'summary.json'),starting_HEAD=head,execution='One bounded actual direct-route design/analysis cycle; no subagents or external launch',save='PENDING_SUPERVISOR_LOCAL_SAVE',new_commit_SHA=None));dump(root/'TRACK_HISTORY.json',h)
assert not [x for x in q['tasks'] if x['status']=='RUNNING']
note='''# Batch6 cycle1 — actual direct Idler removal rejected (2026-11-27)

Started at c3e3d56ff626d7b3a39507f180007bd7f5e6fda0. Exact selected task:
batch6_standard_idler_or_direct_route. One actual bounded design/analysis cycle.
No git add/commit; supervisor validation/local save PENDING, no new SHA claimed.
Result: product_prototype/stage12_integrated/validation/transmission/batch6_route_cycle1/summary.json.

revAW_direct_route2 contains15 actual finite0.5mm cable STEP/STL specimens:
three sectors at five prescribed0/15/30/45/60deg poses, actual AO Finger and AV
drum axes, direct tangent and redirected swivel. Proposed removal27 Idler
instances would remove axle/rivet manufacture/assembly, but is NOT adopted.
No stock component is newly claimed qualified; no custom process actually removed.

Actual route FAIL(exit2): all15 wires intersect the retained Palm by
0.700775..1.197828mm3 against unchanged1e-8mm3 criterion;378 exact context pairs.
At REST the straight line crosses Palm midheight at local x83.1372,z-9.5mm.
Independent STEP reimport repeats all15 Palm intersections; valid single solids,
closed oriented positive STL meshes, tangent and constant total wire length
checks pass. Disjoint translation and corrupt tangent controls pass. Mesh
numerical key rounds9 decimals in mm (1e-9mm); archived comment1nm is a unit typo,
not a tolerance change. No deformed flexible geometry/CCD/strength claim.

Independent virtual work FAIL(exit2): REST closing torque per unit tension
-0.01164224Nm/N; wrong pull direction initially, zero at46.16044deg then sign
reversal.0to60 signed take-up -4.261803mm. Derivatives match refined independent
finite differences. These are prescribed-path kinematics, not loaded equilibrium
or powered Stage3. A Palm cable port alone cannot fix the pull-direction defect.

Initial path-join TypeError(exit1) before geometry preserved in revAW_direct_route1
with pre-run source hash/copy and log. All physical FAILs remain immutable.
Five bounded executions completed/reaped: initial1,route2,verify0,release2,work2;
each4GiB/420s and one thread. No timeout or SOFA run. No live owned analysis child.
Read-only release audit remains INTEGRATED_NOT_QUALIFIED,22 Stage2 gates missing.
RevAA adopted and AO current unchanged; AV motor still unaccepted for operation.

Next coverage task: wider Root cartridge, then simpler Palm. Idler fallback:
standard double-supported shoulder/clevis axle and preload-bypass spacer with
real installation, free-spin, reaction/rating evidence. Direct AO/AV route is
rejected; different architecture required before another direct-route trial.
No full product assembly/BOM, hardware, SDK,criteria,manager or Stage3 changes.
No RUNNING queue records. All pre-existing untracked CAD/BOM preserved.
Exact save_request1.json awaits supervisor validation/local save.

'''
for p in (root/'CHECKPOINT.md',root/'AUTONOMOUS_RESUME.md',repo/'product_prototype/reports/CHECKPOINT.md',repo/'product_prototype/reports/AUTONOMOUS_RESUME.md',repo/'reports/INTEGRATED_CURRENT_STATUS.md',repo/'reports/INTEGRATED_NEXT_TASKS.md'):
    p.write_text(note+p.read_text())
print(json.dumps(dict(status=summary['status'],execution_count=len(records),save='PENDING_SUPERVISOR_LOCAL_SAVE')))
