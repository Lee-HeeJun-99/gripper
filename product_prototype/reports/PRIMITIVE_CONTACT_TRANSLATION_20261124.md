# Finite-radius / planar-translation controls1225–1237

NEW component problem,not repaired thin Skin,jamming or grasp. Same installed
SDK,force ramps,mass0.112g,fixture,dt200us,Native solver settings and all
support collision models. Primitive moving sphereR5mm has appropriate public
I/m=1e-5m²,unlike former layer. Initial surface gap2um. 100steps20ms each
guarded4GiB/60s,actual runtimes~.168s. Commands/scene/source/binary hashes in
each unique result preflight and process command. NO old Raw rewritten.

1225 mu0 and1226 mu.3 at tangential load.01N. 1228 predetermined .15N load
exceeds assumed Coulomb capacity.3*.4=.12N (NOT random parameter fitting).
1229 assessment: center cases remain unqualified.1226 stationary force
balance passes narrowly,but1225/1228 hit iteration limits on departure from
an internal support diagonal. Frictionless1225 x differs independent BE
reference by33.654um,velocity3.731mm/s. Preserve FAIL.
1227 analysis serialization failed on numpy bool;no verdict generated;
fixed new1229 converts bool explicitly,old directory never overwritten.

Next single-variable lab contrast1230–32: initial sphere X0→5mm,still on
the SAME flat support face,all Triangle/Line/Point collisions retained.
This tests plane-translation invariance away from mesh internal diagonal,
NOT repositioning a held object or claiming repaired product performance.
1233 all3 scoped component expectations PASS:

|control|actual final X displacement|actual final Vx|steady contact Fx/Fz|
|---|---:|---:|---:|
|mu0,.01N|3.619041833mm|.791023815m/s|0/.4N|
|mu.3,.01N|0|~1.1e-15m/s|-.01/.4N|
|mu.3,.15N|8.979890079mm|2.160662967m/s|-.12/.4N|

No penetration or iteration saturation. Frictionless entire-output
reference errors X≤3.30e-17m,V≤6.0e-15m/s. Actual translational impulse
identity residual≤4.94e-20Ns;sliding ratio~.3. References use BEGIN-time
force ramp and (1+dt*alpha)m vnew=m vold+dtF+I. No time convergence/whole
energy/material qualification follows from this discrete agreement.
All sphere projections stay inside finite support face;not edge support.

1234/35 added frozen1221 read-only observer to actual center/offset mu.3
controls;prefixq/v/impulse errorEXACT0. 1236/37 uniquely join7/7 normal rows
each: center initially Line–Sphere,offset Triangle–Sphere. Both normals
vertical early,unlike former zero-distance mesh fallback. Departure-stage
line contact and saturation remain a distinct representation sensitivity;
not a universal contact solver failure. Further narrow temporal attribution
may be needed before applying this evidence to B3.

Reproduce(unique tags):
`python product_prototype/sofa/primitive_sphere_control.py --tag UNIQUE --mu 0`
`python product_prototype/sofa/primitive_sphere_slip.py --tag UNIQUE`
`python product_prototype/sofa/primitive_plane_translation.py --tag UNIQUE --source primitive_sphere_slip1225`
`python product_prototype/sofa/primitive_sphere_assess.py --tag UNIQUE --cases primitive_offset_slip1230 primitive_offset_stick1231 primitive_offset_sliding1232`
`python product_prototype/sofa/test_primitive_control.py`

Next independent track: ideal interface-tied two-layer coupon,unchangedE,
compared with free1189. This is an explicit limiting mechanical assumption,
not pressure-controlled friction or actual vacuum jamming. Assess constraint
error,element quality,static state and contact overlap before any ratio.
