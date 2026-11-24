# Finite wire and eccentric eyelet candidate

Starting commit cb1fc7d; original Raw/geometry/FAIL verdicts unchanged.

1411 first chamfer/fillet execution rejected; diagnostic angle arccos produced a
NaN from roundoff. Original output retained. Producer now clips only dot-product
domain for angle reporting, not geometric clearance or acceptance thresholds.
1412 corrected report: same rejection, minimum swept R5 wire clearance bound
−0.028361086mm. Four actual sample collisions at last through-guide, turn about
39.25°, wire-solid gap as low as −0.025861086mm. ID1.2/OD3/length2mm preserved;
explicit new 0.2mm×45° entrance chamfers, finite wire radius0.25mm.

1413 independent arc/support test: arc/support lower bound +0.996864984mm,
cross-route arc/arc lower bound +5.326835684mm. Initial arc subset only, not whole
assembly or dynamic collision proof. Original straight-bore1408 FAIL preserved.

Separate correction1414 moves bore axis to analytic R5 arc midpoint, not fitted
clearance. 1415 explicitly encloses the unchanged eccentric outer body in the
distance calculation; same bound +0.275364237mm. Remaining straight-span minimum
15.301168413mm; minimum wall bound recorded in summary. This is a separate
manufactured bore candidate, not an update to Native point-guide positions or
legacy CAD. Central ID/outer OD unchanged; through-bore terminal anchor, physical
wire equilibrium/friction, tolerances, strength, mass/COM/joints and dynamics
remain NOT QUALIFIED. No Native four-cable or Holding run is justified yet.

Three independent geometry unit tests executed PASS (signed solid distance,
exact R5/tangency, straight limiting case). Not physical convergence.

Reproduce with unique new tags:
```
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/eyelet_entry_geometry.py --tag NEW_ENTRY
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/eyelet_entry_geometry.py --tag NEW_ECCENTRIC --eccentric
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/eyelet_arc_support.py --tag NEW_ARC
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/test_eyelet_entry.py
```
Next actually executable cycle: generate eccentric finite solids with unchanged
outer body, verify manifold and independent analytic volume before any assembly
promotion. Existing time/mesh FAIL and all 100g FAIL remain unchanged.

## Finite solid implementation1416

Following f5f38dc, generated20 separate through-eyelet STL solids from parametric
source `sofa/eccentric_eyelet_mesh.py`; OD3/central ID1.2/length2mm, same declared
chamfers. All20 watertight, consistent winding, positive volume. Minimum radial
wall lower bound0.391607276mm. Independent regular-polygon volume identity error
≤3.56e−15mm³. Analytic circular volume and polygon discretization error are
reported separately. Eccentricity does not change ideal removed bore volume.
Actual mass/material/tolerance/strength NOT MEASURED; STEP NOT GENERATED.
These are local part coordinates, not yet assembled Native/CAD hardware. The
next cycle actually applies explicit route frames and measures STL roundtrip
error before proposing any assembly-level qualification.

Reproduce: `python product_prototype/sofa/eccentric_eyelet_mesh.py --tag NEW_MESH`
and `python product_prototype/sofa/test_eccentric_eyelet_mesh.py`.
