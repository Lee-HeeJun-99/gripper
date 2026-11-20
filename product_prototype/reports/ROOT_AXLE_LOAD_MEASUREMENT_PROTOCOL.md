# Root axle / wire physical qualification interface

CAD calculation841 is NOT measured strength. At the assumed B3 input1.5N/branch,
each actual CAD76deg root turn gives an ideal resultant1.846984426N.
Six world-frame load vectors/centres are in `results/product_root_load841/summary.json`.
Resultant force does not certify the wire, motor, bond, pin or printed fork.
Actual materials, operating tension, friction and load limits remain undecided.

## Bench sequence (all NOT RUN)

1. Record part revision/STL hash, material batch/process, pin and bore diameters,
   wheel width, fork span, groove width and actual axial endplay. Use calibrated
   dimensional metrology and preserve raw readings/uncertainty, not only nominalCAD.
2. Fixture a complete Root bridge at its real Palm bolt seats, with intended
   fasteners/retention. Route actual wire over the wheel at the CAD entry/exit
   directions. Measure both branch tensions with two calibrated load cells.
3. Increase applied load from zero through the intended operating range only
   after a safe fixture/guard and material limits are established. Measure axle
   and fork displacement relative to the bolt seats, not laboratory-table motion.
   Capture residual deformation after unload. No allowable deflection or proof
   safety factor has been approved; acceptance is **BLOCKED**, not automaticPASS.
4. Measure start/steady sliding torque, tension difference, endplay and wheel
   rotation under load in both directions. Use encoder/video plus torque/load
   measurement. Equal branch tension is a hypothesis to test, not fill into data.
5. Retention/pullout and repeated loaded cycles require separate guarded tests.
   Record actual cable minimum bend recommendation, wear, groove damage, wire
   strand damage and retention change. No cycle-life claim before testing.

Blank per-part CSV: `results/product_root_load841/physical_measurements_TEMPLATE.csv`.
Empty cells are unmeasured, not zeros. Instruments, calibration, uncertainty,
batch and timestamp are mandatory for physical evidence. Simulation outputs
must never be entered as measurements. Raw force/displacement/time traces must
accompany the filled sheet; material allowables need traceable supplier/test data.

Ideal screen only: D1mm pin, ASSUMED simply-supported2.8mm span/central load
gives double-shear1.176MPa and bending13.169MPa. Real boss/fork boundary conditions,
clearance/contact and thread stress are not represented. Neither number is a
strength margin, proof load, manufacturing tolerance or material recommendation.

Next software work: check a Native sliding cable/contact component contract against
the839 reference; otherwise keep this featureBLOCKED and continue independent
assembly documentation. Do not invent an ODEsolver, remove collisions or reuse an
old B3 checkpoint with changed routing. Time/contact/FEMmesh/100g/Lift/STEP Gates
remain unchanged.
