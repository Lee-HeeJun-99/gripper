# Native inertial force/tangent validation

## Actual global matrix correction635–657 (supersedes callback inference only)

635 reads the actual Native EigenSparseLU12x12 operator through public API;
observer-on/off q/v/impulse/mapped positions are EXACTLY unchanged.636/637FAIL:
legacy B callback count40 concealed factorZERO. Actual rotational operator was
M-h²K/4 with missing B. Old623binary and every prior verdict/Raw are retained.
638/639 only add factor journaling:legacy K receives1,B receives0. This is an
assembly API issue,not justification to increase physical damping or change mass.

640 implements installed buildStiffnessMatrix/buildDampingMatrix,unscaled K/B.
Native solver supplies coefficients;no heuristic factor rescaling.641 actual FD
and equivalent-COM-basis API PASS.642 actual matrix observer remains EXACTLY pure.
643 preserves the failed installed-header hypothesis M-hB/2-h²K/2.
644 separately verifies the trapezoidal chain rule:configuration increment
h(v_old+v_new)/2 and force averaging h/2 imply M-hB/2-h²K/4. Actual all-step
operator agrees:rotational relative error≤7.23e-15,isolated K/B correction
relative error≤2.05e-12. Translation block error0. No mixed-unit norm dilution.
These are force contribution/assembly checks,NOT derivative-of-mass Newton proof.

641/645/646 actual Native100ms (2.5/1.25/.625ms):647 reference angular momentum
relative errors0.00603301%,0.00282855%,0.00138820%;omega errors0.00720102,
0.00350373,0.00172821rad/s. Still first-order observed trend,not generally order2.
648 EVERY common time/all3pairs worst0.0753113%FREE-ring selected Gate PASS.
653 runner shape-serialization error before SOFA:NOT RUN,preserved.654 independently
rotates/translates INITIAL physical system and executes Native again;strict1e-12
SE(3) objectivity PASS (omega error≤1.43e-14rad/s). Not transformed saved output.

649–651 finite ring CONTACT has0.1%Gate FAIL652:COM6.40457%,surface19.4683%,
omega81.4033%,rotational energy94.5913%,contact equivalent force100%.
No FEM/object/cable/B3Holding test was performed here.655 actual contact operator
observer purity0;656 expands EVERY actual3-row owned friction block. Actual
A*(v_after-v_free)-Jtranspose*lambda residual≤6.40e-22Ns/3.27e-25Nms,
velocity reconstruction≤2.85e-14. Active Native normal target remains-gap/dt
(residual≤1.15e-8m/s). Correct inertial tangent does NOT fix discrete contact entry.
657 ten regressions PASS,including missing-B detection and observer purity.

Reusable builds:cad/build_b3_inertia_matrix_api_build640 and
cad/build_b3_inertia_matrix_api642 (read-only matrix observer). Native children
remain under4GiB/480s;RSS NOT MEASURED. No SDK/old physical332/direct512 changes.
Reproduce with NEW tags:
```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/inertia_force_run.py --tag UNIQUE --build-case b3_inertia_matrix_api_build640 --trapezoidal
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/inertia_world_run.py --tag UNIQUE_WORLD
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/inertia_matrix_audit.py --tag UNIQUE_AUDIT --case b3_inertia_matrix_api642 --reference b3_inertia_matrix_api641 --operator trapezoidal-chain-rule
```
Next:contact transition/feature policy analysis,NOT unmotivated dt/solver/alarm
sweeps. Independent conditional union-mass geometry work may proceed;physical
material/joint data absent. No new B3/checkpoint/100g/Lift/STEP approval.

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
