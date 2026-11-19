# B3 Guide release clearance and Native detection — 2026-11-19

Feature commits:ea03025,83da78d,18bd3eb,bd43763,3b7a4c5.
Final evidence:evidence_product_velocity_v20/manifest.json,linked to
evidence_product_clearance_v19/manifest.json and earlier immutable research.
No SDK,ForceField,ODE/contact solver,old Raw or old verdict was modified.

## 1. Actual-state attribution472/475

Read-only375 audit reproduces the old minimum proxy gap−0.864468777mm.
Only1of1200saved frames is negative:2.390s,finger1/cable0/station98 vs
finger2/cable1/station98. Mapping reconstruction error1.38778e-17m.
Hold-window guide gap stays positive(~0.199767mm).
At2.3875s minimum gap is3.133137mm;at2.390s it is negative.
Native Detector has no selected-pair output at2.390s;it appears at2.3925s.
Native solver residual0 at the negative frame is NOT clearance certification.
The previous step closes by up to4.274mm while alarmDistance is only1mm.
This is evidence of accepted-state/detection timing mismatch,not exact solid
eyelet/support intersection or a theorem about every collision path.

## 2. One-factor hardware candidate473/474/476–479

Change only sector margin0.5→1.0mm:only98mm terminal guides move1mm inboard.
Guide OD3mm,length2mm,wire radius0.25mm,material,mass,force1.5N/cable,
dt2.5ms,friction0.3 and other inputs are unchanged.492 confirms the ONLY config
difference is tendon.sector_margin_mm. Initial guide gap rises1→2mm.

473 frozen-motion replay predicts+0.081355mm;this is explicitly NOT dynamics.
474 actual Native3s/1200steps completes in221.356s,not a repetition of375.
Actual minimum guide gap is−1.102090496mm at2.390s:the clearance candidate FAILS.
It is not adopted. This disproves assuming old motion remains valid after routing
changes. Functional unsupported50g Holding still occurs:slip0.0299995mm,
max speed0.893952mm/s,Skin mean vertical0.490468N,Guide/Rail/Support0N
in the1.6–2.0s hold window. Functional Holding does not repair clearance/time gates.

## 3. Detection experiment480 and minimal Native reference483

Global alarmDistance1→5mm,original375 geometry and all physical inputs unchanged:
480 is CANCELLED_COST_FORECAST_NOT_PHYSICS_VERDICT. Initial4frames/0.01s take
approximately50s;completion forecast greatly exceeds480s. Launcher interrupted
(tool exit130). No child final report exists;child exit/runtime remain NULL.
It is NOT a timeout,OS exhaustion,completed Holding trial or successful remedy.
Partial Raw remains and journals stayed unchanged after interruption.

483 extracts two Guide poses/velocities from actual375 time2.3875s into FREE
Rigid3 bodies:10mg each,same native inertia/proxy radius,NO attachments,FEM,
cables or gravity. This is not a restart of the attached system.
Native4step results:alarm1mm minimum gap−0.968939mm;alarm5mm+0.274056mm.
Linear momentum residual≤1.11e-21Ns. Child runtimes~0.17s.
This supports the detection-range hypothesis in a bounded independent reference,
not a whole B3 fix.

## 4. Bounded Native public-data Controller484/485/488–494

A separate BaseObject Controller writes ONLY the installed intersection's public
alarmDistance. It does not calculate force,impulse,positions,velocities or constraints.
Original375 geometry/config bytes and physical binary332 are retained.
Alarm remains1mm except accepted end-clock2.386–2.396s,where it is5mm.
Native contactDistance0.2mm,solver tolerance1e-10,dt2.5ms,material,friction,
force and fixtures remain unchanged. The window is chosen from observed failure;
it is NOT a general event detector,CCD,adaptive integration or production policy.

485 completes3s/1200steps in133.319s under4GiB/480s guard;no SOFA errors.
492 checks applied alarm/contact-distance/time values at ALL1200outputs:
exactly4wide frames;contactDistance unchanged. All954pre-window frames of
three fingers(q/v/cable force),three Guide bodies(q/v) and object(q/v) match375
EXACTLY(error0),passing strict1e-12. Later states legitimately differ.
No repeatable runtime-optimization claim is made from these single executions.

488 finds NO saved-state guide-sphere overlap:global min+0.194739mm,
release-window min+0.199817mm.493 exact saved-center CHORD interpolation also
has no negative intervals(min+0.194739mm). Chords are NOT actual Native intermediate
states,quaternion paths,swept solid supports or continuous collision certification.

489/490 use unchanged predeclared50g/R30/gravity9.81/friction0.3 protocol:

|Metric|Actual485|Scope|
|---|---:|---|
|Downward slip|0.0323588mm|functional hold1.6–2.0s|
|Maximum object speed|0.272144mm/s|limit5mm/s unchanged|
|Support gap|41.599746mm|limit5mm unchanged|
|Support reaction|0N|limit1e-5N unchanged|
|Skin mean vertical support|0.490513315N|weight0.4905N|
|Minimum Skin weight fraction|0.994652792|predeclared0.8 unchanged|
|Guide/Rail/Support hold force|0N each|actual response-row provenance|
|Response partition residual|2.1684e-19Ns/Nms|no fabricated missing forces|

Skin contact releases after2.3875s;late Skin/Guide-object/Support forces are0.
Object falls~2386.31mm under gravity,NOT Lift. Rail contact occurs briefly during
release(first2.385s);Skin-only holding is not claimed for the entire3s sequence.
Final tip reference error~0.150984mm with gravity still applied;complete elastic
recovery to a separately validated gravity equilibrium remains NOT QUALIFIED.
494 minimum tet volume ratios~0.98149/0.98261/0.98218 are positive at saved states.
Sampled finite-wire/object margins≥3.858mm;wire collision force is NOT MODELLED.
No exact support-solid/self-collision/pressure/contact-area qualification follows.

484 frozen binary:6da7c82044b72a024bc825a476020e75f99499ad4f51c106b0a00b36bde841bf.
Compiled source:0fc9234e959d76f94218e6c4dd123d4b65940665e725baf3ec051dacf8e8f8bf.
Physical/controller332 binary:3eb202b1e2a25f3ec6cded69e92a9d02bc48c304be14f6ca7123b4d758e5d0e0.
Frozen guard:observer_identity.compiled_alarm_window().
SDK:/home/ubuntu/SOFA/v26.06.00;assumed E250MPa and research masses/materials,
NOT measured product properties. Peak RSS/work/pressure/root reaction:NOT MEASURED.

## 5. Time gates retained:496–502

Independent free-guide dt2.5/1.25/0.625ms with alarm1/5mm use identical physical
inputs within each comparison.498 evaluates ALLcommon outputs and ALLthree pairs,
including base-to-quarter,without an absolute floor. Both alarm settings FAIL
the existing0.1% criterion. Worst alarm5 angular velocity difference64.4362%;
alarm1~97.0950%. Clearance alone does not determine consistent impact velocity.

Installed Native FreeMotionAnimationLoop exposes solveVelocityConstraintFirst.
499–501 test it ONLY in the same NO-CABLE free-guide benchmark;the previously
failed Cable velocity-first design is not reapplied to B3.502 still FAILS:
worst alarm5 angular velocity difference63.8029%,alarm1~97.0950%.
No velocity-first B3 change is adopted. No full3-finger time/mesh/energy gate
is repaired. Original243,coarse/refined bending failures and all old gates remain.
100g/Lift/Optuna remain blocked by required physics gates.

## 6. Shared CAD/drawings481/487

Corrected the orthographic route export to use guide_outboard rather than a
constant offset. Added all-six-route top projection and guide_routes_mm.json.
Published a separate BASELINE reference,not the rejected474 geometry:
product_prototype/meshes/precurve_distal40_route_audit_v10 and drawings/same-name.
487 independently checks all6route guide-center arrays against initial375 Scene:
all errors0 and configuration bytes identical. STL,SCAD,SVG and provisional BOM
exist. Guide/support solids,STEP/kernel assembly,fasteners/actuator selection,
wire bend radius and fabrication tolerances are NOT verified. Fabrication ready:NO.

## 7. Bounded disposition and next task

Stop margin sweeps:474 made moving overlap worse. Stop global wide-alarm full
runs:480 cost forecast failed.485 remains a useful bounded detection diagnostic,
not a final general solution. Both tested Native contact orders fail time
sensitivity in a small independent problem. Do not expand to100g/Lift or hide gates.

NEXT:instrument actual Native free-pair normal/tangential relative velocity,
contact impulse and exact response-row geometry around contact entry. Reuse
existing verified mass/Jacobian references,not a new solver. Compare the two Native
orders at the SAME physical event phase,distinguishing pre-buffer activation from
actual physical contact. First add read-only row/detector recording to the small
coupon;do not start another full grasp run or blindly halve dt.
Potential local refinement needs input/work/clock consistency and convergence,
not just a scheduled small dt.

Read-only restart:

```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_pair_time498/summary.json
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_pair_velocity_time502/summary.json
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_comparison492/summary.json
```

Exact executed commands are preserved in each launch_command.json,producer.py
and process/command.json. New full diagnostic reproduction(require cost review):

```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/run_alarm_window.py --tag UNIQUE_WINDOW
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/guide_pair_coupon.py --tag UNIQUE_PAIR --dt .000625 --velocity-first
```

Actual scientific visualization:results/b3_clearance_plot495/actual_native_clearance.png,
b3_window_holding489/holding.png,b3_window_geometry494/b3_alarm_window485.png.
No displacement exaggeration or hidden object relocation. Concept CAD is labelled.

v19 verifies1351prior files(0mismatches),records2000hashes/27cases.
v20 verifies2000prior files(0mismatches),records2087hashes plus4newcases.
All earlier results remain unchanged. All launched sessions ended;cancelled480
lacks a final child report as explicitly recorded. No automatic continuation promised.

