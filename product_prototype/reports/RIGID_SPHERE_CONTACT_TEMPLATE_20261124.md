# Installed Native sphere-template contact contract

## Cause isolated1567, not a claim that Mapping/FEM is generally defective

Previous1561/1563 LocalMinDistance runs missed Skin–Object response despite
3.12mm penetration.1565/1566 rigid facet/surface coupons did respond. Actual
scene inspection exposes a confound: whole gripper uses Rigid3d sphere with
IdentityMapping; those earlier coupons used Vec3d sphere centre RigidMapping.

1567 now compares four actual Native two-step runs, SAME real missed facet,
R30/centre, parent rigid mass/inertia, initial0.1m/s tangential velocity,
friction, solver and boundary configuration. Only intersection class and
sphere child MechanicalState/mapping representation differ.

| Intersection / sphere | Nonzero rows | Max angularJ component | Max angular impulse Nms |
|---|---:|---:|---:|
| Min / Vec3 centre |3|0|0|
| Min / Rigid3 |3|0.02808093|3.284337e-11|
| Local / Vec3 centre |3|0|0|
| Local / Rigid3 |0|NULL|0|

LocalRigid3 actual stdout explicitly reports RigidSphere–Triangle/Line/Point
intersectors NOT FOUND. The installed LocalMinDistance header lists ordinary
Sphere/mesh but not RigidSphere/mesh. The corresponding installed Min and
NewProximityIntersection headers explicitly list RigidSphere/mesh support.
These are installed SDK/source observations, not assumptions about all SOFA
versions. SDK unchanged. This independently reproduces missing response
WITHOUT FEM/multimapping: do not attribute that failure to FEM dynamics.

Vec3 centre mapping is NOT an acceptable physical shortcut: actual angular
contact Jacobian and angular impulse vanish while translating contact remains.
It would remove sphere friction-torque coupling. All whole-gripper candidates
must retain the existing actual free Rigid3 object and its inertia/rotation.

1568 tests ONLY two NEW native NewProximity variants with the same coupon,
without repeating unchanged Min/Local runs. NewRigid3 gives3 response rows,
angularJ0.02694163 and angular impulse3.285728e-11Nms. Vec3 still gives0
angular coupling. Thus a supported installed Native component exists; no
new ODE/contact solver or SDK patch is required for this capability issue.
This is COMPONENT CAPABILITY ONLY, not contact/time/energy/grasp accuracy.

## Actual follow-up1569

finite_hardware_new_contract.py changes ONLY the native intersection class
in the1556 INITIAL scene to NewProximityIntersection, retaining all finite
Eyelet+Support triangles/lines/points, actual Rigid3 object, physical inputs,
mass/inertia assumptions, friction, buffers, solver thresholds and Cable1.5N.
Normalized XML verifies exactly the one component-tag change. No collision
disabled, object state prescribed, Vec3 shortcut or checkpoint restart.
Fresh.6s Native pilot1569 is actually started under4GiB/420s; inspect its
summary BEFORE any promotion. It must pass independent actual Skin gap/
response and Guide–Guide bracing audits before longer Holding trials.

Three actual software regression tests pass: template distinction, forbidden
Vec3 torque loss, retained NewRigid3 response/angular coupling and matched
parent geometry/mass/inputs. These are not numerical or physical certification.
All historical functional PASS and numerical/hardware-bracing FAILs remain.

## Reproduction

```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/rigid_sphere_mesh_contract.py --tag UNIQUE
PYTHONPATH=product_prototype/sofa /home/ubuntu/miniconda3/envs/robot_ws/bin/python -c 'import rigid_sphere_mesh_contract as m; m.main(("New",))' --tag UNIQUE
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/test_rigid_sphere_contract.py
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/finite_hardware_new_contract.py --tag UNIQUE
```

Already completed1567/1568 should NOT be repeated without a new hypothesis.
Producer snapshots, actual Scene/process command, Source/Binary SHA and frozen
observer source identity are recorded per result; no detector.csv is Git-added.
