# Autonomous research log

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
