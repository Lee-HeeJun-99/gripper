# Contact dynamics and actual film–rail–tendon continuation

## Latest 2026-11-17 checkpoint through372 (NOT project completion)

Local source/tool commits through3181ce8. Actual fixed-sphere356 completes
8s;366 completes16s/1600steps in268.204s. Final tip -0.00672mm,max speed
0.00854mm/s,T=0,contact multipliers0. This is frictionless FIXED-object
release/near-rest recovery,NOT free6DOF/3finger grasp or design superiority.
Actual states: designs/visualizations/film_native_20261117_sphere_recovery_actual372/.
Full-cycle buffer-clearance audit358 FAILS (-0.00013543mm at7.99s);the gap
to the radius8 zero-thickness sphere remains positive0.00986457mm. BothSide
contrast367 is REJECTED as a fix:all5 physical journals byte-identical in370.
Time348/351 still FAIL0.1%;full energy/friction/free grasp/Optuna BLOCKED.
Next REAL implementation is candidate-complete triangle contact with its own
row-observer interface;independent temporal work is a shared C2 tendon
profile. No candidate-complete or C2 implementation is claimed yet.
See FILM_TEMPORAL_COUPLING_20261117.md and LONG_RUN_RESEARCH_CHECKPOINT.md.
Historical activity notes below are not live process status.


## 2026-11-17 actual continuation through343 — project NOT complete

Local feature commit518208f adds current closest point/gradient/Hessian and
SQP line-search globalization,without changing accepted forces or tolerance.
Actual333 completes4s/400steps:70.0995s runtime;whole-triangle buffered gap
defect2.21e-11mm versus0.000531mm in307. Radial moment and force pullback
checks pass in limited scope. Discrete force-location covering arc73.208deg
is NOT contact area/pressure/holding performance. Fixed-object,frictionless,
single-finger only;NOT free6DOF or full-energy certification.
Failed320/322 and rejected remedies325/328/329 are preserved. Same-binary
short time comparison337 FAILS0.1%,including pre-contact motion/energy;
the contact event alone cannot explain all time error. Full-window344 and
subsequent development must be judged from their actual final result files.
Details/reproduction: FILM_TEMPORAL_COUPLING_20261117.md and
LONG_RUN_RESEARCH_CHECKPOINT.md. Grasp Optuna remains BLOCKED;no fabrication
or actuator performance is claimed. Historical notes below are not live status.


## 2026-11-17 latest actual checkpoint through305

Project NOT complete. Work continued beyond the old campaigns. Source feature
commits through29ef7e4 are local only; current-sphere geometry is an additional
experimental implementation, not a replacement certification.

Actual fixed-cylinder270 closes over4s;275 completes8s closing/hold/release.
282 completes16s including settling (1600steps,281.424s): final tip -0.007395mm,
maximum speed0.009374mm/s, zero prescribed tension and no positive contact
impulses. These are actual research-parameter results, NOT free-object grasp.
The first800 rows of282 match275 bitwise (state/contact/momentum/coupled CSV).
Sphere284 closes4s but supports locations over73.148deg versus Cylinder
123.752deg. Discrete force-bearing location spans are NOT contact area,
continuous wrapping angle, pressure or holding capacity.

Whole-cycle275/288 time comparison292 remains FAIL at0.1%: tip2.3268%,
normal force14.4819%,attachment energy1.1316%,kinetic energy8.3910%.
Inherited failures remain. Same-binary cache benchmark281 has3 alternating
pairs, all5 physical CSVs bitwise identical, median runtime ratio0.77813
(22.19% reduction);704 mechanical evaluations become402, with302 exact reuses.
This is scoped performance qualification, not physical convergence.

Measurement issue isolated: main journal.x is WORLD, not displacement.
Late world-minus-rest force reconstruction loses precision. Near-rest
prescribed probe293 gives relative impulse residual0.00419962 in294 world
reconstruction versus2.78543e-8 in295 direct local-displacement reconstruction.
296 recorder ON/OFF physics CSVs match bitwise.291's earlier attempt wrongly
interpreted main x as displacement and is INVALID postprocessing, not physics.
Old whole-cycle raw lacks exact local coordinates: do not retro-certify it.

New root cause298: frozen begin normals give accepted exact-sphere radial-law
moment deviation0.6430% in the wide Sphere test. New SphereStep uses actual
current radial gaps/normals and TRUE constraint geometric tangent. Independent
FD relative error2.21e-15;actual30120-step test and302/303/304/305 partial
equation checks pass their LIMITED scopes: accepted radial-law defect1.59e-15,
force-row reconstruction4.97e-17, impulse residual3.49e-6,derived BE identity
4.02e-10. This is a NEW fixed-support sphere model, not native-contact
equivalence, friction, CCD, contact-area convergence or free6DOF certification.
300 source-archive omission is preserved as prephysics FAIL;301 fixes it.

Current actual extension306: inspect summary/result before interpreting its
prefix. No tolerance relaxation, fake forces, SDK edits, hardware, remote push
or paid service.299 rejects unsupported moving colliders before accepted rows.
Three fingers/free6DOF/12-wrench/multimaterial, full energy, final structure
superiority and grasp Optuna remain BLOCKED/NOT RUN.

## 2026-11-17 actual continuation through264 — supersedes older status

Project NOT complete. Functional commits: b8b9cc3 (profiling/routing),
6172967 (cache recovery),9354793 (nonlinear contact),74175ca (BDF2 alternative),
ed40987 (mandatory accepted-stage owner). Sources/builds/raw remain separate.

Actual235/243 complete400/800-step fixed-cylinder closing;246 time FAIL:
force9.27393%,tip0.163093%,attachment0.169901%,kinetic4.73995%.
Independent240/241 confirm accepted impulse equations and the derived BE
identity, NOT whole energy or global force/moment certification. BDF2 actual
244/247/248 also FAIL250; do not adopt it as a qualified time fix.

Actual251 higher-tension one-factor capacity probe fails free Newton at2.95s.
Available2.94s state has73.122deg load-bearing location span, but partial-run
diagnostic258 and plot259 are EXPERIMENTAL/PARTIAL FAILED, not wrapping/grasp
approval.263 with single-Newton predictor gets past that stage to3.36s, then
FAILS the coupled Newton30-iteration budget. This is algorithmic failure,
NOT OS memory/runtime exhaustion. No tolerance/iteration inflation was used.
Short260 accepted impulse/energy checks and actual negative-owner guard264
pass their LIMITED scopes.265 tests previous accepted velocity initialization;
inspect summary/result before using its data. No automatic restart is assumed.

Read FILM_TEMPORAL_COUPLING_20261117.md and LONG_RUN_RESEARCH_CHECKPOINT.md.
Remaining: robust complete closing/hold/release, mesh/history/dt, current-normal
angular consistency, reactions, whole energy, self-contact, free6DOF/3finger/
multimaterial/12-wrench grasp. Final-design superiority and grasp Optuna remain
BLOCKED/NOT RUN. Research parameters are not measured PET/actuator properties.

## 2026-11-17 actual continuation

147–224 add cost instrumentation, qualified workspace reuse, routing/control
comparisons, actual Sphere/Cylinder contact and nonlinear impulse diagnosis.
Native accepted relative residual .93498 reduces to <=3.56e-6 in a short
separate coupled model. Time refinement still FAIL. Near-duplicate native
contact rows also show LCP nonconvergence; actual active-set reproduction
continues225/226. See the two20261117 reports; these are not grasp certification.


2026-11-16 continuation from 04637d3; feature commits 5f0c394, c4c4853,
8646900. This is a measured checkpoint, not final project completion.
All numbers below are actual SOFA unless explicitly labelled independent.
Existing failed campaigns and original SDK/models/raw were preserved.

## Cause isolation and implemented fixes

The public mapped matrix probe found a real MBK-factor cache defect in the
matching SDK's mapped mass projection: first BE step matched reference to
2.653e-17, next BDF2 step differed by 1.93992e-6. The worst diagonal error was
5.05952381e-9, exactly the missing change in the mapped mass coefficient.
Independent ReGripMatrixLinearSystem refreshes mapped mass factors; SDK files
are untouched. Corrected BDF2 matrix error is 1.439e-21. Second-step Newton
iterations fell from13 to2. Corrected200/400/800-step runs cost9.985/14.746/
28.023s, but the old coarse time convergence remains FAIL.

No-contact control time differences are much smaller than post-contact ones.
Interpolated contact onset differs18.4 microseconds between the old coarse
and fine runs. This is a stored-state chord estimate, NOT exact CCD. Independent
clipped-triangle area/force reconstruction matches the observer to1.42e-14 mm2
and2.12e-22 F. Actual modal projections show contact excites higher structural
modes and later separation/recontact. Therefore event-time error alone is not
supported as the whole explanation. Contact-only frequency bound177.48 rad/s
is not the maximum structural frequency. Softer penalty reduced some errors
but still failed and changes physics; it was not substituted to obtain PASS.

Opt-in compile-time nine-DOF membrane derivatives expand to unchanged AD27;
914 randomized element comparisons were bitwise equal. Separate native-host
compilation, without fast-math or contraction, preserved actual CSV and
derivatives. Median runtime ratios native/base: coupon .73775, assembly
.74256. The previous slower runtime gradient-only strategy was NOT reused.

## Scoped coupon time PASS; old failures retained

The continuous endpoint load and predeclared phase window refine dt after
1.3s; this is not CCD or adaptive error-controlled integration. Variable-step
BDF2 is separately derived/tested. BDF2 still failed endpoint contact-force
convergence (.2929%); that failure remains.

Independent Trapezoidal (theta=.5) reference matched actual short SOFA states
to approximately1e-15 relative. Campaigns71/72/73 use3280/6560/13120steps over
0–2s with pre-window dt .00125/.000625/.0003125 and post-window dt four times
smaller. All adjacent AND nonadjacent time comparisons, endpoints and physical
subwindows pass the unchanged .1% gate for tip,U,reference contact area and Fn.
Runtime73.40/139.63/272.94s. Momentum relative residual maximum1.0793e-6, below
.001. Full3280-step repeat77 CSV is bitwise identical. Qualification76 records
the exact metrics. This is only a frictionless fixed-plane rectangular coupon,
not changing-normal friction, free-object grasp, or complete energy approval.

## Spatial findings and rejected alternative

An independent cubic-exact root slope mapping passed mathematical/API tests,
but actual11→41 energy4.9682% and area2.5596% failed. It is rejected as a
spatial improvement; the original mapping remains the comparison default.
With the original boundary, static21→81 energy .46903%, area .49293%, tip
.02147%, Fn .00721% pass1%. Original11→41 FAIL is retained. Static fine-mesh
agreement does not certify dynamic or width-direction spatial convergence.

## Actual coupled assembly, not a geometry-only concept

Independent skin and two flexible rail DOFs, five objective attachments/rail,
and five eccentric actual-normal-offset tendon guides/rail are implemented.
The rectangular equal-core-volume dimensions and exclusions are in
models/film_rail_tendon/README.md. Independent force/Hessian FD errors8.19e-12/
2.34e-10, objectivity5.63e-16; API, query purity and root/world virtual work
PASS. Actual assembled mass/tangent errors5.19e-17 and2.30e-16 PASS.

At T=.0001 per rail, actual8s actuation/release/recovery has maximum skin tip
.637238mm and residual tip .00284620mm, observed recovery99.5534%, speed
.003053mm/s. This is not a grasp release gate. At T=.001, original fixed-step
Trapezoidal and BDF2 failed; failures79/80/81/85/93 are preserved and the
watchdog stops on first final Newton failure. No damping/tolerance was changed
to hide this. Same nominal T with dt .0025 before1s and .00015625 afterwards
completed1.5s (97), then explicit bounded coarsening completed2s (101) in
393.180s with4401steps and zero Newton failures. Tip at2s is -6.97122mm,
speed34.8006mm/s, T=0. This is execution stability, not time/mesh qualification.

Low-tension1600/3200/6400-step4s runs completed119.21/223.28/287.29s.
Motion, shell energy, tendon work pass .1%, but attachment-energy difference
1600→6400 is .82320%,3200→6400 .65352%: coupled time gate remains FAIL.
Small absolute attachment energy does NOT override this relative failure.

Offline synchronized accepted-state energy audit91 includes actual mechanical
tendon work, trapezoid gradient/work quadrature differences and the derived
damping quadrature defect. Maximum cumulative unexplained residual4.3988e-19,
relative to peak work9.1523e-13. These signed, independently defined terms are
not a fitted numerical loss. This is a partial no-object energy identity, NOT
global ReGrip energy certification. Pressure, layer friction and free-object
work remain undefined/absent; whole-system energy BLOCKED.

## Current exclusions and next checks

### Actual native follow-up completed110–118

Follow-up119–127: cumulative vertical impulse waveform100→400 differs2.5341%,
so pointwise impact spikes are not the whole failure. Identical no-contact
BE100/200/400 controls also fail (nonadjacent tip .63450%, shell U .78026%,
attachment U1.70663%,K2.27658%); contact amplifies rather than solely creates
time error. This rejects the hypothesis that native onset timing alone is the
dominant remaining defect. Full .1% time Gate is unchanged.

Actual fixed-sphere1s actuation125 completes400steps with nonzero reaction in
304frames. At1s center-skin atx~79.32 isz~7.34mm while its tip isz~-.392mm.
The structure arches away from the sphere rather than achieving a validated
wrap. Journal skin_tip_z is width-average(-1.3933mm), not center-node value.
No wrapping angle/contact area/success rate is invented. This is a negative
mechanism observation and a reason not to expand to a purported3-finger grasp.

Independent frozen actual-state diagnostic127 decomposes the99→100 coordinate
error at1.12875s with the mapped mass and stored-energy tangent. Largest positive
quadratic-error contribution has omega652.584rad/s and attachment fraction
.37066; further contributors317.954 and741.051rad/s. The maximum eigenfrequency
634807.9rad/s is NOT evidence that all such modes are appreciably excited.
Tendon geometric stiffness is excluded from this stored-energy diagnostic;
it is not a dynamic modal-stability certificate. Same-input local step-window
experiments128/129 test whether post-1s temporal resolution addresses this
attachment transient, rather than changing physical stiffness or damping.
The launch tool initially had an `else2080` syntax typo, corrected before any
output directory/physics process was created; no failed physics was relabelled.

Matching SDK collision modules are absent (109 failure retained), so all three
plugins were separately rebuilt for installed SOFA; ldd rejects patched-engine
dependencies. Native BE factor/API tests PASS. Installed Default/FreeMotion
no-contact controls110/112 match to3.55e-15mm coordinates (113), without
altering physical input. Removed SDK alias DefaultContactManager (111 FAIL)
was replaced with supported CollisionResponse, ODESolver link case corrected.

The first sphere at(75,12,-8.2),R8 did not contact in .5s (114); actual middle
skin initially rises while tip descends. This is a negative geometric result,
not a contact PASS. Separate declared sphere at(95,12,-8.2),R8 is actually
contacted by the tendon-driven skin (115–117). First nonzero reaction .24/.24/
.24125s; peak |J^Tlambda/dt|1.04982e-5/1.21577e-5/1.41098e-5 F.
Begin-stage torque about sphere center is <=2.19e-19 F mm; later free/accepted
geometry would generate a spurious apparent defect. Fixed sphere Jacobian is
projected away, so physical fixed reaction remains null/BLOCKED, not zero.
Reference-area/contact pressure/active-point counts are NOT inferred from
candidate constraint rows or minimum vertex gap.

Native100/200/400-step .5s time test118 FAIL:100→400 tip2.04363%,force25.4231%,
shell energy1.24787%,attachment energy3.00346%,K4.55588%,tendon work1.24914%.
This is actual coupled surface contact, but NOT qualified wrapping/grasp.
Hard contact includes impact impulses; investigate cumulative impulse versus
pointwise force and constrained time discretization before any long free-object
trial. This failure does not invalidate the separate frictionless compliant
plane coupon's scoped time PASS and is not used to replace it.

Nominal97/101 first3600 accepted journal rows are exactly identical. Fine low
load attachment-energy maximum error99→100 occurs at1.12875s, shortly after
the continuous load's derivative changes sign at1s: 1.26558e-11 F mm absolute,
.65352% of peak. Event-slope excitation versus true attachment high modes is
the next falsifiable hypothesis, not a confirmed explanation.

Native fixed-sphere contact is being developed as a separate frictionless
constraint law. BE-only free-motion integration factors match SDK Euler API;
BDF2/Trapezoid constrained histories are explicitly rejected. Before contact,
the no-contact Default/FreeMotion loop control must agree. Actual world
coordinates use rest+u and virtual-work-consistent mappings. Native J^Tlambda/dt
must be evaluated at a declared constraint stage, not confused with candidate
row counts or SDF compliance. No free6DOF object, wrapping or grasp has yet been
approved. Original SphereEvent .146423% and CurvedContact .8519% time failures
remain. Grasp Optuna is BLOCKED; no study was launched.

## Reproduction (unique new tag required)

### Latest completed attachment/energy follow-up128–146

Trapezoidal128/129/131 execute2080/4160/8320steps to1.2s; measured103.85/
182.24/361.04s, all within480s. Same-input local refinement does NOT qualify
the complete interval:129→131 attachment differences .14551% before1s,
.079574% during1–1.2s, .13382% overall;132 retains FAIL. The passing local
interval is not extrapolated backward or to the full4s cycle.

Alternative BDF2 was profiled135/136 and separately tested, rather than adding
physical damping. Local136→137 attachment .14639% before1s and .16437% after1s
still FAIL. Full4s BDF2 runs139/140/141 (1600/3200/6400steps) cost113.29/184.64/
278.47s, no Newton failure. Full nonadjacent attachment difference .74551%,
shell energy .16675%, tendon work .13516% FAIL; fine3200→6400 attachment
.48529% FAIL. This rejects 'Trapezoidal nondamping alone explains the defect'
as a sufficient fix. It does not prove a unique remaining cause.

Independent BDF2 energy audits143/146/145 all PASS their partial discrete
identity; maximum cumulative unexplained/peak work1.52e-11/1.81e-10/2.97e-11.
They reconstruct actual accepted velocities/U/K, derive the G-energy inventory
and BE-startup/BDF2 difference loss explicitly, and retain signed endpoint-work
and elastic quadrature differences. These are numerical terms, NOT Coulomb heat
or pressure work. Full ReGrip energy still BLOCKED. Code and definitions are
diagnostics/film_rail_tendon/BDFEnergyAudit.cpp and tools/film_bdf_energy.py.

Suspected tolerance-based mapping state suppression was also falsified: public
Data setters do not compare Vec approximate equality; actual root/world unit
test144 preserves1e-10→2e-10 increments. No mapping 'fix' was applied without
evidence. Actual surface and energy journals are coordinate-identical in134.
At1s membrane Green strains are approximately[-5.22e-5,4.92e-5]; this is NOT
a bending-fiber stress, damage threshold or material-validation result.

All launched processes through146 are complete, not RUNNING. This response
checkpoint is unfinished because the available response/context budget is
finite, NOT because final research goals were met. No OS-wide timeout, permission
denial or exhausted disk was observed; all latest bounded runs ended normally.
Meaningful further work remains executable. No autonomous restart is promised.
Next priority is controlled force/cache/element profiling and a mechanically
correct wrapping route, not another unprofiled doubling or free-object claim.
Source/code feature commits are recorded in Git; v2 ledger records its exact
source commit and hashes, with no circular claim about its own commit.

Python: /home/ubuntu/miniconda3/envs/robot_ws/bin/python. From repository root:

```
$PY tools/film_window_qualify.py --help
$PY tools/film_contact_summary.py --help
$PY tools/film_rail_run.py --tag NEW_UNIQUE_TAG --reuse 20261116_rail_native95 --steps 400 --duration 4 --tension .0001
$PY tools/film_rail_native_run.py --tag NEW_NATIVE_TAG --installed-sdk --reuse-installed 20261116_installed_control110 --free-motion --sphere --sphere-x 95 --steps 100 --duration .5 --tension .001
```

Do not rerun completed tags. The native command is experimental, NOT an
approved grasp recipe. Every campaign contains exact command/process/raw/hash
records. Actual-state plots are under designs/visualizations/contact_dynamics_
20261116_actual56 and film_rail_20261116_actual94; no displacement magnification.
No PET/TPU/pressure/friction/actuator values were measured. All material and
control inputs remain research assumptions; final construction choice deferred.
