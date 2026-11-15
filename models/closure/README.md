# Active-interval contact research component

Independent of the immutable v4 StickSlipContact. Same line skin / material beam
interpolation / normal density / equal-mu elastic Coulomb law; changed spatial
integration and separate material-history discretization. This is NOT a film
surface or a finite-width torsional-contact constitutive law.

Sphere: exact segment/inflated-sphere intersection. Rounded cylinder/box: bounded
convex line minimization and bisection, no derivative at geometric seams claimed.
Gauss-Legendre order8/16/32 integrates only active intervals. The force vanishes
at a moving boundary, so the continuum force derivative has no boundary-force
term; integrating the local spatial Jacobian is tested against finite differences.
Finite quadrature still has an error, and stick/slip branch crossings are not
silently differentiated as globally smooth functions.

Friction history is anchored to fixed reference-material knots (maximum spacing
.01mm by default), NOT to moving Gauss points. The last committed material
geometry supplies old local coordinates/normals; elastic history is linearly
interpolated then projected onto its old tangent. State changes only at AnimateEnd.
Material history interpolation is a separate research approximation: its spacing
must converge independently; no claim of exact constraint stick or full global
energy balance. Detachment energy is a separately labelled fixed-grid estimate.

Only root/planar finger guides from the old benchmark are used; free object has
no constraints/pose fixes. SpatialLoad allows all6 spatial wrench components;
its output energy intentionally excludes external actuator work. Never treat
recorder's component_energy as a complete total potential.

Build with models/closure/CMakeLists.txt. Latest campaign is results/closure_*.
Keep prior binaries/results immutable; do not relink a previous version in place.
