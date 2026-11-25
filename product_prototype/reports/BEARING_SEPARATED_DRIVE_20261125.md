# Bearing-separated return shaft — actual1869–1874

Starta9a8c2a clean. New physical hypothesis: radial bearing carries transverse
load; rigid lever transmits input to output; compliant shaft carries only
elastic return. This is not a larger shaft or a repair of1866mixed motion.
Nor does root support represent a hidden support on the grasped object.

1869actual independent SI reference, historical1.5N input and10mm moment arm:
input0.015Nm;0.009Nm old B3 REST scale corresponds to0.9N opposing output.
Initial bearing force reference2.4N, shaft return8.118309e-5Nm at0.4128rad
(0.902percent of output torque). Gross nominal pin single shear12.2231MPa,
lever input bending22.5MPa; hole/contact/retention concentration NOT included.
Actual material allowable/fatigue, bearing friction and efficiency NULL.
Return-shaft reference shear3.44percent still needs measured validity.

1870NEW Native stock BeamFEM+finite mapped mass+Cable1.5N+output deadload0.9N:
root fixed, terminal ideal frictionless radial/tilt bearing, intermediate
beam node free. One5step dt0.0001s child4GiB/60s, runtime0.171038s,
normal/noERROR. Constant principal-axis mass makes physical convective load
zero for this supported mode, not for general moving rigid mappings.
Actual final twist-0.393661rad and speed-1299.610746rad/s. All5actual accepted
angular velocities match independent2coordinate elastic implicit operator:
maximum absolute difference2.274e-13, impulse error0, forbidden motion0.
**Component discrete-response PASS, NOT usable controlled drive or grasp.**

1871finite separate sleeve/shaft/hub geometry fails housing connectivity:
endface-only base/sleeve fusion is not a robust connected solid.1872adds
explicit integral0.2mm sleeve/base overlap, no tolerance repair, but strict
CSG signed-volume assertion fails.1873diagnostic preserves actual positive,
negative and zero-volume intersection artifacts at exact-fit blind sockets;
all are retained, none discarded by a floor. Finite joint geometry NOT PASS.
Original1871/1872producer snapshots/partial STL and factual failure summaries
are preserved. Their first direct wrapper exceptions were not captured in
process log files; summaries quote actual command/exception, not invented logs.
New rotor volume73.870723mm3 differs from1870rotor47.157210mm3. Do not reuse
1870dynamic mass or verdict as this finite CAD's dynamics.50um radial gap
also remains inconsistent with inherited200um contact buffer for actual
bearing contact; ideal joint is NOT a contact solver fix. Socket bond strength,
press fit/adhesive/retention, wire installation and output routing unqualified.

1874reads1870Raw only. Reconstructed mechanical/angular work identities
agree<=5.557e-19J and angular update<=6.939e-17rad. Geometric input work
5.726452mJ, resisting-port work3.452150mJ, peak conjugate input power18.7156W
over0.5ms. These are bare-rotor reference quantities, NOT a motor specification
or work delivered to Finger. Frozen geometric remainder and backward-Euler
loss are separately reported; no Native stored-energy API or global energy
qualification. The uncontrolled speed motivates a physical stroke-controlled
winch coupon, not more force/damping or arbitrary q/v reset.

Actual commands use `/home/ubuntu/miniconda3/envs/robot_ws/bin/python`:
```sh
python product_prototype/sofa/bearing_separated_load_path.py --tag bearing_load1869
python product_prototype/sofa/bearing_separated_native.py --tag bearing_native1870
python product_prototype/cad/bearing_separated_geometry.py --tag bearing_geometry1871
python product_prototype/cad/bearing_separated_geometry.py --tag bearing_geometry1872
python product_prototype/cad/bearing_separated_geometry.py --tag bearing_geometry1873
python product_prototype/sofa/bearing_work_budget.py --tag bearing_work1874
```
Historical commands are records, not permission to overwrite directories.
1871/1872must use their immutable producers, not current diagnostic source.
Journal binary SHA3eb202b1e2a25f3ec6cded69e92a9d02bc48c304be14f6ca7123b4d758e5d0e0;
SDK26.06.00. Native scene/process command and SHA, source and per-case inputs
are in summaries; completed file hashes indexed separately, CSV stayslocal.
No SDK/FF/ODE change, q/v correction, collision removal, oldverdict change,
history rewrite or push.1741fullgraspFAIL and1586bracedOBJECT-ONLY unchanged.

##1876actual loaded stroke/hold, not a Finger trial

Changed input **mode**, not tension/damping/dt scan: frozen332NativeCableSequence
commands native displacement with1.5N cap (maxForce=1.5dt in native multiplier
units). Target is4mm output, theta=-asin(0.4), geometric input3.978234423mm.
Same1870ideal supported rotor/return shaft and0.9N resisting output, initial
velocity0; closing0.5s and run0.6s,6000Native steps. Two sequence links point
at the same cable, so identical command writes twice but only ONE physical
constraint row. Controller writes only value/pullPoint with liftHeight0,
not rotor/object q/v. Frozen source and binary hash checked/recorded.
Normal/noERROR runtime3.98339s; force full-precision lambda/dt0.900–0.931274N.
All-time geometric command error<=3.546e-11m. Late500samples: output4mm error
<=4.337e-18m, maxspeed4.718e-14m/s, forbidden motion0. PASS predeclared1um
position,1um/s hold-speed,1.5Nforce cap gates. No tolerance changed.
This demonstrates loaded output-port delivery and holding in an **ideal
bearing research component**, not useful work on actual Finger or successful
100g Holding.1873finite assembly/bearing contact/retention and material remain
unqualified; no full3Finger trial justified by component PASS.
Actual command: `python product_prototype/sofa/bearing_stroke_native.py
--tag bearing_stroke1876` using environment Python above. Per-child4GiB/60s.
