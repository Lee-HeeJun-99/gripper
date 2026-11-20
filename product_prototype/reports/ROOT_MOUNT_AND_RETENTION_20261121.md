# Root mount and retention continuation785–796

Baseline2bf6ab62a006b99d14161857d78a982bb12ae2dc,clean before work.
Existing Raw/Golden/SDK/B3 states and prior PASS/FAIL were not changed.
This milestone is CAD/reference validation,NOT a new SOFA run or Grasp PASS.

## Cycles and actual evidence

|Case|Implementation / measured result|Scope|
|---|---|---|
|785|6Root forks joined to existing bolted bridges,6outward headed pins and6nut proxies;18closedpositive STLreadbacks;298fullparts;43.3065s|Wire/newpart hits0;6Palm coplanar Boolean results ofvolume0 retained;REVIEW not assemblyPASS|
|786|Full10mm swept stepped pins clear6/6;inner R2/10mm nut-tool blocked6/6 by Finger Mount (~16.9374mm3 each);4.7056s|Loose-nut design serviceFAIL preserved|
|787|Integral threaded-boss alternative adds finite receiver material rather than disabling collision|Partial CAD FAIL atf2c0STLreadback:positiveclosedbody plus2zero-volume2-face components;no face deletion;runtimeNULL|
|788|Canonical first-sector symmetry representation,rotated120/240deg;12newclosedpositiveSTLs;292fullparts;50.3344s|Nominal configuration same;digital/tessellation identity NOT claimed. Wire/newpart hits0;6zero-volumePalm results retained|
|789/792|All additive leaf bounds belowPalm bottom,abovePalm top or outsideR64;6/6 sufficient mesh-envelope exclusions|No tolerance/epsilon/status override;not BRep clearance|
|790|First saved-state Root alignment screen|Radial coverage incomplete:usedR3 instead ofR3.25;correction retained,793supersedes|
|791|Boss candidate6fulloutward10mm pin sweeps and6nominalR1/10mm outward driver paths clear;3.7822s|No actualheadslot/thread/wrench/hand/preload/strength qualification|
|793|OLD485actual firstEyelet rigid motion,1200savedframes x6,finite centreoffset preserved;maxaxial bound0.2539359791mm<groovehalfwidth0.4mm|ProposedFIXEDRootwheel +piecewise tangent reference;not newcandidate dynamics/continuousCCD/wireelasticity|
|794|Actual292partCAD/BOM/section review|Section loop color/legend mismatch REJECTED;796corrected source;no figure silently overwritten|
|795|50design/software regression tests PASS;3.2792s|Not physicaltime/mesh/Holding qualification|
|796|Corrected fullCAD,planarsections andBOM generation|ReferenceCAD only;outerR94.6495268mm unchanged,oversizedsupport stillopen|

## Geometry and physical assumptions

New Root connection runs from actual fork back through sector-local
(58,+/-44,-8),(58,+/-44,15),(52,+/-44,15),usingR1.5rods,joining existing
12bolted feet. No additional large tower or changed Skin/Rail nominal shape.
Old inward pin-service failure782 remains;heads face outward as783established.

Boss candidate adds OD3mm receiver z[-4.4,-2.2] inoutwardpinframe,
throughboreD1.1mm;shaftproxyD1mm reachesz=-3.7. Nominal receiver/shaft overlap
is1.3mm,NOT verified thread engagement. Thread form,head drive feature,
material,preload,pullout/fatigue,anti-loosening and real manufacturing method
remain unselected/unmeasured. Existing wheelendplay and toleranceFAIL not fixed.
Do not claim the loose-nut issue has been physically solved by a CAD-only boss.

Root wheel is still a NEW physical mechanism relative to old fixed PullPoint.
Its reference path length change-0.4722757145mm is not a control calibration.
793usesOLD485actual rigid states to screen a proposed path,not to predict new
forces/motion. Tangential3Dkink can remain;no wire bending/friction model added.
No Binary compiled,SDK changed,SOFA executed or100g/Lift/Recovery result added.
Old Native contact/time0.1% and refinedmeshFAILs remain OPEN.

## Artifacts and reproduction

CAD:meshes/b3_root_mount_v32 (loosenut),b3_root_boss_v33(PARTIALFAIL),
b3_root_canonical_v34 (boss alternative,full_assembly_recipe.json292parts).
Raw:results/product_root_mount785,product_root_retention786,
product_root_boss787,product_root_canonical788,product_root_palm789,
product_root_motion790,product_root_boss_service791,product_root_boss_palm792,
product_root_motion793,product_root_review794,product_root_mount_regression795,
product_root_review796. Each case preserves executed producer and source hashes;
787haspartialfailure summary,not completedintersection/assemblyclaim.
CorrectCAD PNG/SVG andROOT_ASSEMBLY_BOM.csv:results/product_root_review796.

UseNEWpaths,4GiB/480s perchild (all actual runs below480s):

```bash
ulimit -v 4194304
timeout 480 /home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/root_mount_candidate.py --tag UNIQUE_ROOT --name UNIQUE_ROOT_CAD --retention threaded-boss --canonical
timeout 480 /home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/root_retention_audit.py --tag UNIQUE_SERVICE --candidate UNIQUE_ROOT_CAD --threaded-boss
```

## Next work (not background execution)

1. Compact the oversized outer support architecture based on actual load/service
   paths;retain Root outward tool/sweep checks and all existing finite collisions.
2. Select/measure a real pin/retention manufacturing concept,then update CAD
   thread/head/tool/tolerance models and strength/pullout qualification. Current
   generic threadedboss is a candidate,not an approved component.
3. Frame force–deflection,axial stack/retention and wire minimum bend/friction
   measurements are missing. Do not manufacture physical property values.
4. Native adoption needs finite hardware mass/inertia,joints andchangedtendon
   path/control verification from a NEW initialstate;do not reuseB3checkpoint.
5. STEP remains NOT GENERATED (noCADkernel in previously audited environment).
   Contact/time/mesh,50gqualification,100g/Lift andfabricationGates remainopen.
