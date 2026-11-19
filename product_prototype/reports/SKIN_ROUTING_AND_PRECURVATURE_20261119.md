# Native distributed routing and manufactured precurvature — 2026-11-19

## Final continuation supplement — force control,negative control and failed physics gates

### Completed post-hold clearance trial375 (final update)

375 finishes3s/1200steps in172.152s. It uses the same1.5N force-controlled B3
closing/holding input as344. ONLY after the1.6–2.0s hold window,the support exits
laterally+x120mm over2–2.2s;its earlier40mm vertical withdrawal stays unchanged.
This is a NEW explicitly recorded fixture input,not a rewrite of325 or an imposed
object position.377 first800states match344 q/v EXACTLY at STRICT1e-12.

376 observes last nonzero Skin contact at2.3875s;late2.9–3s Skin/Guide-object/support
forces are0. Maximum support AND Guide-object force after2s are0 throughout,so
the moving fixture did NOT push/drag the body out. Cable forces are exactly0 at
the end. Object falls freely under actual gravity;final displacement−2386.31mm
is a simulated free fall,NOT Lift or an arbitrary visual relocation.379 renders
fixed cropped viewports and explicitly annotates that out-of-view true object z.
Finger rest-reference tip error is.150984mm under gravity,with very low final
speeds;complete recovery to an independently validated gravity equilibrium remains
NOT QUALIFIED. Native guide-proxy inter-finger gap reaches−.86447mm during this
full sequence378:the moving-hardware Gate is NOT passed despite contact release.
No complete product approval follows from the functional close/hold/release trace.

After375 no physics process remains pending. This bounded candidate family is
checkpointed because repeated time/mesh failures and unstable refined loading do
not justify100g/Lift/optimization expansion. No OS resource exhaustion is claimed.
The actual480s timeout was275;other stops and policy forecasts are separately
identified. Next work must validate native bending/attachments and moving clearance,
not blindly rerun failed settings or invent a passed whole-grasp model.

Functional revisions8f1cbc7,1de4288,0338d02,81640fe,89fb503,4d7d4e9 preserve all
earlier data. Read this supplement before the earlier cycle narrative below.
Trial source_commit can identify the parent of a dirty working snapshot;exact
source/,geometry_generator.py,compiled-source/binary hashes are authoritative.
For example332's working source was subsequently committed as81640fe;do NOT
attribute that binary solely to its recorded parent0338d02.

### Fair comparison and release

308 is a matched native constant-route free-body control at depth65/stroke4,
not the old depth75 trial247. It ALSO meets the experimental holding protocol317
(slip.05015mm,speed3.34035mm/s),with actual Skin source318. Therefore routing A2
is NOT uniquely responsible for making holding possible. Its measured benefit is
improved actual cable following/settling compared with that constant-route control.
No structural efficiency or motor-work superiority is inferred from different loads.

A2 full3s trial325 finishes1200steps in409.355s (forecast418.24s,within480s).
337 verifies the first800 states match291 EXACTLY at STRICT1e-12.338 finds
contact separation is NOT complete:late Skin row-force norm sum up to.13546N,
final Skin gap.19883mm;zero shortening command still needs .104–.112N cable
tension. Object ends40.2mm lower on the withdrawn pedestal. Tip rest-reference
error3.65–3.67mm under gravity is NOT certified elastic recovery. This shows
zero displacement input is NOT necessarily a slack/zero-tension cable.
339's crude final-drop FAIL label applies after commanded unloading,not the earlier
hold window;343/370 publish the corrected separate post-unload scope without
changing339 or any Raw. No Release/Lift/recovery PASS is inferred.

### Stock numerical alternatives,not custom solvers

315 A2 all-pair.6s time gate FAIL:angular-velocity difference.41256rad/s at entry.
316/327 stock NNCG at the same dt changes object velocity by only~1.54e-4 in its
mixed velocity norm,far smaller than that refinement difference. Its maximum native
scalar error6.92e-7 is worse than matched BlockGS3.69e-8;no NNCG product promotion.
Single-finger NNCG improvements284 are not generalized to the coupled system.

Installed FreeMotionAnimationLoop offers solveVelocityConstraintFirst,while installed
SoftRobots CableModel::getConstraintViolation explicitly ignores ConstraintParams.
320/321 first inherit duplicate global/local linear solver setup and both crash;
these do NOT prove anything about the velocity option. After isolating the actual
coupon graph,322 velocity-first gives4.9855mm error for5mm input;323 unchanged
position-based control agrees1.78e-17m. Thus the tested combined velocity-first
input path is rejected,not silently applied to3 fingers. SDK unmodified.

### Calibrated native force input and B3 manufactured geometry

B3:40deg manufactured distal curve over70–100mm (reference radius~42.97mm),
chosen to move curvature toward R30 instead of increasing wire force. Initial Skin
gap1.398798mm;finite guide/object gap5.510742mm;interfinger proxy margin1mm.
324 single displacement run keeps Skin contact but cable error1.015/1.112mm.
It is not promoted as a correctly displacement-driven finger.

330/331 independently calibrate Native CableConstraint force mode:input value
is native impulse T*actual_dt. A1N force on the stock1g/1000N/m spring-mass model
agrees with its analytic discrete BE recurrence within2.4e-16;lambda error0.
81640fe adds ONLY optional C2 input conversion/journaling,NOT a force/contact/FEM
or integration law. New build default_control332 binary:
3eb202b1e2a25f3ec6cded69e92a9d02bc48c304be14f6ca7123b4d758e5d0e0.
333 old displacement branch q/v equality0 for200 actual contact steps.334/335
C2 force inputs and spring-mass states pass1e-12 at two dt. Missing displacement
commands in force mode areNULL,not zero or a fake shortening target.

336 uses1.5N/cable,LESS than the earlier B3 displacement run's~2.127N peak.
This is a DIFFERENT PHYSICAL CONTROL INPUT,not a numerical repair of324.
340:actual force command error1.33e-15N,shortening2.450/2.626mm,Skin Fz.23712N,
no Guide/Rail object force,minimum guide/wire gaps2.745/4.298mm. No displacement
tracking PASS is claimed when there is no displacement target.

344 actual3-finger50g force-driven trial completes2s in142.845s.347/348:

|Quantity|Base result|Meaning|
|---|---:|---|
|Downward hold slip|.032359mm|functional threshold2mm met|
|Maximum object speed|.272144mm/s|functional threshold5mm/s met|
|Minimum support gap|41.599746mm|external support absent|
|Support/Guide/Rail hold object force|0N|actual response provenance,not child-J attribution|
|Skin mean Fz|.490513N|weight.4905N transmitted by Skin|
|Minimum Skin vertical weight fraction|.994653|predeclared.8 condition met|
|Normal_z throughout hold|.855161...857677|favourable direction persists,not one frame|

Zero-force SAME geometry345 is an essential causal control:349 FAILs,slip40.00054mm,
support reaction~.49423N,Skin meanFz−.003287N. Therefore manufactured precurvature
alone did not produce the observed unsupported hold in this protocol. Collision
hardware is retained and object pose never prescribed. This is real limited native
Skin-load holding evidence,NOT final grasp certification or measured hardware.

351 full half-dt2s completes in278.032s;368 still meets functional hold criteria
(slip.022138mm,speed2.91787mm/s),and373 actual Skin meanFz.490480N,Guide/Rail0.
But366 all-pair.6s and367 full2s Base/Half both FAIL unchanged.1% time gate.
366 includes substantial nodal-velocity difference.68165m/s,not just tiny-value
roundoff. Full quarter2s forecast~556–571s exceeds480s:NOT RUN,not OS exhaustion.
336/341/342 single-finger full2s force-input refinement346 also FAILs overall;
native cable force itself agrees while state/velocity/recovery do not.

353 Skin mapping query error0 and actual minimum geometric gap.037443mm stays
outside the actual R30 surface,but BUFFERED gap is−.162557mm relative to.2mm.
Do not promote DIAGNOSTIC_ONLY to whole-surface clearance PASS.354 root-to-tip
angle~48.6deg and curvature~.0313/mm do NOT establish wrapping:connected proximity
arc spans are tiny (e.g.~.083deg),not broad pressure-bearing area.355/356 measure
normal/tangential vertical contributions .418418/.072095N;maximum resultant
moment.00015868Nm. No maximum capacity,torque-resistance or6DOF closure test.
358 collision/body API difference0;359 momentum balances pass ONLY their scopes.

### Critical refinement failure and minimum isolations

360 same1.5N force and dt.0025 with41 longitudinal stations (rather than21) collapses:
119.08mm peak tip motion,2483 inverted-element samples,first inversion.375s,
minimum determinant ratio−10.08,wire/object gap−1.84mm. This is NOT a stable
refined product. Total native UniformMass remains1g but nodal mass quadrature
changes;guide attachment stations stay fixed. Curved reference discretization also
changes slightly. Locking,buckling,attachment discretization and dt are hypotheses,
not conclusions inferred from one mesh change.

363 zero-force41-node rest stays EXACTLY at reference for4steps.365 no-object
loaded isolation ALSO inverts (first.4175s,274 samples),so object contact is not
necessary for the instability.364 quarter-dt first.5s has NO inverted samples,
minimum determinant ratio.7047,but tip16.45mm vs~1.93mm in coarse21-node response.
Thus temporal stability and spatial representation BOTH require validation;no
full.5s/2s fine-mesh convergence certification.369 retains every failure.

372 independently attempts a stock StaticSolver+NewtonRaphsonSolver small-load
linear tetra cantilever at21/41/81,without cable/contact/guides. All three stop at
actual Newton/line-search failure;residual plateaus~3–5e-9N versus1e-12 requested.
No tolerance is relaxed. Its original producer labels absent mesh pairs FAIL;
the correct interpretation is BLOCKED STATIC SOLVE with mesh comparisonNOTMEASURED,
not a measured static mesh error. Producer status corrected prospectively;372 Raw
unchanged. Approximate Euler tip.811795mm is section theory,NOT an executed3D result.
Do not adopt that theoretical curve as a simulated finger. Installed native BeamFEM
and triangular bending components are possible FOLLOW-UP models,not validated here.

### Final disposition and continuation

The present native tetra/contact family repeatedly fails time/mesh/clearance gates.
Stop production expansion of the loaded41-node case;guard prevents3-finger use.
No100g,Lift,Optuna or final fabrication approval. Next work is a small-load,
well-conditioned native bending/attachment validation before using thin tetra
holding numbers as design evidence. Do NOT resume old custom solvers,repeat failed
372 unchanged,enable velocity-first with the failed Cable coupling,or only increase
stroke/friction/force. Release trial375 uses a separately declared post-hold fixture
and is recorded in the final checkpoint;it cannot overwrite325's failure.

v7/v8/v9 parametric references/STLs/SVG/BOM exist. v9 config exactly matches324;
336/344 share that geometry but DIFFERENT actuation metadata. STEP/kernel assembly,
real guide supports,strength,fasteners,wire bend radii,motor and measured materials
remainunqualified. Frozen scenes under sofa/scenes/ are exported from actual344/325;
all Native journals now redirect to exclusive records paths. Export-only is not an
additional physical replay PASS. Final actual-state figures370/371 carry dt,input,
source state/binary identity and explicit NOT QUALIFIED marking.

All child limits4GiB/480s maintained,max concurrency≤4;no paid service,push or SDK
changes. Actual275 timeout is a policy limit;static372 stops on Newton failure.
Peak RSS,root work,whole energy,pressure and contact area remainNOTMEASURED/NULL.

Start:da71cdc. Functional commits:8f1cbc7,1de4288. No SDK or legacy solver
changes,no remote push. This is product trial259 onward,not the legacy campaign
number sequence. Every physical trial has immutable launch_command.json,scene.scn,
geometry_generator.py,source/,config.json,SDK/runner/binary hashes and guarded logs.
Research material/friction/hardware assumptions are NOT measured PET/TPU properties.

## Physics and design hypotheses

Earlier247/256 use depth75mm:late Skin normals push the object down. More normal
force cannot make those measured friction cones support upward load. This work
changes deformation/moment distribution,not a repeated constant-offset/stroke sweep.
The matched single-finger and new free-body comparisons use depth65mm;therefore
their difference from247 is NOT attributable solely to routing.

Common:100mm material length,W24→12mm,root radius50mm,root angle14deg,3x120deg,
Skin.1mm,rails.5mm,E250MPa,nu.3,mu.3,core1g/finger,12 bracket frames10mg each,
wire radius.25mm,guide OD3mm/length2mm,conservative native guide sphere radius
sqrt(1.5²+1²)=1.802776mm. Two independent4mm CableConstraint commands,NOT an
equalizer. Stock EulerImplicitSolver/SparseLDL/BlockGaussSeidelConstraintSolver,
MinProximityIntersection(useSphereTriangle),Rigid3 sphere collision,stock mapping.
All native tests reuse unchanged Controller binary33baec3658a718b7bff6f472f6701f6f75c02a70507bbe5a4ea4260fa478e1c2.

Candidate A:normal offset3→9mm along distal60→100mm via cubic smoothstep.
At each station the same route is used by native CableConstraint and CAD sources.
Unit-tension guide moments differ from constant routing by up to5.859833mm*N/N;
independent rotational virtual-work finite differences agree within1.34e-8mm.
This is a moment-distribution change,not a force-field implementation.

Candidate B:manufactured stress-free circular distal reference,20deg over60→100mm.
Geometry-only259 first rejects30deg starting50mm (initial Skin gap−2.200mm);
30deg starting60mm also fails declared.2mm buffer before physics. The20deg/60mm
reference has1.275807mm initial Skin gap and positive element determinants.
For arc coordinate s,start a,k=theta/(L-a),phi=k(s-a):
X=a+sin(phi)/k−z*sin(phi),Z=(1−cos(phi))/k+z*cos(phi).
Width is unchanged. Root straight section and material-node identities are retained.
Native FEM initializes these coordinates as its rest shape;no q prescription is
applied during dynamics.269 zero input four steps leaves q/v exactly at rest0.
This is NOT evidence that a flat PET sheet naturally acquires this shape;manufacturing,
residual stress and bond assumptions require physical validation.

Candidate C combines A/B only AFTER261/262 independent runs. Its separate sector
variant uses distal8mm (not9) to satisfy finite guide/object initial clearance.
It is NOT a pure one-factor superiority test against A/B.

Native flat reference and mass1g are unchanged in A. B/C tetra volume410.098113mm³
versus410mm³ flat (+.02393%);nominal section/arc length stay the same. This discrete
curved reference is NOT an exactly equal-volume comparison. Constant prescribed
mass also implies a slightly different effective density. No stiffness/friction
was increased to manufacture a successful outcome.

## Completed single-finger fixed-R30 comparison

All800steps,dt.0025s,2s,zero gravity,closing0–.5/hold.5–1/release1–1.5/recovery1.5–2.
Fixed sphere reactions use unprojected mapped collision-state J^Tlambda,not the
projected fixed body's zero reaction. Row-source partition checks agree0. Fixed
reaction is NOT free-body momentum or holding certification.

|Trial|Mechanism|Runtime s|Hold Skin Fz N|Hold cable max error mm|Disposition|
|---|---|---:|---:|---:|---|
|263|constant baseline|16.570|.086128|1.896932|direct Skin,but nonlinear cable FAIL|
|261|A distal|18.674|.092713|2.81e-7|Skin only;121/121 hold frames upward cone|
|262|B precurve|31.118|.196204|1.065602|better direction,but cable FAIL|
|268|C original hybrid|32.390|.154486|1.85e-7|Skin only in single finger;assembly fails below|
|285|A2 sector route|18.350|.127085|4.37e-8|Skin only,121/121 upward frames|
|286|B2 sector precurve|30.155|.207494|1.665979|cable FAIL;not selected|
|292|C2 sector hybrid|12.777|0 in hold|.618763|Guide Fz.285482N;reject Skin grasp candidate|

Actual coupled surface gap,tetra determinant ratios,tip chord angle,wire/guide gaps,
force partition,return error and per-station unit-tension moments are preserved in
264/265/266/271/289/290/296. No inverted element samples in those runs. Full
self-intersection,root reaction,pressure,contact area and whole energy remainNULL.
Minimum dynamic finite-wire/guide-to-object gaps for A2 single:3.949/2.396mm.
Tip recovery is a fixed-object/zero-gravity result,not a free grasp recovery claim.

## Assembly failure discovered and corrected — do not promote267

Original A/B/C outward lateral24mm paths cross neighbouring guide collision proxies
when assembled at120deg. Actual-scene audit287 finds initial proxy gaps−3.359378mm
for267/283 and−2.663441mm for275. Thus267's experimental support-free holding
observation (Skin.4905N,Guide0,slip.5323mm) is retained but cannot qualify an
initially overlapping product. Whole-surface penetration during267 reaches−2.112686mm.
283 finished1600steps in423.024s but is likewise unqualified.275 reached the480s
policy timeout before2s;its partial CSV is NOT completion or holding evidence.
No old result/Raw was overwritten. The new guard293 rejects this overlap BEFORE
launching SOFA;the initial geometry check now includes neighbouring guide spheres.
294 was an analysis import error,corrected in295/297/311,not a physics failure.

A2/B2 route each physical guide within its120deg sector,using unchanged finite
hardware radius and positive margin m=.5mm. For radial position r and width w:
outboard(s)=min(24,sqrt(3)*r−2*(guide_radius+m)−w/2).
It is a distributed3D route/physical support-arm change,not collision deactivation
or a uniform offset sweep. Initial inter-finger proxy gap becomes1mm. It changes
normal and lateral moment distribution,so A1→A2 is not a pure one-variable contrast.
C with9mm distal offset cannot meet both this sector and initial object clearance;
8mm gives1.529mm guide/object initial gap,then actual292 becomes Guide-supported.
That is a measured rejection,not justification to shrink/delete hardware collision.

## A2 actual free-R30/50g gravity test291

Completed800steps/2s in278.824s,zero native ERROR/missing intersectors. Initial Skin
gap2.689863mm,guide proxy inter-finger gap1mm. Identical physical support withdrawal
protocol1–1.5s,support40mm downward;closing0–.5,hold through2,release starts2.
Full3-finger release/recovery was NOT run by stopping at2s.

301 actual Contact pair→response→constraint row partition error2.17e-19Ns.
302 meets the predeclared experimental functional hold protocol1.6–2s:

- downward slip.053164mm≤2mm;maximum speed.00045845mm/s≤5mm/s;
- minimum support gap40.146836mm≥5mm;support reaction0N;
- Skin Fz.4904999994N,minimum Skin weight fraction.9999999988;
- Guide/Rail/object support0;Skin resultant moment is separately inventoried314;
- native gravity9.81m/s²/object.05kg actually integrated,not prescribed object pose.

303 active Skin normal_z stays.484456..484479;upward Coulomb coefficient
.746901..746919 throughout the hold window,not one favourable frame.
312 body/collision q/v/time differences0 over800states at STRICT1e-12.
313 linear/angular momentum residual2.17e-19Ns/4.24e-22Nms inventory only.
314 measures Skin normal Fz.329559N plus tangential Fz.160941N;maximum hold
resultant contact moment3.82e-12Nm. Scalar cone excess2.71e-20Ns is recorded,
not silently clamped or a maximum-load/6DOF wrench-closure certification.

IMPORTANT:This is functional Skin-load holding evidence,NOT whole-product PASS.
304 strict gap/active-response consistency FAIL:maximum active nearest gap
.200000665mm vs declared.2mm. Global minimum actual Skin gap.197219mm is positive,
but that does not waive the failed buffer/proximity condition.305 sampled guide
proxy inter-finger gap.199463mm is positive but guide/guide proximity interactions
and missing full support-arm/wire/palm/self-collision prevent Gate2 certification.
Cable transient shortening error reaches~.0384mm despite tiny settled error.
309 proximity geometry does NOT show broad pressure-bearing wrapping. Do not
equate one closest triangle or row count with contact area or wrapping coverage.

## Numerical evidence and bounded next work

261/270/272 are SAME binary,geometry,input/initial state with800/1600/3200steps.
Full2s common-time/all-pair assessment276 FAIL at unchanged.1% gate,no floors.
Worst relative short-length error200% includes roundoff-scale values,but meaningful
motion differences also exist (maximum aggregate nodal-motion difference.942133mm).
Pre-hold.6–.9 comparisons also FAIL;do not dismiss this as only zero recovery values.
Native residual261 reaches2.66e-6 and245 iteration-limited frames. Stock NNCG284
uses unchanged physics and no custom solver:max residual3.12e-8,no iteration-limited
frames,17.169s vs18.674s. This is NOT a nonlinear/time/whole-contact certification.
300 analysis regression recreates historical243 errors.csv byte-for-byte:
SHA2566f774bbf3597942a45c4515d73f3778ccd54e5e90f8c467050c16b8fa5cdf491.

A2 full2s half/quarter forecasts557.65/1115.30s exceed480s and are NOT RUN.
Short.6s half306/quarter307 forecasts167.29/334.59s fit policy and are separate
contact-entry convergence experiments,NOT hold-window refinement. Actual final
assessment and matched constant-route free-body308 are appended in checkpoint.
Never treat an in-progress or timed-out process as a completed horizon.
Policy timeout is not operating-system memory exhaustion;peak RSS NOT MEASURED.

## CAD and reproducibility

v7 references preserve the rejected assembled paths. v8 contains sector-routed
Skin/rails,guide-envelope reference assembly,STL,SVG,BOM and exact shared config
bytes of285/286/292. Candidate cores are watertight. Old flat FreeCAD/SCAD exporters
now reject curved/profiled configurations rather than silently emitting mismatched
flat solids. FreeCAD/OCC/CadQuery are unavailable in the Python environment;
STEP/kernel assembly NOT GENERATED. Support solids,hardware stiffness,wire bend
radius,fasteners,motor,manufactured rest curvature/tolerances remainunverified.
No PHYSICAL FABRICATION READY designation.

Actual accepted-state comparison figures:results/mechanism_figures299/ and
results/sector_three_actual305/. Each has source/binary/config/dt metadata;no
displacement amplification,concept pose or fabricated pressure distribution.

Exact executed commands are in each results/<case>/launch_command.json and
process/command.json;do not reuse output tags. Reusable build:
product_prototype/cad/build_response_public_187/libReGripProductSequence.so.

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY product_prototype/sofa/mechanism_tests.py --tag NEXT_UNIQUE_MATH
$PY product_prototype/sofa/response_load_assess.py --case distal_sector_three291 --tag NEXT_UNIQUE_LOAD
$PY product_prototype/sofa/response_wrench_assess.py --case distal_sector_three291 --tag NEXT_UNIQUE_WRENCH
```

No100g,Lift,12-Wrench,Optuna or final design selection until required physical
and wrapping gates pass. Mechanical equalizer and measured material validation
remain separate unfinished work. This checkpoint is not project completion.
