# Independent vector function-history reference — EXPERIMENTAL

## Actual SDK isolation continuation

VectorPatchBenchmark.cpp is an independent Vec3 SOFA ForceField for one
uniform material displacement against a FIXED,externally supported tangential
patch. It is NOT a curved contact component,normal contact,birth/death or a
free6DOF grasp. It verifies actual SDK Data/force/dforce/matrix/query/Commit
paths before any proposed3D rollout. Every build has a fresh path and matching
runtime library hashes. No old plugin/model is overwritten.

Actual a01SDK compile FAIL:DerivativeElement exposes +=,not -=. a02API FAIL:
overallocated local loss-error budget at a yield boundary. Switching to a
GLOBAL summed unresolved-loss upper bound fixed that without relaxing its
requested tolerance. a03actual dynamics FAIL after3commits:repeated floating
return at zero increment produced inconsistent near-yield branch tangents.
An exact admissibility/identity branch fixes this;positive yield has an
explicit SELECTED generalized derivative,not a unique classical Jacobian.
Identity/OFF expression storage is algebraically pruned with a monotone epoch;
old Commit tokens never revive. Query,energy and Jacobian calls do not Commit.

Actual a04dynamics100stepsPASS16.808s;cache-only contrast12.436s and energy
journal15.351s have ALL common CSV values EXACTLY equal. API FD6.71741e-11.
The force/energy-query cache key includes epoch,position and,where enabled,
direction. This is observed runtime,not an isolated hardware benchmark.
Implicit Euler actual100→200steps keeps force balance but FAILS original.1%
time diagnostics:motion.364449%,loss1.140386%,stored energy.671829%.
Noncollinear initial-velocity contrast also actually executed100steps;
it is NEVER combined as an identical-condition time comparison.

Actual constant-capacity Euler audit has relative discrete force residual
5.40e-15,kinetic identity3.95e-25,local endpoint identity2.26e-27 Fmm.
Pre/post inventory quadrature gap9.48e-20 and sequential residual2.15e-19
are retained,not set to zero. The separately derived signed contact-force
linearization remainder is NOT heat. This partial benchmark has no unknown
pressure work;it does not solve the gripper's pressure/device energy question.

Further independent failures exposed two issues before directed-SDK rollout:
the global yield Lipschitz bound wasted500000samples during tiny unloading;
and letting a selected tangent change the adaptive force mesh changed force
at fixed pose. The new admissibility bound uses
k²|e0+d|²-c² <= 2k²e0.d+k²|d|² for admissible old e0 and nondecreasing c.
It cancels the old capacity derivative;its summed unresolved-loss inventory
must still meet the SAME absolute integration budget. The selected sided
matrix is integrated separately;forces,energy,loss and committed history are
always from the identical direction-independent pass. Work budget is split,
not doubled. Actual one-sided field FD2.94588e-9;directed SDK API matrix
difference.00010045261 with force/history equality exact. Near a positive
yield equality unloading uses the elastic member,loading the circular-slip
member. An arbitrary central derivative is not asserted at that event.

Newmark(gamma.5,beta.25) is actually present in the Matching SDK Backward
library. It is tested as a DISTINCT integrator contrast;the failed Euler
verdict remains. Euler's discrete energy identity is NOT applied to Newmark.
Actual directed Newmark100step13.087s completed;its own200step contrast is
in progress. Inspect actual summaries rather than treating this chronology
as an indefinitely live process statement.

Not a SOFA component,not moving-contact or full grasp qualification. Existing
scalar/Beam/Curved/Patch implementations and binaries are unchanged.

VectorReturn.h projects a tangent trial vector onto the circular Coulomb disk,
NOT three independent scalar intervals. For trial v=e0+d,r=|v|,capacity c,
e1=v if kr<=c,otherwise e1=(c/k)v/r. At c=0 the operator and tangent are zero.
On a smooth slip branch the fixed-tangent-plane derivative is
c/r*(P-u*u^T),P=I-n*n^T,u=v/r. At positive-capacity equality the classical
derivative is rejected. Traction=k*e1 is the energy gradient;the force on the
moving material is its negative. This tangent is NOT a SO(3)spatial Jacobian.

U1-U0=(k*e1).d-c*|v-e1|-.5*k*|e1-e0|². The final endpoint projection term
is independently derived,not heat or fitted energy closure. The incremental
potential U1+D has gradient k*e1 at fixed old history/capacity. It is NOT the
stored potential of the full frictional device. No pressure-source work is
defined here. All parameters are assumed numerical research values.

VectorField.h represents history as a bounded composition of radial-return
functions of material x in[-1,1]. It evaluates at arbitrary coordinates without
interpolating already-clipped samples. Increments are vector quadratics and
capacity is C*(1-x²). Storage is O(number of steps),point-query cost likewise;
4096steps and500000quadrature evaluations are explicit reference limits.
This uncompressed reference is NOT suitable for48000stepSOFA production.

Adaptive Simpson controls force,material tangent,energy and loss,with a
separate conservative Lipschitz bound to avoid accepting zero-sampled loss
where unresolved slip can exist. Embedded estimates are NOT rigorous error
certificates. Their sum is checked against global goals;the reference rejects
budget exhaustion or unresolved fronts rather than returning PASS.

Actual independent analytic testing exposed an important failure:the tiny
virgin-vector band had17.1718423%loss error EVEN AFTER making the absolute
integration tolerance stricter. For a constant-vector virgin trial the exact
fronts x=+-sqrt(1-k*|d|/C)now split the domain before quadrature. This reduced
that actual relative error to2.62427e-9 with D~1.98264694e-37Fmm. The old
failures are retained. This SPECIAL analytic split does not prove arbitrary
stateful/vector yield-front isolation;that remains a required research step.

Actual validation01:600point states FD1.55721e-12,energy residual6.61744e-24;
12step noncollinear/reversing/capacity-change field against an independently
implemented dense plastic-vector slider,65536point relative loss6.83695e-8.
Integrated endpoint residual8.58281e-28;20step exact collinear scalar loss
absolute difference1.03762e-18;integrated material tangent FD1.98887e-11.
These are mathematical tests,NOT actual SOFA/real PET measurements.

Reproduce into a FRESH directory (existing tags intentionally refused):
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/curve_vector_reference.py --tag NEW_TAG`
Each compiler/test child uses the existing4GiB bounded runner,source snapshots,
commands,exit/log/binary hashes. Old campaigns are immutable. Full physical
energy,12wrench and100mm grasp Optuna remain BLOCKED/NOT RUN.
