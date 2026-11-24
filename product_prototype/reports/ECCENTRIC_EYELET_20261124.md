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

## Initial placement1417 and actual-state replay1418

After ae4bef8, actually generated20 initial world-coordinate STL parts plus
combined visual assembly. Explicit right-handed frames retain original outer
guide centres; only bore axes are eccentric. STL roundtrip maximum vertex error
4.443900557e−6mm; polygon hole sagitta and measured serialization error deducted
from analytic clearance leave minimum +0.275119080mm. PASS_INITIAL_PART_PLACEMENT
ONLY. Terminal anchors and complete support unions are not part of this assembly.
STEP/material/tolerance/strength/dynamic assembly remain unqualified.

Then actually implemented1418 trajectory replay, using all240 accepted guide
frames from existing Native1398. Each hypothesized R5 arc is carried rigidly by
its original Guide Rigid3; links between arc endpoints are straight. Initial
maximum tangent mismatch2.95e−14°; during opening maximum7.545254830°, endpoint
7.544934256°. Minimum endpoint link length8.869085127mm. Thus REJECT fixed-arc
C1 replay proxy: static local fit does not ensure a smooth wire under motion.
This does NOT prove a real flexible wire cannot slide/bend. Hypothesized attached
arc motion is a replay of old ideal-body states, NOT new hardware dynamics.

No new Native physics run was justified: four-route wire/contact representation,
terminal anchors, measured material/mass/joints remain missing. Existing Native
1398 data were reused, not rerun. Next READY finite_wire_motion_contract must
check installed Native finite wire/guide features in a small coupon, with actual
wire radius and changing curvature; no custom solver or offset/dt parameter sweep.

Reproduce with unique tags:
```
python product_prototype/sofa/eccentric_eyelet_assembly.py --tag NEW_ASSEMBLY
python product_prototype/sofa/eyelet_arc_replay.py --tag NEW_REPLAY
python product_prototype/sofa/reinforcement_cycle_validation.py --tag NEW_REGRESSION
```

## Actual Native finite beam follow-on1420–1423

Did not stop at replay rejection: inspected installed BeamAdapter examples and
headers and implemented `native_finite_wire_pilot.py`. Uses stock
BeamInterpolation + AdaptiveBeamForceFieldAndMass + EulerImplicit + BTD, radius
0.25mm,length20mm,10edges. E2GPa,density1000kg/m³ are explicit research assumptions,
not measured tendon properties. Root fixed,zero gravity,tip force10µN,dt100µs,
20steps. Existing frozen332 observer reused without source/binary edits.

1420 failed during factory creation: GenericConstraintSolver is not a registered
v26 component. Error/log/zero outputs preserved. Correction1421 uses installed
BlockGaussSeidelConstraintSolver ONLY as unused read-only journal target; no
Lagrange cable/contact constraints exist and DefaultAnimationLoop compatibility
is NOT being certified. Raw1421 scope still calls the journal target Generic;
actual Scene is authoritative and current producer wording is corrected.

1421 actual20 outputs,SOFA errors0,tip y7.663760011µm,fixed-root error0,
runtime0.1054s. This transient is NOT static equilibrium or theoretical stiffness
agreement. Matched zero-load1422 actual20 outputs,max q−rest6.94e−18m,
max velocity8.20e−14m/s: original coupon1e−12 criterion,NOT bitwise identical,
runtime0.1051s. Independent tests compare both Scenes: only force and log path
differ. Limits4GiB/60s;peakRSS NOT MEASURED. Complete command,Scene/observer/
BeamAdapter/runSofa hashes and raw state in per-case summaries. 1423 regression
FAIL preserved: newly added bitwise-equality assertion was stronger than original
coupon1e−12 and failed on actual roundoff.1424 also FAIL: an atomic patch was
rejected and the intended test edit was not applied before that retry. Both
logs preserved.1425 actually reruns corrected original1e−12 scope,not a relaxed
physical threshold. Its summary is authoritative.

NextREADY finite_wire_motion_contract is now specifically a finite beam/eyelet
contact and sliding representation coupon, not redoing1421/1422. Native finite
beam availability is scoped component PASS. Guide bore contact/friction,
changing contact location,full wire equilibrium,material calibration and
constrained-loop/time/mesh/energy gates remain open. No new four-cable or grasp
run,100g success,STEP or fabrication claim. No process remains intentionally
running after session.

Reproduce only with fresh tags:
```
python product_prototype/sofa/native_finite_wire_pilot.py --tag NEW_WIRE
python product_prototype/sofa/native_finite_wire_pilot.py --tag NEW_ZERO --zero-load
```
