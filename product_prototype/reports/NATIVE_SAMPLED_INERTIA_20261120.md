# Native sampled-inertia research candidate

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

