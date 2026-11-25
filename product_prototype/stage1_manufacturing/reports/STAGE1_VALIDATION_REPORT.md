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
