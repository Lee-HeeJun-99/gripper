# Thin-wall ferrule alternative — unqualified research candidate

Independent next cycle after axial-setback rejection, not a chamfer/offset scan.
Primary dimensional source checked2026-11-24:
[Vita Needle stock tubing chart](https://www.vitaneedle.com/products/small-diameter-tubing/master-tubing-gauge-chart).
16RW nominal OD.065in / ID.047in; OD tolerance±.0005in, ID±.0015in.
Converted nominal OD1.651mm, ID1.1938mm, wall.2286mm. Chart identifies full-hard
welded/drawn304SS and also lists316 options. These are supplier dimensions,
not measured ReGrip material or domestic availability/price/strength claims.
2mm cut length and its finish/tolerance are ReGrip assumptions, not supplier data.

1692 generated all36finite tubes at original centres/axes with all collision
features retained. Original cable force/path/Guide attachment unchanged.
1693onOLD1586motion:1,382,400pairframes, no uncertified inter-finger envelope
clearance; minimum hardware/Object surface gap1.71030mm. Replay only.
BUT independent support/slab radial projection reveals14supports occlude
manufacturer maximum bore ID; worst clearance−.099136mm. FAIL preserved.
No Native run of this obstructed candidate.

1694 implements physical SUPPORT through-relief: minimum inscribed1.4mm
diameter, extending beyond actual support axial bounds. Tube bore untouched.
Manifold mesh CSG (NOT FreeCAD/OCC/STEP). All36supports remain one watertight
connected positive-volume solid; original3foot centres retained inside each.
Independent every-triangle clipped-slab radial minima give minimum clearance
**.08404999mm** to manufacturer's maximum ID. Axis containment checks also
exclude a solid blocking the hole. Total support volume removed.643916mm3.
Tube/support radial reach is only~.01915mm at minimum specified OD; this is
NOT adhesive joint strength, retention or manufacturing tolerance approval.

Current actual1695 Native.6s pilot RUNNING; do not rerun/overwrite. No full2s
unless new FEM/contact/geometry/runtime gates pass. Actual config includes new
tube dimensions; inherited rigid mass/inertia NOT recalibrated to304steel or
machined holders. All output/source/scene/SDK/binary hashes preserved.
The ideal Native CableConstraint is NOT a solution of1675finite-wire sliding
or1678normal-update failure; no finite-wire/physical/completeUNBRACED grade.

Reproduction with UNIQUE tags:

```bash
$PY product_prototype/sofa/capillary_guide_candidate.py --tag UNIQUE
$PY product_prototype/sofa/capillary_bored_support.py --tag UNIQUE
$PY product_prototype/sofa/capillary_native.py --tag UNIQUE
$PY -m unittest discover -s product_prototype/sofa -p test_capillary_bore.py
```
