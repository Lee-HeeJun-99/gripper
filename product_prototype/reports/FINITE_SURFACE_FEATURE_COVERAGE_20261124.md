# Native finite-surface feature coverage — 2026-11-24

## Actual next cycles1671–1675

After locald590f55, executed both missing factorial cells, not a repeated
diagonal or a report-only task.1671 open/aggregate and closed/partition both
complete2Native steps in0.305/0.368s. Independent complete facet audits1672/
1673 give the completed table:

| Static shape | 32Guide Triangle models | One Guide Triangle model |
| --- | --- | --- |
| Open wire | 2/2penetrating states1666 | 0/2penetrating states1672 |
| Closed wire | 2/2penetrating states1673 | 0/2penetrating states1669 |

1674 actual q/v/impulse comparison: cap-only effects EXACTLY0 in both columns.
Ownership alone changes position1.676867um,orientation.00134684rad,linear
velocity.00838433m/s and angular velocity6.41317rad/s in this particular
assumed-inertia STATIC INITIAL coupon. Not physical material/mass calibration,
not a1.68um design improvement,not energy/time convergence. A physical-surface
equivalent collision representation is changing contact reduction/order.

Actual next Native dynamic_guide_ownership1675 RUNNING: reuse1655initial Beam
scene, keep11BeamDOFs/local25umwiremesh/openendgeometry,E/rho/mass/ALLGuide
faces/Line/Pointfeatures,BC,dt,friction,solver; only merge Guide Triangle model
ownership.110steps through11ms includes1655 first facet failure10.6ms. Bounded
420s/4GiB,forecast114s from measured206.38s/200steps. No unverified checkpoint,
state overwrite,full3finger rerun or static-success promotion.

Inspect actual completion before execution. Then independent roundedsolid
vertex and wholefacet audits. If it fails, stop this ownership family rather
than sweep partitions/dt/forces. Previous failedNative/static/Ray results stay.

```bash
$PY product_prototype/sofa/finite_surface_factorial.py --tag UNIQUE
$PY product_prototype/sofa/finite_surface_factorial_assess.py --tag UNIQUE
$PY product_prototype/sofa/dynamic_guide_ownership.py --tag UNIQUE
```

Start6022c14, clean working tree. Earlier Raw/verdicts preserved. No SDK edits,
new contact law/solver, full gripper rerun or remote operations.

## Registry and matched actual-shape coupon1663–1667

New public-API registry observer1663 builds against installedSDK in3.280s.
It queries `Intersection::findIntersector` once; no registration or mechanical
writes. Exact compiled source and binary hashes frozen per build/coupon.

1664 fails **initialization**, not physical instability: RequiredPlugin Mass
appeared after the wire node, so UniformMass was unavailable during parsing.
The bounded guard's generic `nonlinear_failure` label is not a Newton diagnosis.
Keep both failed logs. Prepending only the Mass declaration gives fresh1665:
control/probe both2steps,0.475/0.511s, actual q/v/surface/impulse differences0.

Actual registered Min pairs: Triangle–Line and Triangle–Triangle are NULL;
Triangle–Point, Line–Line, Line–Point, Point–Point supported. Installed
MinProximityIntersection.h explicitly says the first two are ignored. NULL
does not prove all composite mesh collisions are impossible: other features
still generate actual responses.1666 entire saved-facet audit finds actual
penetration in both accepted states of the isolated geometry coupon.

This uses ALL6144 wire facets and ALL768 Guide facets from actual1655 at10.6ms.
Only for isolation, the deformed wire is a FREE rigid INITIAL shape at zero
initial velocity with inherited positive, uncalibrated inertia. No Beam, cable,
runtime state override or checkpoint restart. Deliberate initial overlap is a
diagnostic condition, NOT an admissible initial grasp or actuation success.

Independent1667 finds16 actual wire-edge/Guide-triangle crossings over8saved
wire faces using strict interior segment fractions/barycentrics. Their direct
Native Line–Triangle pair is NULL in actual1665 registry. This supports a
feature-coverage limitation at these exact geometries, not a sole-cause claim
for wholegrasp/time convergence or blanket failure of every Native algorithm.

## Documented stock RayTrace alternative1668–1670

Primary installed example/header requires RayTraceNarrowPhase with
TriangleOctreeCollisionModel. The coupon tests this supported model contract,
not a renamed unsupported BVH pair. BOTH variants aggregate the exact original
768 Guide facets into one model and close the physical finite-wire endcaps:
two end-centre points/32 outward triangles added far from Guide, all original
faces and Line/Point models retained. Wire becomes a closed6176-facet solid.
Mass/inertia assumption, physical gaps, dt, mu0 and solver tolerance unchanged.
This is not an isolated one-parameter change from the old open-wire coupon.

| Variant | Native execution | Actual response | Complete saved facets |
| --- | --- | --- | --- |
| Closed Min/BVH control | 2steps,0.305s | nonzero Triangle–Point row | no intersection1669 |
| Closed Ray/Octree | 2steps,0.168s | no nonzero row | penetration in both states1670 |

Ray candidate REJECTED for this concrete all-feature model contract. Do not
remove Line/Point features or tune buffers to fabricate a qualification.
Installed existence/zeroexit is not physical validation. The Min control's
initial-overlap correction is not wire sliding, dynamic bending or grasp PASS.

Next actual task: two missing cells of a2x2 static geometry contrast isolate
endcap closure from Guide collision-model ownership. This is needed before
interpreting why the new closed Min control differs from1665. No new large
Beam/grasp run based only on these static results.

```bash
$PY product_prototype/sofa/build_intersector_registry.py --tag UNIQUE_BUILD
$PY product_prototype/sofa/finite_surface_capability.py --tag UNIQUE --build-case intersector_registry_build1663
$PY product_prototype/sofa/wire_edge_facet_contract.py --tag UNIQUE
$PY product_prototype/sofa/raytrace_finite_surface.py --tag UNIQUE
$PY product_prototype/sofa/rounded_wire_surface_contract.py --tag UNIQUE --case raytrace_finite_surface1668/ray
$PY -m unittest discover -s product_prototype/sofa -p test_finite_surface_contract.py
```

All actual commands, source/scene/binary identities, SDK and runtime bounds
stored in new result folders. Prior time/mesh/API/Guide-bracing FAILs unchanged.
No new100g Holding/Lift, material, energy or fabrication qualification.
