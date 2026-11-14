# Stabilization research modules

The certified/earlier `plugin/`, `models/integrated/`, `models/finite_rotation/`
and independent FEM are not edited. CMake generates a build-local wrapper of
the integrated implementation, changing only exported registration names.

## ForceAudit / Newton continuation

Independent calls to each actual ForceField sum unprojected forces. Fixed roots
are excluded from the physical free-DOF residual; inferred root reactions are
reported separately. Linear force and torque use distinct denominators. Zero
gravity and absence of cable constraints in these scenes are explicit, not omitted terms.
`StaticSolver` + `NewtonRaphsonSolver` solves equilibrium rather than reproducing
dynamic trajectories. Static time/dt continuation checks are NOT dynamic timestep
certification. Friction history depends on the loading path. The original failed
dynamic experiments remain immutable.

## DistributedContact

For each beam segment, trapezoidal line quadrature uses reference-length weights.
The penalty constant is a line density (F/mm²), not an identical spring per sample.
The interpolated point `p=(1-s)*p_a+s*p_b` interacts with an analytic signed-distance
shape and a research skin radius. Normal energy is `.5*w*kn*min(gap,0)^2`.
Point forces scatter with the same interpolation weights. The object's torque is
included. This is a centerline-skin surrogate, not a measured film surface, a
triangulated collision pipeline or a complete contact-patch torque model.

Relative velocity includes the free object's angular velocity. Kinetic friction is
`Ft=-mu*Fn*vt/sqrt(dot(vt,vt)+speed²)`. Consequently `Ft·vrel<=0`, but there is
NO exact static stick: supporting tangential loads involves creep. The coordinate
and velocity Jacobians are differentiated separately and assembled through actual
SOFA stiffness/damping APIs. Spatial wrench Jacobians need not be symmetric;
these scenes use EigenSparseLU, not a symmetric-only solve.

Sphere, infinite local-y cylinder and cube SDFs are supported. Cylinder endcaps,
box seams/corners and singular shape centers are not certified by smooth-branch
derivative tests. No claim of real PET/vacuum/object friction calibration is made.
The API tests exercise all18 DOFs of two endpoint nodes and a free object,
position/velocity finite differences, objectivity, force/moment balance,
kFactor/bFactor, matrix assembly, dissipation and null-input safety.

## Opposing fingers

Two 100mm, 2-layer fingers have independent tendon commands and prescribed-pressure
LayerNetworks. Their Y/rotX/rotZ DOFs are explicitly guided to retain the validated
small-planar layer law (<.005rad). The object's6 DOFs are NOT constrained or corrected.
These are not fully free3D soft fingers. Root placement ±5.305mm and the5mm object
radius are uncalibrated research assumptions, not the final50mm-body cartridge design.
One DiagonalMass supplies both finger and object masses; actual engine queries
verify a.0001 object mass and isotropic sphere inertia. Other shape inertias remain
explicit research inputs. Global Rayleigh damping is recorded numerical damping;
the static force gate excludes it so drag cannot masquerade as load support.

The old single-finger negative control retains its.001mm criterion. The new
guided-finger benchmark permits.05mm elastic motion (1% of object radius), but also
requires velocity, angular velocity, contact and force/moment criteria. Passing
translation alone is never accepted. Surface/dt/mesh gates and the static-stick
limitation still block full grasp certification/optimization.

## Energy scope

Normal contact energy, layer/cable diagnostics, kinetic energy, sampled actuator
work and friction dissipation are available. The installed BeamFEM energy API
reports not implemented. Full beam energy and Rayleigh dissipation are NOT assumed
zero; complete system energy balance remains BLOCKED. Sanitizers instrument our
plugin/tests, not the distributed SOFA engine; detect_leaks=0 is not a LSan pass.
