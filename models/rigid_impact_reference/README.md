# Limited actual Rigid3 impact references — NOT a grasp solver

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
