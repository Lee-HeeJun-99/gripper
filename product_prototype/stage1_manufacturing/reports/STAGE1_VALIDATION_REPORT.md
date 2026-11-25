# Actual Stage1 CAD execution journal

No Native/hardware execution in this Stage1 branch of work.

1. revA:46 OCC parts,21 positive-volume collisions. FAIL, retained unchanged.
2. revB:52 OCC parts;0 nominal bulk collisions; all exported part meshes
   watertight, winding consistent, positive volume. Actual independent STEP
   assembly reread volume agrees. Conservative full360degree drum envelope:
   no foreign-part overlap. Own shaft overlap of filled envelope explicitly
   reported, not hidden. Prescribed0–60degree Finger strips sampled every2deg:
   no interFinger intersection. This is NOT continuous collision detection,
   a full Finger/terminal/wire trajectory, or Native mechanics. Mounting feet
   in this revision do not yet have a complete physical connection.
3. revC:112 OCC parts incl nominal M3 head/shank/nut envelopes, integrated
   machined mounting flanges and actual motor bolt holes.12 interference
   pairs, FAIL. Enlarged pedestals needed for bearing-safe vertical bolts
   conflict with Root/front-clamp tool/bolt space. Do not fabricate revC.

Raw evidence: `cad/exports/rev*/audit.json`, each revision's STEP/STL; revB
independent mesh/rotation/motion/tolerance results in
`validation/motion_revB/summary.json`, exact hashes in input_export_sha256.json.
revB/revC producer snapshots retained. revA producer is in Git f0166cd.

Commands (NEW revision/tag mandatory; old directories deliberately refuse overwrite):
```
PYTHONPATH=/tmp/regrip_stage1_ocp /home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/stage1_manufacturing/scripts/build_stage1.py --revision NEW_REVISION
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/stage1_manufacturing/scripts/verify_stage1.py --revision EXISTING_REVISION --tag NEW_TAG
```
Toolchain: temporary `cadquery-ocp7.9.3.1.1` and `vtk9.6.2` under/tmp only.
System/SOFA SDK untouched. Scripts use real OpenCascade BRep Boolean and STEP
translation, not renamed meshes. Purchased envelopes omit bearing internals,
true motor internals, helical threads and fastener recesses; they are NOT
manufacturing CAD for purchased components. No physical strength inferred.

Bulk collision reporting threshold1e-7mm³ is numerical Boolean reporting,
not a physical permitted penetration. It is not a dimensional-clearance proof.
Zero bulk overlap does not certify positive tolerance clearance or assembly.

## Subsequent actual implementation cycles

- revD121single solids:6cross-module shaft/pedestal-to-motorplate overlaps.
  Inward relocation rejected, not reduced by a tolerance allowance.
- revE157single solids:3idler-foot/bolt-head overlaps. New outer drive bank
  with fixed idler resolves Root service space; the first foot still failed.
- revF157single solids:0bulk overlaps. Independent export lookup FAILED:
  `Path.with_suffix` truncated decimal part IDs. CAD STEP assembly existed,
  but per-instance BOM paths were wrong. Original outputs retained.
- revG fixes filename generation;157closed meshes,0bulk/foreign rotor-envelope
  overlaps. Actual six wire span tests find3routes obstructed by idler foot
  and terminal front. These are real finite-radius obstacles, not ignored
  as desired contacts. Service extraction25poses clear. Initial driver test
  touched its own head face at mesh precision; this was not hidden by a
  larger collision tolerance. New declared approach stops0.1mm before face.
- revH adds real foot relief and an incoming-direction aligned open wire seat.
  All157BReps single valid solids; STEP reread error and all actual collision
  pairs in audit.json. All meshes closed;0bulk overlaps;6/6straight finite
  REST wire spans clear; circular idler arc only analytic intended contact.
 25unloaded extraction poses clear. Full-assembly tool approaches blocked6/12;
  declared pre-pedestal assembly approaches clear12/12.
- Corrected motion uses Root clampz=-7 (93mm span) and finite transported
  terminal hardware. First interFinger collision58deg;0–56deg samples clear.
  This replaces the incomplete bare-strip proxy as the CURRENT kinematic
  evidence, without altering its old result. Whole-wire/fixed-part motion
  remains open. No continuous CCD or actual dynamics inferred.

Authoritative final evidence: cad/exports/revH/audit.json;
validation/service_revH_completed/summary.json;
validation/motion_revH_rootdatum_v2/summary.json. Review projection drawings
are under cad/drawings/motion_revH_rootdatum_v2, not shop-release GD&T.

Two orchestration failures also occurred: checks dispatched before revH audit
completion could not read audit.json; corrected Root-datum analysis then hit
an existing drawing directory. No failed output was overwritten. Producer
completed first; new tags and tag-specific drawing paths fixed orchestration.
Manifold empty-intersection centroid warnings occurred; they are not read
as a physical signal or used to synthesize a force. No Native experiment.

Current verdict STAGE1_DESIGN_RELEASE_FAIL. Full assemblies exist as actual
STEP, but axle capture, torque locks, tendon retention, tolerance/drawing and
full motion/extension gates are not complete. Neither tests nor CAD quantity
changes that verdict. No purchased part strength or hardware measurement.
