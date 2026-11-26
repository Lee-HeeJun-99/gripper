# Actual AK root finite pressure witness

Fixed hypothesis: nonuniform positive normal pressure may balance the actual
bolt height without requiring the previously tested full-area uniform pressure.
This is one finite geometry analysis, not a parameter scan or a FEM solution.
All235 actual AK part hashes were checked before analysis. For each Rail,
three actual FRONT/SKIN, SKIN/RAIL, RAIL/BACK contact faces were intersected
in their common yz projection within a predeclared z4..6mm band. Their
common finite patches have area6mm² each, centroid y=-10/+10mm and z=5mm.
Each carries a hypothetical0.5N, pressure0.083333MPa per total1N compression.
Total normal force and rigid-body moment match two equal bolt loads at z5mm.
No preload value is assigned physically. Original uniform-area3.455241199
Nmm/N residual is preserved: that distribution differs from this witness.

Independent .001/.002mm interior-volume slices on BOTH actual solids at
all6interfaces reproduce the6mm² areas (24 solid tests). Independent direct
moment and virtual-work checks pass. A0.1mm pressure-height corruption is
rejected. Two analysis/verifier children exit0 under4GiB/420s, one thread;
actual outputs, source snapshots, hashes and bounded execution metadata saved.
No this-cycle failed child; all historical failures and CAD/BOM preserved.

This is only an existence witness for necessary normal rigid-body equilibrium.
The separated bolts at y±16mm still require plate load spreading to y±10mm.
Actual elastic pressure, preload, bending/stress, contact opening, tolerance,
friction and full Finger behavior remain unqualified. A positive witness
cannot imply compliance/strength, grasp or whole-system energy PASS.
No adopted design, actual geometry, criteria, SDK or manager control changed.
Read-only release audit remains INTEGRATED_NOT_QUALIFIED. Next B work requires
bolt/plate/contact elasticity and source-backed preload/material evidence,
or separately analyzed positive retention; do not repeat patch scans.
Independent C six-DOF/ground attachment and A protection gates remain open.
Supervisor local save is PENDING; no Git writes or commit SHA claimed.
