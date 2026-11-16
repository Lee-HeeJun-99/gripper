# Autonomous research log

## Profiling continuation and rejected optimization

Actual profile28:150steps cost50.859s; force/damping39.406s, gradient/RHS9.862s,
linear solve1.399s, mapped mass product.00724s. Nested residual timing includes
force/mass: do not double-count it. Instrumentation preserved every CSV value.
A runtime gradient-only AD experiment preserved exact state/force/energy, but
cost94.966s (1.867x slower), shifting work into repeated Hessian evaluations.
It is rejected as an optimization; default AD and FilmShell were restored and
cleanly rebuilt/tested in final30. Failed code is retained in Git eebbb45,
campaign29/sources and the archived test under reports/film_newton_experiments/.
No original model/raw/Golden was removed. Full time/grasp Gate remains FAIL.
Next cost research should first count accepted/rejected force evaluations or
test element-local derivative dimensions/compile-time specialization, against
both mathematical equivalence and actual runtime; do not repeat runtime flags.
All launched runs are complete. There is no claimed background continuation.

## Follow-up after the first corrections — alternative hypothesis tested

Did not stop after fixing Newton. Implemented and actually tested hard slope
mapping with conservative force/mass pullback, fixed mapped residual defects,
then completed200/400/800-step dynamics. All Newton solves reported convergence,
but the complete time Gate still FAILS. Independent mapped FEM agreement PASS;
unmapped regression unchanged below8.7e-19mm. Hard/penalty waveform comparison
argues against the large root penalty as dominant cause. Phase-resolved actual
data instead show the largest discrepancy after first sampled contact1.41s.
The common frictionless film problem and friction-history temporal problem are
separate. Further brute-force refinement would exceed default per-child budget
at1600steps with this mapped implementation; profiling/short diagnostic next.

## 2026-11-16 — actual Newton-stage investigation and continued implementation

First compared public SOFA residual/update code with actual force-stage
RHS/solution/state data. The first RHS and linear solve were consistent, so a
blanket stiffness rewrite was rejected. Found tolerant Vec equality in a
force cache, old-position tangent assembly, and unscaled position increments
during BDF line search. Added targeted regressions and independent BDF solver.
Actual 20 s 11/21/41 scenes now remain finite with final relative force residuals
3.62e-9/4.26e-7/1.76e-6. Did not stop at endpoint success: full trajectory
assessment exposed large transient errors. Tested trapezoidal and BDF2;
neither passed all trajectory metrics. BDF2 implementation itself matches
independent FEM below 2.89e-10. Tested hard slope mapping as a separate boundary;
its first SOFA failure isolated mapped-mass pruning and duplicated mapped
force accumulation. Corrected independent residual products; short mapped
Newton warnings decreased four→zero. Next hypothesis is stiff-boundary versus
contact-event temporal error, not arbitrary damping/material tuning.
Existing images/Golden/raw/SDK preserved. No physical grasp advantage claimed.

## New actual work — film energy/contact,source guards,and failed alternatives

Implementedstructuredmembrane+curvature/twistROM,AD2,actualSOFAForceField,
clippedplanearea/pressureinventory,rootfixtureanddisplacementDOFs. Unit/APIand
independentplate/cantilever PASS. Actualsame-volumecouponcontactimplemented;
notbaseline3fingergrasp. Discoveredandfixedrequested/actualSolverXMLbug,retained
allpriorrawandrelabeledscope. Nonlinear/dynamicfailuresretained,notjusttipPASS.

Comparedsudden/rampedload,rootboundary,Newtonstopping,stableGreenstrainand
absolute/displacementDOFs. ThesealternativesdidnotcloseactualdynamicsGate.
IndependentfullNewton200/400finishwith~1e-13residual;100failsNewtonlimit.
FirstactualfreeglobalmatrixmatchesAD+mass/damping5.58e-17,sofirstassembly
mismatchhypothesisrefuted;nextactualnonlinearRHS/stateauditselected.
New exactgreat-circlefrictionwork70digitreference narrowslossquadrature but
isnotgeneralSOFAlaw. Source38f3966,b86e305;detailsFILM_SHELL_PHYSICS.md.

Same-corevolumeskin+railgeometry,backingoffsetv2,3Pythonchecks,4existingdesign
regressionsPASS. Competitiontechnicalbasisand11separatesupportdraftsections
fitusercharacterlimits;unknownactuator/team/hardwareperformanceexplicit.
NoSOFAgraspOptuna,hardwareorremotepush. NoOSresourceexhaustionobserved.

## Additional actual development — sphere events and failed temporal alternative

Implemented SphereEventReturn.h,SphereEventBenchmark,unit/API tests and bounded
SOFA/prescribed runners. Exact chord sphere roots + implicit derivatives include
birth/death/transit;grazing and undefined normals reject. Unit FD2.54823e-10,
rotation/no-contact/grazing and discrete energy identity PASS. Source commit1108fad.
Hypothesis:missing birth event dominates temporal loss. Actual32substepSOFA
20→80error2.32535%;identical no-Solver2.32532%. Refinement128then512reduces it
but512SOFA0.146423%stillFAIL. Adjacent pairsPASS do not approve fulltimeGate.
Thus birth roots alone insufficient;next focus on evolving-capacity loss/work
integration,not Solver tuning. Old results unchanged. Full derivation/caveats and
commands:TEMPORAL_SPHERE_EVENT_RESEARCH.md. Immutable ledger853filesPASS.

## 2026-11-16 — physics + differentiated design workstreams

Resumed clean b3ed788,same branch;general_manifest_v1 1737artifacts integrity
PASS. Original models/SDK/raw preserved. Implemented NEW MovingReturn.h:
active-contact normalized-normal-chord/affine-capacity/affine-displacement path,
substep circular return,all intermediate history AD propagated to endpoint.
Independent FD1.03955e-10,discrete friction identity1.80041e-23,covariance
2.1684e-19PASS. This is not event-exact CCD or a Birth/Death/patch owner.

Actually compiled and loaded MovingSphereBenchmark into matching SOFA SDK.
Canonical04API F/dF/matrix/purity FD9.54367e-13PASS;actual20/40/80step supported
sphere/one-point dynamics completed. Maximum phase plastic relative difference
1.77531e-5(.00177531%)PASS.1%. Different physical configuration from old free
sphere/Hermite test:its.8519%FAIL is NOT reclassified. General Curved adapter,
Birth/Death path and adaptive spatial history compression remain unfinished.
Failures preserved:initial abstract/API build,missing initExternalModule plugin
entry point,and inherited geometric sqrt guard wrongly rejecting tiny positive
plastic norms. Robust hypot+its exact derivative fixes the last,no heat cutoff.

Extracted baseline from existing source AST/coordinate formula:100mm,3fingers,
2layers,root radius95.148mm,guides. Generated tapered24→12mm film candidates,
8assumed.05mm layers,50mm body,dual edge tendons and3shared zone circuits.
Actual OBJ315vertices/480triangles and matching inlineXML load into SOFA PASS;
mesh loading is NOT shell/contact performance. Generated front/side/top/isoSVG,
section/mechanismSVG,prescribedsequenceSVG and geometry-derivedPNG. Initial
MeshOBJLoader failed because matching SDK lacks IO.Mesh;v2inline same geometry
passes without ABI mixing. mplot3d namespace mismatch bypassed with pure2D
projection of actual3D data,not a new geometry or fabricated SOFA state.

Numerical design screen reveals material-volume5.73588xbaseline,so no fair
performance advantage is claimed. Equal-volume thickness8.717μm may be hard to
fabricate. Constant-widthEB assumedstiffening16 givesproximal30mm effective
ratio2.60374,not pressure calibration or actual tapered-shell result. Prescribed
curl.77stillhas.306284mmgap;firsttouch.776699rad/draw1.16505mmisgeometry-only.
Four design regression tests PASS;all old full-grasp/energy/Optuna Gates retained.
See REGRIP_DESIGN_RESEARCH/COMPARISON/PROTOTYPE_PLAN/FINAL_DESIGN for actual
designs,prior-art overlap,manufacturing risks and still-unselected final design.

## Latest regression and inertia control

Source-matched06repeat20step actual journals are identical(absolute differences0).
Current03six-test independent regression PASS,including vector temporal-event
common-frame covariance1.11022e-16. API/build/wrench verification is pinned to
verified06actual compiled.json/source copies,not inferred from later Git HEAD.

Audited SDK RigidMass serialization and separated the initial defaultI/m=1
numerical benchmark from explicit solid-sphereI/m=.4 atR=1. The latter ran actual
20/40/80steps with noERROR;phase-loss time FAIL.851917%remains. Do not label
the old default-inertia condition a physical solid sphere or mix these cohorts.
Endpoint frames use declared research inertias,not a validated beam mass model.
Neither condition is the100mm gripper. Assessment rejects mixed inertia models.

All launched children have actual completion records. No host resource exhaustion
was observed;this checkpoint is incomplete research,not final-goal achievement.
The remaining changing-normal temporal law and adaptive state compressor are
real unfinished implementations. No automatic restart/background continuation
is installed or claimed. Follow latest NEXT and new immutable general manifest.

## Newest measured continuation — adaptive integration isolates temporal defect

Implemented consistent adaptive material quadrature in the NEW actual SOFA
adapter,then continued beyond its first PASS. Verified05actual integration
.02/.01/.005mm contrasts PASS including each aligned phase plastic increment;
max phase relative difference9.40617e-9. Actual smooth sphere Force/Jacobian
FD1.18994e-13,total internal wrench8.61292e-22. No compensating torque added.
Initial radial-normal torque estimator and componentwise nearzero force-scale
failures were isolated and preserved;vector force/moment budgets now remain
separate from each energy/loss budget. Exact unchanged-configuration identity
prevents repeated rounded projection at postcommit,no physical loss floor.

Did NOT stop at this integration PASS:actual20/40/80step temporal contrast
FAILS small-phase loss(max.851919%)despite cumulative.0642703%<.1%. Ran an
independent prescribed-geometry control without SOFA/Solver. First fixture
omitted initial active-contact transaction and FAILS;fixed SAME initialization
as SOFA prepare(),time02COMPLETES and reproduces.851935%phase FAIL. This
strongly narrows the dominant mechanism to temporal return/capacity treatment,
not a Solver explanation alone. Physical Gate remains unchanged and FAIL.

Then implemented/tests scalar variable-capacity event-work analytical reference:
endpoint-capacity errors.108990/.054957/.027594%at20/40/80(first order);
event-integrated capacity work<6.46e-15relative error. This is not inserted
as an unjustified3D dissipation formula. Continued with TemporalYield.h:
256vector fixed-plane affine first-yield roots and IFT derivatives,root
4.24e-22andrelative FD4.01e-9PASS. Fixed-plane tangent projection is included
in AD;already-yielding/no-event/ill-conditioned branches are explicit. Changing
normal/full vector temporal integration is still unfinished,not certified.

Fresh bounded clean build+owner+actual SOFA API+wrench PASS:
results/vector_history_owner_20261116_verified06. Independent latest-six-test
regression is results/vector_history_general_suite_20261116_current02. No prior
long Hermite/11/21/41campaign rerun or grasp Optuna was launched. All outcomes
are research assumptions/math or actual SOFA,not material measurements.

## 2026-11-16 — actual general moving-history continuation (not completion)

Same branch resumed e151c278;clean tree confirmed. Old vector v1 integrity
4203artifacts/41blobs PASS;old curvedv2 4945/149 PASS. No old physics restarted.
Implemented independent models/general_vector_history Owner and registered
GeneralVectorCurvedContact. Exact functional history is independent of force
quadrature;immutable geometry and original Birth/return law are reused. This is
a finite128operator reference,NOT the still-missing adaptive general state fitter.

Actual moving sphere owner2910states matches explicit material-point prefix
exactly;death/recontact/query purity/stale commit controls PASS. Moving-normal
common-frame covariance2.1272e-16,111slip states,chart seed/budget guard PASS.
Actual SOFA API/FD force,dForce,matrix/query/commit PASS in midpoint/Gauss modes.
Short free sphere/Hermite dynamics20/40/80steps COMPLETE;source-matched
contact-observable dt→dt/4plastic difference.0551516%PASS.1% including aligned
phase-loss checks. This is NOT full gripper motion/energy/time qualification.

Independent integration contrast FAIL:midpoint.02→.01mm changes loss~4%;Gauss
also leaves small-phase FAILs. Thus removing history interpolation did not solve
contact integration alone. Added experimental adaptive material quadrature.
Initial cell-local relative estimator FAILS a positive-part analytic front.
Global measure-scaled width budgets resolve the same front to3.07278e-9relative
even at1e-20amplitude,without a heat floor. Actual first sphere adaptive failure
then isolated to roundoff normal-torque estimator(global~1.35e-23);sphere radial
normal torque is analytically zero,so only the estimator uses that identity.
Actual assembled force/torque remains untouched. All failed raw/builds preserved.

Raw:results/vector_history_owner_20261116_moving01/02,gauss01,adaptive01/02/03;
results/vector_history_moving_20261116_*;compare_20261116_*;frames_20261116_a01;
material_rule_20261116_a01/02;rule_geometry_20261116_a01/02. Actual summaries,
not historical RUNNING prose,determine current process/validation status.
Full adaptive state fitting,3finger qualification and grasp optimization remain
unfinished;continuation experiments are described in newer entries as they finish.

## Subsequent development — actual sphere capacity/material jet

Did not stop at the vector-patch qualification:implemented SphereHistoryChart.h
and bounded independent runner curve_general_reference.py. The immutable old
Hermite geometry supplies a spatially varying sphere normal and
capacity=mu*kn*(R+skin-|r(s)|). Tangential history is projected/normalized in
that actual tangent plane;first/second material jets use existing unchanged
Beam Taylor algebra. This removes the PARABOLIC assumption from this chart's
derivation,but is NOT the complete moving-contact SOFA adapter.

Two failures retained:manufactured active-fixture geometry was wrong once
Hermite director sag was included;then strict covariance1.66533e-16failed
1e-16. Computing relative Bezier controls before interpolation reduced that
error to7.71952e-17 without relaxing the line.129active states PASS:elastic
first FD9.29132e-12,second FD1.87758e-11,capacity first FD1.15255e-14,
normal orthogonality1.19855e-19,Coulomb excess0. NaN,undefined tangent and
exact contact-event rejection also PASS in sphere_chart04.

All current children completed. Remaining work is the actual adaptive
general-history owner/Commit and curved SOFA force/Jacobian integration,
not another repeat of the now-tested chart or fixed patch. No host OOM,disk
or permission failure occurred;27GiB available RAM and1.1TiB disk were
observed. This response's finite working-context checkpoint is NOT a claim
that the project is complete or externally BLOCKED. No automatic restart.

## Latest measured result — continued beyond first patch campaign

The normalized cubic phase-boundary failure was reproduced and corrected by
an admissible linear-gap fallback,without changing physical state thresholds.
Actual noncollinear SOFA100/200/400steps completed115.056/227.369/455.897s;
the quarter-step run was actually completed under480s,not extrapolated.
Its costly rational predicate motivated a NEW equivalent arithmetic prefilter:
each finite binary operation is enclosed by outward representable neighbours;
only conclusive Bernstein signs bypass rational work.384exact coefficient
checks and257material-interval exact-predicate checks PASS. No loss is clipped.

Actual20/100/400step and50step reversal journals are ALL-VALUE identical with
and without prefilter. Actual fast100/200/400times3.5717/5.8295/6.7775s.
The finer-history100case took6.4769s. Repeated100journal is exactly equal.
Base→quarter loss.01805761%,x.00032505%,y.00103590%PASS.1%;finer history
loss.00034348%PASS1%. No qualified three-finger improvement is inferred.
The updated dense reference exposed coarse-grid zero/nonzero small-loss cases;
an initial assessor infinity serialization FAIL is preserved. New outputs
explicitly report that diagnostic,not a fabricated zero or false PASS.

Next selected research was the moving material-coordinate chain derivative:
implemented MaterialDerivative.h and AD Taylor lift.257manufactured cell
states agree with unchanged Beam Taylor algebra and finite differences;
first derivative FD error3.855e-15,second chain FD6.748e-16. An initial C++
vexing-parse compile FAIL was fixed and retained. Cell boundaries explicitly
reject an undeclared classical derivative. This is a prerequisite,not an
already integrated moving-curved-contact force law.

Constant-frame vector-history covariance771states through3rad also PASS.
All references/actual physics finished;none automatically restarts. The
remaining integration requires nonparabolic normal-force capacity and varying
contact frames/Birth/Death on the original material coordinate. The current
parabolic fixed-patch helper cannot be silently substituted into the gripper.

## 2026-11-16 continuing checkpoint — actual integration,not goal completion

Same branch retained. The earlier premature campaign stop was an agent choice,
not evidence of a host/session limit. This continuation has implemented and
executed vector-history SOFA code. The full ReGrip objective remains unfinished.

Actual fixed-patch Newmark projected-cubic runs completed100/200/400steps in
23.559/45.998/91.128s. Base→quarter movement difference.0049881%,plastic loss
.0155430%PASS the unchanged.1%time line. Independent analytic monotone-return
loss and actual repeat200(all common CSV entries exactly equal) also PASS.
This is a prescribed fixed-normal tangential patch,NOT a three-finger grasp.

The first Newmark energy assessment incorrectly assumed fresh acceleration
each step. The actual SDK cpp retains acceleration;its independently
reconstructed recurrence satisfies the matrix equation to9.23e-14relative
and the measured fixed-patch energy identity to5.18e-24Fmm. Cached-acceleration
work and signed return/linearization terms are explicit,not relabelled heat.
The previous incorrect assessment remains immutable beside its correction.
SDK source-file SHA256:c08a2786b9cb38b1a02b6835cfb76a8be55c70e19b19ed7fd268acdd052457a4.

The noncollinear projected-cubic100step attempt actually timed out480.004s
after60completed steps. Exact-sign range caching was independently checked
at257points but its20step profile still took72.023s. No unearned speedup or
full-duration PASS was claimed. The fixed-time failure motivates a different
representation,not a larger timeout or loss cutoff.

Independent normalized gap/direction history:linear version passed five
strict adaptive-reference loss probes(including1.0562593e-26Fmm) but required
5620cells and exhausted8192cells in the1e-11mm SOFA API fit test. Cubic Bezier
controls reduced the standalone case to481cells/11084source queries,withheld
state error5.89444e-10mm,zero phase mismatches on131072withheld points. All five
strict loss probes PASS1%;the tiny-loss relative error is4.25173e-9. These
are independent mathematics,not grasp certification. Actual normalized cubic
SOFA API tests PASS,including force/Jacobian/query purity. Its first dynamic
attempt failed at step11 after10commits due to an inadmissible cubic gap
control near a phase boundary. That failure is preserved. A shape-preserving
linear-gap fallback(no clipping of physical state) and exact-query memoization
are under bounded SOFA revalidation in a NEW output directory.

Raw:results/vector_history_*;unchanged original models/golden/SQLite/SDK.
No automatic background restart exists. Live status must be read from tools
and completed summary.json,not inferred from historical RUNNING text below.

## Latest — adaptive state attempt and explicit bounded failures

Completed directed Newmark200steps119.875s:dt/2motion.000833938%,D.00259944%
PASS.1%in this fixed-patch isolation ONLY. Exact prefix-operator memo gives
bitwise same ALL CSV values but119.563s:the speedup hypothesis is NOT supported.
Did not blindly run400steps with an unjustified default480s budget.

Implemented independent AdaptiveSnapshot cubic vector FUNCTION plus circular
admissibility projection,with energy inventory change and prospective return
loss checks,not force-only fitting. Dense131072point tests exposed coarse
58.14%/2.668%loss FAILs. Fine471cell withheld state5.16291e-10mm meets1e-9;
observed representation energy change1.61591e-18Fmm,NOT friction heat.
Dense prospective loss alone appears to pass(.05964%worst),but the stricter
adaptive reference FAILS. This prevents a false SOFA rollout.

Preserved distinct failures:seed01depth44;seed02depth60then500000budget;
seed_local01local Lipschitz/partition;seed_relative01aggregate loss bound;
seed_reintegrate01same TOTAL budget including discarded passes;
seed_fronts02degree6/10front partition. No failed output overwritten.
Latest seed_diagnostic01 pinpoints quantity17(unresolved-loss upper bound),
last error6.32955e-28 vsallowed1.15620e-28 near x.9636128864;
resolved D4.73578e-18,unresolved sum1.59831e-24Fmm. It is a conservative
bound/representation certification blocker,not observed physical dissipation.

Independent Boost50decimal conditioning probe72samples actually FAILS4branch/
1%loss cases,max absolute loss DENSITY difference1.82610e-29F. This supports
precision conditioning near yield,NOT a proof of sole root cause. All failed
diagnostic source/binaries/logs are retained. Next distinct method selected:
cell-wise polynomial sign certification with explicit equality/rounding handling,
not another blind point budget increase. Adaptive snapshot is NOT connected
to SOFA or approved for grasp. Actual current-source clean SDK/API/20step
uncompressed Newmark smoke PASS;no3finger/global-energy/Optuna claim.

## Continuation — actual vector-history SDK benchmark and failed time gate

New fixed-normal VectorPatchBenchmark is a real separate SOFA ForceField,
NOT3Dcollision/free-grasp approval. Data registration/parsing,actual F/dF/
matrix,stored-energy query purity and5historyCommits pass;API FD6.71741e-11.
Each matching-SDK build/raw has unique vector_history_sdk_20261116_* path.
Compile/API/actual-dynamics failures a01/a02/a03 are retained. Actual a04
100step16.808s has100Commits/state changes/nonnegative D. Cache and stage
journal contrasts match every common CSV value EXACTLY. Local energy residual
2.26e-27,actual force residual5.40e-15;inventory quadrature gap9.48e-20 is NOT0.
Euler100→200steps ACTUALLY FAIL.1%:x.364449%,D1.140386%. Actual200step107.432s.
Noncollinear initial-velocity contrast17.201s also executes100steps;assessor
refuses mixing its initial conditions into a time comparison.

Selected follow-up:distinguish temporal scheme/selected generalized tangent
from material-history spatial error using SDK Newmark,not another uniform
history-grid refinement. Two independent directed attempts FAILED first:
500000sample unloading bound exhaustion,and direction-dependent quadrature
force roundoff. Derived admissibility-square bound and separate directional-J
integration remove those without changing the force law or threshold.
One-sided mathematical FD2.94588e-9,SDK directed cache test passes exact F/D
invariance. Positive-yield derivatives remain explicitly nonclassical.
Actual directed Newmark100steps13.087s completed;200step same-condition child
is currently being measured. This is only a fixed-patch isolation study,
not the requested3finger model or a solution of moving contact/birth/death.
ConservativeBeam/oldCurved/plugin binaries/golden/SQLite remain unchanged.

## Active continuation — vector function history,2026-11-16

Resumed same branch at clean fb6a698,no existing physics child. Both inherited
indices actually verify4945/149and34/3,zero errors. Completed Hermite/mesh
campaigns were not rerun. No host exhaustion was observed at startup.

Implemented independent VectorReturn.h/VectorField.h and bounded fresh-output
curve_vector_reference.py. Fixed-normal circular vector return,exact
function-valued return composition,query purity and epoch Commit;not yet SOFA.
Actual return600statesPASS(FD1.55721e-12). First field a02/a03/a04FAIL unresolved
yield front. Diagnostic a04localized zero initially sampled OFF-DIAGONAL
tangent scale;global embedded budgets update from newly observed components.
a05passed the weak positive-tiny-loss test,but a NEW analytic test genuinely
FAILed:17.1718423%relative loss. Tightening tolerances alone FAILED identically.
Exact virgin constant-vector yield-root domain split corrected that case:
2.62427e-9relative error,loss1.98264694562e-37Fmm. No tiny-loss cutoff used.
Actual validation01PASS independently compares65536plastic-vector points,
20exact scalar-history steps,field tangent FD1.98887e-11 and endpoint balance.
Raw snapshots/failed logs preserved in results/vector_history_20261116_*.

Next selected work:objective vector transport,function-field covariance and
general stateful yield-front error control;then bound/profile expression-history
cost before any SOFA deployment. Reference4096step cap is NOT production
qualification. Scalar/old3Dmodels,all physics thresholds and Optuna gate remain.

Baseline63970172ad196e0add3ad42a67ccaee4c7a8975e,clean worktree; requested branch
created. Actual environment remains Ubuntu22.04.5/GCC11.4/CMake3.22.1/Python3.10.20.
Existing birth assessment reproduced and1845raw/source/binary hashes passed.

## Hypothesis1 — state/measurement discretization mismatch

Inspection: old `compute` integrates plastic return at interpolated active
Gauss points; `commit` instead returns and stores nodal material states.
This does not prove an implementation bug,but dissipation measured at a different
state discretization may not represent the actually committed plastic flow.

Selected contrast: fixed material-coordinate midpoints,with force/return/Commit
and dissipation at the same immutable reference points;no history interpolation,
no zero boundary anchors. Normal active-interval Gauss and constitutive birth/
Coulomb/transport kernels remain unchanged. This is an independent numerical
model,not a replacement or a claim of a new exact continuum solution.

Planned falsification: analytic uniform plane slip,actual field Jacobian/API,
Commit/query purity,then same physical three-finger profiles and independent
history/mesh/time tests. Spatial integration error remains and must be measured.
No grasp optimization is authorized by unit success.

## First measured results

New v1 compilation failed in test code(unqualified pose helper);v2 unit initially
compared separately accumulated AD/scalar totals for exact equality instead of
checking the before/after state of a pure query. Corrected the assertion to its
actual contract,not a physical gate. Both failed logs remain. v3 source snapshot
and clean build pass;analytic plane D=.000051,actual field FD6.84e-10,API/query/
Commit checks pass. First failed test-source snapshots were not archived before
correction;their reconstruction limitation is explicit. Subsequent snapshots
are automatic before build. No claim of early failed-source certification.

Prescribed moving Sphere contact(no Beam or ODE) identifies an actual energy
representation jump at old-model Commit:at h.005/200steps signed sum-1.27181e-7;
new material points give about-4.4e-20. Old jump quadruples with doubled spatial
spacing and doubles with doubled step count in this test. New queried plastic
and actually committed plastic match. This supports the mismatch mechanism but
does not by itself establish the full3finger cause or global energy closure.

Actual4s profiles31.16s(coarse)and49.56s(finest) justify four bounded history
runs,all4GiB/480s. Their full convergence results are still under evaluation.

## Measured SOFA contrast and priority update

All four history runs finished. Immutable material points make actual committed
plastic return and recorded plastic return identical,including birth and death
counts. Same-hold cumulative loss differences are .129703%,.279753%,.049621%
for h=.01/.005/.0025/.00125,all below the original1% line. Motion differences
are4.61737%,1.01697%,.0300247%;the first two remain FAIL. Thus the hypothesis
is supported for the loss/state mismatch,not as a complete convergence cure.

Repeated fine run has exactly identical hold motion and loss.11→21→41nodes
still gives4.95984%,2.80102% translation differences,FAIL1%;rotation and loss
differences are smaller. Local hold force/moment gates pass,not global grasp
certification.24s base and fine-repeat recover/release;18s cases cannot certify
the complete24s sequence even though their local hold gate passes.

dt-half on the fine history has motion difference.0977366% and loss difference
.0999735%,both narrowly under.1%. A4s quarter-dt profile151.79wall seconds
predicts683.07seconds for18s. One bounded900s exception,4GiB,was selected to
test whether that borderline result is robust.41node profile133.92seconds
similarly justified a single900s run,which completed in635.76seconds. No
unchanged failed high-resolution campaign was blindly relaunched.

## Independent falsification and partial energy

Prescribed geometry calls actual old/new ForceField APIs with no Beam/ODE.
New maximum absolute pre/post Commit energy jump8.70e-20 vs old1.02e-6;
new queried/committed D agree exactly. Both old and new loss converge below1%
on this simpler path,so it does NOT prove every old full-model error has one
cause. Endpoint work residual decreases with smaller dt but remains nonzero.
It is not labeled friction or fitted numerical heat.

A seeded10000step scalar spring-slider test verifies the DERIVED identity
W_endpoint−ΔU−F1Δp=.5k(Δe)^2 with max residual1.02e-17. This scalar capacity
model includes no vacuum-chamber work and cannot close global SOFA energy.
Actual native-driver birth/no-contact scenes pass;resolved through-chord
contact is explicitly rejected as expected,not accepted as physical success.

## Next hypothesis: contact centerline interpolation

Fixed cubic cantilever geometry gives linear-centerline normal-integral errors
4.834%,1.468%,.1049% at11/21/41nodes against independent SciPy quadrature.
The prescribed cubic Hermite representation reproduces that cubic. Offline
reconstruction of actual SOFA states gives linear/director-Hermite normal
integral differences3.085%,.1008%,.04865%;these are NOT re-solved equilibria.
This motivates a kinematic investigation,not an attribution of all remaining
Beam nodal-solution error to interpolation.

Implemented a separate objective director-Hermite virtual-work pullback kernel,
including nodal torques,geometric tangent and left-SO(3) connection.60states
pass FD1.56e-9,normal-energy derivative3.47e-10,objectivity6.11e-16 and
force/moment1.73e-17. Sparse analytic assembly agrees with dense AD2 reference
within2.78e-17. It is NOT integrated into SOFA contact yet;linear current
campaign remains unchanged. No production speedup is claimed without profiling.

## Preservation correction and regression

During tool addition an existing tools/research_trial.py name was accidentally
reused. Restored its exact6397017content and moved new runner to
tools/autonomous_trial.py. Hash-based preservation test passes. First campaign
commands using the old path refer to the intermediate621266c source revision;
reproduce via the new runner path. Historical physics/raw/golden were not edited.
The restoration is retained in Git history,not concealed by rewriting commits.

Python89tests and3existing C++ suites pass;new actual Beam61state and dense100
equivalence checks pass. Two independent600step FREE golden runs pass all
9recorded metrics with unchanged1e-10+1e-6|reference| tolerances. The original
45physics gates are not rerun or expanded into new-contact certification.

## Final temporal cross-check

Quarter-step completes679.151s/144000steps,actual queried/committed D equal,
local hold force/moment gate PASS. Half→quarter motion.015950% and loss.074528%
pass.1%. However base→quarter accumulates.113702% motion and.174427% loss,
both FAIL.1%. Added the nonadjacent cross-check instead of presenting adjacent
PASS as full base-dt qualification. Hence time remains incompletely qualified
alongside the independently unresolved spatial error. Quarter-step detachment
inventory relative differences also remain large;no global energy claim.

## 2026-11-16 actual continuation,not a completed research objective

Termination audit:the previous turn had no recorded session/resource failure;
all children had exited normally. Ending at the campaign checkpoint was the
agent's own premature decision,not a forced stop or achieved final objective.

Implemented independent models/curved_contact with the verified Hermite
virtual-work map,physical nodal torques,consistent spatial Jacobian and a
conservative4/27director sag envelope. Both normal and tangent use immutable
material midpoints;the prior models/builds/raw remain unchanged. API FD6.27e-10,
90actual ForceField covariance/force/moment/Jacobian checks pass. Independent
curved normal integration reference converges. Initial CMake dependency and
namespace compile failures are snapshotted in new campaign build_v1/v2;v3passes.
The copied v3unit test has a nonphysical multi-character-newline warning;
it is not claimed warning-free. No physical threshold was changed.

Actual18s11/21/41runs completed252.37/394.69/722.51wall seconds. Keeping the
inherited all-node layout gives6.0498%/2.6847% translation differences,FAIL1%.
Hold local force/moment gates pass. Half-dt motion.077264% and loss.073839%
pass the adjacent.1%line,not a complete temporal certificate.

New cause found in source/XML audit:LayerNetwork stiffness is explicitly a
POINT stiffness,while empty connectorIndices creates all nonroot nodes.
Refinement changes10→20→40connectors at unchanged k=1 and kn=.001;total
elastic couplings double. Cable guides also change11→21→41. These old
comparisons are therefore not pure Beam refinement at fixed physical layout.
Their numerical FAILs are retained,not rewritten. Added fixed10mm connector/
cable-guide controls and separate one-factor ablations,now actually running.
No stiffness scaling or fabricated compensating force is used.

Also testing strict-FP native ISA build(no fast-math,reassociation or FMA
contraction)against actual generic raw states before any cost-qualified
quarter-step run. At most4long physics children;each4GiB/default480s or
profile-qualified single900s attempt. No automatic restart is installed.

### Continued measured diagnosis and21node candidate

Fixed-layout ablations do not remove the coarse error:10connectors and11guides
give6.596%/3.298% motion differences. A derived reference-length tributary mass
quadrature,without changing total mass or per-mass inertia,gives actual peak
motion4.84330750e-6/4.92195155e-6/4.94290540e-6mm at11/21/41nodes.11→21
still FAILS1% at1.598%;21→41PASSES at.423918%. Thus21is a resolved candidate;
11is not silently certified. A pre-recorded modal-mass proxy predicted the
trend but is not a force correction or measured trajectory. Source/scene audit
and one-factor connector/cable controls are preserved in the new raw campaign.

Recompiled unchanged Beam and contact with strict-FP native ISA(no fast-math,
no FMA contraction). Kernel/API/dense-reference and actual4s raw equivalence
PASS exactly. New single-runtime-pair21node campaign actually confirms mesh,
history(.0025→.00125),repeat and24srelease/recovery. Half-dt motion passes,
but cumulative friction-loss difference.160535% FAILS.1%. Quarter-step profile
predicts1164s before margin,so no full quarter-step single process was launched
under the900s policy. ISA optimization and scalar EigenSparseLU storage were
tested,not assumed;the storage contrast gives no measured speed improvement.

A new root-level pre-child-Commit/post-all-Commit journal now executes in SOFA.
2000steps produce6000stage rows with exact unchanged X/V/R. Actual contact
Commit energy jump4.85e-27 and layer jump0. Derived Euler kinetic-work identity
uses actual force/Jacobian/mass,Rayleigh terms and velocity projection,with max
absolute residual3.44e-21 in the1s test. This is NOT stored-energy closure;
pressure/friction accounting remains explicitly null. v2journal failed because
the ODE lives on the parent node;v3uses SearchUp. Failed snapshots/logs retained.

Independent actual-state normal integration(v2reference) has about3e-6to6e-6
relative error,well below1%,separating normal quadrature from friction state
error. v1reference is explicitly invalidated:a NumPy trimmed-polynomial
broadcast bug was found and fixed without overwriting its source/results.

Next executable research:validated full mechanical/history checkpoint between
bounded children,so the SAME144000step quarter-dt problem can run without a
process exceeding480/900s. This is not yet implemented or certified,and is NOT
an automatic session restart. q/v,time,contact history,layer plastic state,
cable rest lengths and counters must round-trip and match uninterrupted SOFA
before any chunked physics result is accepted. No existing physics is changed.

### Continued actual experiments: restart,return energy and bounded quarter dt

Checkpoint v2/v3 were actually implemented and FAILED the8s path equivalence
test. All q/v/time,reference geometry,contact material state,layer plastic state,
cable rest lengths and counters are serialized with hashes. Restored total force
AND public assembled force Jacobian agree EXACTLY. Nevertheless max8s X/V/R
differences are1.41068e-8/2.06759e-7/3.39792e-10. These are failed diagnostic
results,not approved restart physics. A v4 public actual linear-system comparison
isolates the first resumed step:MBK differs1.73472e-18,RHS0,solution1.09759e-25.
This supports roundoff/assembly-history amplification at nonsmooth friction,
without establishing that every possible state omission is excluded. No engine
private state is touched;symbol-hidden bridges only read/write public OWN model
state. Uninterrupted quarter-step dynamics are used instead.

An explicit one-attempt1320s exception was recorded BEFORE execution from the
actual258.7566s4s quarter-step profile(1164.4s predicted18s).4GiB/≤4children
remain. Original900s blocked decision is preserved. This is a bounded
profile-supported exception under the user's exception policy,not an observed
environment timeout,physical threshold change or automatic session restart.
Full18s quarter run is active;no result is assumed before completion.

Actual root-level synchronized journal now covers8s(cable/pressure/torque):
16000transactions,48000rows,X/V/R exactly unchanged,max kinetic algorithmic
residual1.47501e-20. Global stored-energy closure is still BLOCKED.

Derived an independent identity of the EXISTING tangent radial return:
U1-U0=kt e1·d-cap|p|-.5kt|e1-T e0|². The endpoint projection is mathematically
derived and separately labelled,not fitted heat.2000independent states PASS.
Actual read-only pre-Commit SOFA journal:16000steps,852births/39deaths;
plastic4.82067560e-11,endpoint projection9.30527841e-13,detachment6.02313505e-18,
max weighted identity residual2.63344e-26,X/V/R exactly unchanged. This local
material-frame identity is NOT equivalence to global nodal work.

Matched actual8s energy journals expose -5.42552e-9 unexplained balance before
unmeasured pressure/geometry/nonlinear terms. It is not assigned to dissipation.
A global-J quadratic proxy predicts5.34978e-9 but cannot be labelled conservative
energy because friction J is nonconservative. Therefore a new actual Beam-ONLY
quadratic-projection journal is running;the nonlinear remainder is explicit.

Independent1Dmonotone slider experiment shows the inherited endpoint-capacity
plastic-loss formula is first-order in time even with exact final plastic state:
relative error.883584%→.442184%→.221483%→.111133%→.055664%→.027857%.
An event-integrated reference matches the analytic work;this is NOT a replacement
of production loss or grounds to relabel the actual .160535% dt FAIL. Actual hold
loss is constant13.9–14in both runs,excluding mean-window sampling bias here.
Failed build v1(log-file collision),v2(protected accessor),v3(missing includes)
of the energy diagnostic are preserved;v4uses public API and passes actual run.

### Quarter-step actual failure selects structural summation experiment

The one-off uninterrupted18s run actually finished1101.4157s,exit0,no timeout.
It FAILS the original physical hold gate:global moment relative .0010318117
versus .001. All other local hold checks pass. Motion-only half→quarter and
loss .0361667% pass.1%,but this does NOT override the underlying physical FAIL.
Base→quarter loss .196644% also FAILS. No full-grasp approval or Optuna trial.

Hypothesis selected from the new evidence:the fine-dt global equilibrium floor
may involve lost structural position increments. Implemented an independent
CompensatedBeamTranslations component using the unchanged,previously tested
Compensated.h kernel. ONLY structural free global X/Z translations are included;
object,all quaternions,roots and guided Y are excluded. Non-roundoff discrepancy
or >2ULP change is rejected. This is numerical accumulation,not force/target
correction. Actual5000step SOFA scope test:object/root/rotation/velocity changes
EXACTLY0;structural analytical accumulated position recovered exactly,ordinary
Euler misses1.25056e-12mm. Actual coupled4s profile56.37s PASS;max adjustment
2.84217e-14mm. A bounded base/half/quarter contrast now runs. New helper means
new integrator identity:old motion/history/space gates are NOT transferred.

Energy diagnosis continued rather than ending at the quarter campaign:
read-only actual Beam,Frame and normal-contact Jacobian projections are measured
at BEGIN and potentials at END.8s v5 journal X/V/R EXACTLY matches baseline.
Beam quadratic projection5.00869e-9,layer1.12941e-11,normal2.52608e-10 explain
most of the raw -5.42552e-9 mismatch;their nonlinear remainders stay explicit.
Remaining1.52549e-10 suggests omitted algorithmic cable work because implicit
Euler uses f0+hJv,not just f0. A v6 actual journal now measures that term from
the cable's own Jacobian. No residual is relabelled heat;global energy remains
BLOCKED pending this independent calculation and full phase/time validation.

### Actual structural arithmetic and synchronized energy results

The independent compensated structural run has now ACTUALLY completed all
base/half/quarter18s holds:286.225/578.165/1164.952s,all physical checks pass.
Global moment relative1.99483e-5/3.22488e-5/6.21926e-5 is below unchanged1e-3.
No object/quaternion/root correction is applied. The standard quarter FAIL
is not overwritten.24srepeat353.111s passes recovery and identical hold metrics.
The new arithmetic model's half→quarter motion/loss comparison PASS;base
time-loss comparisons still FAIL. Independent same-half-dt11/21/41and finer
history runs are active,not inherited from the old numerical integrator.

Actual v6standard-Euler journal measures algorithmic cable work from its own
Jacobian.8sbegin-force active work4.2426349333e-6 versus Euler active work
4.2424824468e-6 differs1.52486561e-10,explaining the prior remaining mismatch.
With separately derived potential/velocity/return projections,the balance is
4.83156e-13;after explicit signed potential remainders,-6.21490e-14. None of
these remainders is assigned to heat. This does not certify full energy yet.

Added a validated observer stage AFTER the same live structural accumulator
but BEFORE every ForceField history Commit,using public remove/add scene APIs
while retaining forcefield order. Actual1s and8s paths match the independent
compensated baseline EXACTLY. v8same-run8s journal records material return and
Frame loss directly:derived balance4.51719e-13,explicit potential remainder
5.13990e-13,remaining-6.22707e-14,max contact return residual2.15350e-26.

New independent pressure-cap test separates U(s,z)=.5k(s-z)^2 from the returned
candidate energy. At fixed s,capacity2→1 releases.15=.10plastic+.05endpoint
projection;capacity1→.1 releases.0495=.009plastic+.0405projection. This is not
external mechanical pressure work at fixed stored state,and is not vacuum
thermodynamics. It motivates a read-only Frame-return bridge,not a new force.
Actual v9one-second Frame-return residual0,X/V/R unchanged. Full24s v9 journal
is now running under a900s allowance qualified by actual8s271.54s profile.
Null pressure/global closure fields are preserved until scope/phase/dt
qualification is finished. Original894artifact SHA verification still PASS.

### Continued actual execution: fine references,full-cycle loss and clock audit

The prior stopping reason remains an agent-selected checkpoint,not an observed
environment/session resource failure. This continuation has not declared the
ultimate project complete. The requested actual Hermite SOFA implementation
and11/21/41experiments are done;failures selected new research rather than a stop.

Structural-summation same-half-dt21→41motion.4162894%,rotation.0199916%,loss
.0654006% PASS1%;history.0025→.00125motion.1337257%,rotation.0085701%,loss
.0233980% PASS1%. Coarse11→21motion1.6242346% FAIL1%. Actual mesh41/historyfine/
mesh11wall906.907/841.724/420.194s;all original physical hold gates pass.
Own profiles qualified the recorded1080/900s bounded exceptions;4GiB retained.

Full24s energy v9 completed734.112s:48000steps/144000stage rows,actual X/V/R
exactly unchanged. Derived residual4.10813e-13;after independently computed
signed potential/return remainders,-1.45037e-13. Material/frame return maxima
5.9329e-26/3.9249e-33. Unknown/global terms remain NULL/BLOCKED,not zero or heat.
Value-only energy API versus AD600frozen-class states PASS(maxrelative3.700e-15),
but8s timings266.362s versus271.54s are not an isolated speedup benchmark.
Actual half-dt8s read-only journal495.893s,X/V/Rexact,remaining-3.16172e-14.

Additional full0–18s loss audit FAILS time.1% even though final hold comparisons
pass:base→half.734005%,half→quarter.269622%. Release16–18s contributes most of
the absolute error. These remain distinct from13.9–14s hold diagnostics.

Correction to loose earlier prose:actual frozen controllers are step schedules,
NOT ramps. CableON/OFF.5/16s;pressureON/OFF3/15s;external torqueON/OFF6/14s.
Every recorded clock bit-matches repeated SDK dt addition. Half-dt OFF events
14/15/16s are one step late;quarter-dt torqueON6s is one step late relative to
the unchanged controller1e-12 margin. This is input epoch roundoff,not a proof
of the source of all friction error.

Independent integer-index clock calls unmodified SDK mechanics and changes no
q/v/force or schedule margin. Unit recovers all4misalignments. Actual4s and24s
base paths X/V/Rexact versus old clock. Actual base24/half24/quarter18wall
346.019/675.151/1093.497s;all hold gates pass;24sbase/half recoveryPASS,quarter24
NOT RUN. Half→quarter motion/hold-loss PASS,but full-cycle loss.441979% FAIL.1%.
Clock error was real,but was not the sole cause;do not merge old/new grid data.

Independent normal-contact Rayleigh counterexample has positive stiffness
damping work. It does NOT establish injection on the coupled trajectory.
Actual public solved-MBK probe4s111.526s,X/V/Rexact;first4sampled free-system
damping matrices have positive minima. Full release17.1s probe is running to
falsify the hypothesis before any physical damping change. No damping change
has been applied. First probe configure(relative prefix)and incomplete-type
compile failed,then absolute matching prefix/header and warnings fixed.

Next experiment is an explicitly independent nonuniform time-grid contrast:
preserve half-dt until cableOFF16s,then halve/quarter only release steps. This
tests the identified release temporal error within bounded cost;it is NOT a
replacement for failed uniform-grid evidence. Dyadic clock math/build passed;
actual4s prefix equivalence is running before any full launch. Forcefields,
friction,loads,damping,all original physical thresholds remain unchanged.

### Falsified damping hypothesis and localized energy work discrepancy

Actual17.1s public-MBK probe completed523.994s with exact X/V/R equality to
the independent fixed-clock reference. All14sampled free-system minima are
positive(about1.49e-6to5.23e-6 after length congruence);projected mass is exactly
constant. These samples do not prove PSD everywhere,but do not support negative
coupled damping as the root cause. No physical damping change is justified by
this experiment. The independent normal-only counterexample remains valid,
and is not conflated with the actual coupled matrix result.

All48000 matched Post-Commit→next Begin inventories have EXACT zero gap in
Beam/layer/contact/K. The potential-jump hypothesis is falsified for this run.
The remaining energy term instead compares material endpoint spring work
with mapped BEGIN contact force/Jacobian work. Independently derived
R_t=W_material+h*f_t0·v1+h²*v1ᵀJ_t0*v1 is signed,NOT heat or a fitted global
energy residual. Independent planar stick/slip identity max1.36e-20 PASS.
Actual v11one-second journal X/V/Rexact,remaining1.30771e-15 versus independent
R_t1.30755e-15;remaining after that term1.61947e-19.8s/half-dt validation follows;
this discrete identity does not certify physical/time accuracy or full energy.

Event-grid actual4s112.748s profile PASS,all X/V/R differences0. Two full18s
release refinements are ACTUALLY running;predicted1.2-margin costs<900s,4GiB,
three/four bounded children at most. Existing uniform-grid failures remain.

### Actual release experiments and next nonuniform-grid qualification

Release-only div2/div4 full18s completed654.148/736.912s. Both original hold
gates pass,all X/V/R before16s are EXACTLY identical to the uniform half-dt
reference. Full-cycle D=1.05993038306e-10/1.06132387621e-10 F·mm;difference
.1312976% FAIL unchanged.1%. Last recorded active contact16.320/16.32125s.
This identifies localized temporal cost without relabelling a failure.

The next independently declared grid uses coarse quiet steps and refined
known actuation/load transients:events0,.5,2,3,4,6,7,14,16,16.5;divisors
1,2,1,2,1,2,1,2,16,1. Its ALL-step factor-two refinement is the test,not
release-only refinement with an unresolved identical prefix. Coarse base h
.0005 gives74000steps/24s;fine base.00025 gives148000. Physical fields/materials/
loads/damping and original thresholds are unchanged. These are NOT uniform-dt
trials. Pilot actual4s99.799/201.723s supports finite900/1320s limits,4GiB.
Actual coarse24s492.806s PASSES original hold AND recovery;global moment
2.40950e-5 versus1e-3. Birth/Death852/852,unresolved0,Commit/observer plastic
EXACT agreement. Fine24s is running;do not certify time convergence yet.
New-grid41nodes/finer material sampling have their own4sprofiles running.

Full v11split energy24s actually completed684.570s,X/V/Rexact,old columns agree
with independent full-AD reference within5.53e-21. After independently derived
mapped-friction remainder,the final unexplained discrete residual9.82387e-18
F·mm;8shalf-dt residual-1.05002e-18. The remaining signed remainder is not heat.
No unknown pressure/global field was replaced with0,and this old-grid journal
is not certification of the new phase grid.

For future affordable new-grid energy tests,an ALGEBRAICALLY EQUIVALENT grouped
observer avoids the extra normal Jacobian:Rc=DeltaUn+W_material+h*fc0.v+h²v.Jc0.v
=Rn-Pn+Rt. Independent600shape/separation tests PASS,max1.6941e-20. Actual
v12one-second group difference versus independent split8.760e-20,X/V/Rexact;
actual8s222.913s difference2.914e-18,remaining8.770e-20. No production force,
Jacobian or history change. Unused split columns remain NULL,not fake zeros.
Further v13 reuses the ACTUAL return snapshot energy for pre-Commit and prior
post-Commit energy ONLY at an identical pose/transaction in the frozen one-owner
scene. Actual direct-query checks every1000steps must match BITWISE or fail.
Its1stest passed;8stest is running. This is diagnostic-query optimization,
not a revised constitutive law or a proven whole-model speedup.

### New-grid actual results and preserved finer diagnostics

New-grid fine24s completed1074.824s. Coarse/fine both original hold/recovery
PASS;global moment relative2.40950e-5/3.71272e-5. Full-cycle D difference
.0682459% PASSES original.1%;movement/rotation differences also pass.
This is NOT an all-phases energy/grasp certification. Additional small-phase
loss checks still FAIL:wire transient.294329%,7–14s.490155%,14–15s.107132%,
15–16s.360739%. Absolute differences are retained in qualification_v1.json.

Actual new-grid41nodes849.013s and finer material sampling741.837s both
hold/recoveryPASS;space comparisonsPASS1%. The initial profile/full prefix
comparators wrongly compared h=.0005 against old h=.00025. Original FAIL JSON
is retained. Actual .5s SAME-grid fixed-clock controls6.281/3.974s match X/V/R
EXACTLY;new metrics_same_grid_v2.json reanalyzes existing actual raw data with
the proper comparator and unchanged physical criteria,without an expensive
physics rerun. Repetition565.855s gives actual whole24s X/V/R differences0.
Material-sampling full-cycle loss.06299997% PASS1%,but7–14/15–16increments
6.41528%/5.46712% FAIL1%. These are not erased by the aggregate PASS.

Actual bin localization falsifies the assumption of continuous quiet creep:
plastic increments cease around8.12s and remain constant through14s. Most
unresolved7–14s loss is a decaying transient7–7.43s,not proof of an ongoing
object-coordinate roundoff floor. No object-pose correction/accumulator was
implemented on the basis of that unconfirmed hypothesis.

Independent prescribed parabolic-capacity/virgin scalar benchmark reproduces
the scale separation:at h=.0025,traction error.0209004% but plastic loss error
9.22198%. Boundary-split Gauss3 agrees with an independent closed integral and
local energy/work derivative. Narrower virgin slip bands are entirely missed
by all tested point grids although force errors stay below1%. This is a
mathematical reference,not a SOFA or real-material measurement and not yet a
replacement history model. Actual per-point SOFA trace4s query-purity tests
pass X/V/Rexact;two24s traces are collecting production-kernel return fields
before Commit to test whether the real residual is similarly localized.

New-grid actual v14coarse24s journal840.463s,X/V/Rexact,unexplained discrete
residual-1.55243e-19 after separately derived signed terms. Fine8s561.341s
gives-3.06377e-19;fine24s forecast1986.658s exceeds1320s policy,attempts0:
BLOCKED by recorded finite policy,NOT an observed server/session failure.
Research continued instead of declaring completion. Profiling/source audit
found repeated unchanged cable AD assemblies,including an optional T*L gauge
that is NOT stored energy. New public-assembly reuse preserves actual F/J/work
and explicitly omits that unused gauge as NULL,not0. Frozen EnergyField/Cable
class definitions are byte-identical across the physical/diagnostic sources;
generated-source proof passes.100SDK API states and actual1s exact F/J/cache/
X/V/R checks pass;runtime15.750s versus prior20.064s is an observed comparison,
not an isolated benchmark.8sverification completed160.047s,PASS,actualX/V/R0,
all96cable snapshot checks exact. New-grid4scoarse passed133.897s;fine4s
is being measured before longer runs. No force/Jacobian/Commit code changed.

### Actual narrow-slip-front observation and bounded follow-up

Both24s read-only point traces completed551.234/708.429s,20snapshots each,
query-history changes0,X/V/R differences0. At7.2s coarse has813active points,
8positive-loss points (7carry95%loss);fine has1623active points,12positive-loss
points (10carry95%). Actual per-step loss1.03570542e-16/7.78752490e-17Fmm.
These are instantaneous samples,NOT cycle-integrated losses or a full cause
proof. The scalar thin-band reference and this actual localization support
testing a yield-front-resolved state/integration representation next.

A .000625mm cold-start initialization ACTUALLY FAILED the unchanged .001mm
minimum guard,with exactstderr retained in history625nm_profile4_v2. A prior
runner KeyError occurred before physics;its empty directory is not a physics
trial. No guard was removed. An independent .001mm/4s profile is running;
its own measured rate controls whether an8.2s cold-start follow-up is safe.
The8.2s prefix was selected from observed loss ending around8.12s,not as a
replacement for full24s hold/release certification. No checkpoint restart,
load/friction/damping reduction,object correction or relaxed criterion used.

### Independent immutable element refinement — actual implementation

Implemented a NEW `PatchRefinedContact` in models/patch_refined_contact,
preserving original curved/history components and binaries. Explicit immutable
per-reference-element spacings change only prepare-time material counts.
The same one-million-total-state and per-element allocation guards remain.
An empty vector reproduces the original global-spacing path. The entire
spacing vector joins the frozen signature,so mid-trial changes are rejected.
This is numerical resolution,not a new friction law or a moving remapper.

Five declared source transforms are reversed independently;the ENTIRE frozen
parent generated source is restored byte-for-byte. Force/Jacobian/return/
transport/Commit bodies are unchanged. Actual SDK API on explicit refinement
PASS,FD6.75082e-10,analytic plane loss5.1e-5,query/Commit/matrix/factor tests
and invalid/mutated-grid rejection PASS. Actual4s empty-vector path matches
parent X/V/R exactly,137.117s. This is not just a compile-only claim.

Predeclared local region90--100mm on all6layers keeps immutable sites for the
whole trial,including detached states. Background .00125mm,local625/312.5nm
uses528000/624000states,below the original million-site memory cap. It does
NOT silently remove the original component's global .001mm guard. Arbitrary
future contact may leave this predeclared region;no universal qualification
is inferred. Actual4s local profiles are running before bounded8.2s cold starts.

The original component's .001mm prefix completed302.340s.7–8.2s loss is
4.39536177605e-14Fmm versus4.40497175516e-14 at.00125,relative.218639%PASS1%.
All observed prefix phase-loss contrasts PASS1%;late pressure/release are
NOT covered. Its own measured rate justified one finite1320s full24s run,
currently active. Independent new-grid normal reference at actual13.99s
PASS,relative errors3.6854e-6/3.6854e-6/3.1156e-6/4.6566e-7(coarse/timefine/
mesh41/historyfine),separately demonstrating small normal quadrature error.

v15 new-grid fine8s completed489.679s,PASS,X/V/R0,explicit discrete residual
-3.06377e-19. Fine24s measured forecast1733.038s exceeds1320s policy,attempts0,
BLOCKED;not an observed server/session timeout. Research moved to the local
refinement component rather than declaring the final objective complete.

### v1 XML registration failure found and preserved,not accepted as convergence

Actual local625/312profile losses were suspiciously identical to uniform.
Inspection found SOFA `Unused Attribute: edgeSpacing` warnings and unchanged
patch weights. Therefore both v1local profile runner PASS values are
INVALIDATED for refinement;see PATCH_V1_INVALIDATION.json. Kernel tests using
direct C++ setters genuinely passed but missed XML Data registration.
Calling initData in the constructor body did not register the member.

The independent v2 constructs Data in the member initializer list. Its new
API test requires findData pointer identity and SOFA string parsing before
checking actual grid counts. New dynamics reject Unused Attribute warnings
and require actual prepare-time PATCH_GRID totals/element counts,not just
exit0 or requested XML. Old v1binary/source/raw/incorrect original assessment
remain intact. New v2build/API/actual uniform/local contrasts are separate.
No physical threshold was relaxed. This is a project implementation fix,
not evidence of an engine or physical-law defect.

### Applied v2 results,real timeout and a distinct recording alternative

V2actual90SDKstates PASS:objectivity3.0531e-16,internal force2.7756e-17,
moment7.1665e-18,Jacobian covariance8.8818e-16,query/Commit0. Actual immutable
local625nm4s287.302s and8.2s478.444s completed. Parent1250->local625prefix
phase loss contrasts PASS1%;this does not cover late pressure/release.

Local312.5nm/default recording ACTUALLY TIMED OUT480.011s,exit-9,last complete
state3.945s. Its identical longer prefix is BLOCKED,attempts0. A different
pure-recording contrast(200instead20) at625nm completed250.088s versus
287.302s:observed~13%gain,not an isolated benchmark or proof of dominant I/O.
Full4s X/V/R and every common contact CSV value match EXACTLY. Finer312.5nm
record2004s completed404.776s with exact state/contact agreement through the
ACTUAL old timeout prefix3.945s;the reference is explicitly not complete4s.
This retains every force evaluation/Commit and changes only recorded cadence.
It is NOT used to approve undersampled full-cycle contact/energy gates.

New312.5nm8.2s/record200 started with measured forecast801.457s,finite900s and
4GiB. Planning allowance10%is backed by two actual same-grid profile/prefix
rate ratios1.039555/.925167,not a changed physical tolerance. The old timeout
and old blocked decision remain. Current finer prefix is a real child,not an
automatic future restart.

Original-component1000nm full24s completed827.740s,hold/recoveryPASS;global
force/moment relative1.61582e-6/1.72270e-5. Peak movement4.91751578307e-6mm,
rotation.000210707781458rad. Whole loss1.062965101515e-10Fmm. Nevertheless
1250->1000late15–16s loss1.085017% FAIL1%(absolute5.6300e-16Fmm). Full
contrast remains FAIL;the1.25refinement factor is not a factor-two certificate.

### Stateful exact scalar yield-front reference,not a3D SOFA replacement

Dense point refinement is expensive and can still miss thin yield bands.
Implemented an independent piecewise-quadratic MATERIAL HISTORY FUNCTION
for a fixed1Ddomain/normal,prescribed parabolic Coulomb capacity and quadratic
increment. Each trial splits exact quadratic yield roots,returns branchwise,
and integrates force/energy/loss with Gauss3(exact degree4in exact arithmetic).
No interpolation of already-clipped point states or moving quadrature history.
Trial queries are pure;stale/double Commit is rejected;piece count bounded8192.

Actual independent C++120step load-reversal/cap-change test PASS,max10pieces.
Virgin loss versus separate closed reference relative7.02389e-14;endpoint
energy identity residual3.93814e-30;incremental potential derivative error
2.08155e-12. Projection is an explicitly derived ENDPOINT algorithmic term,
not heat or a fitted residual. This model has NO3D normal transport,contact
birth/death,moving patch,SOFA API or full-grasp certification. Those remain
NOT RUN;its purpose is a rigorous stateful reference for the next algorithm.

### Completed high-resolution prefix and remaining FAILs

Actual312.5nm/record2008.2s completed781.959s within its recorded900s cap.
Both requested local grids were applied(528000/624000states).625->312.5nm:
prefix peak movement.0206302%,rotation.00721867%,normal force/capacity
~.00000222%,7–8.2s plastic loss.309961% differences PASS1%. BUT2–3s loss is
0versus4.3650774e-19Fmm,relative100%FAIL1%. Prefix judgment therefore remains
FAIL,not silently rescued by tiny absolute error or other passing phases.
Local material refinement jointly changes normal/tangent integration and
history sites;it is not an independent legacy Gauss-order convergence test.

Actual memory measurements include148000steps in the earlier uniform-site
new-grid model,and23400steps in each refined prefix. All sampled FDs12;
refined312.5nm peakRSS163948KiB. Post-unload live allocation/allocator retention
are distinct. These are bounded measurements,NOT LSan/240k/hours or full-model
no-leak certification. First memory postprocessor assumed a full grid log;
actual EventStepClock logs1000-step BEGIN samples. Corrected mapping uses
the matching BEGIN epoch and actual final contact CSV/iteration marker.
No physics rerun/raw modification was needed for that analysis error.

The scalar stateful reference now includes3x3potential-gradient/Hessian tests
and independent256--65536point plastic-slider histories. Loss error decreases
1.22710%->.0000158273%. Generalized tangent absolute FD error3.15902e-17.
A NEW regression exposed an actual zero-capacity tangent bug(4instead0);
pre-fix exit1/source/stdout are preserved. Fixed the exact C=0return operator,
not by epsilon capacity. Current v4reference passes the old sequence,dense
reference and zero-capacity regression(0). Whole intervals exactly on yield
are explicitly flagged nonunique;classicalTangent()rejects them,and loading/
unloading directional derivatives are tested separately. No3D or SOFA
integration of this scalar reference is claimed. All previous v1/v2/v3raw and
failures remain;the deployed3Dcontact component is unchanged by these tests.

### Evidence checkpoint and actual sealed-case replay

Source checkpoint a5703be sealed4945actual artifacts/149historical Git source
blobs. Actual independent verification completed189.932s,exit0,zero hash
errors(4GiB/480s child limit). This is integrity,not a new physics PASS.

Added a fresh-output replay CLI for sealed graph_probe cases. Its first
preflight rejected the older Frame DLL because it is outside the autonomous
build-file glob;NO physics had launched/output directory existed. Resolved
that missing direct-index role by checking its exact frame_sha256 in the
sealed inherited identity,not by accepting arbitrary hashes or ignoring it.
SDK driver and other libraries retain explicit sealed hashes. Output paths
are restricted to results;existing directories are refused. Two current
role/path guard tests pass. Original source/control/grid/binary/step count
remain unchanged;only output filenames differ.

Actual sealed v2uniform4s replay completed199.861s,X/V/R differences0. The
executed RunnerSource snapshot is indexed separately from the current
stricter preflight guards. Replay supplement verification34files/3Git blobs
PASS,zero errors. This supports a precise non-overwriting reproduction
command,not a renewed physical certification. No pending physical children,
automatic restart,remote push or golden/SQLite/raw overwrite remains.

The COMPLETE research target remains unfinished. Current meaningful next
development is the independently validated vector/objective extension of the
stateful yield-front reference before any further3D SOFA rollout. Scalar
kernel PASS is explicitly not used as full contact/grasp approval;all small-
phase FAILs,global-energy uncertainty and grasp-optimization BLOCKED remain.
