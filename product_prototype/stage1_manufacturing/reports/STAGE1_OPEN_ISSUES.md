# Current Rev AA disposition — 2026-11-26

Stage1 bounded engineering definition: PASS, actual release_revAA2. Historical
RevH design blockers below are preserved, not silently deleted/reclassified.
The actual successors I..AA implement bearing capture, positive pin/coupling,
finished-end retention, full sampled nominal motion, actual tool/assembly
paths, source-based interface requirements and jamming mounting space.

Remaining external/Stage2 qualifications are NOT MEASURED:

1. Shop acceptance of actual thin-rim/tool/profile/grinding/gauge capability,
   first-article material certificates, matching and dimensional inspection.
2. Clamp/jaw/swage/thread/retention preload/torque, free-spin, friction,
   fatigue and strength under actual load. No powered or suspended-object use.
3. Loaded cable seating/working radius, actuation/return and as-built motion;
   prescribed31pose geometry is NOT actual dynamics/continuousCCD.
4. Real vacuum chamber/pressure/friction/materials, driver/thermal behavior,
   harness/limit control and all later physical/100g grasp qualification.

No purchase/hardware/external shop contact is authorized by the design save.
Do not rerun historical SOFA trials to fill these absent physical readings.

## Historical original open issues — preserved

# Release blockers and next actual implementation

1. **Bearing/shaft axial capture**: current closed bearing envelopes and
   through pedestals do not retain races/shaft axially. Design removable
   outer-race plates and a manufacturer-compatible shouldered shaft/inner
   spacers. Do not press on seals or treat radial load support as axial capture.
   Verify all plates/bolts, motor/coupler space, installation and endplay.
2. **Shaft–drum/coupler torque lock**: current radial holes are not a complete
   locking device. Select machined split clamp or keyed interface; model
   real clamp screws and shaft shoulders; check part insertion and tool paths.
   No arbitrary set-screw capacity or motor loss is assumed.
3. **Tendon retention**: revH angled open seat clears the actual route, but
   the clearance seat does not clamp wire. Design a removable pressure pad/
   positive end stop with real adjustment/capture and supplier wire choice.
   Check0.5mm installation, wire crush, tail capture and pullout protocol.
   Drum crossholes alone also do not constitute retained termination.
4. **Motion scope**: final Root-datum strip+terminal calculation is prescribed
   kinematics, not an actual closing law. Entire moving wire and fixed-hardware
   clearance, continuous motion, root end strain and return remain unqualified.
5. **Manufacture**: finalize exact material lots, bearing fits/race shoulders,
   motor pilot projection, washer/locking/recess geometry and all machining
   tolerances. Current drawings are bounded review projections, not shop
   dimensioned GD&T release drawings. Electrical/limit interface unselected.
6. **Extension**: actual jamming chamber attachment/space is unfinished.
   Competition rules and physical material/strength tests need external data.

The first three are design tasks still executable in a subsequent bounded
session, NOT an assertion that every independent engineering path is blocked.
Hardware tests are NOT MEASURED; new CAD does not inherit B3 functional PASS.
