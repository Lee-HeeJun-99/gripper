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

1695 Native.6s pilot completed58.465s, positiveFEM(min.989664),224Skin response
outputs.1696GuideGuide0;1697actual72hardware414720pairframe screen clear;
1699all crossFinger responses0, including Guide/foreignSkin/Rail sources.
1698Skin/Sphere minimum actual surface gap~.0996mm, no saved penetration.
This successful pilot did NOT qualify the final motion.

1700full2s Native completed224.325s/800outputs perFinger;2xpilot forecast
389.77s<420s cap. Positive savedFEM min.989314. Original100g/R30/mu.3 and
1.6–2s/2mm/5mm/s protocol unchanged.1703actual object goal FAIL:
slip.233781mm, speed25.59132mm/s, Support gap42.22625mm, Skin meanZ.984388N;
Guide/Rail/Support/other object loads0. Momentum residual4.337e-19Ns.
Solver reaches1001/1000 iterations; no numerical/physical PASS.
1704finds738crossFinger hardware rows,99inHold;no other crossFinger sources.
1705actual geometry screen1,382,400pairframes:76inside-buffer pairframes,
ALL are physically separated convex envelopes (axis gap.199414–.199999mm).
Do NOT call these actual solid overlap or ignore the real Native impulses:
buffer-mediated support still fails the UNBRACED gate.1701Root/6origins API
PASS100um/10ms only,not Lift. Full Holding failed, so Lift was NOT run.

1706actual new trajectories:18guides fail straight radius.25mm wire/bore
consistency; real flexible-wire bending is required,not proven by idealCable.
1707necessary fixed-pose outward routing intervals remain nonempty (minimum
width9.29734mm for this candidate),but actual ring own-sector excess reaches
1.83178mm. This disproves a universal geometric-impossibility claim,not a new
dynamic route success. Previous two replay successes failed to transfer;do not
repeat a frozen-margin/offset root search as if it guaranteed mechanics.

1708separates actual speed and torque:peak at1.7125s,velocity
(7.6283,-.19975,24.42713)mm/s; maxhorizontal20.74952mm/s,
maxabsolutevertical24.86472mm/s. Normal-row sphere torque3.56078e-5Nm
(old1586peak3.53275e-6Nm); normal angular midpoint object work+1.32161e-5J,
tangent−1.25045e-5J. Not global energy/friction closure or sole-cause proof.
Coulomb cone excess<=2.711e-20Ns does not certify correct contact kinematics.
1710crosslinks actual buffer geometry/rows:235active pair-times,76inaccepted
buffer list,159outside; previous/free/accepted phases differ,not automatically
a detector bug. Simply subtracting.2mm buffer still leaves1.63178mm worst
fixed-pose sector excess. No buffer scan,zero-margin trial or gate relaxation.

1702examined documented stock SlidingLagrangianConstraint as an alternative:
2transverse bilateral rows/2endpoint unilateral rows,not finite-bore clearance,
friction or material-edge reassociation. BLOCKED as an equivalent wire-contact
replacement; no cosmetic joint coupon or hidden transverse support added.

Actual config includes new
tube dimensions; inherited rigid mass/inertia NOT recalibrated to304steel or
machined holders. All output/source/scene/SDK/binary hashes preserved.
The candidate is REJECTED for the original functional goal; no tube-size scan.
The ideal Native CableConstraint is NOT a solution of1675finite-wire sliding
or1678normal-update failure; no finite-wire/physical/completeUNBRACED grade.

Reproduction with UNIQUE tags:

```bash
$PY product_prototype/sofa/capillary_guide_candidate.py --tag UNIQUE
$PY product_prototype/sofa/capillary_bored_support.py --tag UNIQUE
$PY product_prototype/sofa/capillary_native.py --tag UNIQUE
$PY -m unittest discover -s product_prototype/sofa -p test_capillary_bore.py
```
