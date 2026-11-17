# Limited actual Rigid3 impact references — NOT a grasp solver

## Native mixed-state control (separate physical law)

`ReGripRigidBE` is an independent BE-only specialization of the project's
solver,not a replacement for its verified BDF2. It does not add Rigid3
coordinates (7 scalars) into derivative vectors (6 scalars). Each trial
sets qTrial=q_n+h*vTrial via the public Coord+Deriv SO(3) exponential,
so BE's first residual is identically zero. Only one isotropic free rigid,
zero-offset sphere-center mapping,no orientation-dependent regular forces,
and order1/theta1/nativeConstraintBE are supported. Unsupported broader
rigid dynamics are rejected. The original solver and installed SDK are
unchanged. The included LGPL public NonLinearFunction.h is byte-identical
to the project source SDK header omitted from the Installed SDK package;
the binary links only Installed SDK libraries.

`NativeFreeBodyProbe` passively reads actual public constraint Jacobians
and multipliers on BOTH states. It records Native J^T lambda,BE momentum,
full-triangle buffered clearance,begin/end moment residuals and mapping
consistency. This is NOT the custom candidate-complete/event-aware owner.
Actual556 preserves the old Rigid Coord/Deriv arithmetic error.558 executes
but FAILS because a typed Vec3 LinearSolverConstraintCorrection does not
publish the Rigid3 correction.559/560 use public GenericConstraintCorrection
on the common system;actual8/16/32-step mixed trajectories and independent
BE spin recurrence pass limited identity checks563. Body motion is genuine.
No fixed-object guard was removed from the custom event owner.

Actual C2 closing562 completes1s/400steps in59.286s and moves the free body,
but full-triangle minimum buffered gap -2.18155e-5mm FAILS.564's identity
audit PASS is deliberately NOT that clearance/time/energy/grasp gate.
Its OBJ/PNG are actual saved states at scale1,not a successful grasp.

```
$PY tools/film_native_free_body.py --tag NEW_PROFILE --mixed-be --generic-correction --c2-closing
$PY tools/film_native_free_body.py --tag NEW_CLOSING --mixed-be --generic-correction --reuse NEW_PROFILE --c2-closing --steps 400 --duration 1 --profile NEW_PROFILE
$PY tools/film_native_free_assess.py --tag NEW_AUDIT --case NEW_CLOSING
```

Longer runs require a measured same-binary completed profile and estimated
cost <=480s. This control has neither custom accepted candidate closure,
impact restart,friction history,3finger grasp nor physical energy qualification.

This is separate from FilmWholeSurfaceEventOwner. Its fixed-object guards
are NOT removed or disabled. All material/mass values are research fixtures.

`RigidSuppliedPlaneFlight` is a SOFA ODE component for ONE supplied material
point impact at time0 followed by isolated exact force-free flight of an
isotropic rigid body. Actual mass/inertia is read through PUBLIC
BaseMass::getElementMass(index,BaseMatrix*). Translation and quaternion are
written to the actual free Rigid3 state. No pose/velocity clamp is used.
The Newton impulse oracle is reused from film_impact/ProjectedImpact.h.
The normal velocity,body impulse,orbital+spin angular impulse and kinetic
loss are checked. A derivative bound certifies the material point's short
separating flight. It rejects anisotropic inertia,external forces,other
masses,mappings/projective constraints and unsupported subsequent steps.
It is NOT automatic whole-body CCD,sustained contact or arbitrary-tensor
rigid-body integration. There is no finite collision mesh in this reference.

`FilmRigidSharedImpulse` is an actual TWO-STATE ZERO-TIME mechanical API
reference,not a joint time integrator. It reads actual film nodal mass,uses
the existing quarter-root projection B,and reads the actual Rigid3 mass.

```
Mshared = diag(B^T Mfilm B, Mbody6)
Jshared = [Jfilm B, -normal^T, -(r_world cross normal)^T]
Mshared (v+ - v-) = Jshared^T p
```

Both actual states are updated and queried after mapping propagation.
The two supplied material contact points must already coincide. The normal
is explicitly supplied,not a claimed sphere/box SDF normal. Query purity is
tested before commit. Exported M,J and pre/post reduced velocities support
an independent NumPy impulse check. Root reaction impulse is MEASURED from
the full nodal momentum residual,not an added corrective physical force.
Global linear/angular balances include that root fixture impulse. The
quarter-root fixture deliberately has nonzero external root impulse/moment.
Regular elastic forces are NOT integrated by this zero-time reference.
The enclosing one-frame batch call must not be reported as coupled dynamics.

Actual548 passes plastic/half/quarter,restitution,rotated-frame fixtures and
the expected anisotropy rejection. Actual552 passes tip light/heavy and
quarter-root light shared API fixtures. Inspect each archived identity,
scene,actual mass matrix and process result. Neither result certifies free
film/object dynamics,friction,3finger grasp,lifting or force closure.

```
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/film_rigid_reference.py --tag NEW_RIGID_TAG
OPENBLAS_NUM_THREADS=1 $PY tools/film_shared_impulse.py --tag NEW_SHARED_TAG
```

All tags must be new. Installed SDK only;no SDK modifications or remote push.
