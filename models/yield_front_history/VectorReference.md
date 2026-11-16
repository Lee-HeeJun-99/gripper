# Independent vector function-history reference — EXPERIMENTAL

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
