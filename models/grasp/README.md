# Objective elastic Stick-Slip research model

This independent component does not edit the certified planar or earlier kinetic
contact models. History is stored in the object's material frame. Smooth-branch
normal transport uses Rodrigues' minimal rotation; antipodal normals are rejected.
Only AnimateEnd commits state. Solver/addForce/Jacobian/observer queries are pure.

The trial elastic displacement is transported old elastic displacement plus the
projected relative material-coordinate increment. Return mapping enforces
`|kt*u| <= mu*Fn`. A single equal static/kinetic coefficient is used. This provides
nonzero static traction without a velocity regularizer, but is an elastic penalty
stick, NOT exact zero-displacement Lagrange/complementarity constraint. Different
static/kinetic coefficients, rolling resistance, contact patch torsion and exact
static constraints are not certified here.

Plastic dissipation is `mu*Fn*|du_plastic| >= 0`. Loss of stored elastic spring
energy at detachment is recorded separately as release dissipation, not as
Coulomb work. The flat-contact backward-Euler work identity includes the
nonnegative algorithmic `.5*kt*|delta(u_elastic)|²` term. Normal/curvature-dependent
increments and global beam/actuator energy require a separate audit.

Shapes are sphere, finite capped cylinder(local y) and cube. Smooth side/face and
edge/corner branches are analytic; at geometric seams the SDF is nonsmooth and
there is no unique derivative. Sampling uses reference-length trapezoidal weights,
not independent unweighted springs. Geometry remains centerline+skin quadrature,
NOT a continuous 3D film surface.

The object's6DOFs are free. Four finger roots are fixed; finger Y/rotX/rotZ have
explicit planar guides to preserve the inherited layer law's small-planar domain.
Object pose corrections, artificial holding forces and compensated object motion
are not used. Force/moment/velocity gates, failed controls, spatial/time convergence
and release must all be evaluated before claims about grasp performance.
