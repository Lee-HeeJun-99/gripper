# Bench torque and jam qualification — NO OPERATION AUTHORIZED

Actual candidate: `fixtures/torque_arm1`,4STEP/STL parts plus assembly. Its
nominal BRep check is not structural proof. Existing supported shaft/bearing
module is used on a separate bench; production Drum/cap/bolts/pin/plugs and
Idler/other obstructing hardware are NOT installed in that bench test. Never
treat this declared test cutset as deletion of operating production hardware.

100mm nominal opposed load eyes counterbalance the ideal arm's own weight.
Measure the actual lever and zero/tare. Force transducer needs signed±20N
range,0.001N resolution, calibration uncertainty separately supplied; length
resolution0.01mm and angular measurement cover±5deg. Resolution alone does
not establish accuracy. Guard the arm, pinch points and fragments. Define
physical stops and a certified bench attachment before any load application.
Actual sensor end links, plug sockets, support fixture and proof strength are
NOT yet qualified; no static/dynamic safe test load is authorized here.

After engineer approval of the complete rated fixture/guard/load limit:

1. Inspect pin/shaft/threads/supports, fit pin then retention plugs with actual
   qualified torque, secure bearings and independent arm travel stops.
2. Calibrate force/zero/lever/angle, record specimen, operator, time, gauge
   calibration and temperature. Check both force signs without driving a motor.
3. Torque=`(F-Fzero)*L*cos(angle)`. `scripts/torque_records.py` propagates
   bounded force/zero/lever/angle uncertainty; never assume zero uncertainty.
4. Characterize limiter torque in both directions at approved thermal and
   rate conditions. Preserve peaks and repeatability, not only mean torque.
5. Quasi-static setting maximum plus uncertainty must not exceed the eventual
   certified structural protection budget. Minimum setting minus uncertainty
   must exceed verified normal demand. These limits are still unresolved;
   no arbitrary setting is filled in as a safe value.
6. A separate guarded dynamic test must measure actual tendon peaks during
   intermediate-stroke jams, including driven inertia and cable compliance.
   A good static torque result cannot pass dynamic force-cap qualification.

Stop on gauge saturation, support motion, loose pin/plug, sensor side-loading,
overtravel, unexpected deformation, rising temperature beyond approved range,
broken strands or guard damage. Isolate power before touching the fixture.
No purchase, fabrication, powered operation or simulated physical data occurred.
Blank recording templates stay blank; synthetic controls are software only.
