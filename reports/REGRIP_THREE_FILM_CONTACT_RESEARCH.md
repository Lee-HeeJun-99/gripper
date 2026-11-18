# Three-film/shared FREE sphere — actual narrow contact,through851

## Latest completed1134–1138 — exact chain and transmission/energy diagnostics

1134 independent same-plan reference matches ALL64 actual31.6..38ms q/v
and accumulated times EXACT. The different-plan endpoint clock comparison
(1.38778e-17s,velocity4.05720e-11mm/s) is NOT waived under1e-12 API gate.

1135/1136 use actual20ms q/v,public mass and root mapping without integrating
or applying signed diagnostic forces to SOFA. Frozen tendon-force affine
error8.32728e-20N;unit-force norm3.92120469 acts on Rails,unit Skin force0,
direct normal acceleration gain0. The local zero-velocity linearized delayed
reaction second-time-derivative gain norm is7.96365944/s². This does NOT mean
zero eventual control authority,nor establish nonlinear response time or
required actuator force.1138 verifies the delayed-response formula against
an independent analytic three-mass model (second-order Taylor convergence).
Larger tensions/body-only loads in1135/36 are FROZEN sensitivity inputs,
NOT new actual grasp trials,gravity simulation,or repairs of old FAILs.

1137 reconstructs192 ACTUAL FREE recovery stages31.6..38ms. Stage weights sum
EXACTLY to actual elapsed0.006400000000000017s. Actual ForceField energy error
2.71051e-19Nmm;Wt=0 (actual T0),Wext=8.11563637e-6Nmm,
Wdamp=6.25963299e-6Nmm,delta(stored+K)=1.86086141e-6Nmm.
Signed defect=+4.85802552e-9Nmm,NOT heat. Root Work NULL.
Relative to measured energy change,this defect is about0.261% (diagnostic
normalization,NOT a new acceptance criterion). Whole energy remains BLOCKED.

Current actual endpoint remains38ms/checkpoint280. No holding,lifting,
completed recovery,friction,mechanical equalizer or final design certification.
No OS/RAM exhaustion or child timeout caused these results. No automatic
post-session process/restart is provided. Next development should investigate
delayed Rail→Attachment→Skin control response and error-controlled longer
physical-time integration,not merely increase tension or delete38ms bounds.

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


## Actual repeated contact and time gate — newest through868

ThreeFilmPersistentODE now supports a guarded REST-initialized100us window,
<=32 actual macro steps,not only ONE step. It reads and propagates actual mapped
states/public masses each step;REST checks are applied only at the initial state.
No hidden reset/clamp/velocity projection was added. Native/Event owners preserved.

Independent4/8/16 grids852/853/854 COMPLETE but strict time855 FAIL:
U_rails4→16 relative0.1442388023%,absolute3.84916725761e-37Nmm;reference
2.66860733406e-34Nmm. The small energy is NOT ignored or rounded to zero.
Observed coarse order3.91019. Frozen symmetric out-of-plane209-DOF reference856
has a common free-body mass term m/(n_z^2)j*j^T and three-film stiffness/mass.
It omits nonlinear geometry and is NOT a full nonlinear/SOFA reference. Modal
constant-force and Lobatto solutions reproduce the rail trend(order3.88108),
frozen-to-nonlinear energy differences1.78e-5/2.54e-5/2.78e-5 relative in858.
This supports temporal rail dynamics,not contact-event timing,for this coupon.

Measured16-grid64.4923325510s;the32-grid forecast257.969330204s was recorded
by857 and stayed<480s,actual32-grid83.1384s. Only the allowed GRID count changed;
Newton budgets/tolerances/materials/physical duration unchanged. Assessment859
verifies model hashes and exact UniformContact.cpp equality after normalizing
ONLY the known4/8/16→4/8/16/32 budget/error-string edit. All other edits reject.
New independent8/16/32 PASS does not change old4/8/16 FAIL.

Actual860/861/862 use ONE DLL and identical physical XML exceptdt/count/output
paths. Public three-film/freely moving body masses are used,not three separate
fixed-object tests. Runtimes32.3713/70.6831/127.0043s. Actual versus independent
all-macro q/v discrepancies<6.5e-18. Actual partial-energy observers864–866
evaluate actual accepted and stage states,checking FF totals<8e-31Nmm. They
separate skin/rails/attachment/film and rigid kinetic energies,external/damping/
contact work. Tendon work0 is a VERIFIED T0 input,not a missing term filled0.
Root reaction work remains an ideal fixed-root assumption,not measured.
Signed residuals≈3e-27 to9e-27Nmm are NOT physical heat/full energy certification.

Actual867 passes all-pair0.1% time on listed observables:

|actual grid comparison|separate rail energy relative difference|
|---|---:|
|8→16|0.00899563138%|
|8→32|0.0101266755%|
|16→32|0.00113094238%|

Actual32-stage/used-J/FF/whole-surface audit868 PASS:minimum world-stage buffer
gap-1.77636e-14mm;unit-row action/reaction2.29e-16,moment1.68e-14mm.
Full3finger wrapping/grasp/torque/friction/thickness/energy certification is NOT
claimed. Current rows are one unique closest patch per finger;true independent
ties/release still reject. Fixed9-row-per-macro journal ordering/time is checked
for this schema,not presented as general lifetime tracking.

Reusable actual repeated build:
build/three_film_20261117_three_film_actual8_860/libReGripThreeFilmContact.so
Last prior functional commitc971225;this repeated-window unit follows it.

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY -m json.tool results/autonomous_film_20261117_three_film_actual_time867/summary.json
$PY -m json.tool results/autonomous_film_20261117_three_film_actual32_audit868/summary.json
$PY tools/film_three_film_audit.py --tag UNIQUE_REPEAT_AUDIT --case 20261117_three_film_actual32_862
$PY tools/film_three_film_actual_time.py --tag UNIQUE_ACTUAL_TIME --cases 20261117_three_film_actual8_860 20261117_three_film_actual16_861 20261117_three_film_actual32_862 --energies 20261117_three_film_actual_energy864 20261117_three_film_actual_energy865 20261117_three_film_actual_energy866
```

Next actual cost instrumentation before actuation/longer trials. Three-field
geometry currently reevaluates all AD candidates plus high-precision distances;
mass factor/stage factor/material cost must be measured rather than guessed.
No final design/performance/actuator/material measurement is claimed.

Project NOT COMPLETE. No OS/session exhaustion occurred in these experiments.
Actual contact IVP is implemented,not yet an actuated three-finger grasp.

## Actual and mathematical results

- Independent math833:fixed two-row Lobatto,true stage Jacobian FD,curved normals,
  analytic fourth-order errors6.33439e-9/3.96261e-10/2.47720e-11,rank/release guards.
- Independent nonlinear842:three100mm rectangular Film/Rails coupons,proper
  120degree frames,root-centres50mm,ONE free R30 sphere,1953DOFs,T0,external
  Fz=-.001N,100us,gravity0. Assumed E250MPa/nu0,skin.05mm,rail.1mm;not measured.
  Three contact reactions≈2.21e-8N. One Newton update;momentum residual
  1.70799e-23Ns,normal velocity residual2.28536e-18mm/s;minimum gap-7.10543e-15mm.
  Body displacement z=-4.99957e-8mm. This small motion is NOT visible wrapping.
- Actual SOFA843/844/846/848 executes this shared solve using actual public
  mass/inertia and actual mapped field parameters.848 versus independent842
  maxq2.82594e-20mm,maxv3.47297e-19mm/s. One100us step,not a time certificate.
- Actual stage/field/whole-surface audit851 PASS:world map1.38778e-17mm,
  unit-row action/reaction1.24127e-16,unit-row moment5.08551e-15mm,
  contact point1.67581e-14mm,whole-stage minimum buffer gap-1.42109e-14mm.
  These are kinematic/virtual-work checks,NOT independent full Hessian FD or
  whole-system momentum/energy/work certification.
- Nine actual physical CSVs across the added read-only body-commit guard850
  are byte-exact. Actual846/848 stage vectors are journaled,not end-only.
-844 explicitly registers/checks fixed radius30.01 Data.843 inherited unused
  default8.01 although the hard R30.01 geometry was used;this API inconsistency
  was corrected,not treated as an R8 experiment.847 unsupported8.01 is a
  preserved FAIL. Runtime rejects initialization before any accepted commit;
  guarded-process generic 'nonlinear_failure' label is CONFIGURATION rejection,
  NOT Newton nonconvergence,OS memory depletion or an authorized physics change.

## Failure-driven geometry work

834 +z force releases contact correctly. Different -z1e-6N/1us835 completes
with zero Newton iterations/sub-ULP body motion;not meaningful dynamic success.
Stronger -z.001N/100us836 fails fixed feature ownership. Rescan838/observer839
fail when face115 and edge116 both report double gap0 but their generalized
gradients differ4.25097e-9. Compile827/832 and CLI837 failures are preserved.

The hypothesis 'these MUST be physical independent simultaneous contacts' was
not justified. Observer840 uses EXACT same stored double geometry and independent
Decimal80/120 arithmetic. Gaps resolve to-4.23660179583e-18 and+9.74511387323e-19mm;
precision disagreement<8e-79mm. The ordering,not a fake contact force,is missing.
PreciseDistanceOrder.h compares squared distances at113/334bits,requires the
same ordering,checks all triangle candidates,and rejects unresolved independent
ties.841 checks840 fixture,exact90degree rotation,face/degenerate cases. The
selector changes NO existing double gap,normal,AD force/Hessian or tolerances.
New opt-in842 succeeds. This is numerical-precision evidence,not a formal
arbitrary-geometry interval/CCD proof. True independent ties/more than one
active patch per finger/release still need a production active-set extension.

## Actual implementation and restrictions

SharedFilmSystem.h assembles three material-coordinate film energies and exact
root-map masses,one common body mass,affine world/shared Jacobians/Hessians.
PersistentRows.h extends the existing nonsymmetric Lobatto equations to fixed
independent compressive rows;no regularization,diagonal shift,component clipping
or post-step velocity/position correction. ThreeFilmPersistentODE reads actual
three fields/four masses,checks free body and sole ODE,integrates then commits
all mapped film/body states exactly once. It is an independent component;older
Native/Event owners and installed SDK are unchanged. SDK ldd logs are archived.

This actual owner explicitly supports ONE REST/T0/100us/R30.01 trial only.
No whole-surface event/birth in this three-finger owner,full C2 closing,shared
tendon equalizer,self-collision,friction,lift/hold/release,12wrench or Optuna.
Sphere rotational Jacobian is physically zero;rotation has not been excited or
generically certified,not fixed by a hidden rigid constraint. Radial normals
alone are not six-dimensional force closure. Pressure/contact area unmeasured.
R30.01 is a midsurface buffer,not certified skin.05mm/rail.1mm thickness clearance.
Root-centre50mm extends beyond50mm in physical skin/hardware envelope. Rectangular
coupons are not the tapered equal_volume_v2 manufacturing design.

## Checkpoint/reproduction

Preceding functional commit5a7879e. New functionality is saved by the following
local feature commit;use git log to resolve it,not a fabricated self hash.
Reuse build/three_film_20261117_three_film_commit848/libReGripThreeFilmContact.so
with its immutable source snapshot. Reuse build/combined_20261117_combined_sparse_1ms821/
libReGripCombinedContact.so for the separate combined-event1ms specimen. Current
live source guards may reject reuse after new development;do not bypass them.

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY -m json.tool results/autonomous_film_20261117_combined_1ms_time829/summary.json
$PY -m json.tool results/autonomous_film_20261117_three_film_commit848/summary.json
$PY -m json.tool results/autonomous_film_20261117_three_film_commit_audit851/summary.json
$PY tools/film_three_film_audit.py --tag UNIQUE_ACTUAL_AUDIT --case 20261117_three_film_commit848
$PY tools/film_three_film_persistent.py --tag UNIQUE_INDEPENDENT --precise-ties
$PY tools/film_three_film_sofa.py --tag UNIQUE_ACTUAL --reference UNIQUE_INDEPENDENT
```

Actual scale1 PNG/OBJ:results/autonomous_film_20261117_three_film_commit_audit851/.
They use stored SOFA coordinates and explicit compiled frame transforms. Film
deflection below visualization resolution is clearly labelled,NOT magnified
or called wrapping. Matplotlib3D unavailable;three orthographic views are used.

## Next development,not a completion claim

1. Independent three-film repeated steps at same physical inputs,whole stage
   clearance,common-time force/energy metrics,unchanged0.1% time gate. Profile
   using measured8423.215s/step before increasing duration/count.
2. Only after independent proof,extend actual owner beyond its guarded ONE
   step;common C2 actuation and actual event integration still required.
3. General patch/row activation,release/reimpact and thickness-aware geometry.
4. Friction/self-contact,actual closing/wrapping/lift/hold/release and comparison.
   No final material/actuator measurement/design superiority is claimed.
5. Preserve old failures and generate a NEW byte-evidence manifest after this
   development unit. Old v8 snapshots are not rewritten/live-current certified.

Resource policy remains4GiB/480s/max4 long physics children. No background
automatic restart is promised;reports/checkpoints are for explicit resumption.
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
