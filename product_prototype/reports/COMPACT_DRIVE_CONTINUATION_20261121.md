# Compact drive continuation797–805

Baseline featurea57d9db1b0b64ef71580584a57c874af2a6f3ccf. Actual CAD/reference
work only;no new SOFA,holding/lift,time/mesh or fabrication qualification.

## Implemented and measured

797 changes the support topology from outerx78mm backbone to behind-pulley
x58mm backbone. Same boltedfeet,finite wheels,wire routing and turn2service
dogleg are retained. This is a deliberate load-path/envelope candidate,not an
actuationStroke/GuideOffset sweep.67closedpositiveSTLs,37.0902s,wirehits0;
6zero-volumePalm-matingBoolean results retained (NOT erased/rounded).

798 joins the new bridge set to finite Root forks/bosses,retaining previous
36shims and all obstacles:12newreadbacks,292fullparts,49.5772s. Wirehits0,
same6zero-volumePalm results. No new connection force/stiffness certification.

799 checks intermediate244part drive:12bores/12nominaldrivers/54pin samples
allclear,5.3133s. This is NOT final292part full-motion service certification.

800 full-service audit stopped on unsupported nested canonical transform:
FAIL preserved with exact executed source.801 independent matched comparison
finds ONLY6support bridge shape recipes changed among292identicallynamedparts:

|Reference|Outer radius mm|Six support solid volumes mm3|
|---|---:|---:|
|V34outer backbone|94.6495267853|16368.6625882|
|V36behind-pulley backbone|84.2533606026|13726.0170921|

Radius reduction10.3961661827mm /10.98385437%. This is a static envelope
improvement,NOT stiffness/mass/fatigue/holding improvement or an equal-material
physicalcomparison. Skin/Rail/Guide/Rootwheel/pin/drum recipes are unchanged.
802actual292partCADreview/BOM/sections:results/product_compact_review802.

803 repaired transform composition (outersector x innerpinframe) before
constructing exact union of axially extruded cylindrical pin components:
24full10mm pin sweeps,12actualPalm+integralbridge boregauges and18nominal
driver paths allclear;4.5048s. Existing18turnpins withdraw negative localaxis;
6Rootpins outwardpositive localaxis. Threads/headslot/supplierwrench/hands/
retainercapture/physical tolerances/strength are NOT qualified.

### Important earlier evidence correction

The nested-transform finding also invalidates791's4f1/f2Rootservice placements:
that auditor used only outermosttransform. Twof0records unaffected;raw791 kept
with COVERAGE_CORRECTION.json. Do NOT cite791as6/6actualservice qualification.
804 repaired the same auditor and rechecked originalV34:actual6pins/6drivers
allclear,3.7191s. Thus actual corrected result exists,but not by reclassifying
the earlier raw. Fullcompact803usescomposedtransforms independently.
805:52design/software testsPASS,2.4105s,including nested-rotation and unchanged
component guards. No physical Gate is promoted.

## Reproduction and next work

Source/raw hashes and executedproducers are in eachresults/product_*797–805
folder;800exception runtimeNULL,not invented. No installedSDK/binary modified.
NewCAD:meshes/b3_compact_bridge_v35 and b3_compact_root_v36.
All existing old FAILs,partial787and800,790coveragecorrection and794rejected
sectionlegend remain preserved.

Use NEW names,robot_wsPython,4GiB/480s perchild:

```bash
ulimit -v 4194304
timeout 480 /home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/palm_bridge_candidate.py --tag UNIQUE_BRIDGE --name UNIQUE_BRIDGE_CAD --topology tower --backbone behind-pulley
timeout 480 /home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/root_mount_candidate.py --tag UNIQUE_ROOT --name UNIQUE_ROOT_CAD --retention threaded-boss --canonical --bridge-candidate UNIQUE_BRIDGE_CAD
timeout 480 /home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/complete_drive_service.py --tag UNIQUE_SERVICE --candidate UNIQUE_ROOT_CAD
```

NEXT:real Root retention manufacturing/thread/head drive selection and measured
pullout/preload/anti-loosening,material-dependent frameforce–deflection,existing
wheel stack/tolerance/friction and wire minimum bend qualification. V36is a
smallerCADcandidate,not approved finaldesign. Contact/time/FEMmesh Gates and
100g/Lift/STEP remainopen. Native adoption must account for newmechanism mass/
inertia/joints/changedwirepath fromNEWinitialstate,not old B3checkpoint.
No session-exit automatic continuation.
