# Native triangle-surface contact

Status: **PASS** for independent box/plane calibration; full gripper **EXPERIMENTAL/FAIL**.
Sources `scenes/closure_native_calibration.py`, `closure_native_gripper.py` and matching tools.
All runs are actual SOFA/SofaPython3, not independent FEM or recorded replay.

## Physical multiplier calibration

The isolated cube has mass.01, side2mm and analytic inertia; it has no hidden pose
constraint. Plane is explicitly fixed. Native FreeMotionAnimationLoop,
BlockGaussSeidelConstraintSolver, MinProximityIntersection and friction contact
use four face contacts. Body-scoped implicit/linear solvers avoid mixing floor DOFs.
LocalMinDistance lost diagonal triangle contacts and was unstable; earlier failed
topology, normals, incompatible pair and solver experiments remain in raw directories.

`native_box_min_confirm/result.json`, dt.001: normal load .01, physical reaction
.01000000027994, raw multiplier1.00000002799e-5; maximal static force/moment defect
2.66154e-8, stick speed1.59045e-9, slip speed.100000417mm/s.
`native_box_half/result.json`, dt.0005: reaction.00999999836321, raw multiplier
4.9999991816e-6, defect9.58297e-8, stick speed3.0515e-9, slip.09990038mm/s.
Both release to zero active rows and recontact. Native multiplier is an **impulse**:
physical force/torque is `J^T lambda / dt`, verified against applied load and dt scaling.
Nonzero candidate rows alone do not prove a nonzero active reaction.

## Full film-skin experiment

Independent triangle skins: width8mm,thickness.2mm; sphere latitude24/longitude48.
These skins do not recalibrate original beam EA/EI and are not actual PET surfaces.
Old elastic SDF contact is REMOVED, avoiding double contact force. Object remains6DOF.
`native_gripper` and `native_gripper_scalar` run24s but have zero hold multipliers,
force residual1 and body speed≈.005mm/s: **FAIL**, despite clean engine completion.

MinProximity triangle-point distance is unsigned. At contactDistance0, a zero-thickness
surface can cross without persistent negative gap. A separate positive numerical
skin experiment uses an explicitly recorded .001mm buffer and surface normals.
It is not the same normal compliance as the SDF penalty benchmark. Actual24s
`native_gripper_buffer1/result.json` now has sustained reaction: relative force
residual6.30510e-6,moment1.67163e-6,body speed6.55834e-9mm/s,minimum24 hold constraint
rows; all three bounded hold subchecks pass. Full surface grasp remains EXPERIMENTAL.
The separate .0005mm buffer experiment and post-processing are in the compact evidence.
Offset/dt/triangle refinement and cylinder/box gripper surface tests remain required.

Measured .001/.0005mm buffer comparison: hold displacements1.69534445387e-7 /
1.69546524615e-7mm,relative difference.00712443% (<unchanged1% diagnostic). Both
have at least two positive-normal-impulse contacts,friction-cone ratios≤.28305,
and zero final active contact multipliers. Candidate rows24 include inactive contacts;
they are not24 physically active points. This narrow buffer comparison is PASS,
not a triangle/dt/12wrench/energy certificate. Hard contact vs soft SDF displacement
differs greatly because normal compliance is different, not because one is exact PET.

Full native contact is not certified by the box-plane test. λ distribution must be
mapped through J and divided by dt, with force/moment balance, not only visual collision.

```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/closure_native_gripper.py \
 --name native_gripper_buffer_half --buffer .0005
```

Use unique names; each run480s/4GiB maximum. Earlier native failures are retained.
