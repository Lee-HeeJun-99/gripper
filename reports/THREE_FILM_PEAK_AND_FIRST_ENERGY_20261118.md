# Actual first C2 peak and first-impact interval inventory

## Additional verified1130–1133 — value-only geometry and grasp feasibility

12000 independent closest-point queries are bit-exact with original AD2.
Optional clearance-only mode (defaultOFF) leaves mechanical Force/Hessian
unchanged. Actual1131 eight-step state/stage/ForceField CSV match1124 bytewise.
Actual1132 three alternating A/B pairs all PASS strict replay and snapshots:
median4.175684s→3.310452s,20.7207% reduction,ONLY unloaded FREE recovery.
No general collision/impact speedup claim.

Actual20ms-row audit1133 finds frictionless sphere wrench rank3 and exactly
zero normal torque. Upward normal force observed5.27745e-6N is NOT a holding
capacity.100g Earth-weight reference.981N is a calculation,NOT measured lift.
Actual gravity remains0,Fz=-.001N. Friction/self-contact remain unqualified.
Thus simply extending zero-tension recovery will not establish stable grasp.
Full12-wrench dynamic trials and final design/Optuna remain NOT RUN/BLOCKED.

## Latest verified checkpoint — 2026-11-18, Campaigns1091–1129

- Actual1091 fixes the representable RK interval duration without changing forces:
  independent q/v EXACT;1092 verifies sum(stage weights)==actual elapsed time.
  Prior1076/1089 clock failures remain preserved.
- Actual unloaded recovery reaches **38ms** (1124 and seven bounded1127 plans),
  via V5 persistent clock/used-dt/next-dt/plan/counter state.1125 independent
  q/v/time EXACT;1126 four-step actual resume and checkpoints BYTE-IDENTICAL.
  Earlier1112/1113/1117 exact resumes and1114 corruption rejection also PASS.
- 1110 actual same-time800us recovery subset PASS (max all-pair0.01281255%).
  The longer independent6.4ms200/100/50us comparison1121 FAIL0.11718728%;
  separate100/50/25us1123 PASS0.02950534%. This is NOT full-cycle time PASS.
  1106's multiplied/common-time API bridge FAIL5.57e-12 is preserved;the actual
  next-dt scheduler aligns all11 contexts rather than overwriting q/v/time.
- 1096 release power inventory: mechanical tendon work -5.45816e-8Nmm,
  signed defect -1.11372e-12Nmm;not heat/full energy certification.
  Root reaction work NULL. Legacy sampled-work private origin is not restored.
- Actual1128 at38ms: skin width-mean tip z=-0.34690653mm,vz=-3.74943732mm/s;
  skin RMS displacement0.12074783mm and squared-RMS rate +1.07056815mm²/s:
  **shape recovery not completed**. Rails relax while skin continues moving.
  Body vz=-1.29190161mm/s;gravity0,Fz=-.001N,friction OFF:NOT hold/lift.
  1129 scale-one actual geometry/OBJ uses saved state,not prescribed deformation.
- Independent current-deformed frozen spectrum1087 has longest undamped
  period5.85155s;NOT measured nonlinear recovery time. A naive long rollout is
  not justified.1116's old32ms admission block was model scope,not OS/session
  exhaustion;independent work and separately qualified actual extension followed.

Reusable DLL:
`build/three_film_extended_20261118_three_film_extended_actual1124/libReGripThreeFilmRecovery.so`
SHA256 `9767481765017b112b4789afabdda3412cd556ec7b775a92b8b9cec754d4ba5c`.
Latest actual state:
`results/autonomous_film_20261118_three_film_recovery_chain1127_plan7/three.checkpoint_280.txt`.
Raw/manifests and earlier FAILs remain immutable. Actual30ms/32ms legacy caps
remain;only separate Extended Owner admits this qualified31.6..38ms window.
New sources currently based on77706b;see next feature Git commit for live code.

Next: profile/validate value-only geometry queries (do NOT alter mechanical
Force/Hessian),then choose a qualified longer-time or structural study from
actual shape response. Do not blindly extend beyond38ms or call zero tension
recovery. Full contact time/mesh/energy,friction,thickness,self-collision,
mechanical equalizer,wrapping/hold/lift/12-wrench/Optuna remain NOT CERTIFIED.
Exact replay command (unique TAG,foreground,not automatic restart):
```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/film_three_film_v5_resume.py --tag UNIQUE_TAG --parent 20261118_three_film_extended_actual1124 --step 220 --steps 4 --compare
```

Older entries below are historical,not current RUNNING processes.

## CURRENT verified — deformed release1079 and exact FREE resume1082

Actual1079 independently matches q/v EXACT at original1e-12 API; applied
normal forces nonnegative,whole-stage gap>=1.42109e-13mm,momentum3.55122e-19Ns,
outgoing normal velocity>=.00631256mm/s. Separate20us acceleration
complementarity plus remaining free-midpoint variant;old failed Lobatto
horizons remain FAIL. RK/free accumulated-clock join is EXACT after fixing
1076's reconstructed-clock mismatch9.02056e-17s. No force/velocity projection.

Actual1081 reaches27.6ms separated.1082 restores FREE V3:two subsequent
steps,q/v/stages/ForceField observations EXACT,two snapshots BYTE-IDENTICAL.
Whole quadratic midpoint numerical-path surface CCD rejects new impacts.
NOT an exact continuous nonlinear CCD/full time/mesh/energy/grasp certificate.
1083 is the next bounded24-step Unload-to30ms experiment;inspect its actual
process/summary before claiming completion. No background restart promised.
Reusable DLL:build/three_film_release_20261118_three_film_actual_clock_release1079/libReGripThreeFilmRelease.so
SHA25622add00153af4573a0e852c954af0514f444ca4d23c03a1d9f5136ab05e9cc51.
Full details:REGRIP_THREE_FINGER_GRASP_CONTINUATION.md. Older states below
are historical;full time FAIL,friction/self-contact/lift/optimization BLOCKED.


## CURRENT — typed Edge resume qualified; Unload stops at release

1059 actual Face->Edge event PASS;1060 four-step V2 resume EXACT including
byte-identical snapshots.1061 requested30ms FAILS after accepted27ms at
negative stage reaction (127.184s,not timeout).1062 independent signed
diagnostic reproduces +1.06418e-7N at27ms and -4.88759e-7N at27.05ms.
No negative reaction committed.1064 independent passive-observer regression
and query-purity PASS. Next is zero-reaction event and coupled release;
full time/energy/wrapping/lift remain UNQUALIFIED. Detailed1059–1061
evidence and reusable DLL are recorded below; earlier status is historical.


## Latest implementation — through1048,project INCOMPLETE

Persistent resume1014/1015/1016 strict1e-12 EXACT;actual C2 Hold reaches20ms
in1022. Actual Unload200us1024 and100us1033 FAIL:stage position drift and
new surface contact support.334-bit audits exclude a large geometry roundoff.
1042/1043 isolated117 Birth/shared6-row impulse kernel qualified;1044 ACTUAL
SOFA deformed124->117 support migration PASS,q/v/impulse/time EXACT,global
momentum/whole-stage clearance pass. This releases OLD ROWS,NOT the object.
1048 actual segmented work/impact inventory PASS consistency,not full energy.
1047 subsequent ordinary continuation FAILS at another event after23.6ms;
next actual development is generalized inactive-surface birth/retained-row
handling,not unchanged long-step retries.1041 time gate remains FAIL;full
Unload/object release/wrapping/holding/lift/friction/self-contact/full energy
remain unqualified. Detailed evidence/builds:REGRIP_THREE_FINGER_GRASP_CONTINUATION.md.
Lower RUNNING/checkpoint sections are historical,not current process claims.


## New persistent continuation checkpoint — through1017

Separate checkpoint/resume owner implemented;actual1014 four-step transfer,
1015 serialized retransfer and1016 through10ms match continuous1002 q/v/time
and all used stage rows EXACT under original strict1e-12. Field control,
geometry and stored energies exact in1014. No old REST counter spoofing.
1017 actual10→16ms Hold COMPLETE,scoped EXPERIMENTAL;not wrapping/lift.
1018 negative-test harness FAIL preserved;1019 read-only reassessment confirms
five invalid checkpoint guards reject before accepted commit.1020 partial
stage-work inventory PASS consistency;private legacy sampled-work is NOT
restored or joined. Overall time997 FAIL and deformed-release999 FAIL remain.
Full energy/root work/friction/self-contact/full-thickness/grasp unqualified.
Details,Raw/build and commands:REGRIP_THREE_FINGER_GRASP_CONTINUATION.md.
Next actual task:bounded Hold to20ms,then C2 Unload and genuine release analysis.
Lower checkpoint/RUNNING entries are historical,not current process assertions.


This checkpoint is NOT a final grasp or full physical-energy certificate.
Every measured value below is classified by its origin.

## Actual SOFA to10ms

1002 actually completes50x200us in193.40398s,forecast404.9591s below480s.
Three actual FilmRailTendon states/masses,ONE free Rigid3,proper fixed mounts.
Research assumptions:film100mm,root-centre radius50mm,sphereR30mm plus.01mm
midsurface buffer,film1g each,sphere100g,gravity0,Fz=-.001N.
C2 Tmax=.0001N PER RAIL,ramp10ms,release20–30ms. Common input is not a
physical tendon equalizer. Initial sphere z offset+.0001mm,vz=-1mm/s;not
closing a stationary object from rest. No friction/self-contact/layer jamming.

Minimum whole-stage buffered gap-1.10134e-13mm,momentum max8.52437e-20Ns,
normal-velocity residual2.75054e-13mm/s. Geometric/force residual gates retained.
1004 independent mapped/end-surface/used-impulse audit PASS.
Actual scale1 images/OBJ in1004,actual width profiles1003:
skin centre-node tip+.000662151mm but width-mean tip-.02496388mm;
rail width-mean tips about-.101045mm. NOT wrapping/lift/holding evidence.
Contact area,pressure and holding load remain null/NOT MEASURED.

## Absolute API gate error discovered and corrected

Original inherited absolute state API gate is STRICT <1e-12.
Three new runners mistakenly used1e-11;source predicates are restored.
1006 independently re-audits all completed continuations WITHOUT changing Raw:
966 and978/979/980/986/993/994 still pass1e-12;1002 versus original reference
1000 FAILS(v3.82804899e-12,q1.11e-16). Its original loose-runner PASS is
preserved but MUST NOT be used as qualification.

Independent nonlinear FEM1008 uses ONE compiled binary to isolate ONLY the
floating input clock:accumulated t+=dt versus multiplied step*dt. No SOFA state,
force or velocity is injected into reference integration. All other inputs,
exact public masses,algorithm and C2 law unchanged. Both complete50 steps.
Accumulated clock:q/v EXACT to actual1002;multiplied clock reproduces exactly
the original3.82804899e-12 velocity difference. Clock discrepancy only
6.07153e-18s but relevant to strict bit-level stiff-dynamics comparison.
Runtimes145.45/147.59s(each bounded480s/4GiB).

1009 hash-bound same-actual reassessment checks archived kernel headers,
plugins,physical XML,masses/control proof and all Raw;STRICT1e-12 PASS with
q/v/time differences0. No tolerance/actual force/state changes.
This is NOT a new SOFA execution and does NOT erase1006 or full-time997 FAIL.
Future independent-to-SOFA comparisons default to accumulated input clock;
multiplied mode remains an explicit counterfactual.

## Source-corrected force generator observation

1005 initial extra generator audit FAIL assumed T*L. Existing Kernel.h actually
uses T*(L_current-2*100mm). This is a force generator,not stored elastic energy.
1007 corrects only the observer definition;old1005 remains FAIL. Stored/kinetic
inventory,mechanical -integral T*dL and signed residual are unchanged.
Actual endpoint control mismatch0N,stored/film kinetic callback error6.10e-20Nmm.
Interval200us..10ms:stage tendon work9.80103177e-5Nmm,
signed residual-3.87613e-12Nmm. First interval was not included in this ledger.
Residual is not heat;full physical energy remains BLOCKED.

## Actual first free/impact/remainder journal

1010 implements opt-in firstIntervalJournal,default OFF. Same DLL OFF/ON actual
trials both COMPLETE16.57/17.06s. All ELEVEN physical CSVs byte-identical
to each other AND prior964,including forces/impulses/states/displacements.
Added journal contains7 actual accepted-stage records:
initial,free midpoint,pre-impact,post-impact,remainder initial/midpoint/end.
Weights sum exactly200us. No new force/velocity/position correction.

1011 independent full-AD inventory of those ACTUAL recorded stages:

| Term | Nmm |
|---|---:|
| Stored+kinetic change |1.59156280008e-7|
| Tendon mechanical work |5.74839650396e-16|
| External work |2.00158100406e-7|
| Rayleigh damping work |4.00636480748e-8|
| Normal constraint work |-4.59748335431e-25|
| Stable plastic impact loss |9.38172883664e-10|
| Signed residual |-1.38829341120e-17|

Actual-field stored/film kinetic error1.07e-27Nmm,stage and endpoint control
errors0N. Kinetic subtraction minus stable impulse loss=-1.14432e-20Nmm is
a numerical inventory,not additional heat. Root reaction work remains null:
ideal fixed/mapped-root virtual-work assumption is not an independently
measured reaction journal. This is a first200us coupon ledger,NOT FrameLayer,
pressure,friction,fullcycle or total-gripper energy qualification.

## Independent timescale evidence,not a mode or real material measurement

1001 nonlinear FEM Hessian at stress-free T0 uses an admissible quadratic
film trial and shared body translation satisfying all3 contact-tangent rows.
Rayleigh quotient omega=.0602317rad/s,conditional lowest undamped bilateral
period lower bound104.317s. This is NOT an eigensolve,dominant forced mode,
actual wrapping duration or damped response prediction. Film kinetic fraction
of this trial=.001629;100g sphere dominates. It shows why a10ms diagnostic
cannot by itself establish slow full-gripper adaptation or a failed route.

## Still unqualified

997 overall post-time FAIL(legacy work.7214%,normal-work residual relative
FAIL);event/impulse time refinement,nonlinear earliest-event completeness,
mesh/history,physical-thickness clearance,general friction,self-contact,
deformed release/re-impact,wire-driven wrapping,holding/lift,12wrench,
multimaterial and Grasp Optuna.999 weak pull-away release hypothesis FAIL:
the deformed state still needs positive normal reaction. No fictitious
ungrasp operation was applied.

## Exact safe commands

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/film_three_film_clock_qualify.py --tag NEW_QUAL --proof 20261118_three_film_clock_reference1008
$PY tools/film_three_film_first_inventory.py --tag NEW_INV --case 20261118_three_film_first_journal1010
# Actual reproduction only if needed;both exclusive NEW output paths:
$PY tools/film_three_film_horizon.py --tag NEW_REF --clock accumulated
$PY tools/film_three_film_peak_sofa.py --tag NEW_ACT --reference NEW_REF
```

Reuse actual peak DLL:build/three_film_peak_20261118_three_film_first_peak_actual1002/
libReGripThreeFilmEvent.so. Current first-journal DLL:
build/three_film_first_journal_20261118_three_film_first_journal1010/
libReGripThreeFilmEvent.so. Source/binary/SDK and generated scenes in campaigns.
Do not rerun archived scenes into existing outputs. No automatic continuation
or OS/RAM exhaustion is claimed.
## Latest verified continuation — 1059/1060; Unload1061 FAIL (2026-11-18)

Actual SOFA1059 implements bounded deformed Face->Edge transition at
23.67137720356692ms, preserving velocity without an impulse or projection.
Independent q/v/time match EXACT; whole-stage gap >= -7.21201e-13mm.
New material-edge owner stores ordered nodes [77,73], source triangle117,
birth time, exact normal/parameter and accumulated clock in REGRIP_EDGE_V2.
Actual1060 restores the V2 state in a separate Edge Owner: four subsequent
steps, all36 stage rows and ForceField observations match EXACT (legacy
sampled-work excluded with a declared new origin); four checkpoints are
byte-identical. Original strict1e-12 API gate retained.

1061 attempts 59 steps from24.1ms to30ms. FAIL after29 individually accepted
steps, latest checkpoint170 at~27ms: next bilateral stage reaction is negative.
Runtime127.184s, exit-6, NOT timeout/resource exhaustion. Unilateral guard
correctly refuses the trial; no negative reaction is committed. This is not
completed Unload, object release, wrapping, holding or lift. Existing1041
time FAIL and whole-energy/friction/self-collision/mesh BLOCKED remain.
Next: locate zero-reaction event using signed diagnostics only, remove
released material-edge rows, re-solve coupled dynamics and recheck ALL triangles.
Do not simply continue with negative force or reset velocity.

Reusable DLL:
`build/three_film_primitive_20261118_three_film_primitive_actual1059/libReGripThreeFilmPrimitive.so`
SHA256 `52d558a749f2a5288a51ab9b522b1cc128cd9b804eb1300ce62705d1310fc637`.
Raw: `results/autonomous_film_20261118_three_film_primitive_actual1059/`,
`...three_film_edge_resume1060/`, `...three_film_edge_unload1061/`.
Sources at0fa09fb plus archived feature-development source snapshots.
No completed grasp or automatic background restart is claimed.
