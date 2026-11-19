# Native BeamAdapter reference and assembly inventory432–440

2026-11-19;branch development/regrip-autonomous-research.
Feature commits:e5d4dae,bc762c1. Previous HEAD8cf025b and all old evidence retained.
This continues the precise next task,not the completed429 directional FD test.
No SDK,ForceField,contact law,ODE solver or B3 geometry was modified.

## Implemented diagnostic

NativeRigidTangentObserver now exports initial native force/torque, native
interpolation lengthList, full addDForce matrix, and actual native assembled
matrix at the SAME initial q. Diagnostic assembly uses M=0,B=0,Kfactor=-1;
it changes the diagnostic linear-system buffer,not q/v. It is not claimed to be
passive with respect to matrix caches. Native StaticSolver subsequently rebuilds
its own matrix. Actual q/v equality is checked separately with unobserved controls.
Rotational and translational matrix blocks are compared separately because their
units differ. Force and torque norms are also separate. Root nodes0/1 are projected.

432 compares flat straight=true,flat straight=false and curved straight=false,
each with/without instrumentation.439 repeats ONLY to validate a necessary typed
17-digit native Data export:432's generic getValueString serialized lengths at
insufficient precision.432 lengths are not used as fine-rounding evidence.
All old432 bytes remain unchanged. New439 initial force and both matrix CSVs
match432 EXACTLY in all nine comparisons440. Zero-load flat/curved geometric-rest
control/observer mapped-center q/v differences are EXACT0 at both native outputs.
This is not post-step quaternion or loaded-state certification; the observer's
initial full Rigid3 q/v mutation check is separate.

## Actual measured results

| Initial geometry / native reference | Free force norm,N | Free torque norm,Nm | Native rest result |
|---|---:|---:|---|
| flat / straight=true |1.0124381827632884e-12|0|strict Newton FAIL,including unobserved control|
| flat / actual rest transforms |0|0|positions retained exactly|
| manufactured40deg / actual rest transforms |0|0|positions retained exactly|

For all three initial states, actual modern assembled versus full addDForce
TT/TR/RT/RR matrix block differences are EXACT0. Thus the separate native spring
derivative-path defect415 is NOT reproduced in this BeamAdapter initial test.
Do not transfer415's diagnosis to BeamAdapter or infer arbitrary-state FD accuracy.

439 native length/chord difference for flat geometry is1.214306433183765e-17m;
curved maximum2.818781062298957e-6m reflects spline arc versus chord,not an
automatic strain or collision defect. Both flat reference choices have the same
lengthList,but different rest-transform handling. Changing straight to false
removes the observed zero-load residual without changing geometric dimensions or
fitting material. It does NOT solve loaded equilibrium.

## Implemented alternatives and failures

433 uses geometric rest in the actual loaded native rectangular coupon at
21/41/81nodes. All three strict loaded trials FAIL. Initial-reference correction
is not misrepresented as a loaded solver fix.

434 attempts native LinearForceField load continuation but uses unsupported
keyTimes/keyForces attributes; actual applied load is zero. Its old summary says
completed diagnostic;it is explicitly EXCLUDED from loaded evidence in437 and
new manifests. Raw/source are preserved,not retroactively edited. Current runner
rejects ANY Unused Attribute.435 fixes actual installed fields times/forces,
uses20 bounded quasi-static load stages,unchanged force1e-6N,geometry/material/
Newton thresholds. It still FAILs actual Line Search (iteration8,then later
failures). Initial squared native residual2.5e-15 corresponds to5e-8N,consistent
with the first actual ramp increment. This is load continuation,NOT a physical
dynamic trajectory or time-convergence test. No tolerance or stiffness was fitted.

436/437/440 independently solve the measured initial native tangent,NEVER install
that result into SOFA. PRIVATE linearized tip5.48719999999504e-5m versus approximate
Euler5.487199999999999e-5m;relative difference9.0384e-13. Free force/torque residuals
1.18304e-17N/1.82141e-20Nm;global force balance~5.58e-19N,angular~8.21e-20Nm.
Linearized energy2.7436e-11J versus half external work differs1.72e-22J.
These certify only the algebraic linearized reference inventory,NOT actual loaded
native deflection,nonlinear energy,mesh/time gates or B3 attachment. Do not claim
holding/lifting or a measured stiffness ratio from PRIVATE matrix references.

## Evidence, builds and reproduction

All raw are unique `product_prototype/results/native_*432–440`;exact paths in
`product_prototype/reports/evidence_native_reference_v13/manifest.json`.
Snapshots include producer,scene,command,process,source/binary SHA,SDK identity,
matching installed ABI/ldd and CMakeCache. Child limits4GiB/480s retained.
Actual native jobs were short;no new long full-grasp prediction or trial was made.
Plot:`evidence_native_reference_v13/native_reference_inventory.png` shows actual
initial native forces,not loaded deformation. Unmeasured contact/work remainNULL.

-431 cad/build_reference_observer431/libReGripElasticObserver.so:
 `11fb14726ed0c020a33eb504905cfb577b4f99325113bcf2dfaab89238e89d14`.
-438 cad/build_reference_precision438/libReGripElasticObserver.so:
 `7ec6421cc915a636cd57155c5c8fed67df415e9c159c916cf0e0702c483faf3c`.
-Frozen compiled source/binary guards are in sofa/observer_identity.py. Do not
 rebuild old directories or label edited live C++ as these compiled sources.
-v12 verifies534 prior-v11 immutable files without mismatch;v13 contains the
 final preservation audit. Historical B3 and all FAIL records remain unchanged.

From repository root,read-only restart:

```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/native_beam_reference_precision439/summary.json
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/native_beam_precision_assess440/summary.json
```

Reproduction only if justified;fresh tags mandatory:

```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/native_beam_reference_inventory.py --tag NEW_reference_inventory
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/native_beamadapter_coupon.py --tag NEW_geometric --nx 21 --geometric-rest
```

## Remaining gates and next independent hypothesis

Stop repeated reference/iteration/load-ramp sweeps:reference retention and initial
assembly consistency are now measured,while loaded failure persists. Next useful
diagnostic is native FORCE at the PRIVATE linearized reference440,partitioning
axial/transverse/torsional residuals and coordinate-representation error before
choosing another native solver plan. Do not inject the PRIVATE predictor into
an accepted state or write a custom solver/force law. Native tangent agreement at
rest does not prove nonlinear consistency at that finite probe.

B3 functional50g holding/release stays preserved,not newly rerun. Full wrapping,
mesh/time.1%,whole energy,moving hardware clearance,100g,Lift and fabrication
remain unqualified. No new CAD/STEP claim. No physics child is intentionally left
running and no background continuation after session is promised.
