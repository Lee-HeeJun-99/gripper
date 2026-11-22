# Rail clamp continuous-service and stack continuation — 2026-11-23

Baseline clean branch `development/regrip-autonomous-research`, HEAD `0a52556`.
Main implementation/evidence commit `371b318`.
Existing 892–914 and Native895 preserved; no SDK edits, push, purchases or new
SOFA physics runs. Native adoption remains BLOCKED on actual joint data, not
on an invented substitute mass/preload. This work is CAD/reference verification.

## Cycle 1: close the sampled-service evidence gap

New `cad/rail_continuous_service.py` uses the actual 288-part908 recipe. A
whole-body convex hull of original and translated vertices contains every
intermediate straight translation. Empty intersections therefore bound the
whole nominal path; a hull intersection on a concave part is only UNRESOLVED.
No arbitrary contact distance, mesh thickening or collision exclusions added.
Exclusions follow the already declared sequence: unload/unthread wire, remove
clamp screw, remove pad, then move the seven-part subassembly rigidly together.

915 (5.792s): pad inboard4mm and six keeper/Eyelet/fastener bodies along
outboard8mm+longitudinal8mm have empty envelope intersections. Support hull
overlaps Skin1.05629mm³/Rail5.22343mm³. NOT proof of actual collision: the hull
fills the concave clamp opening. Existing sampled910 scope remains unchanged.

## Cycle 2: refine only the unresolved Support

Actual triangle translation prisms replace the whole concave Support hull for
the two hull-hit obstacles. Initial Support solid is checked separately.
916 failed in6.734s because nearly planar numerical prisms are not valid
volumes for Native manifold CSG. Failure/logs retained. 917 explicitly retains
nonvolume prisms as unresolved rather than deleting faces or adding thickness.

917 (7.260s): 2798 Support triangles,830 CSG comparisons, no reported prism
intersections and no initial solid intersections; **41 unresolved nonvolume
prisms**. Status `SURFACE_SWEEP_REVIEW_REQUIRED`, NOT continuous-service PASS.
Exact zero-volume candidates would also be counted; tangency and certified
floating-point CCD are outside scope. Do not keep retrying with epsilon floors.

## Cycle 3: actual CAD free-stack closure contract

New `cad/clamp_stack_contract.py` extracts actual Root-frame section geometry.
919 exposed a vertex-window defect: transformed Skin top x10 vertices fell
just outside x>=10 while bottom vertices remained. Its erroneous0.17mm output
is preserved with `CORRECTION.json`, not silently replaced or accepted.
920 uses the actual mesh/plane section at interior station x12mm:

| Nominal CAD term | mm |
|---|---:|
| Lower seat–Rail gap | 0.05000001192 |
| Skin–pad gap | 0.01000000000 |
| Pad–screw gap | 0.01000000596 |
| Pad thickness | 0.03000000000 |
| Ideal free-stack closure travel | 0.07000001788 |

These are CAD dimensions, NOT measured hardware. Rail/Skin is not a freely
translating rigid block in reality. Compliance, root constraint, pad indentation,
thread pitch, friction and preload remain NULL. No force/stiffness/pressure
inferred from this kinematic sum. 0.03mm pad remains a research geometry proxy.

## Regression / qualification / next work

918:101 legacy software tests passed. 921:111 tests passed, including a collision
only between endpoints, clear parallel motion, a concave-hull false positive,
rigid-transform volume invariance, invalid inputs and stack-extraction regression.
921 guarded runtime2.512s; test body1.957s. These are NOT product physics Gates.
Peak RSS NOT MEASURED; bounded CSG/regression children use existing4GiB guards.
The short stack extraction is CAD-only; no dynamic binary/SDK was invoked.

Next: review a finite manufacturable pressure pad and qualified screw/thread
interface against the actual0.07mm free-stack closure, with real material and
preload/slip/indentation evidence before any matched Native joint adoption.
For continuous Support service, obtain a robust CAD-kernel sweep/clearance
result or redesign for a provable convex decomposition. Do not mark41 numerical
prisms clear. Other sectors, moving wire/object clearance, time/mesh convergence,
100g/Lift/STEP and whole product qualification remain open. No unchanged273s
Native895 repeat or legacy B3 checkpoint reuse is justified.

Read-only resume (actual evidence):
```
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/product_rail_surface917/summary.json
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/product_clamp_stack920/summary.json
```
New-hypothesis reproduction only, use NEW names:
```
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/rail_continuous_service.py --tag UNIQUE --surface-support
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/clamp_stack_contract.py --tag UNIQUE_STACK
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/manufacturing_test_run.py --tag UNIQUE_TEST
```
Source hashes, actual commands, timing and failures accompany each new case.
No new physical Holding, Native, time/mesh, fabrication or STEP PASS claimed.

## Cycle 4: resource guard and immutable chain

The initial short CAD-only919/920 invocations were not resource-wrapped; their
actual runtime was below1s, not a claim that they had the child guard. The
stack CLI now uses the existing4GiB/420s guard (feature7635633). 922 executes that launcher and
matches920 CAD coordinates and closure dictionaries EXACTLY (no tolerance,
model or geometry change);923 checks this and all prior software regressions:
112tests PASS,2.592s testbody/3.281s guard. No product physics qualification.
No costly Native rerun. Evidencev51 verifies12831 prior immutable filehashes,
zero mismatches,12989 total hashes,7cases including failures/correction. Follow-on
v52 includes922/923 and updated source snapshots; no old evidence rewritten.
Remaining meaningful progression needs actual joint/material evidence or a
robust finite CAD sweep. Do not repeat the same CSG nonvolume failure or infer
preload from the nominal kinematic closure. Current product Gates remain open.
