# Open hinge continuation1771–1775

Start HEAD74e2d31, clean branch development/regrip-autonomous-research.
No Native child or new grasp run: geometry prerequisites remain incomplete.

1771: finite clevis/leaf/unretained pin constructed as separate positive closed
solids. Initial zero CSG overlap; provisional diagnostic only because the first
producer used max(0, volume) on empty intersections. Empty-intersection warning
retained; not an authoritative nonfinite check.

1772: explicit empty-face handling and finite/nonnegative volume assertion.
141 samples0..70deg, three pairs per sample: fork–leaf, fork–pin, leaf–pin.
Every intersection0mm³. Nominal pin radius.25mm, hole.30mm, radial clearance
.05mm, leaf thickness.4mm, fork walls.3mm, axial gaps.05mm, stack1.1mm.
SAMPLED GEOMETRY PASS only, not continuous clearance/dynamics/strength.

1773: all24actual hinge positions from1768 (six guides, two levels, root/carrier)
with72finite parts. Original1700actual tube axes and incoming wire endpoints.
No positive inscribed finite wire intersection or negative sphere gap.
INITIAL SCREEN only; not completed root/carrier linkage.

1774: additional actual original eyelet/support solid intersections, excluding
support5 specifically replaced by proposed mechanism, not deleting actual tube.
REJECTED:12positive intersections, each lower carrier fork/leaf with own eyelet5.
Fork~.021189mm³, leaf~.014126mm³. This is a physical obstruction witness.

1775: single physical response to1774: subtract actual tube mounting bore
radius.8755mm from NEW carrier-end fork/leaf only, preserving original tube
OD1.651/ID1.1938/L2mm and wire diameter.5mm. No collision model disabled.
All72new parts remain single positive-volume connected solids; original
hardware intersections0, incoming finite wire intersections0, sphere failures0.
INITIAL SCREEN only. A cut bore is actual geometry, not an ignored collision.
Not all new–new pairs, Skin/Rail, moving wire or full linkage are checked.

Reproduction (NEW unique tag required):
```
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/open_hinge_coupon.py --tag NEW --sweep
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/open_hinge_placement.py --tag NEW --hardware --mount-relief
```
Each result has producer snapshot, source SHA, summary and metre STL.
Placement also hashes original scene, seed summary and hinge source.
No binary/SDK used in these CSG tests: binary SHA NOT APPLICABLE.
Materials, strength, retention, fit tolerances, friction, assembly tooling and
hardware measurements NOT MEASURED. No numerical or unbraced grasp PASS.
Latest actual full grasp1741/1742 remains FAIL:32.928255mm/s and30internalHoldrows.

Next READY: integrate connected link bodies and true root/carrier forks,
retained pin construction, all new-part pair/Skin checks and moving-wire
clearance before any new Native single-finger mechanism. Do not claim the
standalone fork coupon as a finished six-guide mechanism.
