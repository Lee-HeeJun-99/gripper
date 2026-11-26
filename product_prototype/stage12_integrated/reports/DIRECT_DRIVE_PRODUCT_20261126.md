# Actual direct-drive product candidate — not released

## RevAE failure → RevAF physical correction

AE1: 244 parts /63 nominal interfering pairs. AE2:238/51, FAIL retained.
AF6: **238 actual parts, 82 changed, zero changed-vs-all nominal interfering
pairs**. Full Assembly STEP and each changed STEP/STL exist. Root radius50mm
is unchanged. Drive center moves80→110mm; actual Palm OD230→290mm.
Real motor plate and its four motor bolts move with the motor; base bolts/nuts
move to matching new Palm bores. Existing Root/Terminal geometry is retained.
Footprint grows; this is not an unconditional improvement or adopted design.

Nipple cap bore is enlarged to clear the clutch; its actual retention/strength
must be requalified. Friction annulus8.3..9.6mm, two faces on AF. Actual free
wire is regenerated at220.652884386mm nominal, not the old190.809325mm supply
specification. Reusing the old wire procurement length or motion PASS is invalid.

Five failed AF generation directories remain. Incorrect inherited4.75mm beta
radius despite11.25mm idler geometry caused a discontinuous route. Configuring
both modules fixes it; exact torus/cylinder spans independently reproduce
wire volume. No tolerance or mechanical interference acceptance was relaxed.
Partial failed CAD remains local with full hash manifests, not bulk re-tracked.

## Independent results

- AF_geometry1:82 changed solids valid, single, positive; STL closed/positive,
  <1% volume discrepancy. Full assembly integrals agree within1.83e-11 relative.
- AF_drive_motion1:24 full-turn plus24 slip poses,1,272 BRep comparisons,
  zero detected intersections. This is sampled DRIVE geometry, not full
  Finger motion, continuous collision detection, wire sliding or powered dynamics.
- actual_boundary_AD1: actual PET free end/finite stop mapping, not a clamp
  or large-rotation strength result. No extra generic rod equilibrium experiment.

## Actual load-window and protection failure

AF_load_window1/2 use actual rotating-part geometric inertia coefficients.
Second scenario assigns aluminum-like2700kg/m³ to the cap, not the first
scenario's steel-like7830. Both are explicit sensitivity assumptions, not
certified densities. Bearing outer-race and entrained-wire inertia remain absent.
No resulting rpm is a safe operating speed or guaranteed tension cap.

AF_bypass1 finds a more important product problem: an input-supported drum
bearing is a **parallel torque route**. Even counterfactually granting perfect
friction torque limitation does not bound a seized bearing route.40N from
0.45Nm/11.25mm is only an illustrative holding-torque reference, not measured
jam force or certified motor maximum. AF is not an approved overload protector.

The corrective mechanism now being implemented is RevAG: ground-supported
hollow spindle, motor shaft clearance passage, independently retained bearing
inner ring, front input collet and ONE friction face. This is actual new load
topology, not an AF dimension scan. New axial bearing/collet load and hollow
spindle alignment/strength must be checked. No AF two-face torque result is
transferred to AG.

## Calibration preparation

AF_clutch_stand1 has actual fastener/Drum interference (FAIL). Stand2 moves
M4 fasteners beyond the actual17mm Drum radius; actual ten-part fixture has
zero nominal intersections and passes independent STL/integral audit. Input
hub is reacted through a keyed split stand, not assumed motor holding torque.
The stand is NOT proof-rated; sensor, bench anchoring and safe load permission
remain unqualified. No hardware operation was performed.

## Status

Official RevAA unchanged. No maximum protected load, physical material/strength
release, full Stage1/2 release or hardware PASS. Generic rod refinement is
deprioritized. Track changes A→B→C→A are actual CAD/analysis executions.
Automatic external launch budget remains0; no service was restarted.
