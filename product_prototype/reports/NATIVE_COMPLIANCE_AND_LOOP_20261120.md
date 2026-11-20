# Native compliance and higher-order loop compatibility — 2026-11-20

## Scope / preservation

Continuation after facd9e2 contact-policy commit.663–691 are separate candidates,
API-negative controls and regressions. No old Raw/verdict/SDK/controller/FEM/CAD
was replaced. No B3 scene or checkpoint was resumed under a new force model.
Trial source_commit records the parent of a working snapshot;producer.py,frozen
C++/CMake,scene and binary hashes are the actual source identity,not that SHA alone.

## Native finite-compliance reference663–670

Separate physical law from661 e=0 impact:1g sphere,-.01m/s,initial buffered gap15um,
assumed100N/m unilateral elastic spring,zero gravity/damping/friction. Exact
analytical birth1.5ms,release11.4345882658ms,initial kinetic energy5e-8J.
This stiffness is a research assumption,not measured ReGrip contact compliance.

663 FAIL:old `default` response alias is unavailable. Actual factory explicitly
lists `PenalityContactForceField`;664 uses this name and runs80/160/320steps to20ms.
Do not interpret663's fallback/partial traces as the intended penalty model.
Read-only observer confirms actual ks=99.999999999999986N/m,threshold1.2mm.
665 corrects contact-data snapshot field names;666 observer-off states match
EXACTLY. Source addContact resets pen to0 after force evaluation:the end-of-step
stored pen/ks*pen are NOT an addForce journal. Old664 misleading headings remain
in Raw;667 explicitly rejects that force interpretation. Actual force callback
values remain NOT MEASURED;momentum-inferred effective force is separately named.

667 BE reference diagnostics:maximum reconstructed energy defect21.4081%,
11.5503%,5.95221%;all-common0.1%Gate FAIL (including100% inferred-force entry
difference). Inferred net incremental force can be negative near release;this is
not a claim that the last evaluated/clipped force callback itself was tensile.
668/669 stock trapezoidal comparison uses SAME physical law/input.670 defects
11.1985%,5.92082%,3.01941%;all-common Gate FAIL (velocity182.399%,absolute
0.000122178m/s near reversal). Do not fit physical damping to hide these results.
Native PenalityContactForceField.getPotentialEnergy is unimplemented and emits
ERROR;independent spring-energy reconstruction is NOT Native global energy PASS.

## Native candidate compatibility671–681

-671/672 VariationalSymplectic+FreeMotion finishes but leaves positions FROZEN
 despite nonzero velocity.673's common-time agreement is only identical wrong
 trajectories.678 independently rejects force-free kinematics before contact.
 The original673diagnostic and all Raw are preserved,not relabelled in place.
-674 uses DefaultAnimationLoop and actual solver schema. Parameters are `steps`
 and `explicitIntegration`,not guessed newtonSteps/explicit. It moves but hits
 unimplemented penalty potential API.675/676 still hit that API after incremental
 energy option change;677 refuses partial analysis. Stop this direction.
-679 Native BDF requires an explicit NewtonRaphsonSolver.680 adds it but the
 tested Rigid3 graph emits coordinate/derivative vector-operation errors.
 Do NOT remove guards or claim all Native BDF implementations universally fail.
-681 translation-only Native BDF candidate hits SubsetMapping topology setup and
 matrix/projective-constraint segfault in the mixed static-geometry graph.
 This is NOT a completed collision reference. Runner now stops later resolutions
 after a failed child;failure logs are preserved. No SDK fix or tolerance relaxation.

## ODE vs collision-graph isolation682–684

Native PlaneForceField on one Vec3 with the SAME100N/m elastic law removes the
collision/static-plane graph. This is an exact translational symmetry surrogate,
NOT Native Collision Detector/rigid/guide/B3 qualification. Actual Native force
SLOT and Newton status/residualGraph are logged;the slot is not assumed to be the
force evaluated at accepted q. No custom ODE or force algorithm is implemented.

682 Euler,BDF1,BDF2;683 Newmark gamma=.5,beta=.25;each250/125/62.5us,20ms.
All12 Native runs complete.684 independently tests the analytical elastic solution
AND the discrete equations,not merely the solver's own convergence message.

|candidate|250us max velocity reference error(m/s)|62.5us error(m/s)|all-common0.1%|
|---|---:|---:|---|
|Euler|0.00111731|0.000301930|FAIL|
|BDF1|0.00116262|0.000305619|FAIL|
|BDF2 tested graph|0.00711809|0.00708748|FAIL|
|Newmark|0.0000623373|0.00000390561|FAIL|

BDF1 full nonlinear BE equations agree≤1.73e-15m/s and2.09e-17N.
The tested BDF2 graph violates the standard first-order-system position equation
by approximately0.005m/s even as dt decreases;Newton convergence is not sufficient.
This is a scoped counterexample,not a patch or universal unsupported-component claim.
Newmark reconstructed energy defect improves1.24805%→0.312378%→0.0781174%,
but velocity all-common comparison still11.6734% (absolute1.20086e-5m/s).
No floor/zero exclusion.690 fixes the actual parameter name vdamping=0 and skips
unnecessary observer rebuild;all q/v/force-slot outputs are EXACTLY unchanged.

Actual plot:results/b3_native_plane_ode_reference684/actual_native_ode_comparison.png.

## Newmark + Cable/loop calibration685–688

685 uses existing straight spring-mass coupon,1g/point,1000N/m,1N/point.
Two channels:Native CableConstraint(value=F*dt) or Native ConstantForceField with
zero cable force. SAME physical force direction/geometry/mass/spring. Six Native
trials. Cable multipliers are exactly F*dt,external-channel cable multipliers0.
Nevertheless both channels fail independent average-acceleration Newmark state
reference:at250us first v=.246153846m/s is correct,but q=.061538462mm instead of
.030769231mm. Over20ms Cable position/velocity errors reach.719495mm/.662397m/s;
external-channel errors.708941mm/.667783m/s. Correct units alone are not enough.

686 separately builds a REJECTED,OPT-IN numerical interface candidate:
ReGripNewmarkFactors inherits Native solve() unchanged and only overrides two
public position-integration factors to dt/2 for gamma=.5,beta=.25. No ODE/force/
contact implementation or state overwrite;installed SDK unchanged.687 shows first
cable correction changes,but FULL state reference still FAIL. External-channel
trajectories are EXACTLY unchanged from685. Do not use this adapter in B3.

688 captures installed library/header hashes and read-only objdump of
FreeMotionAnimationLoop.computeFreeMotion and ConstraintAnimationLoop.freeMotion.
After SolveVisitor(free=true;NOT a velocity-only-named argument),the free position
is formed by MechanicalVOpVisitor(freePos,pos,freeVel,dt). The fixed dt vector
operation and measured685/687 counterexample explain why factor overrides alone
cannot restore average-acceleration free positions. The protected helper is not
virtual. Merely changing a scalar compliance factor cannot repair the missing
old/new velocity combination while preserving the force channel.

## Current verdict / stopping boundary

No candidate above is adopted into B3. Existing limited50g Skin Holding/release,
all old time/mesh FAILs and hardware interference remain unchanged.100g/Lift/STEP
and fabrication readiness remain BLOCKED. Material/joint/inertia calibration absent.

This numerical candidate family is stopped at reproducible compatibility limits:
not OS memory exhaustion or an invented elapsed-time limit. Further meaningful
higher-order constrained development needs a separately validated animation-loop
integration contract using matching SDK source,or an upstream-compatible fix.
No SDK edit,post-step state repair,unvalidated loop rewrite or custom FEM/contact
solver is performed. Do not continue parameter/dt/alarm sweeps without that change.
An updated numerical loop would first need EXACT standalone force-channel and
constraint-free reference regressions BEFORE any B3 run. Its development is not
already complete or scheduled in the background.

689 eight regression tests PASS;691 nine tests PASS including exact690replay.
29campaign records preserve67actual Native child attempts;19contain SOFA errors
and are NOT physics successes. Actual maximum Native runtime0.506147s. These are
small discriminating coupons,not long B3 runs. All Native/build children used
4GiB/480s guards,sequential;RSS NOT MEASURED.
Native error text and actual partial counts take precedence over generic guard
label nonlinear_failure (some failures are API/configuration,not Newton divergence).
Evidence:evidence_product_native_ode_limits_v34/manifest.json.
Reusable observer:cad/build_b3_native_plane_force682;rejected adapter:build686.

Safe restart/verification commands (NEW tags;not new physical research):
```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_native_plane_ode_reference684/summary.json
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/contact_policy_test_run.py --tag UNIQUE_REGRESSION
```
After an actual loop-contract implementation/change only:
```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/native_newmark_cable.py --tag UNIQUE_FORCE_CHANNEL
```
Without selecting that implementation this command reproduces the known FAIL;
do not count it as new work or promote a first-step/selected-energy PASS.
