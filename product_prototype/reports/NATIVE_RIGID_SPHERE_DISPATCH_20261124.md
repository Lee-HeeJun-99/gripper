# Native RigidSphere dispatch compatibility — 2026-11-24

This is a registration-only ReGrip compatibility module, **not a new contact,
FEM, ODE or constraint solver**. Installed SDK files are unchanged. No object
state is prescribed. All finite Eyelet and Support collisions remain enabled.

## Actual evidence and rejected alternatives

- 1567: stock Local lacks RigidSphere/mesh intersectors. Replacing the sphere
  with a mapped Vec3 centre loses angular contact Jacobians: rejected.
- 1569: stock New whole-finger pilot timed out at .1275s and inverted Skin
  (minimum volume ratio -0.6422): rejected; original evidence retained.
- 1570: actual separated Skin gap +.398266mm, above .2mm buffer, yet New gives
  three nonzero rows. Min gives zero rows and zero motion.
- 1571: actual New detector points are 30.398266mm from the Skin surface;
  installed triangle projection branch reconstructs negative barycentrics.
- 1572: cyclic facet starts fix separated/loaded reference coupons without
  changing unordered facets or their orientation. This is not a full fix.
- 1573/1577: cyclic whole pilot completes with positive FEM but the sphere
  rests 30mm too low. Therefore this candidate is not a valid Holding model.
- 1576: detector-point/previous-accepted Skin-surface difference
  3.22526e-7m **FAILS** strict1e-12 API comparison; unchanged failure evidence.
- 1582: independent free100g RigidSphere on fixed Vec3 sphere under gravity:
  stock Min and Dispatch rest centre error 1.38778e-17m, mean Fz .981N,
  momentum residual 1.08420e-18Ns. New rests **30mm too low** despite correct
  .981N force. Force balance alone does not validate contact geometry.

## Implementation and validation scope

`sofa/native_rigid_sphere_dispatch/Dispatch.cpp` subclasses installed
LocalMinDistance and registers installed MeshMinProximityIntersection callbacks
for RigidSphere/Point, Line/RigidSphere and Triangle/RigidSphere only. Other
pair dispatch remains Local. No custom collision arithmetic is implemented.
The stock helper receives the active intersection's alarm/contact distances.

1578 built but 1579 failed dynamic loading: missing template definitions.
Adding the installed Intersection.inl include produced independent build1580.
Both failed build/load evidence and corrected build are preserved.

- Binary SHA256: `80aaf8c58ac22c8f874addf0d6cf35a7b904fbf163c429ea13d7dc471078b176`
- Compiled source SHA256: `0c093c723e54cd117f4adca0c9ba7304eddc221e5944b00b20e61c6301efddfc`
- 1581: five actual primitive/reference cases match stock Min q/v/impulse
  exactly (error0); loaded primitive angular J retained. Mesh-only Local
  contrast also error0. **Component contract only**, not convergence PASS.
- 1583: fresh three-finger .6s pilot, 60.546s runtime, 240 outputs/finger;
  minimum saved volume ratios .989778/.989945/.989950.
- 1584: actual Skin gaps .09963–.09967mm, no saved physical penetration,
  224 nonzero Skin response outputs; maximum Skin resultant1.14921N.
- 1585: **639 nonzero Guide–Guide rows** before .6s. This is real indirect
  mechanical coupling, not equivalent to Guide–Object support. No unbraced
  qualification from this pilot. Hold interval was not yet simulated.

All inherited hardware mass/inertia and finite support hull assumptions remain
uncalibrated. No actual wire, fabrication, time/mesh, energy or hardware PASS.
Old object-only 100g functional results1537/1541/1551 remain immutable and are
not promoted to unbraced finite-hardware qualification.

## Reproduction (new unique tags required)

Python is `/home/ubuntu/miniconda3/envs/robot_ws/bin/python`; run at repo root.

```bash
$PY product_prototype/sofa/build_rigid_sphere_dispatch.py --tag UNIQUE_BUILD
$PY product_prototype/sofa/rigid_sphere_dispatch_contract.py --help
$PY product_prototype/sofa/mixed_sphere_gravity_contract.py --tag UNIQUE_RADIUS
$PY product_prototype/sofa/dispatch_finite_hardware_grasp.py --tag UNIQUE --duration .6
$PY product_prototype/sofa/skin_gap_contact_contract.py --case UNIQUE --tag UNIQUE_GAP
$PY product_prototype/sofa/guide_pair_response_inventory.py --case UNIQUE --tag UNIQUE_PAIRS
```

Actual full2s run `dispatch_finite_holding1586` started after these component
and pilot checks. Inspect summary/process before any rerun. Preregistered
original100g Holding protocol retained; separate hardware-bracing audit required.
