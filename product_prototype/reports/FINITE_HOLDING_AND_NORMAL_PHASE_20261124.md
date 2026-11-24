# Finite hardware Holding and contact phase diagnosis

## Actual full trials

| Case | Runtime | Slip mm | Max speed mm/s | Skin mean Fz N | Hold Guide–Guide rows | Verdict |
|---|---:|---:|---:|---:|---:|---|
|1586 original finite eyelet|117.577s|.0020415|4.149775|.9810043|2073|Object-only exploratory PASS; unbraced qualification FAIL|
|1594 terminal outer chamfer|167.499s|.0432545|12.957875|.9832376|504|Functional FAIL (speed); not selected|

Both actual runs completed800 outputs/finger with positive saved FEM volume
ratios (minimum .989778 and .989418). Guide/Rail/Support **object** loads0 in
Hold; real Guide–Guide contact still couples fingers internally. Do not equate
these two load classifications. Both solvers reach1001/1000 iterations.
No physical/time/mesh/product PASS. No100gLift was run.

1590 actual active hardware pair detector points were all on the outer endrim.
ONE0.3mm45degree external chamfer retained OD3/ID1.2/L2 and .6mm endwall.
No collision models or buffers were removed/changed. It reduced contact rows
but worsened object motion.1592 pilot84rows vs639 was not a reliable full-goal
predictor.1602 shows new contact locations radial1.194–1.361mm: contact migrated
onto the finite relieved region. Do not continue an unsupported chamfer scan.
Mass/inertia were deliberately fixed for geometry sensitivity, not calibrated
to reduced material volume; this is not fabrication qualification.

## Independent actual force and moment evidence

1598/1599: configured free sphere angular impulse residual≤2.118e-21Nms;
kinetic midpoint identity error≤4.066e-20J. This is a body bookkeeping identity,
**not** full system/contact-work/friction energy closure. Skin forces exchange
work with the sphere; individual positive object work is not negative friction.

1600/1601: sampled complete nonzero contact-triplet subsets admit static
gravity force/moment equilibrium in an eight-ray inscribed cone. This is frozen
subset feasibility, not capacity or dynamic stability. Both have favourable
normal z≈.945–.956. Increasing cable force is not justified by these data.

1603: actual Coulomb multiplier excess≤5.422e-20Ns, no negative normal rows;
but normal row sphere torque up to3.533e-6 and1.752e-5Nm. This is not a full
complementarity residual; solver iteration limits remain unresolved.

## Native mapping phase isolated, not a complete fix

1604 reports all translation-reference alternatives separately; none exactly
reconstructs the normal angular Jacobian.1605 then predicts the radial lever
rotated by exp(dt*previous angular velocity). It reconstructs saved angular J
within5.223e-18m (1586) and7.166e-18m (1594). The unrotated detector point is
radial relative to previous accepted centre within7.27e-18m.

Installed RigidContactMapper stores inverse-current-orientation detector
offsets. RigidMapping apply caches rotatedPoints; updateXfree applies free q;
constraint transpose uses this cache. This is evidence of a frozen-normal /
free-rotated-material-point linearization phase effect. Internal free q/cache
was **not directly observed** here: predictions and installed source support
the diagnosis, not a claim of full internal-state observation or sole cause.

1606 actual independent fixed-plane/free100gR30 sphere, zero-friction response,
gravity0, positive physical gap .1mm inside .2mm response buffer:

- zero spin: actual normal angular J0;
- spin10rad/s: actual normal angular Jx=.000374990234451294m;
- actual normal angular impulse2.92846825e-6Nms raises spin to10.08134634rad/s;
- stock Min and registration-only Dispatch actual results identical.

Ideal radial spherical normal force has zero moment, independent of spin.
This finite-step normal-torque gate therefore FAILS. It does not prove that
this small contribution alone causes full-grasp instability; native friction
moments and FEM/constraint errors also remain.

1606 producer's reference vector mistakenly used Y instead of X. Its original
reported prediction error is invalid and preserved.1607 reanalyses **the same
Raw without a Native rerun**, correct Rodrigues/cross-product prediction error
5.422e-20m. Current producer corrected; snapshot1606 unchanged.

1608 stock penalty-force phase coupon aborted because the Lagrange-only row
observer cannot find a constraint in a forcefield response. This is an
instrumentation failure, not proof penalty is unavailable.1609 removed ONLY
that observer, retained all physics/collisions, and actually ran4steps.
Zero-spin control gives nonzero normal response with angular change0; spinning
case changes angular velocity by11.829rad/s and FAILS. Native default penalty
stiffness is uncalibrated; do not adopt penalty as a grasp fix or scan stiffness.

## Fixture and next work

1595 allthreeRoot/sixCableOrigin fixture positions and interior velocity
PASS<=1e-12; no object motion was prescribed. This is not objectLift.
Next read-only coupon observer should sample actual current/free orientation
and normal J at the same assembly phase, verify observer purity, and distinguish
measured internal cache from independent prediction. No fullgrasp rerun absent
a new justified improvement. Existing .1%time/1%mesh and API failures retained.

Reproduce analyses with **unique tags**, using environment Python from repo:

```bash
$PY product_prototype/sofa/sphere_normal_lever_stage.py --tag UNIQUE_STAGE
$PY product_prototype/sofa/spinning_normal_reference.py --tag UNIQUE_REFERENCE
$PY product_prototype/sofa/finite_contact_row_contract.py --tag UNIQUE_ROWS
```

Actual scenes, commands, source snapshots and binary hashes are in result
folders1586–1609. No old Raw or verdict was modified; no push/history rewrite.

## Direct phase observation1610 actually completed

Reused existing frozen ContactGapProbe1211 binary (no observer rewrite):
SHA9729a5bcebad1f7825a0b4dc4f39c8009945fe5906b02ad5e516f81f2f7e9c6a.
Actual current build orientation is identity, actual free orientation quaternion
(.00624995931,0,0,.99998046881). Independent exp(dt*omega) matrix error0.
Measured free-rotated detector lever reconstructs actual normal angular J
within1.08421e-19m; observer q/v/impulse purity error0 vsoriginal two-step run.
The private cached vector itself is not read; its Jacobian consequence is.
This completes the direct-state part of the diagnosis, not the contact fix.

Next work: native_radial_contact_refresh_feasibility in actual queue. Inspect
installed documented Native phase controls and prior failed loop contracts
before selecting another coupon. Do not substitute Vec3 centre, zero velocity/
torque, SDK edits, or unconstrained penalty. Original physical/time/mesh gates
remain unsatisfied. A new fullgrasp needs a distinct justified improvement.

## Independent finite wire route audit1611–1612

Actual current guide poses/cable segments replayed with wireR.25mm, existing
boreR.6mm/L2mm.1611 finds straight finite-tube wall intersection at18guides,
worst analytical clearance -1.21214mm (reference) / -1.21377mm (chamfer).
This is geometry replay, **not** an actual finite-wire Native simulation.

1612 independently derives maximum single-leg angle18.584998deg, maximum
two-leg turn37.169996deg through this bore. At guide3, allsix paths have
actual turn43.725595deg. Thus even an ideal bisector-axis straight-leg model
cannot clear this bore. This does not prove a flexible wire cannot bend inside
or pass a flared entry. It does prove that simply rotating the ideal finite
eyelet while retaining the point-kink wire model is insufficient. Existing
300partCAD is not validated by either functional Holding result.

Next independent coupon should use existing Native BeamAdapter with an actual
guide3 turn snapshot and explicit stress-free-wire/entry/contact assumptions.
Do not call a prescribed curved centreline actual elastic wire bending. Actual
wire material, bend stiffness, friction, tension and support joint data remain
NOT MEASURED. No purchase or hardware operation was performed.
