# 100g functional reproduction and indirect Guide bracing

## Preserved achievement and qualification limit

Actual paired-QR294node Native trials1534 and1538 independently complete2s,
800states/finger. Independent original-goal assessments1537/1541 both pass:
slip0.000239391mm, maximum speed2.508229mm/s, support gap41.993608mm,
Skin mean vertical force0.980995N versus0.981N weight. Guide/Rail/Support
object forces are zero. All saved tetrahedra have positive signed volume.
Object Raw SHA is identical in both independent executions. This demonstrates
reproducibility, NOT time or mesh convergence. Old numerical FAILs remain.

Actual response audit1540 nevertheless finds1449 nonzero Guide–Guide rows
during1.6–2s. Peak scalar multiplier/dt0.046946N is NOT a reconstructed
Guide body force/wrench. Hardware may brace fingers indirectly without
directly supporting the sphere. Original object-only exploratory verdicts
remain immutable, but unbraced mechanism qualification is NOT satisfied.

## Single geometry-root intervention, not parameter search

1542 derives sector margin0.8921217941633586mm from the original0.5mm:
40bisections in the declared0.5–1.5mm bracket restore1mm minimum finiteGuide
gap in actual saved1534 parent-pose replay. Predicted Guide–Object gap2.493mm,
finite straight-segment wire–Object gap4.045mm. Only mapped child-guide rest
offsets/pullpoints change. All finite SphereCollisionModel radii, parent
frames/masses, Skin reference/material, T1.5N/cable and friction0.3 remain.
This is a counterfactual replay, not new equilibrium, physical eyelet/COM
qualification, fullCAD swept interference, or Holding evidence.

Actual new Native fixedsingle1543 completes.25s in4.020s; free3finger1544
completes.6s in73.431s; withdrawal1545 completes1.2s in68.848s. All saved
tetrahedra remain positive, minimum ratio0.989898. No SDK changes.

1546/1547 actual response rows show the intervention does NOT remove all
Guide bracing:804 nonzero rows before.6s, onset0.3625/0.365/0.3725s in the
three neighboring finger pairs. Actual proxy gap1548 stays near0.199054mm,
the Native0.2mm contact distance, not the old-pose prediction1mm.
1550 directly compares new accepted Guide coordinates with the old-parent
pose prediction at exact common times: maximum differences0.543–0.654mm
per cable, near0.36–0.39s. Thus coupled motion changes after rerouting;
the old-pose clearance cannot be promoted to new dynamic clearance.
No collision removal or further random margin sweep is justified.

Full1549 completed2s/800states each in81.388s, all saved FEM positive.
1551 original object-only goal PASSES: signed downward displacement−0.00009770mm
(slightly above1s reference, NOT a negative physical slip magnitude), speed
0.297867mm/s, SkinFz0.980999934N, all other object-load partitions0.
But1552 STILL has1449 nonzeroGuideGuide holdrows, peak scalarλ/dt0.040137N.
Thus this candidate FAILS the newly explicit unbraced qualification, despite
lower object speed. Preserve both independent verdict scopes. Stop this
saved-replay-margin family rather than tune more margins. Next meaningful
diagnosis is actual Guide contact-wrench attribution and load-path mechanics,
not collision removal, larger contact tolerances or force/dt scanning.

## Fixture and reproduction

1535 independently verifies current-mesh root free-subset translation and
public Cable pullPoint motion: max position error4.07e-19m, interior root
velocity error0, origin error1.76e-19m. No object was present: NOT100g Lift.
Actual Root work, actual hardware material/attachment/inertia and global
energy are NOT MEASURED. Existing strict1e-12 mirror velocity FAIL1528,
time0.1% FAIL and mesh1% FAIL remain unchanged.

Commands, from repository root using robot_ws Python:

```bash
python product_prototype/sofa/grasp_goal_assess.py --tag UNIQUE --case paired_mesh_repeat1538
python product_prototype/sofa/guide_pair_response_inventory.py --tag UNIQUE --case paired_mesh_hold1001534
python product_prototype/sofa/test_unbraced_route.py
python product_prototype/sofa/guide_bracing_events.py --tag UNIQUE --case unbraced_three1544
python product_prototype/sofa/route_replay_error.py --tag UNIQUE --case unbraced_three1544
```

Three route-contract unit tests actually pass; these verify frozen config,
parent frames/collision preservation and replay scope, NOT physics accuracy.
All result directories preserve producer snapshots, source/input hashes,
actual Scene and Native process manifests where applicable. detector.csv
remains local and excluded fromGit. No remote Push/history rewrite.
