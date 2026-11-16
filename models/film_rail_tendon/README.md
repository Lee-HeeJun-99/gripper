# Experimental coupled film, rails and tendon

This is an actual independent-DOF SOFA force field, not an OBJ animation or
a claim of qualified grasp performance. See
`reports/FILM_CONTACT_DYNAMICS_20261116.md` for the qualification boundary.

The rectangular research coupon has a 100 x 24 x .05 mm skin and two
100 x 1.32232986291 x .1 mm flexible strips, at z=-.075 mm. Its core volume
is 146.446597258 mm3/finger, one third of the old baseline's 439.339791775 mm3.
This is NOT the tapered equal_volume_v2 geometry. E=250,nu=0 and total mass
1e-6 are research inputs, not measurements of PET or supplied actuators.

Each rail has its own width/length displacement DOFs and shell energy. Five
material attachments per rail transfer vector forces between the interpolated
skin and rail normal-offset surface. The objective attachment stiffness is
.001 F/mm. These attachments are not layer jamming or a welded whole skin.
Five actual normal-offset tendon guides on each rail define a routed path.
The .2 mm eccentricity produces moments through the energy gradient rather
than a tip force. Generator potential is T*(length-rest_length); this is not
stored cable strain energy. Mechanical input work uses -integral(T dlength).
The two paths have equal ideal prescribed tension, without guide friction.

RootMapping handles three independent root/slope blocks. WorldMapping exposes
rest+u coordinates, with identity Jacobian/virtual-work pullback, for geometric
queries and separate native collision experiments. Displacement u must never
be passed directly to collision as physical position.

Kernel tests cover force/Hessian FD, rigid-motion objectivity, total internal
force/moment; API tests cover force/dForce/matrix/query purity. Root/world
mapping tests include virtual work. Archived builds are never overwritten.
Control is sampled once at BeginStep and frozen during force/tangent queries.
Adaptive retry/rollback at the same begin time is NOT implemented.

No self-collision, layer friction, pressure, real actuator, free object or
qualified grasp is implemented in this module. Native fixed-sphere trials are
a separate compliance/friction model, not a replacement SDF qualification.
