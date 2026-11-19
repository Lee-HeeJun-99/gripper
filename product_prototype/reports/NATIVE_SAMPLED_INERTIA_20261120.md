# Native sampled-inertia research candidate

## Follow-on cycles600–622 (after functional input commit844afa1)

600/601/602 SAME592 binary,finite geometry,initial state and contact settings;
dt2.5/1.25/0.625ms,10ms duration,two equivalent COM bases. All Native runs complete
without errors and basis q/v≤1e-12. No contacts removed or detector distances altered.
604 all common output times/all3pairs FAILURE preserved:

|Quantity|Maximum relative difference|
|---|---:|
|COM displacement|6.48978%|
|Mapped surface displacement|19.3158%|
|Angular velocity|81.3824%|
|Rotational kinetic energy|94.5976%|
|Equivalent contact force|100%|

603 early analysis used a mixed N/Nm generalized norm;604 separates units explicitly
and still fails.603 frozen,not used as preferred physical comparison. Neither
contact force peak sampling nor free-spin success explains away actual motion error.

609 independently verifies tau=-omega cross Iomega at every input stage:
max law error1.36423e-22Nm;actual Native free predictor error9.60e-14;
Mprevious*dv - sampledInertiaImpulse - ALLcontactImpulse residual7.64e-22Ns,
9.72e-24Nms. This closes discrete input/mass accounting,NOT physical time accuracy.
Actual first active rows:
base2.5ms output/0start,vnormal+=-1.18929811m/s;
half2.5ms output/1.25ms start,vnormal+=-0.71012927m/s;
quarter1.875ms output/1.25ms start,vnormal+=-1.42026030m/s.
Each follows the Native buffered-gap/dt target with max residual3.21e-8m/s.
These discrete times are NOT claimed to be continuous first impact events.

606 reuses independent facet crossing classifier on ACTUAL mapped surface arrays:
0strict crossings,0uncertain tests over28saved states. NOT containment or swept
clearance;no support/FEM/wholeassembly assertion.

607 normal/tangent work mismatch exposed an independent analysis bug:
Native response first_row is the first row of an ENTIRE contact group,which can
contain several3-row contacts. Earlier group-only loops omitted later contacts.
native_response_blocks.py now expands each actual group and rejects incomplete,
overlapping,or unowned rows.608/609 cover ALL actual rows.607 failure remains frozen.
Actual energy identity uses three distinct signed terms:
sampled inertial coordinate metric work + contact impulse metric work +
rotating mass metric transport = actual mapped kinetic change.
Maximum closure residual1.17607e-21J;ALL-row work reconstruction1.69407e-21J.
No term is relabelled heat/actuator work;root work and physical impact heat NULL.
610 all-pair cumulative comparisons FAIL,including tiny residual relative error
192.3769% with absolute1.63e-21J. No denominator floor or exclusion.

611 regression failure is a cancellation-bound mistake:cross-product error scales
with input norm |omega|*|L|,not cancellation-small output |tau|.612 uses an
operand-based floating-point bound for tau dot omega;all6tests pass,without any
physical tolerance change.622 adds stock-scheme exact-identity test:7tests pass.
Offline derivative test checks functional-law derivative only. The actual held
ConstantForceField Jacobian remains ZERO and is NOT advertised as implicit gyro.

613–615 extend FREE spin to100ms with SAME physical inputs,40/80/160steps.
Measured cost~0.169–0.205s/child (100ms fine cost is in process logs);4GiB/480s guard.
Projection from the measured short runs was far below480s;no long B3 process run.
616 base/half/quarter angular invariant errors0.133470%,0.0667322%,0.0333655%.
617 all-common-time/all-pair worst0.100100244% angular momentum at100ms:FAIL.
This almost-threshold result is NOT rounded into PASS.10ms599 scope unchanged.

618 changes ONLY installed EulerImplicitSolver trapezoidalScheme=1 at same
100ms/base dt.619 no improvement;622 confirms exact q/v/impulse identity to613.
Installed Euler header formula reduces identically for held input with B=K=0.
No further trapezoidal parameter retries justified. Native solver not replaced.

New ownership coverage is also applied to untouched historical552/550 Raw:
620 parent/mapped API unchanged,position1.39e-17m,velocity6.67e-16m/s;
621 all active point-to-actual-surface≤1.56e-17m. Body-point counts become
7eyelet/3support vs old5586/2;not area/physical contact count. Old files unchanged.

Evidence:inertia_v274163files,contact_inventory_v284395files,long_inertia_v294630files.
Latest prior4393immutable files verified0mismatches. Native22 successful children
this session,31archived campaigns592–622;no B3/Holding/Lift rerun or SDK edit.
Every analysis and failed test definition has a frozen producer/log or summary.

NEXT:do NOT adopt sampled-input candidate into B3 or continue blind dt/alarm/
trapezoidal sweeps. A genuine velocity/rotation-dependent inertial force tangent
must be independently validated before stock nonsymmetric LU integration;the
sampled ConstantForceField is not that tangent. Separately isolate Native contact
event policy from global input,as609 demonstrates. Full product Gates still unmet.

Exact fresh commands and reusable builds are in CHECKPOINT. Current direction
stopped at reproducible validity limits,not a claim of OS/session exhaustion.

## Why this scoped addition

565–591 already established COM geometry,world angular contact Jacobians,Native
constant-world input inertia convention,and missing composite mapping acceleration.
572/577/578 off-axis angular invariant error remained0.660162% independent of dt;
principal control582/584 passed. Those results remain unchanged.

The candidate is NOT a new FEM,ODE,Gauss,tendon or contact solver. An AnimateBegin
input computes the absent rotational coordinate term using actual mapped equal
Cartesian mass positions:
Iworld=sum mpoint((r dot r)Identity-r rTranspose),
L=Iworld omega,
tau_inertial=-omega cross L.
It sends this torque to stock Native ConstantForceField,held constant for the
current Native EulerImplicit step. No position/velocity assignment or postprocessing.
No implicit force/Jacobian is claimed:the force input is sampled at the step start.
This is a NEW narrowly scoped inertial candidate,not stock behaviour or calibrated
hardware. Native mass and contacts remain unchanged;the10mg/ring mass is assumed.

## First independent Native validation592–599

592 build is bounded4GiB/480s and matched solely to installed26.06.00 SDK.
Input binary SHA0e9d7336992942af5a0606e72323155335ced9f1eac3d9c540b8fe31cf3009b7;
source SHAf590fac8ec3cdc755597382badf8759352ccd22effbf2d096a0eeb59b3f3318e.
Same binary/geometry/initial state10ms,dt2.5/1.25/0.625ms593/595/596.
Actual basis-permutation q/v comparisons satisfy strict1e-12.
Analytical-reference assessments594/597:
angular invariant error0.0154663%,0.00773297%,0.00386646%;
omega error0.00286461,0.00143227,0.000716132rad/s.
This first-order decrease is compatible with the EXPLICIT sampled input.

598 principal-axis positive control vs old582 q/v/generalized impulse error
≤7.11e-15. No destruction of the successful zero-gyroscopic reference.

599 checks every common saved time and every resolution pair,including base-quarter.
Vector/tensor norm relative errors have NO absolute denominator floor.
COM displacement,linear/angular velocity,rotation-matrix change,actual mapped
surface displacement/velocity,L,rotational/translational/total kinetic energy:
worst0.0622731% at10ms,rotation-matrix change. Selected FREE-ring Gate PASS.
No endpoint-only extrapolation to continuous trajectory,contact or B3.

Analytic instantaneous tau dot omega=0;observed roundoff power is retained in
input journals(max~1e-24W free). It is NOT heat,external actuator work or global
energy certification. Root/contact/damping/global energy remain separate.

Native child runtimes~0.137–0.169s. Actual RSS NOT MEASURED;4GiB guard imposed.
v27 evidence4163 paths,3931 prior immutable hashes checked0mismatches.
Every actual run has commands,scene,logs,source/binary identities and actual states.

## Next cycle

Use same new inertia input with real finite-eyelet contact600–602. Check actual
all-row impulses,mapped mass,whole saved surfaces,active contact timing and all
common-output force/state/energy comparisons. Do not adopt candidate into B3 or
resume old B3 checkpoints before all necessary gates. Existing full B3 time/mesh,
50g final qualification,100g,Lift,CAD STEP and fabricated mass remain unresolved.

Commands (unique output tags required):
```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/inertia_input_run.py --tag UNIQUE_FREE
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/inertia_input_run.py --tag UNIQUE_CONTACT --case b3_finite_com_mapped571
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/finite_free_spin_reference.py --tag UNIQUE_EXACT --cases UNIQUE_FREE
```
