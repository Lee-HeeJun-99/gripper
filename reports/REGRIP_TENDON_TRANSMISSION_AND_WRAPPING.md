# ReGrip tendon transmission and wrapping research —2026-11-18

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
