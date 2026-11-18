# ReGrip tendon transmission and wrapping research —2026-11-18

## Actual stationary-origin26.8ms geometry and transmission —2026-11-19

Release refinement evidence (not yet whole time certification):
40us local-window32/64/128 (1576/1577/1580) all FAIL at unchanged
positive-reaction tangent gate;normal-velocity defects3.6512e−9,
9.1282e−10,2.2821e−10mm/s respectively. The approximately second-order
RK internal-stage defect motivates reducing only the local window,not changing
material/control/contact law or increasing the128-grid cap.
10us window32 (1581) FAIL2.3137e−10mm/s;10us64 (1582) reference PASS:
root bracket[71.87081566080452,71.87081575393679]us after26.8ms,
last-active/first-free RK STAGE times26.871792690660784/26.871870815660785ms.
These are NOT certified continuous-time exit roots. Final27ms gap minimum
−5.8690829973784275e−12mm,outgoing normal velocity+.012739307327679385mm/s,
summed reduced momentum bound8.066896214799044e−19Ns.
Measured root/RK/free costs68.1243/45.6836/.4777s within480s.
No tensile force,projection,clock reset or forced active-mask removal.

1583 actual-module compile FAIL duplicate historical registration;1584 compile
FAIL embedded legacy EDGE API after adding a FACE overload. Both preserved.
The embedding adapter now wraps ONLY old registration and retains original EDGE
overload bodies alongside the qualified FACE functions;physical functions are
not replaced.1586 compilation PASS but initialization rejects runner's incorrectly
changed maximum-step budget1. Original validated inherited budget is restored
unchanged;isolated solve still permits exactly count0 and runSofa executes1step.
1587 is the corrected actual trial;read its completed summary before claiming PASS.
1585 pure FREE footer roundtrip and7 invalid geometry/clock/history/origin/active
fixtures PASS. Known last global impact is retained,not renamed row birth time.

Functional commit4fc7200;actual1573 checkpoint134. Stationary sphere/film initial
velocities0,external force0,gravity0;new IVP,not incoming-body history splice.
1565/1566 independently resolve/execute additional rank6 impact at
22.62314827800726ms.1567 verifies frozen same-core source handoff;subsequent
actual1573 reaches .026799999999999949s with q/v and contact stages EXACT.
Gap−1.1691980716932449e−11mm,reduced momentum bound9.765636736557555e−19Ns.

1578 read-only actual nonlinear force inventory at26.8ms:

| Quantity,representative finger | Actual value |
|---|---:|
| C2 tension per rail,N |1.9052625920000715e−5|
| Direct Skin tendon force norm,N |0|
| Rail tendon force norm,N |2.5838801825274753e−4|
| Skin attachment force norm,N |1.1826961684533375e−4|
| Skin attachment power,Nmm/s |+5.767409770974783e−4|
| Rail attachment power,Nmm/s |−2.8756768616332966e−3|
| Width-mean Skin Tip local-z displacement,mm |−.2875729315313698|
| Centre Skin Tip local-z displacement,mm |−.09117523192875018|
| Left/Right Rail Tip local-z displacement,mm |−.3825419197660118 /−.3820240473977512|
| Skin maximum discrete mean-line curvature,1/mm |.0026564739022279377|
| Left/Right Rail maximum curvature,1/mm |.01538702319113262 /.015219040423364959|
| Skin tip width warp,mm |.33916012457661016|
| Actual endpoint owned normal force per row,N |8.323114780402672e−7|

Endpoint force is NOT holding capacity;power is NOT cumulative stage work.
Rail distal arch persists while mean Skin bends much less. This actual input
achieves wire-driven contact but does NOT establish continuous surface coverage,
wrapping,holding,lifting or recovery. No structural winner is selected.
Root work/contact area/pressure/holding load remain NULL.

1579 actual accepted-state reconstruction error7.070732888081466e−15mm.
Geometry scale1,orthographic equal-aspect view;profile axes independent.
Colors identify fingers,NOT pressure. Actual Scene force/gravity verified.
Image: `results/autonomous_film_20261119_stationary_shape268_1579/actual_geometry_curvature.png`.
Raw: `results/autonomous_film_20261119_stationary_force268_1578/response.csv`.

1572 positive-only continuation rejects release;longer actual NOT RUN.
1574 preflight anchor failure and1575 edge-owner mismatch remain preserved.
1576/1577 face-owned release32/64 reject positive force at RK trial states with
normal-velocity defects3.6512e−9/9.1282e−10mm/s (gate1e−10 unchanged).
The near4x reduction motivates a separate local-window numerical refinement,
not a tensile reaction,projection or tolerance change. See new reference
runner options `--stationary-268 --window-us 10`;require completed reference
PASS before executing the prepared StationaryReleaseODE actual owner.
No full time/energy/mesh/impact-friction/grasp certification is implied.

## Current stationary wire contact22.6ms,not yet wrapping —2026-11-19

Verified feature commits9e5126f and0b55c2d implement actual stationary-origin
closing/impact and typed persistent contact. Initial velocity/external force/
gravity are all0;this is distinct from the incoming-body experiment.
1549 independent isolated root,1550 impact/remainder and1552 ACTUAL SOFA
PASS with all final/pre/post q/v,impulse,event metrics and force-stage rows EXACT.
Event20.364869768894265ms,6rows/rank3,loss8.10396002971e-9Nmm,
gap−5.32907e-14mm,reduced momentum bound7.54995e-20Ns.
First contact is AFTER the20ms Hold end:transmission is nonzero but the current
control schedule has no pre-unload contact Hold. This is not proof that a
longer Hold will wrap;such a different input needs a separate common profile.

1555/1558/1561 continue actual contact through22.6ms;API/control/clocks and
ALL force-stage rows exact.1560 persistent suffix reproduces full checkpoint
tokens and stage rows exactly. Minimum1561 whole-stage gap−3.04965e-11mm,
momentum norm bound6.37823e-19Ns. Root continuous work remainsNULL.
Actual checkpoint113 and binary path/hash are in current STATUS/checkpoint.
1553 nonlinear endpoint transmission reconstructs Field coordinates within
7.09e-15mm;skin direct tendon force0,attachment net force/moment cancel to
1.23e-20N/6.69e-19Nmm. No inferred area/pressure/load capacity.

1559 8-step independent continuation FAILs depth5 after two completed
reference macros;actual for that horizon NOT RUN.1561 independently executes
ONLY the two qualified macros in actual SOFA.1563 passive attempt trace:
accepted state/force prefix exact,requery gap error0,observed115/3 edge and
117/6 face,min/max rejected stage gaps−9.54855e-8/+8.60380e-8mm.
Smallest tried h6.25us;depth/attempt/physical gates unchanged. This is NOT
OS exhaustion. Distinguish independent support birth from smooth transition.
1564 fails because the archived old-face analytic extrapolation was not an
old-edge law;failure preserved.1565 replaces it with qualified owned-edge
geometry/domain checks,without changing force/control/gates. Result must be
inspected before any actual transfer. No generic variational/RATTLE solver
has been implemented or certified by this work.

Caption erratum:1542/1554 correct geometry was labelled with hardcoded old
Fz−.001N.1556/1557/1562 read immutable actual Scene force0;OBJ hashes stay
identical.1562 additionally fits time/dt/condition caption inside the canvas.
Actual scale1 PNG/OBJ are not a prescribed wrap pose or pressure map.
All prior whole Time/Mesh/Energy/friction/clearance/grasp FAILs remain.

## Two distinct actual IVPs: unload30ms and stationary closing10ms —2026-11-19

Feature commit f16eecb introduces actual deformed lateral release and typed
FREE resume.1527 actual27.2..27.6ms API q/v EXACT;1530 suffix restart also
reproduces ALL free-stage rows and full checkpoint tokens exactly.
1531/1532/1534 extend SAME incoming-body IVP to accumulated
.02999999999999993s,original C2 unload endpoint.1544 final suffix restart
also has exact q/v/stages/full checkpoints. Tension is zero at the endpoint;
body separation is NOT stable holding or lifting. Minimum1534 force-stage
gap+.00306953867mm,momentum residual1.15516e-18Ns.
Latest actual incoming lateral checkpoint:
`results/autonomous_film_20261119_lateral_unload30_1534/three.checkpoint_150.txt`.
Build `build/lateral_free_20261119_lateral_free_actual1527/libReGripLateralRelease.so`,
SHA839f5b4e353273a6915a68275bcd480c18d4bb97193b7d3916b36060ffae49ba.
1529/1536 force inventory reconstructs actual Field positions within7.10e-15mm;
direct Skin tendon force0,attachment net force/moment cancel. Empty normal
force is justified by an explicit accepted empty Active Set,not missing-data0.
1537 actual scale1 curvature/OBJ:Skin max discrete width-mean curvature
.00248510/mm versus Rails .0134777/.0133246/mm. This is not recovery complete.

NEW stationary-body IVP: all initial film/body velocities0,external force0,
gravity0;same geometry/material/masses/route/C2. No incoming speed or copied
physical checkpoint.1538/1540 actual1.6ms,1541 actual10ms PASS strict API.
1539 default-mass reference velocity error3.06954e-12mm/s FAIL preserved.
1543 audit: ALL actual model sources,binary,states,free stages and six Field/
displacement CSV files BYTE-IDENTICAL before/after correcting only reference
public mass binding. Reference q/v error becomes0;threshold remains1e-12.
This demonstrates reference input consistency,NOT time convergence.
1535 missing reference sample API compile failure is preserved.

At the10ms first tension peak,actual contact is NONE on committed force
stages. Minimum stage gap+2.82860287e-5mm.1542 actual shape:Skin mean tip
localz−.02496365mm/root-tip angle.268336deg;Rail tips−.101584/−.100790mm,
angles2.33342/2.31376deg. Thus transmission is nonzero and delayed/unequal;
the initial peak does not demonstrate capture from rest. It also does not
prove eventual failure. Longer stationary-origin continuation requires the
new typed zero-load owner;do not use incoming-body schemas/force assumptions.
Its first step1545 is separate validation,not presumed PASS.

Stationary first-peak checkpoint:
`results/autonomous_film_20261119_lateral_stationary_peak_public1541/three.checkpoint_50.txt`.
Build `build/lateral_rest_20261119_lateral_stationary1535/libReGripLateralRestClosing.so`,
SHAf7505d0bd484a63996caef6af447750f425aa0e1fe26a19d5ac8e159c344089c.
The reused compiled1535 module was unqualified until actual1538/1540/1541;
its reference-only compile failure never counted as a physics PASS.
No friction/area/pressure/holding/lift/mesh/time/whole-energy certification.

## Actual lateral release and distributed joints —2026-11-19

Campaign1491/1494/1501/1509 extend the actual lateral six-mm-outboard
three-film/free-sphere system to accumulated .026999999999999948s.
All accepted q/v, micro-stage forces and clocks match independent references
exactly. This is not whole temporal convergence. The original, quadratic,
lateral and profiled route histories remain separate.

1506 rejects the next persistent-contact interval: the old material edge's
required normal reaction becomes negative. Unlike1470's new contact birth,
this is an all-row release candidate. Negative diagnostic forces are never
applied to the unilateral physical solution.
1513/1517 release32/64 FAIL normal-velocity bounds;1518 release128 reference
PASS. Actual1522 SOFA27.0..27.2ms PASS: q/v and all512 RK stage q/v/force,
times/weights/masks EXACT; minimum gap -1.55644386268e-11mm,
outgoing normal velocity +.0238153195854mm/s, sum-of-segment momentum
residual norm bound7.38835904289e-19Ns. This bound is not an independent
global vector balance. Runtime229.561s versus measured forecast373.707s,
under480s/4GiB. Contact-exit bracket is numerical admissibility, not an
exact continuous-time root. Whole time/energy/recovery/grasp remain BLOCKED.

Latest completed actual lateral checkpoint:
`results/autonomous_film_20261119_lateral_release_actual1522/three.checkpoint_136.txt`
Build `build/lateral_release_20261119_lateral_release_actual1522/libReGripLateralRelease.so`
SHA256 bf6a7f2f534c5635398ea03e8db34fa0124c5369b2f763b9633324cbb93ba9db.
Schema REGRIP_LATERAL_FREE_V1 explicitly preserves UNKNOWN edge birth history,
not an invented prior contact time. SDK unchanged /home/ubuntu/SOFA/v26.06.00.

1495 material-edge identity/force-kind audit: same state/time endpoint and
next initial normal multipliers differ by .138252736%, maximum1.73077e-8N.
Endpoint collocation and acceleration-constraint forces are distinct numerical
observables; no averaging or temporal PASS claim.1496 passive stage labels,
1497 purity: all old columns/state/Field/displacement/checkpoint physical
tokens EXACT.1499 actual25.2..26.0ms measured-micro partial inventory:
Wt5.300771107e-7Nmm, signed partial defect -5.59195501e-13Nmm,
normal work -9.04883e-24Nmm. Root work NULL, not heat or whole energy PASS.

Separate distributed attachment candidate1503/1504/1514/1515:
same core439.339791775mm3, materials, masses, root, route and no-object C2
input; root spring .001N/mm and FREE stiffness sum .004N/mm per rail preserved.
20 free attachment stations replace4 free clips. Adhesive/hardware mass and
volume NOT matched/modelled. Mode0 matches old lateral dynamics exactly.
Actual50ms mode2 matches independent states/stages exactly, NOT mesh/time PASS.

|50ms no-object metric|five clips/rail|distributed mode2|
|---|---:|---:|
|width-mean tip local z, mm|-.743267|-.834985|
|centre tip local z, mm|-.785108|-.699924|
|75mm centre arch local z, mm|+.372966|+.341182|
|transverse tip warp, mm|.0731253|.247774|
|root-tip width-mean angle, rad|.0643616|.0995159|
|tendon work, Nmm|.000149076386|.000140670528|

Mixed result: increased mean bending and reduced work do NOT establish
wrapping superiority; centre-tip bend decreases and tip warp increases.
1520 signed partial work defect2.86762e-11Nmm is not whole energy certification.
1521 actual scale1 equal-aspect surface PNG/SVG/OBJ;1524 VIRTUAL sphere overlay
finds sampled minimum gap -.0354185734mm. This overlay is NOT a contact-solved
trajectory, contact area or pressure.1523's legacy parameter label mistakenly
says mm; preserved, superseded by dimensionless typed1524 metadata.
Final design selection, stable holding/lifting, friction, self-collision,
full-thickness clearance,12-Wrench and Grasp Optuna remain BLOCKED/NOT RUN.

Reproduce completed release with a NEW tag:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/film_lateral_release_sofa.py --tag UNIQUE_RELEASE`
Typed lateral FREE continuation implementation is under separate validation;
do not feed this schema to the old quadratic FREE_V3 owner.

## Current actual lateral contact continuation to24.4ms —2026-11-18

Feature commit0c1d40d:bounded contact-admissibility reintegration and
isolated six-row birth,independent references AND actual SOFA.
1469/1472 actual controlled prefix through23.4ms has ALL micro-stage
q/v/force/time EXACT to reference.1475/1476 nonquadratic test exposed a
positive active-stage gap omission;1477 STRONGER two-sided active-stage
check passes circle analytic and sine independently-refined RK references.
1480 actual stronger-guard replay PASS,without changing accepted old prefix.
These are NOT general error-controlled time integration or whole energy PASS.

1470/1473 longer reference FAIL is124→117 NEW CONTACT BIRTH,not object
release. Rejected signed forces were NEVER applied or committed.
1478 isolated reference and1481 ACTUAL SOFA event at
.023503224464179916s PASS:6rows,3retained,impact loss4.54963e-12Nmm,
momentum1.05928e-20Ns,global angular balance4.34163e-24Nmm*s.
Actual q/v/event time/impulses EXACT. This is an externally isolated
numerical branch,NOT global earliest continuous-trajectory CCD.
1483 actual post-impact and1485/1486 continued to.024399999999999963s:
ALL micro stages/absolute clocks exact,gap−3.90123e-11mm,
momentum1.02815e-18Ns. Existing1458/1459/1460/1470/1473 FAILs preserved.
Latest COMPLETE actual lateral state:
results/autonomous_film_20261118_lateral_post_birth_four_actual1486/three.checkpoint_122.txt
Build:build/lateral_controlled_20261118_lateral_post_birth_actual1483/libReGripThreeFilmResume.so
SHA22bf301e5f55a1d5d8210164b3563512876f9d46cd7eb8d0698c2373ccab2731.
SDK /home/ubuntu/SOFA/v26.06.00,unchanged runner/ABI. Binary reuse1486
requires EXACT ALL-model source identity to qualified1483,not relaxed parity.

1487 actual endpoint force inventory:at24.4ms,T6.11425e-5N/rail,
direct Skin tendon force0,Attachment Skin power+.00164815Nmm/s,
Rail power−.00230185Nmm/s;Skin75vz+9.46331,Rail75vz+18.78199mm/s
(positive local z is AWAY from object). Thus coupling transmits energy,
but the observed deformation is NOT certified wrapping.
Nodal force norms are NOT resultant grasp capacity.
Attachment net-force/moment residuals<3.87e-20N/3.18e-18Nmm;
actual Field cable length error0. Root work/contact area/pressure remainNULL.
Actual scale1 PNG/OBJ1484/1488. No invented wrap pose.
Current profiled FREE50ms candidate remains unselected:more work AND worse
75mm arch. Original,quadratic,lateral and profiled histories remain separate.

Next bounded reference1490 is a NEW24.4ms IVP;inspect completed summary
before any actual continuation. If PASS,reproduce with unique actual tag:
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/film_lateral_controlled_sofa.py --tag UNIQUE --reference 20261118_lateral_after244_four1490 --parent 20261118_lateral_post_birth_four_actual1486 --reuse-build 20261118_lateral_post_birth_actual1483
No wrapping/holding/gravity lift,full time/mesh/energy,friction,selfcollision,
full thickness,mechanical equalizer,12-Wrench or final Optuna certification.
No OS/RAM/disk exhaustion is claimed;no automatic background restart.

## Latest completed transmission comparison and contact limit —2026-11-18

Feature0337fe2 lateral resume/actual energy diagnosis;bcd2de7 separate
distributed-profile route and actual short regression. No remote push.
Actual lateral coupled Hold1440/1447 passes to19.6ms;1448/1450 and
1451/1457 pass Unload through22.799999999999973ms:q/v/clock/normal force
EXACT to same-IVP reference,Field energy differences<3e-19Nmm.
Latest FULLY qualified lateral checkpoint:
results/autonomous_film_20261118_lateral_unload_next1451/three.checkpoint_114.txt
Same1420 DLL SHA526872e0d040f77b37b5f950c79b24dfc94d5b5cb9033311a1253ef395fb3dc3.
1458/1459 intended24.4ms horizon FAIL;only one accepted23ms prefix exists.
1461 verifies that prefix q/v/time/checkpoint EXACT,but does NOT certify
the failed horizon. At rejected23.1ms MID stage selected triangle124/face
gap−1.05835e-10mm,endpoint+1.97957e-11mm;normalv~1e-14,momentum5.93e-19Ns.
Same selected surface,not evidence of a missing triangle.1460 uniformhalf
reference also FAIL endpoint drift. No rejected state was committed.

1436 separate profiled route API PASS;1437/1438 and1442/1443 actual short
no-object dynamics PASS;1444 zero-profile versus original lateral6 EXACT.
1445 actual294step50ms PASS execution/API,NOT time convergence.
1454 SAME core/Tmax/C2:mean tip−.743267→−.761872mm;75mm centre upward
arch+.372966→+.399852mm;mid mean−.097787→−.134871mm.
1455 actual stage mechanical work.000167955009Nmm versus baseline1394
.000149076386Nmm (~12.7% MORE),not matched-work superiority.
1456 virtual fixed-sphere overlay on NO-OBJECT states has minimum buffer
gap−.0185480mm;NOT valid contact/wrapping solution. Wire centreline
gap+.263898mm does not certify finite wire/guide clearance.
Candidate NOT selected as a wrapping improvement.
Actual equal-aspect scale1 PNG/SVG/OBJ:
results/autonomous_film_20261118_profiled_surface50_1465/
Coordinate comparison1454 explicitly labels unequal-axis geometric ratio.

New EndpointControlledRows is isolated,never replaces old law silently.
It discards entire inadmissible uncommitted steps and reintegrates halves
using SAME forces/gates;NO q/v projection or fabricated reaction.
Only explicit endpoint-drift observation or returned whole-stage gap failure
admits subdivision. Release/ambiguous geometry/other errors propagate.
1463 unit-mass circle fixture FAIL line search;1464 dimensioned1g fixture
fails incorrect test expectation of endpoint rejection.1466 correct circle
test PASS:7stage rejections,15attempts,gap6.36e-11mm,analytic position
error3.58e-12mm. These failures remain preserved.
1467 same ACTUAL23ms-IVP independent one-macro reference PASS with
unchanged gates. Actual controlled-owner qualification is still separate;
do not claim general adaptive-time or whole-energy PASS.

No final wrapping/holding/gravity lift,friction,selfcollision,full-thickness,
whole time/mesh/energy,mechanical equalizer,12-Wrench or Optuna certified.
Original-route44.4ms,quadratic-route50ms,lateral22.8ms and profiled FREE50ms
are DIFFERENT histories and must not be spliced.
For an EXACT same-state short lateral replay inside known qualified history:
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/film_routed_resume_continue.py --tag UNIQUE --parent 20261118_lateral_unload_next1451 --checkpoint-step 110 --steps 4 --end-time .0228 --reuse-journal-rows

## Current lateral transmission/contact qualification —2026-11-18

Feature c369746 binds SAME objective6mm lateral cable to actual Field,
implicit force/tangent and active shared event path.1416 THREE real films
plus FREE Rigid3 reach10ms C2 peak,actual q/v/impulse/time EXACT to reference.
1420 persistent replay and1422/1426 transfers retain exact physical state,
quaternion/public clock/root/mass ownership.1428 actual Hold to
.011600000000000004s;1430 strict API comparison PASS:q/v/force/control error0,
stored/kinetic inventory difference4.7434e-20Nmm.
Gap minimum−3.62377e-13mm,momentum2.04578e-19Ns.
This is NOT actual holding capacity or wrapping certification.
Latest lateral checkpoint:
results/autonomous_film_20261118_lateral_hold_short1428/three.checkpoint_58.txt
Build:build/routed_resume_20261118_lateral_resume1420/libReGripThreeFilmResume.so
SHA526872e0d040f77b37b5f950c79b24dfc94d5b5cb9033311a1253ef395fb3dc3.
Prior lateral stage-work origin NULL;never splice quadratic-route work.
Actual scale1 geometry:results/autonomous_film_20261118_lateral_coupled_shape1425/.

1419 frozen REST actual-mass basis has lowest period5.297s,but is NOT an
actual nonlinear completion-time estimate.1427 complete-basis reconstruction
of actual50ms motion is exact;fast tip−.743267mm vs frozen-static−41.5368mm.
Actual response still includes positive75mm skin arch.1417 lower-load static
witness passes residual at9.375e-5N,but full-load1374/1376 FAIL remains;
virtual object penetration means static FREE branch is not contact solution.

1421/1423/1424 ACTUAL saved-state energy decomposition:100/50/25us cumulative
signed defects2.85848e-10/7.12760e-11/1.78801e-11Nmm are dominated by
potential-chord single-midpoint quadrature,not momentum/cancellation.
Momentum-energy terms~1e-19Nmm,chord4/8-point diagnostic errors~1e-18Nmm.
Diagnostic quadrature does NOT alter physical forces or time integration.
1411 relative-defect time FAIL remains FAIL;root work NULL,whole energy BLOCKED.
Slow40ms-ramp1404 is a DIFFERENT C2 input;less arch AND less bending,not
proven superior wrapping.1418 corrected unequal-axis chart captions preserve
original1406 evidence and explicitly report geometric exaggeration.

1431/1432 isolated quarter-guide profile [5.5,5,4.5,5,5.5]mm plus same6mm
outboard passes independent FD/objectivity/zero-profile parity. Initial wire
centreline gap+.366772mm,core unchanged,hardware mass/finite-wire clearance
unknown. Actual profile dynamics NOT RUN until separately qualified build.
No final grasp,lift,friction,selfcollision,full thickness/full time/mesh/energy,
mechanical equalizer,12-Wrench or Optuna certification.

Exact next bounded lateral continuation (new unique tag):
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/film_routed_resume_continue.py --tag UNIQUE --parent 20261118_lateral_hold_short1428 --checkpoint-step 58 --steps 8 --end-time .013200000000000008 --reuse-journal-rows
$PY tools/film_routed_hold_reference.py --tag UNIQUE_REF --parent 20261118_lateral_hold_short1428 --checkpoint-step 58 --qualification 20261118_lateral_hold_api1430 --reuse 20261118_lateral_hold_reference1429
$PY tools/film_routed_hold_api.py --tag UNIQUE_AUDIT --case UNIQUE --reference UNIQUE_REF
Do not extrapolate isolated/free trajectories into object holding.

## Actual50ms recovery and C2 transmission contrast:1392–1414

a5a9b88 actual FREE horizon/recovery;ba964e7 stage-work observer;prior
defd292 geometric certificate.1392 separate FREE endpoint limit50ms,
unchanged forces/control/counter,actual1393→31.6ms and1395 strict suffix
replay EXACT.1396 twelve bounded segments to.04999999999999981s.
1403 read-only audit of ALL joins verifies exact q/v/time/quaternion,
actual projected masses,root maps,full released-owner inventory,and all
actual Field inputs(error0). Rest reconstruction7.11e-15mm;independent
mass-based film K vs actual Field K error1.36e-19Nmm.
At50ms skin mean tip−.1623459mm,rails−.004106/−.001917mm,maxspeed42.5619mm/s,
body vz−1.379764mm/s,gap+.223084mm. Thus rail relaxation does not mean skin
has recovered. No retained contact or lift. Actual scale1PNG/OBJ1399,
time/energy curve1403.31.6..50ms signed defect3.325305e-8Nmm,root workNULL;
not heat or whole energy PASS.1396 chain is NOT full time convergence.
1402 initial read-only audit incorrectly included changing accumulated time
in invariant-tail comparison;corrected1403 validates time separately. No
physical state was changed and no failed dynamics was relabelled PASS.

1405/1408/1409 reuse original aligned observation method100/50/25us
on SAME actual31.6ms IVP,only declared copied numerical dt/provenance change.
ALL physical state/counter/control preserved. Actual q/v/time EXACT to
standalone reference,all11contexts. EXACT final32.4ms,not interpolation.
1411 overall endpoint time assessment FAIL:signed defect relative301.04%,
1498.69%,298.63%,while other physical/work observables ≤.0637656%.
Only final epoch common across ALL grids;not whole-stage time certification.
1414 independent80-digit quartic oscillator identity
DeltaE=k*qmid*(Deltaq)^3/4 explains why a midpoint truncation-error residual
can tend to zero with roughly300%/1500% relative comparisons. Existing
ReGrip FAIL remains FAIL;this example is not the sole actual cause proof.
V6 numerical-observation checkpoint RESUME NOT QUALIFIED.

40ms rise is a CONTROL CHANGE,not a numerical fix of the10ms-rise FAIL.
1398 build/API,1400/1401 short actual and1404 actual50ms pass strict
state/stage/public-clock/Field-control identity.1406 atsame50ms/sameTmax/core:
tip−.743267→−.444770mm,skin75centre+.372966→+.0783884mm,
angle.0643616→.0377583rad. Thus less adverse arch and less tip bending.
Actual stage work1394/1397 fast.0001490763855/.0001490763186Nmm;
1410 slow.0001462498350Nmm. Damping6.08725e-6→2.25232e-6Nmm.
No matched-work,hardware efficiency,holding or wrapping superiority claim.
1407 virtual fixed-sphere overlay still crosses buffer−.00204308mm;
NO-OBJECT motion is not a valid contact solution. Its wire centreline
min+.367377mm does not certify finite guide/body/wire clearance.

1412 new lateral implicit-stage FD gate passes.1413 actual THREE lateral
films and ONE FREE Rigid3 first bracketed event pass:event/state/impulse
EXACT,whole-stage gap−1.06581e-14mm,momentum7.27576e-19Ns,
normalv2.73602e-13mm/s. No contact law,mass,root orTmax alteration.
Active force/implicit/event-family/Field paths bind SAME lateral6;
unused general System::advance sensitivities are NOT qualified. Initial
incoming sphere−1mm/s,+.0001mm gap,gravity0/Fz−.001N:NOT grasp from rest.
1415 short coupled continuation must be inspected by completed summary.

## Additional actual dynamics and structural contrast:1336–1391

Implementation commits:df6748f(query-local identical-distance reuse),
60a0341(material-edge ownership/resume),32849a7(bounded actual release),
d766032(objective outboard route). Each experiment's immutable summary
stores compiled/generated source hashes,binary/SDK identity,commands and logs.

### Quadratic-route actual contact and release

1336 actual face→edge event25.34324085354ms;1341/1344 strict state and
accumulated-clock identity through27ms.1346/1347 longer runs fail stage
compression;1349 certifies ONLY accepted prefix through27.2ms.
1350 RK32/1352 RK64 fail existing1e-10mm/s stage normal-velocity criterion.
1354 independent circular-path witness shows O(dt²) intermediate RK stage
off-manifold velocity even from valid position/velocity/acceleration;it is
not proof of the sole cause in the full film.1355 existing RK128 micro-law
passes bounded gates.1360 ACTUAL SOFA same helper27.2→27.4ms:all512 stages
and final q/v/clock EXACT,all rows inactive,outgoing+.00052887956mm/s,
gap−5.11235498e-12mm,segment momentum norm bound7.71931727e-19Ns.
No velocity clamp,position projection,negative unilateral force or changed
stiffness. Local admission boundary is a collocation admissibility bracket,
NOT exact continuous contact exit. Global time/energy not certified.

1364 FREE runner configuration cap mismatch fails initialization;1365
corrected FREE fails surface-event budget512 before any accepted state.
Fixed-direction interval supporting-plane exclusion1370/1371 also fails
that algorithm budget;NOT OS exhaustion.1373/1375 reconstruct the actual
27.4ms IVP midpoint numerical path read-only.33 sampled gaps are positive,
but sampling is NOT CCD. First unresolved triangle116 needs tiny fixed-plane
intervals around fraction.00383 despite~6.56e-9mm pointwise gap.

`RotatingPlane.h` reuses outward-polynomial/Bernstein arithmetic to certify
time-dependent separating directions. Vertex direction r(t),edge direction
r(e·e)−e(r·e),or signed face cross product are geometric witnesses ONLY.
For every triangle vertex,certify N·r>0 and (N·r)²−R²(N·N)>0,plus N·N>0.
Strict outward bounds mean inconclusive intervals fall back/reject;no radius,
normal or gap tolerance modification.1369/1378/1380/1382 unit proofs include
middle-only collision,tangent rejection,curved face,edge and vertex witnesses.
1366 intentionally hit undefined zero-distance normal in an early test fixture;
1377 old test expected subdivision even when polynomial witness succeeded;
both preserved.1379 actual-IVP path now strictly excluded with984 plane
queries/12 subdivisions;NOT exact ODE motion claim.

1383 separate SDK-matched FREE DLL:
build/routed_separation_20261118_routed_rotating_build1383/libReGripThreeFilmRelease.so
SHA256103c1ef94696d82ba3b5c38f716e910d92d36b9bc7e8f705e9e322d54f93b0b3.
1385 actual27.4→28.2ms passes;1387 checkpoint139 resume suffix q/v=0
difference,ALL free-stage rows and complete checkpoint physical tokens EXACT.
1390 actual8steps extends to29.8ms;1391 bounded final Unload step PASS
at accumulated time.02999999999999993s,whole-stage minimum gap.00242127mm,
momentum1.02378e-18Ns. This completes C2 Unload on this route,not recovery.
No legacy sampled-work origin is reconstructed;no missing work is set to0.
Scale1 actual28.2ms PNG/OBJ:results/autonomous_film_20261118_routed_free_shape1389/.

### Outboard6mm route:interference and authority,not wrapping success

Keep5mm normal lever,add objective6mm outward rail-width offset. Same core
439.33979mm3,material,public mass,root and prescribed tension;guide hardware
mass/volume and finite radii remain UNKNOWN. Initial wire/arm centreline
R30gap+.370865mm vs original−2.607968mm,rest cable length200mm unchanged,
unit discrete closing-mode work9.75Nmm unchanged.1353 math/1356 actual
SOFA force/dForce/stiffness/objectivity/query-purity and Data guards pass.
1362 zero-offset actual q/v parity EXACT.1363 actual294-step50ms and1372
588-step50ms both complete with state/stage/control/API EXACT to standalone
same-kernel reference. This API parity is NOT independent physics convergence.

1367 comparison to completed original graded-plan1235 at294 EXACT epochs:
mean tip−.73835869→−.74326741mm,centre tip−.77704268→−.78510775mm,
root-tip3D angle.06392641→.06436158rad,centre75mm+.370615→+.372966mm.
The upward arch remains. No actual contact/holding advantage is shown.
1368 virtual fixed-sphere overlay:wire centreline min+.341364mm but
triangle buffered min−.0170890mm;the NO-OBJECT trajectory cannot be used as
a collision-resolved contact state. Actual contact/area/pressure remain NULL.
Scale1 comparison PNG in results/autonomous_film_20261118_lateral_hold_comparison1367/.

1384 ALL common epochs base/half FAIL centre-mid z at20.8ms:relative
.121871773%,absolute1.25791379e-11mm. Keep FAIL despite small absolute error.
1388 actual base/half/quarter local0..3.2ms ALL-pair observable PASS,
max.03712239%;not50ms/global contact certification.1386 full-quarter policy
forecast529.913s>480s:BLOCKED BEFORE physics,not OS exhaustion.1374/1376
static16/32-load-stage continuation fail60Newton budget at final load near
1.2e-12N floor;no final force-equilibrium or static wrap claim.

### Exact arithmetic reuse qualification

1351 opt-in query-local Q/H distance reuse only:2048 unit comparisons,
17 actual state force/Hessian/J/gap parity EXACT,9 physical CSVs byte-exact
and physical checkpoint tokens unchanged. Two opposite serial run orders
7.1587%/6.4588% reduction for bounded8step19.6..21.2ms only. Cache lifetime
one immutable query;no coordinate tolerance. Not adopted silently in current
release DLL. Do not combine with earlier journal-reuse speedup percentages.

1392 is a separate FREE-only horizon50ms build in progress;inspect final
summary before any build/actual claim. It adds only virtual endpoint limit,
not physical force/control changes or step-counter manipulation. Continue
only in bounded profiled chunks with exact physical checkpoint payload.

Whole energy/root work,full time/mesh,friction,selfcollision,full thickness,
mechanical equalizer,wrapping,holding,gravity lift,12-Wrench and final grasp
optimization remain BLOCKED/unqualified. Original-route44.4ms state and
new quadratic-route continuation are separate histories;never stitch them.

## Actual routed independent-contact birth:1327–1335

The124→117 switch was NOT merely an interchangeable triangle alias.
1325 existing FaceEdgeTransfer correctly rejected an independent birth
before the face-edge boundary.1327 existing detected-birth bracketing
failed because its FULL trial left the old face before root isolation.
New1328 uses existing exact physical feature6 expression analytically
continued ONLY for root bracketing. ALL accepted pre-event stages must
still have strictly positive physical-face barycentric coordinates. No
outside-face accepted force,normal clipping,velocity reset or gap projection.
Existing six-row Shared Mass/ManyRowImpact and post-contact law are reused.

1328 independent root:24.237106380844455ms,width9.31323e−14s,6rows/3retained,
minimum stage gap−1.45661e−13mm,linear balance5.88299e−21Ns,angular balance
1.08660e−25Nmm·s,impact loss1.13763088e−13Nmm. This externally isolated
symmetric branch is NOT global earliest CCD or general active-set contact.
1329 actual SOFA binds all routed forces/fields and this event header;
q/v/clock/event time/impulse EXACT versus1328. Public q/v/quaternion/mass/
root/contact payload is restored;only a copied provenance token changes.
New explicit200us24.2ms fixture replaces an old100us fixture ONLY in a
separate generated archive;original models and SDK remain unchanged.
Actual24.4ms checkpoint122 and scale1 actual PNG/OBJ1335 are preserved.
Old-row release is NOT complete object release or lifting success.

1330 preflight FAIL:noncanonical .. dependency key;NO physics child ran.
1332 handoff to old persistent DLL78ec827b uses SHA parity of actual .o.d
compiled model dependencies against new event archive,not broad assumptions
about all unused headers. Actual/reference longer26ms trials FAIL next
endpoint drift.1333 proves ONLY4accepted states through25.2ms q/v/time
EXACT;failed horizons remain FAIL.1334 tests existing FaceEdgeTransfer at
that new supplied checkpoint. Its old hardcoded24.2..24.4ms summary label
is a METADATA defect,not the actual25.2ms input clock;future runner records
header time/dt explicitly. Inspect final result before any success claim.

## Previous Hold/Unload,nonlinear transmission and branch diagnosis:1300–1326

1300 actual200us32-step13.2→19.6ms completes under measured277.6s forecast;
1301 same-IVP reference and1303 strict API q/v/time/normal-force EXACT.
1307 actual19.6→21.2ms C2 Unload begins;1310/1311 same strict identity,
endpoint T=9.856811008e−5N/rail from the ORIGINAL compiled C2 function.
No prescribed control equality is interpreted as mechanical equalization.

1302 observer compile FAIL (std::array addition);1304 read-only observer
FAIL exposed absolute-coordinate/displacement-input mismatch,NOT a solver
defect. Both preserved. Correct1309 uses actual displacement DOFs and
actual rest+u for moment inventory.96 actual endpoint samples:bond net
force<3.0e−20N,moment<1.61e−18Nmm;Skin direct cable force EXACT0.
1315 Unload inventory adds actual Field cable length equality EXACT.
At19.6ms finger0:rail75 tendonFz−1.89903e−5N,skin75 bondFz+5.50976e−5N,
skin75 meanVz+.86647mm/s,rail75 meanVz+12.1164mm/s;power/force directions
reflect nonlinear lag and elastic storage,not zero control authority.
Skin mean tip−.117741mm,centre tip−.198934mm,root-tip angle.0142212rad;
rail mean tip−.198934mm. These are actual small motions,NOT wrapping.
1306 actual scale1 OBJ/PNG;1314 force reconstruction:bodyFz+5.70371e−6N,
zero sphere-centre normal torque,rank3. External−.001N/gravity0 remains;
100g Earth weight.981N is an unrun reference,NOT certified holding load.

1316 connects measured0..21.2ms stage work through EXACT physical q/v/time
bridges:Wt=.000275939839188Nmm,D=8.54354e−6Nmm,impact9.38173e−10Nmm,
signed defect−3.61970e−12Nmm. Root workNULL/private sampled-workexcluded.

1312 actual longer Unload and1313 reference both FAIL at attempted24.4ms;
their15accepted states through24.2ms match EXACT.1317 same-IVP half-step
reference reduces preceding Gap drift but still FAILs near that transition.
1319 minimal rejected-step observer (no rejected commit):selected triangle
124/face6→117/face6 on all3fingers;mid gap−1.45847e−9mm,end+1.96782e−8mm.
The velocity constraint remains~1e−14mm/s while geometric position drifts.
This indicates a feature-transition issue;it is not proof that ALL time
errors have one cause.1322 separate constraint-defect local bisection uses
unchanged force/criteria,then encounters a negative stage reaction and
correctly FAILs rather than clipping or projecting. Existing FaceEdgeTransfer
is being connected in1325;its actual result must be inspected separately.

1318 separate public-context100us restart BEFORE animation preserves q/v,
quaternion,mass/root/contact payload;only a COPY's provenance token changes.
All11 Context clocks/dt change together;one-step Lobatto has no BDF history.
Actual16microsteps complete21.2..22.8ms.1320 q/v/time/force EXACT at8common
endpoints of FAILED1317's accepted prefix. Prefix proof is NOT completed
27.6ms time convergence. New HALF_V1 schema prevents silent dt mixing.
1323 unit-mass analytic circle FAILs existing absolute momentum/line-search;
separate1324 gram-scale analogue PASS does NOT erase unit-mass failure or
certify general mass scaling. No actual film stiffness,mass or tolerance changed.

## Previous continuation:1282–1299

Persistent new-route actual Hold now reaches13.2ms,checkpoint66 in1296.
1289/1296 run the unchanged .0001N/rail C2 Hold under gravity0,Fz−.001N;
1291/1299 standalone same-IVP state/API q/v/time/normal force EXACT.
Neither maintained tension nor contact is a demonstrated stable grasp.
1298 renders ACTUAL11.6ms geometry at scale1;reconstruction7.044e−15mm,
contact area/pressure/holding load remain NULL.

1295 compares ALL8 common macro endpoints and interval works for
200/100/50us references,all3pairs from actual saved10ms IVP. Maximum
relative errors:film q change1.66445e−7,velocity7.43032e−7,normal force
4.21748e−7,attachment energy4.53370e−7,interval tendon work1.87585e−6.
Normal-work numerical residual max relative35.01494(cumulative),67.54576
(interval) FAIL with no absolute exemption. Overall time FAIL retained.
No fine SOFA trajectory or full-cycle/mesh/whole-energy certification.

1294 links measured0..10ms inventory1276 to actual10..11.6ms stages with
EXACT initial q/v/time and zero energy-bridge error. Wt=.000113108803321Nmm,
impact loss9.38172884e−10Nmm,signed defect−3.28132097e−12Nmm. Root work
NULL;normal residual is NOT heat;private sampled-work was not restored
and is excluded. Raw/process/source/binary identities in campaign summaries.

1284 existing exact journal-row reuse:all9physical CSVs+4checkpoints
byte-identical,21.9921→14.3398s. Fresh serial pair1286/1288→1290:
16.5070→14.8398s (10.0998%). These separate observations vary;do NOT
generalize34.8% or combine with old free-recovery gains.1285 opt-in
inclusive profiling is passive per1287 bytewise proof.4 steps:coupled
18.2148s,stage14.8695s,geometry7.0631s,selected geometry5.1657s,
material F/H2.9142s. Nested timings MUST NOT be added;heap allocations
NOT MEASURED. Selected search is a candidate for separate exact-primal
optimization,not a reason to repeat rejected gradient-only RHS work.

## Current outcome and scope

Actual source starts atf70a46f. V12 integrity PASS19717 files;no preexisting
physics process. Separate single-film SOFA coupon isolates actuation from
object impact,using the SAME current material/geometry/root map/public nodal
mass/control. It is NOT a free-object/three-finger wrapping experiment.
Previous3-film38ms endpoint and all historical FAILs remain intact.

##1. Tendon→Rail→Attachment→Skin

Original Assembly.elements generates physical eccentric path forces from
T*dL/dq (five guides/rail). Coupling is ten objective point attachments,
not a rigid whole-surface tie or calibrated layer jamming.
At rest linearization,M*d2dq+C*ddq+K*dq=B*dT,withC=2M andB=-grad(L).
B_skin=0 does not imply no eventual control. For a step load and zero initial
perturbation,rail displacement starts atO(t²);throughK_skin,rail the skin
displacement starts atO(t⁴). For the actual C2 ramp beginning asO(t³),these
onsets change. Existing1136/1138 contact-reaction/three-mass tests remain
limited local analyses,not nonlinear transfer-time or actuator predictions.

##2. Actual nonlinear versus independent linear response

1141/1143 short actual API profile PASS;1144/1145/1146 same20ms endpoint,
100/50/25us,all q/v/time EXACT against nonlinear free-block reference.
Actual ForceField endpoint tension matches the common compiled C2 profile.
1139 FAIL was exact recomputed-vs-public nodal mass mismatch;use the archived
1002 mass on BOTH paths,not a relaxed identity test.1140 wrongly sought that
older mass entry in V12;correct immutable identity lives in V10.

1148 independent mass-scaled649-mode linearized midpoint model at rest:
nonlinear20ms displacement L2 difference7.8374266%,velocity12.4932183%.
This is MODEL linearization error,not proof of a Solver defect.
Minimum frozen omega1.1861257rad/s is not a dominant forced response or
nonlinear recovery time. The linear static skin tip prediction-41.5368mm
has large rotation and is not a validated nonlinear static equilibrium.

##3. Actual shape at20ms,baseline1144

|Quantity|Actual nonlinear result|
|---|---:|
|Skin width-mean tip z|-0.167328030mm|
|Skin centre tip z|-0.022899499mm|
|Skin width-mean midspan z|-0.000147723mm|
|Skin root-tip total tangent angle|0.02072185rad|
|Tip width z-warp|0.25434080mm|
|Left/right rail width-mean tip z|-0.28868749/-0.29114539mm|

The width-mean bend is not uniform skin conformation. Midspan motion is very
small and skin centre moves much less than edges. No object is present,so
continuous contact coverage,pressure andholding capacity areNULL/NOT RUN.
Curvature definitions:legacy signed xz tangent turning/chord-arc spacing;
additional3D total curvature uses atan2(norm(cross),dot)/mean chord length.
Centre and width-mean traces are separate. Analytic straight-line/discrete
circle metric checks pass in tests/test_transmission_shape.py.

##4. Force/work inventory,actual1152 observer

Read-only reconstruction at ALL200 actual accepted states;stored/kinetic
energy agrees with ForceField to4.07e-20Nmm. At20ms:attachment force norms
on Skin7.6080e-5N,on Rails5.9752e-5N;tendon force norm4.37328e-4N.
These are nodal-vector norms,NOT grasp resultants or holding capacities.
Attachment net-force residual2.40e-20N,net moment1.71e-19Nmm.
Stage-consistent midpoint tendon work1.00275627e-4Nmm,
damping work1.22364693e-6Nmm,signed energy defect1.02585e-10Nmm.
Root Work NULL;defect is not heat or full-energy certification.

##5. Time integration and computational cost

1153 midpoint100/50/25us ALL-pair endpoint Gate FAIL at0.1%:
max100→25 difference0.6291442%,50→25 difference0.1259985%.
Midspan displacement/curvature cannot be omitted as small absolute signals.
Separate Gauss order4 reuses EXACT constitutive force/Hessian and sameM,C,T.
1154/55 analytic errors1.4888e-7,9.3048e-9,5.8154e-10(~16x refinement),
nonlinear stage tangent FD8.38e-13.1156 short SOFA q/v/time/stages EXACT;
1157/58/59 actual20ms EXACT.1161 all-pair endpoint errors are0.00431148%,
0.00458128%,0.000269789% for200→100,200→50,100→50us:PASS0.1%.
This is ONLY the exact20ms free-coupon endpoint,not whole-trajectory,
contact,mesh or all-gripper time certification. Reference/actual runtimes
for1157/58/59 are31.83/36.73s,62.89/61.72s,114.99/135.56s respectively;
concurrent workloads differ,so no isolated speedup ratio is asserted.
Separate actual two-stage journal prevents applying midpoint work quadrature
to Gauss. No improvement in speed is claimed before wall-clock comparison.

##6. Structure candidates,one factor only

1150 changes onlyattachmentK:.001→.01N/mm,same material/volume/mass/route/T.
At20ms Skin mean tip-.170860635mm,centre-.030781645mm,width warp.248589499mm.
Some control reaches centre more efficiently,butthis does NOT certify wrapping
or stronger holding. Attachment stiffness is an assumed mechanism parameter,
not a fabricated material modulus or measured joint property.
1151 reverses guide offset+5→-5mm only;Skin mean tip changes sign to
+.166542595mm. The original sign drives towardnegative localz,where the
reference target sphere would lie;blindly reversing it does not improve wrap.
Comparison is fixedT/control/time/volume. Work is NOT constrained equal;work-
normalized observations must not be represented as matched-work trials.

##7. Nonlinear static attempts and alternatives

1147 fixed16 load stages and force-residual globalization fail atNewton60
before first accepted load. Small accepted steps~1/512..1/2048 suggest stiff
geometric strain/poor residual merit,not inability to bend under any load.
1149 physical constant-T potential Armijo reachesfirstload6.25e-6N,
force residual6.08e-13N,then fails nearsecondloadresidual1.11e-11N.
Potential differences approachroundoff;force Gate1e-12 stays unchanged.
1165 hybrid physical-potential/force-residual globalization PASS at16 loads,
maximum residual9.98265e-13N (unchanged1e-12N gate),runtime46.99s.
AtT=.0001N/rail:Skin mean tip-43.05871mm,centre-43.00656mm,
midspan-11.38046mm,root-tip angle0.827697rad;rail angle~0.9184rad.
Combined cable length190.06874mm versus200mm at rest. Thus the same structure
CAN have a substantially bent no-object force equilibrium,whereas20ms is
far from that equilibrium. This is an independent nonlinear static result,
NOT actual SOFA dynamics,stability,object wrapping,contact clearance or grasp.
1147/1149 failures remain preserved;no physical stiffness/damping was changed.

1164/66/67 independent38→44.4ms64/128/256-step all-pair endpoint subset
PASS in1173,max0.02999976%. Separate actual Owner1174 then passes first
8step API1176 and4step resume1177:q/v/time EXACT,field error0,checkpoint
bytes identical.1178 seven remaining actual V5 plans reach44.4ms.
1182 ALL64 actual q/v/time match preserved same-plan reference1134 EXACT.
Reference1118 lacks the `plans` clock mode:1181 rejected before integration;
that failure is preserved,not conflated with a physical Solver failure.
Independent common-end clock and actual eight-plan accumulated clock are
different numerical plans;no1e-12 bridge waiver or actual cross-grid time
certification is claimed. Original38ms Owner cap is unchanged;the new class
has a separately admitted44.4ms cap. All paths reject reimpact,not mask it.

##7b. Actual pulse energy and physical control hypothesis

1169 actual no-object Gauss250step50ms cycle API/stages/time EXACT;
reference78.76s,actual90.03s. Skin mean tip-.38082105mm,centre-.57327854mm,
midspan-.10098897mm,root-tip angle.03102525rad. Still moving,not recovered.
1175 actual shape/static comparison distinguishes those two result types.
1179 integrates ACTUAL two Gauss force stages (not midpoint interpolation):
tendon work.00012119183184Nmm,damping.00000771352625Nmm,
remaining stored+kinetic.00011347832209Nmm,signed defect1.64990e-11Nmm.
Root Work NULL;not whole-gripper energy certification.
1185 conditional energy analysis:the pulse injects23.2744% ofthe.000520708899
Nmm stored energy of1165's static configuration. With T=0 after30ms and
passive damping,merely extending this unloaded trajectory cannot reach THAT
configuration under the stated model. This does NOT prove all possible
lower-energy contact-guided wrapping configurations impossible.
1180 overlays those no-object static shapes with the ORIGINAL fixed sphere
using all320 triangles/ClosestPrimitive:maximum-load buffered gap-29.6233mm.
This is geometric infeasibility of an unconstrained shape,NOT a contact
Solver failure,wrapping or pressure measurement. Contact must be solved.
Therefore a longer same-Tmax HOLD is a separate next control-design test,
not a higher tension,stiffness repair or deletion of the old pulse result.
1183 bondK10x static trial FAIL atNewton60 nearstage15 (force~1.0184e-12N);
the unchanged1e-12N equilibrium gate is not waived.

##7c. Same-Tmax longer HOLD and initial-time failure

1186 adds a SEPARATE C2 input:release50..60ms instead of20..30ms,all other
material/mass/root/route/Tmax unchanged.1187/1189/1190/1199 actual50ms
Gauss250/125/500/1000step q/v/time/stages EXACT against their kernel reference.
1191 shared1.6ms prefix and1193 all250 original-pulse states/stages/time are
EXACT after the control refactor. Different control work is never labeled a
same-work structural comparison.
At50ms:Skin mean tip-.73835869mm,centre-.77704268mm,midspan-.09689811mm,
total root-tip angle.06392641rad;tip width warp.06800614mm. These are still
NO-OBJECT motions,not continuous wrapping or holding force.
1194 true-stage work.00014514548522Nmm,damping.00000601767193Nmm,
remaining stored+kinetic.00013912782191Nmm,signed defect8.61859e-12Nmm.
Combined cable shortening1.54554116mm,maximum1.87444198mm at36.8ms.
Tendon power becomes NEGATIVE while tension remains positive:the prescribed
load can absorb mechanical work during dynamic recoil. Not numerical heat,
motor electrical energy or a measured actuator/equalizer capability.
1200/1202 add attachment/tendon raw nodal-force norms at ACTUAL force stages;
old work columns remain byte-identical. Initial indirect response is not a
measured finite propagation dead-time.

1198 actual50ms400/200/100us all-pair FAIL:velocity error up to.26717137%.
1206 actual50ms200/100/50us all-pair endpoint PASS:max.00514502%,including
all recorded energy/shape/velocity quantities. This is NOT whole-time PASS.
1199 cost was calibrated from COMPLETE250/500-step same-input trials:
max seconds/step,+20% slowdown margin,+30s overhead=>469.92s/child forecast.
The hard limit remained480s/4GiB;actual reference304.14s,SOFA240.37s.
No900s exception or OS exhaustion. This is not an isolated speedup benchmark.

1204 exact accepted0.8ms comparison (NO interpolation) remains FAIL.
At200→100us:q L2.040475%,v.072873%,butSkin mean tip.502295%
(absolute1.42569e-11mm),Skin midspan18.5355% (absolute1.87146e-16mm).
Tiny absolute differences are recorded,not waived.400→100us bulk q/v also
FAIL(.669357%/1.050982%).1201 frozen-REST modal projection puts96.34% of
400→100us velocity error mass-norm² in10⁴..10⁵rad/s;this is NOT a measured
nonlinear spectrum or proof of a sole error source.
1205 generated long-double FORCE oracle freezes original input geometry and
lifts actual double q without invented digits. At0.8ms attachment force
difference2.66600e-17N L2 (~4.63690e-7%),shell1.57683e-21N.
It is not an extended-precision trajectory and cannot excuse the time FAIL.
Both AD force variants use a common long-double accumulation in this oracle;
it does not measure the production double summation path separately.
Next distinguish the absolute Newton residual floor from timestep error.

##7d. Independent startup references and localized refinement

1207 default Newton1e-18 reproduces the SAME reference binary SHA as1186
and all actual0.8ms q/v EXACT.1208/1209 tighten only Newton to1e-20/1e-22:
complete,butmean Skin tip changes~8e-21mm,far below100us timestep error.
This tests that100us endpoint,not every future step/tolerance regime.
Production default/momentum gates unchanged;compile-time probe can only
tighten,never relax1e-18. No tighter setting is silently adopted in SOFA.

1214/1215/1219 independent continuous frozen-rest LINEAR response uses
adaptive DOP853 and an archived compiled ControlProfile::evaluate shared
library—not a Python C2 copy.1220 all-pair rtol1e-8/10/12 endpoint reference
check PASS,max2.20e-9%. Finite double-precision adaptive reference,NOT an
analytic/nonlinear SOFA solution. At0.8ms continuous linear Skin mean tip
-2.839278285e-9mm,midspan1.021588669e-15mm.1203 nonlinear100us differs in
bulk q/v by.00284231%/.00647355%;cross-model discrepancy is not solely
integration error. rtol1e-12 costs748877 RHS calls/27.76s versus3965/.504s
at1e-10:do not blindly tighten production solver tolerances.
1210/11 tooling FAIL:archived worker missed helper import;1212/13 FAIL:
incomplete helper dependency closure. No ODE trajectory was produced there.
All failed folders/stderr are preserved,not labeled physics/OS failures.

1216/17/18 ACTUAL SOFA localized0.8ms32/64/128step tests use the explicitly
archived1186 default model/DLL/reference,with ALL source/build/input and
binary hash guards intact. New live Newton experiments do not silently
change the archived tested physical model. All q/v/time/stage/API EXACT.
1221 all-pair25/12.5/6.25us onset endpoint PASS:max.0271423%,including tiny
Skin metrics;1204 coarse onset FAIL is preserved. This supports testing a
new localized-refinement numerical plan,NOT declaring whole50ms time PASS.
Intermediate physical epochs and contact/moving-object dynamics still
require independent qualification;fixed two-window outcomes cannot replace
all-time validation. No physical stiffness,damping,Tmax or gate was changed.

##7e. Explicit public-clock step-expansion experiments

New FilmTransmissionPlanODE schedules NEXT public dt at every accepted
endpoint;it never changes physical time,q orv to align output. All4 child
contexts are checked. Standalone variable-plan reference uses the SAME
endpoints,actual force stages and unchanged default Gauss/Newton law.
This is a deterministic numerical-plan experiment,NOT error-controlled
adaptive integration or a contact integrator. Unit plan-clock/count tests PASS.
1222 actual8step profile API/stages/time EXACT.1223–25 one fine0.8ms epoch
then8x expansion FAIL at1.6ms(max1.05571%,1226),not extended blindly to50ms.
1227–29 two fine epochs passall4 canonical epochs through3.2ms,max.0712951%
(1230).1231–33 graded25→50→100→200us (scaledby1/2,1/4) passall4 epochs
through3.2ms,max.0271423% atfirstepoch and.00985773% at3.2ms(1234).
1235/1237 actual graded50ms294/588steps are API/stages/time EXACT.
1239 quarter1176-step run is pending at this checkpoint:NOT a time PASS.
Only after completed all-pair ALL canonical-epoch assessment may its sampled
trajectory be called converged;continuous-time/contact/mesh remain separate.

##7f. Shape and wire-route limitations,not just Solver error

1236 ACTUAL no-object Hold snapshots:material x=75mm Skin centre arches
towardpositive localz,+.37061522mm at50ms,whilemean tipmovesnegative.
Whole320-triangle virtual-fixed-sphere overlay haspositivegap.36598062mm.
This is NOT contact-solved dynamics,butshows whytip motion alone cannot
demonstrate wrapping. The earlier moving-contact model must be evaluated
independently rather than copying this virtual geometry as actual contact.

1238 independent wire/guide preflight uses ORIGINAL guide kinematics and
the ORIGINAL initial R30 sphere/50mm mount geometry. Existing constant5mm
offset cable CENTRELINE gap is-2.60796821mm. Earlier whole-TRIANGLE tests
do not cover wire collision. Baseline physical-route clearance FAIL remains
even if its skin/rail triangle constraints pass. No wire reaction was modeled.
Constant2mm offset hascentrelinegap+.14852245mm;quadratic material-coordinate
offset e(s)=5-4.5*4s(1-s) has+.26020791mm andcombinedlength201.00833432mm.
These are mathematical path candidates,NOT actual SOFA candidate dynamics.
Finite wire radius and guide bodies are unmodeled;no full clearance or
manufacturability PASS. Box/other object geometries are not covered.
Core skin/rail volume staysfixed,buttotalguide/wiremass/volume isUNMEASURED.
Preflight SAME force/Hessian/objectivity/wrench gates as existing kernel tests
PASS;baseline force/H matches original EXACT. Quadratic route creates
negative-z station forceatx75 (-.17247749N/N unit multiplier),whereconstant
routeinitialstationforceis0. This motivates testing distributed loading,
not increasing tension. Unit multiplier isNOT1N actualactuation.
Next:shared route kernel→independent regression→distinct actual ForceField/
Owner API→same-Tmax dynamics→wire/triangle clearance→coupled contact.
No final structure orholding advantage isselected from preflight geometry.

1192 inherited RAW/build/SDK byte preservation PASS19096 files,no changes.
Evolving live sources/reports are separately versioned,not falsely called
unchanged by the oldV12 ledger. Old manifests themselves remain untouched.

##8. Remaining contact/grasp/design boundaries

Existing1133 frictionless sphere normals have zero centre torque andwrench
rank3. No12-wrench holding certificate,measured friction or gravity lift.
Singlecoupon proves a transmission response exists,not full-surface wrapping.
The old3-finger geometry is rectangular with50mm roots,not tapered artwork;
thickness clearance,self-contact,mechanical equalizer/general friction and
all-gripper time/energy/mesh remain unqualified. Final design/Optuna BLOCKED.

## 8a. Local public-clock time verification and cable interference (1238–1247)

1239 completed1176 steps to50ms,reference327.53s/actual324.68s,below480s.
1235/1237/1239 share EXACT63 canonical physical times;1241 tests ALL pairs at
ALL63 times including tiny shape/energy signals:PASS,max0.0271422922% vs0.1%.
No interpolation/no tolerance relaxation. This is a NO-OBJECT coupon and exact
sampled-epoch qualification,not all-time/contact/mesh/global-energy certification.
The graded local plan is deterministic,NOT an error-controlled adaptive solver.

1238 exposed a separate MECHANICAL defect:original5mm-offset wire centerline
intersects the initially overlaid R30sphere by2.60796821mm. Existing triangle
contact does not model cable collision. Constant2mm and quadratic variable
offset give initial centerline clearances0.14852245/0.26020791mm respectively.
These are NOT finite-wire/guide-body clearance proofs. Preserve old contact
results with their actual triangle-only scope;do not fabricate wire reaction.

Implemented separate generated FilmRoutedTendon+FilmRoutedPlanODE,unchanged
Assembly layout and original Field/mappings/SDK. e(s)=5-18s(1-s)mm;five guides
per rail;only route changes,core material/mass/root/C2 unchanged. The cable is
1.00833432mm longer at rest. Actual cable virtual-work loads distributed Rails;
Skin is still indirectly driven. Source/generator/binary hashes archived1240.
1240 full independent mechanics and actual SOFA Force/dForce/matrix/query-purity
APIs PASS for amplitude0/4.5. Runtime geometry mutation rejected.
1242/1243 actual8step XML runs PASS:q/v/time/stages EXACT,all4 contexts exact,
actual ForceField tension equals solver input.1246 amplitude0 preserves old
1222 q/v EXACT.1245 plot KeyError failure preserved;fixed output1246,new tag.
1244 is the actual50ms quadratic-route experiment;only its completed summary
may be used to report a result. No claim of wrapping/holding/lift from profiles.

New routed sources:models/film_routed_tendon;generator:film_routed_generate.py.
Reusable DLL:build/film_routed_20261118_routed_math_api1240/libReGripFilmRoutedTransmission.so
SHA256:0b5606781a4a8b21369e25d572d4a5ff1f4490c24d95cb32ed17fc0ac930e1e1.
Raw:results/autonomous_film_20261118_routed_*1240..1247.
Wire finite radius/guide body/mass/friction/self-contact and matched-work
comparison remain unqualified. No full energy/time/grasp certification.

## 8b. Distributed-route actual result and rejected superiority claim (1244–1257)

1244 actual50ms294-step route experiment completed (SOFA84.111s,reference
94.351s);q/v,time,all4 contexts,all588 force stages and applied tension EXACT.
1248 half-step588 completed (SOFA191.713s,reference180.857s),same exact checks.
1256 compares ALL63 common epochs;the two-resolution pair passes0.1% at each,
but the overall qualification is BLOCKED because quarter-resolution is missing.
1255 predicted1176-step cost490.111s>480s;child was NOT started. This is policy
cost blocking,NOT OS exhaustion.1257 tests a smaller3.2ms quarter-step prefix;
do not claim whole50ms convergence from that local check.

Same T=.0001N/rail,core volume/mass,geometry/root,Hold profile and time plan:

| Actual50ms observable | Existing route1235 | Quadratic route1244 |
|---|---:|---:|
| Skin width-mean tip z,mm | −0.73835869 | −0.39959346 |
| Skin centre tip z,mm | −0.77704268 | −0.50766937 |
| Skin centre75mm z,mm | +0.37061522 | +0.25384502 |
| Skin3D root-tip angle,rad | 0.06392641 | 0.03122251 |
| Skin max3D curvature,1/mm | 0.00537055 | 0.00372507 |

Positive localz is AWAY from the initial sphere. Both tips close but material
75mm arches away by50ms. This is NOT a wrapping improvement.1249 actual-scale1
figure:results/autonomous_film_20261118_routed_shape_full1249/actual_route_comparison.png.
The new route fixes one initial centerline interference issue while reducing
effective bending. No final design selection or holding superiority follows.

1250/1253 actual Gauss-stage work uses the NEW route's length gradient,not the
old cable formula:Wt=.000115662469493Nmm,Wdamp=4.176548332e-6Nmm,
stored+K=.000111485923419Nmm,signed defect−2.25801222e-12Nmm,NOT heat.
Mechanical/electrical actuator work and root reaction work remain distinct;
root work NULL.1254 additional station-force instrumentation preserves ALL
old work/force columns EXACT. At material75mm the rail tendonFz remains
negative(−2.48070e-5..−2.54132e-14N),but skin attachmentFz changes sign
(−3.82352e-5..+1.13226e-4N). This verifies a NONLINEAR delayed force response,
not zero control authority or a measured contact reaction.588 actual stages.
Actual response figure:results/autonomous_film_20261118_routed_force_response1254/actual_transmission_response.png.

1251 virtual original FIXED sphere overlay of actual NO-OBJECT states:
wire centerline min+.20303917mm;triangle buffered gap min−.02185858mm at
27.6ms (6/320triangles). At50ms triangle gap+.250878mm and wiregap+.376977mm.
The obstacle was not in the equations:these are geometric feasibility checks,
NOT actual contact forces,contact-solver failure,contact area or CCD proof.
Finite cable thickness/guide body clearance and moving-object contact untested.

1252 independent16-stage static Newton continuation at unchanged Tmax passes
force gate1e-12N(max endpoint residual3.49951e-13N);same globalization as1165.
New-route equilibrium skin tip−19.965055mm,centre−19.931113mm,root-tipangle
.31147494rad,stored energy.000146408118Nmm. Existing-route1165:−43.05871mm,
.82769689rad,.000520708899Nmm. No-object statics,NOT SOFA,stability/contact
or dynamic arrival certification. Actual50ms is still FAR from either equilibrium.
No external friction/material/actuator data were invented;core material assumptions
and incomplete thickness/self-contact/general-friction/whole-energy gates remain.

Next priorities:qualify routed local time prefix;eliminate redundant zero-tension
cable AD only with exact physical parity and measured wall-clock benefit,or use
an independently qualified persistent one-step continuation. Then adapt the
coupled event/contact FORCE callback to the NEW route and verify all owner/field
queries use it. Merely loading the new Field beside an old-route contact owner
would be physically inconsistent and is NOT permitted. Full-surface finite
thickness/cable/guide clearance needs its own physical geometry specification.

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/film_routed_run.py --tag UNIQUE_LOCAL --amplitude 4.5 --duration .0032 --refinement 4 --profile 20261118_routed_candidate_half1248
$PY tools/film_transmission_plan_assess.py --tag UNIQUE_PREFIX --until .0032 --cases 20261118_routed_candidate_full1244 20261118_routed_candidate_half1248 20261118_routed_quarter_local1257
```

Do not repeat completed runs just to recreate plots. All original failures,
quarter budget block1255 and failed plot1245 are preserved. No automatic restart.

## 8c. Local qualification and explicit rejected performance claim (1258–1264)

1259 three-resolution NO-OBJECT initial0..3.2ms prefix ALL4 exact canonical
epochs PASS,maximum0.00494009%. It does not remove1255 full50ms quarter
policy block or certify actual contact.1256 remains overall BLOCKED despite
its two-resolution63-epoch pair passing. No adjacent-only substitution.

1258 guarded opt-in generated-core specialization omits only eight discarded
zero-tension baseline cable AD terms. Original shell/attachment/contact body
is extracted verbatim,not rederived;original Kernel/Assembly layout/SDK unchanged.
Unit source tests verify original bytes and reject generated-output overwrite.
This variant removes an extraneous baseline-cable degeneracy rejection;it does
NOT certify arbitrary folded/self-contact states. Default variant unchanged.
1258 independent math and ACTUAL SOFA APIs PASS;1260 actual profile EXACT.
1261 actual50ms294-step run and1264 regression:ALL actual state,stage,clock,
ForceField energy/work,displacement,plan and mass CSV bytes IDENTICAL to1244.
All compiled source changes are restricted to generated Core/Route headers.

Measured reference94.351→92.184s(−2.30%),SOFA84.111→89.054s(+5.88%).
Therefore **NOT ADOPTED as a speed improvement**. This is a measured mixed
result,not an operation-count success. Concurrent scheduling/no repeat timing
prevents a robust speed claim.1263 is the same optional variant's588-step
study;its completed summary is required before reporting a result. No policy
limit or physics tolerance was changed;old failed/rejected approaches retained.

## 8d. Actual NEW route coupled3-finger integration (1265–1281)

1265 mechanical-stage adapter passes:amplitude0 old potential/gradient/Hessian
EXACT;tangent FD1.84714e-18,potential FD7.23489e-17,tension derivative9.19031e-16.
Actual separate generated source binds the SAME route to SharedFilmSystem force,
pre-event mechanical solve,event-family derivative and actual FilmRoutedTendon.
Original live contact/film owners are NOT modified. Generated class names are
Routed-prefixed.1268 standalone reference passed but module compile failed:
renaming also changed an include filename;failure retained.1269 fixes symbol-only
renaming and reuses completed reference with all compiled headers unchanged.

1269 actual200us first event+remainder PASS:event time9.996003594715e-5s,
18 rows/rank3,world impulse balance8.85621e-21Ns,angular1.76651e-23Nmm·s,
impact loss9.38172884e-10Nmm. Actual event/pre/post/end/impulses EXACT to
standalone SHARED-KERNEL reference. This is API/state integration consistency,
not an independently different physical model or a global earliest-CCD proof.
1270 actual8steps1.6ms PASS:q/v/accumulated time EXACT,whole-stage triangle
gap−1.06581e-14mm,momentum8.33581e-20Ns,normal velocity2.74800e-13mm/s.

1272 actual50steps to10ms first C2 peak PASS:same strict API/clock agreement
at ALL50 steps. Actual197.659s/reference162.095s,forecast319.077s,480s hard
unchanged. Whole-stage min gap−5.61329e-13mm. Same original pulse,NOT the
separate longer-Hold no-object input. Incoming sphere v_z−1mm/s,gravity0,
externalFz−.001N is NOT stationary capture or gravity lift.
1275 identical actual per-finger tension at all50 common epochs;finger0:

| Actual10ms | Original1002 | Quadratic1272 |
|---|---:|---:|
| Skin width-mean tip z,mm | −0.02496388 | −0.02057746 |
| Skin centre tip z,mm | +0.00066215 | +0.00055553 |
| Skin75mm width-mean z,mm | +0.00077955 | −0.00118854 |
| Skin3D root-tip angle,rad | 0.00468336 | 0.00385599 |
| Object v_z,mm/s | −1.07909233 | −1.07909782 |

Small material75mm sign improvement is NOT full wrapping/contact coverage.
Centre and width-mean tip move differently;body continues downward,NOT holding.
No pressure/contact-area/holding capacity derived from three selected rows.

1274/1276 OFFLINE actual new-route stage work includes the COMPLETE first
free/impact/remainder and every subsequent Lobatto stage;old constant-offset
observer is deliberately NOT reused unchanged.1273 wrong stage-clock preflight
(end-minus-begin vs actual used dt) rejected before integration;failure retained.
Corrected observer uses declared used dt AND exact accumulated-time equality;
no clock tolerance widening.1276 first10ms measured Wt8.6968197364e-5Nmm,
Wext1.0396800791e-5,Wdamp2.5097544259e-6,Wnormal−4.2843092257e-24,
plasticImpactLoss9.3817288366e-10,signed defect−3.2796883876e-12Nmm.
Actual field energy error6.77626e-20Nmm,tension/length errors0. Root workNULL.
Signed defect is NOT heat;relative tiny normal-work residual is NOT waived;
full energy/time/contact/mesh certification remains BLOCKED/NOT RUN here.

1277 ACTUAL moving-sphere geometry at612 accepted/recorded-stage film samples:
all320triangles per sample,minimum buffered gap−5.61329e-13mm;wire centerline
minimum+.23067080mm. This is no longer a virtual fixed-sphere overlay. Still
NOT finite-wire/guide-body/full-thickness or continuous-time clearance proof.
1281 uses saved actual geometry at scale1;surface colors are finger IDs,not
pressure,wire not rendered. No fabricated wrap pose.

1278 separate route-bound checkpoint replay40→44 PASS:q/v/time/ALL stage
rows and actual field values(excluding legacy work) EXACT. Magic is NEW
REGRIP_ROUTED_PERSISTENT_V1;token binds amplitude4.5,source,binary and actual
parent1272. NO old-route checkpoint transplanted. Quaternion exporter permits
ONLY this proven zero-spin history;actual C++ snapshots save public quaternion.
1279 actual checkpoint44→48 retransfer PASS:q/v/time/stage rows EXACT.
Legacy Field length/T/work history is NOT restored;exclude sampled-work from
splicing. Stage-work physical origin and preceding1276 inventory are separate.
1280 is the next two-step replay to known peak;use completed summary only.

Reusable event DLL:build/routed_coupled_20261118_routed_coupled_event1269/libReGripThreeFilmEvent.so
SHA:a21639f13140bc1e1d4244928e2dbdc100fd5b57ca165dfba7d8b62ff5eae176.
Reusable resume DLL:build/routed_resume_20261118_routed_resume1278/libReGripThreeFilmResume.so
SHA:78ec827b1136f2dc91a4a31ebd129c924af5def52a43e1b4842f0ee77ce717cf.
All geometry/material values remain research assumptions(E250MPa,nu0,
skin.05mm,rails.1mm,100mm,50mm roots,1g/finger,100g sphere,R30mm).
Actual friction,self-contact,guide hardware,full thickness,equalizer,gravity
lift and final design/Optuna remain unqualified. Old fixed-route endpoint44.4ms
and new-route10ms are DIFFERENT models/checkpoints,not one stitched trajectory.

##9. Reproduction and artifacts

Raw:results/autonomous_film_20261118_transmission_*1139..1168/ (each own
source snapshots,binaries,SDK/ldd,commands,exit status,actual CSV).
Actual Figure:results/autonomous_film_20261118_transmission_linear1148/actual_vs_linear.png.
Reusable baseline DLL:build/film_transmission_20261118_transmission_common_profile1143/libReGripFilmTransmission.so.
Reusable Gauss DLL:build/film_transmission_20261118_transmission_gauss_profile1156/libReGripFilmTransmission.so.
All children4GiB/480s;first8stepprofile before longer runs;max4 simultaneous.

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/film_transmission_run.py --tag UNIQUE --steps 200 --duration .02 --common --scheme gauss --reuse 20261118_transmission_gauss_profile1156
```

Run only with a NEW tag andmatching archived/current compiled source guard.
Existing runs need not be repeated.
The next research report update must replace pending status only after actual
completion. No automatic post-session continuation is provided.
