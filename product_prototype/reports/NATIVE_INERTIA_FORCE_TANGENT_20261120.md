# Native inertial force/tangent validation

## Scope and prerequisites

Existing Native composition lacks measured composite acceleration591;sampled
ConstantForceField592 improved10ms but100ms617failed. Old results preserved.
Historical Ubuntu FREE reference report INTEGRATED_CURRENT_STATUS.md records600point
regression PASS;this is not a new empty FEM smoke test. No original FEM/contact/ODE
solver is modified. A scoped gyroscopic force with actual derivatives is now tested.

For body COM tensor I=R Ibody Rtranspose and world angular velocity w:
tau=-w cross(Iw).
dI=[dtheta]cross I-I[dtheta]cross,
dTau/dTheta=-[w]cross dI w,
dTau/dw=[Iw]cross-[w]cross I.
No translation force,position/velocity overwrite,artificial damping or restitution.
Gyroscopic potential contribution0 is not a whole-system energy certification.

## Actual implementation and independent FD623–625

623 installed-SDK build,4GiB/480s bounded;frozen Force.cpp and binary hashes in summary.
624 fails because SparseLUSolver moved to CSparseSolvers;error/segfault logs retained,
not interpreted as physical failure or missing-all-LU capability.
625 uses installed EigenSparseLU;its header explicitly supports nonsymmetric systems.
Never assemble this nonsymmetric tangent into an LDL-only symmetric solver.

Actual C++ evaluate() rotation FD relative error≤6.65e-11,velocity≤3.31e-10.
40actual K assembly and40B assembly calls per body in625/627.
Equivalent COM basis mapped q/v strict1e-12 PASS.
These observations are NOT yet a global matrix coefficient audit.

## Native free-ring integration625–634

Same physical geometry,10mg assumed mass and initial conditions;100ms duration.
Backward Euler625 still angular invariant0.132861%FAIL626.
With actual force K/B,Native trapezoidal627 improves to0.0112466%PASS628.
Half629 andquarter630 give0.00555120%,0.00276304%;omega reference errors
0.00709183,0.00347787,0.00172226rad/s. The observed trend remains approximately
first order,not asserted to be generally second order from a scheme name.

632 EVERY common actual output and ALL3resolution pairs (no interpolation/floor):
free-state,actual mapped shape,L and kinetic observables worst0.0748267%,
base-quarter rotation-matrix change at100ms. Selected free-ring0.1% Gate PASS.
633/634 principal-axis reference error omega≤9.01e-14rad/s,Lrelative≤4.21e-15.
This is NOT coupled contact/B3/mesh/global-energy/holding/lift qualification.

## Evidence and next cycle

v30 records4953paths;prior4628immutable hashes checked0mismatches.
Installed SDK and physical332/direct512 binaries unchanged. Every Native case
has scene,commands,logs,state,force evaluation/FD and matrix-call journals.
Build:product_prototype/cad/build_b3_inertia_force_build623.
Reproduction (new output tags):
```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/inertia_force_run.py --tag UNIQUE --trapezoidal
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/finite_free_spin_reference.py --tag UNIQUE_REFERENCE --cases UNIQUE
```
Next actual matrix audit,objective world transform,and finite contact. Do not
silently replace old B3 mass/checkpoints. Materials/join/union inertia unmeasured;
original contact/time/mesh failure and100g/Lift/STEP blocks remain.

