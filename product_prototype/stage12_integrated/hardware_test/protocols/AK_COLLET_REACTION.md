# AK collet combined-load test preparation — NOT authorized to load

Fixture `fixtures/AK_collet_stand1` contains the actual AK input hub/clamp bolt,
a nominal minimum4.988mm D-shaft with4.4mm across flat, an integral machined
flange, reaction plate and two finite M4 bolt/nut envelopes. Actual STEP/STL
and independent mesh inspection exist. No motor bearing or holding torque is
used as a fictitious reaction. No weld is assumed between shaft and flange.

This is a **reaction fixture only**, not a complete calibrated rig. Do not use
it until its material, shaft/flange stress concentration, M4 grade/thread
engagement, plate bending, rated bench anchors and guard are qualified. No
actual safe test load or powered authorization exists. The mounted minimum
shaft tip Y14.5 gives9.7mm nominal grip; the actual motor flat orientation and
finish require verification. A fixture-defined+X flat does not prove the
motor's actual orientation relative to the clamp bolt.

Before loading:

1. Inspect shaft diameter, flat, straightness, surface finish and bore.
2. Record actual clamp bolt grade, lubricant and tightening method; instrument
   preload or validate the torque/preload scatter. Do not equate bolt preload
   to shaft contact normal force.
3. Fit a separately designed torque/axial loading adaptor to actual hub
   geometry; verify that it does not bridge the tested shaft/hub interface.
4. Calibrate axial load, torque and independent hub/shaft slip displacement
   measurements. Store certificate/hash, uncertainty, zero and timestamp.
5. Qualify fixture and install guard; define safe maximum and stop limits
   **before** test, from structural/rated evidence, not the desired result.

Apply torque-only, axial-only and combined loads gradually, including actual
spring-reaction direction. Measure first slip and permanent displacement.
Repeat after controlled release/retightening with specimen identity retained.
Stop at fixture strain limit, unexpected displacement, sensor saturation,
fastener motion or the authorized maximum, whichever comes first. No automatic
loading is implemented here. A no-slip test only supplies a tested lower
capacity bound at that load/uncertainty; do not infer ultimate capacity or
fatigue life. Maximum product transient tension is still unqualified.

Required record columns: timestamp_s,specimen_ID,shaft_diameter_mm,
flat_across_mm,grip_mm,bolt_preload_N,torque_Nm,axial_force_N,
hub_shaft_relative_angle_rad,hub_shaft_relative_translation_mm,
fixture_strain,temperature_C,calibration_ID,authorized_limit_ID,stop_reason.
Blank cells mean unmeasured, never zero. Fixture CAD preparation is not a
hardware PASS, Stage1 manufacturing release, or Stage2 system approval.
