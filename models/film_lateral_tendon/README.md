# Separate outboard tendon candidate

## Additional control contrast,not input-identical superiority

1398 separate source-bound40ms C2 rise uses SAME generic ControlProfile,
Field Data,Gauss stage force and journal input.1398 API,1400/1401 short
actual and1404 actual294step50ms PASS strict q/v/stage/time/control parity.
Default10ms route implementation and old results remain untouched.
1406 at50ms:skin mean tip−.743267→−.444770mm,centre75mm
+.372966→+.0783884mm,angle.0643616→.0377583rad. Less adverse arch but
also less total bending;NOT wrapping/grasp success.1407 virtual fixed
sphere overlay still has min triangle-buffer gap−.00204308mm,so it is
NOT a collision-resolved contact solution. Wire centreline min+.367377mm
is not finite wire/guide-body clearance.
1394/1397 measured10ms-rise Gauss stage mechanical work at50ms
.0001490763855/.0001490763186Nmm;1410 new40ms rise.0001462498350Nmm.
Different prescribed profile and work,not a matched-work comparison.
Damping integrals6.08725e-6 vs2.25232e-6Nmm are this free assumed model,
not motor energy,friction heat,or whole-system certified savings.

`Force.h` separately reuses original implicit-stage pullback with lateral
provider.1412 potential/gradient/Hessian/tension FD and zero-route EXACT
baseline PASS.1413 actual3film/free Rigid3 bracketed initial event PASS:
all event/state/impulse outputs EXACT to independent same-kernel reference;
gap−1.06581e-14mm,momentum7.27576e-19Ns,normalv2.73602e-13mm/s.
This200us incoming-sphere fixture is NOT capture from stationary rest or
40ms-rise coupled closing. Active Shared/implicit/BlockFree derivative
callbacks and Field all bind lateral6. General unused System::advance
sensitivity paths and long contact closure/release remain unqualified.

`Route.h` reuses original Film/Rails/Attachment mechanics and5mm normal
moment arm,adding objective6mm outboard guide offset along local rail width.
Zero offset is exactly original force/Hessian/energy. Guide body/mass and
wire finite radius are absent;same439.33979mm3 core is NOT same total hardware.
`Step.h` uses existing projected Gauss map,unchanged root/mass,C2 Hold
Tmax.0001N/rail,ramp10ms,release50..60ms. Not the coupled20..30ms pulse.

1353 independent force/Hessian FD and rigid-motion objectivity PASS.
Implemented undeformed geometry:initial R30sphere wire/arm CENTRELINE
gap+.370865mm vs original−2.607968mm,combined length200mm unchanged.
Unit discrete closing-mode work9.75Nmm both routes;not measured holding.
1356 actual SOFA force/dForce/stiffness/query-purity/Data parsing API PASS.
1358 zero-route actual regression1362 q/v EXACT to original provider.
1359/1361 actual6mm short dynamics PASS;1363 actual294step50ms PASS,
all q/v/stage/context clocks EXACT to same-kernel standalone reference.
Actual DLL SHA931168c93ecd39559a96830fcb523e589b044bb9ad411dafd1f2347f5c8ec33e.

1367 read-only actual comparison at294 common exact epochs:
original/lateral skin mean tip−.73835869/−.74326741mm,
root-tip3D angle.06392641/.06436158rad,centre75mm+.370615/+.372966mm.
Thus bending retained but the upward arch remains;NOT wrapping superiority.
1368 virtual fixed-sphere overlay of NO-OBJECT states:wire centreline gap
minimum+.341364mm,triangle buffered gap minimum−.0170890mm.
The latter means the free trajectory is NOT a valid contact solution.
Contact force/area/pressure/holding/lift remain NULL/NOT RUN.
Time/mesh/friction/selfcollision/full-thickness and real fabrication gates
remain unqualified. No final-design selection or actuator claim.

Reproduce a NEW bounded actual coupon using an immutable provider:

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/film_routed_run.py --tag UNIQUE --design lateral --amplitude 6 --provider 20261118_lateral_api_build1356 --duration .05 --profile 20261118_lateral_six_onset1361
```
