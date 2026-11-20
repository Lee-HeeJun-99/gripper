# Palm bridge and axle retention continuation761 onward

Received clean HEADa0080c0 on development/regrip-autonomous-research.
Followed AGENTS/CHECKPOINT/NEXT. No oldNativeSolver/time/mesh tests rerun;
noSDKchanges,remote push,purchase or manufactured measurements.

## Hypotheses and actual implementation

761direct bridge joins3forks/branch to twoPalm boltfeet. New headedpin/nut
proxies retain18axles geometrically;threads/material/preloadNOTqualified.
Actual67newpartSTLreadbacks,then18solid and6wireintersections;FAILgeometry.
Rootcauses include6mmbolt pitch causinghexnutoverlap,brace crossingPalm
andwire. 762tower alternative failed f0c0bridge singlebody readback:lower
forkbranch ends belowtowerstart15mm,disconnected. PartialSTLs andoriginal
failedproducer/summary preserved;not a completedassembly.

763changesbolt pitch to8mm(44/52,+/-30mm),tiesfeet andextends tower to actual
lowerforkconnection. Nut-pairconflictsremoved and67partscreated,but21solid
and750wire-envelope hits remain. Connectingtooutboardtower directly passes
through pulleyflanges andupperwire. This is not a material/solver problem.

764uses physicallydifferent brace topology:fromforkback localX=-5.5 to-10,
raise5mm,outboardY=+/-50,towerradialX78. Footbrace goes viaY50,notdiagonal
throughwire. Actual39.512s bounded worker4GiB/480s,pre-snapshot producer
hash/dependencies unchanged.67closedpositive singlebodyASCIISTLreadbacks.
Wirehits0;6nonempty Palm/bridge matingresults remain EXACT volume0.
Generic764status REFERENCE_GEOMETRY_INTERSECTIONS_REMAIN is preserved.

766independent STRICT sufficient-envelope test classifiesonlythatinterface:
eachuncut unionbit either minz>=13 orsector-localAABB radiallowerbound>64,
soit excludes originalPalm openinterior(z<13,r<=64). Borecuts onlysubtract.
All6bridges satisfy;noepsilon,physicaltolerancefloor orpriorFAILoverwrite.
This is finite-mesh mating evidence,not BRep/tolerance/strength/assemblyPASS.

765actual finiteassembly audits:
-12boregaugesR1.65 throughPalm/bridgeR1.7:0blocked.
-12nominaldriver-shankpathsR2.25,length25mm:0blocked.
-18headedpins at2/5/10mmwithdrawal afterownnutremoved:3blocked10mmsamples
  (c0secondturn,oneperfinger),~0.31117mm³braceoverlap. FAILsampledservice.
  Did not reduce required10mm orremovebrace/collision to make itpass.

767newcandidate changes ONLYsecondturn connector path after back/raise:
outboardY56 whilebelowwire,thenraiseanother7mm,thenreturntoY50tower.
It avoids pulling pin through thepreviousoutercrossbar withoutcrossingwire
plane.768retains original54service samples;769repeats strictmating proof
on changedcandidate. Read final summaries beforeclaiming these outcomes.

**Final767–769:**67newSTLreadbacks,wirehits0;6Palm-mating results volume0
remain in generic status,not hidden. Actualbuild41.386s/sourceidentityverified.
768retains all54pin samples including10mm:0blocked,12boregauges/12driverpaths
also0blocked.769all6strictsufficient matingexclusions proven;not BRepPASS.

## Stack, size and stiffness follow-on770–777

770found nominalwheel axialwander0.5mm vswire sidegap0.15mm:alignmentFAIL.
Two0.4mm thrustshims reduce nominalwander to0.1mm (margin0.05mm),but explicit
ASSUMED tolerancecase(span/wheel0.05,shim0.02mm) margin-0.02mm stillFAIL.
No claimed shopcapability/ISO fit,measuredtolerance/endplay or newphysicalPASS.
771created36finiteOD2.5/ID1.2/t0.4mmshims,allSTLreadbackclosedpositive;
wirehits0.16wheel-face CSGpositivevolumes~0.4–1.5e-6mm³ retained asunresolved
numeric/mating evidence,not rounded tozero orcalledassemblyclearancePASS.
280part fullrecipe:new67bridge/retentionparts +36shims +177parentreferences.
Axleremoval mustcaptureloose shims;physicalassemblysequence unverified.

772reviewimage labels incorrectly retainedold160partcaption due renderer
ignoring passedtitle/footer. Originalfigures retained withVISUALIZATION_REJECTION.
774rendererfixed,newfiguresvisuallyreviewed,280parts/proxies correctlylabelled.
Image repair isnot newphysics. Regression added toassertcustomlabels areused.
Fullradius94.64953mm vsbaseline67.89142mm;rootradius50unchanged. This is
a LARGE experimental supportframe,NOT final compactproductselection.
776single50mm/D4cantilever sensitivity underconditional2.121Nturnload:
assumedE250/2000/200000MPa givesidealEBdeflections28.13/3.517/0.03517mm.
TheseareNOT actualbranchedframeorselectedmaterialresults;large delta/Linvalidates
small-deflectioninterpretation. Frameforce-displacement/materialvalidation open.
777finaldesign/software regressions;not time/mesh/Holding qualification.

Nextpriority:compact supportarchitecture andfiniteRootinletredirect (current
idealpullpoint isnot actualpulley);thenframeforce-deflection/fastenerretention,
tolerance/friction andwearcoupon,actualNativecandidate withdefinedmass/joints.
Do not simplyreuseoldB3acceptedstates or6prescribedforces as newdriveapproval.

## Qualification boundary

New full neutralrecipe references177unchangedparentparts/wheels +67newparts.
New Palm has12actual bores;6integralbridges include18forks. PinD1,headD2.5,
nominal nutAF2.5;unthreadedproxies with0.1mmcombinedaxialplay,not supplierfit.
12M3-like bolt/nutsets,nominalgeometryonly,no thread/preload/boltstrength.
Toweroutboardstructure increasesoverallenvelope;NOT compact50mmradiusproduct
approval. Conditional2.121Nturnload from757 remainsidealized,materialunknown.
No actual Native candidate dynamics,mass/inertia/material certification,
Holding/Lift/mesh/time/STEP/fabrication-ready advancement in theseCADcycles.

## Reproduce only NEW candidates / outputs

Finalfunctionalcommitsad19a6e,101a17a;77745design/softwaretestsPASS.
evidence_product_palm_bridge_v40:10724files/19campaigns,10134priorimmutable
hashesverified0mismatches. Failed/partialcases and772image-labelrejection
explicitlyretained;archive membershipnevermeans allcasesPASS.

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY product_prototype/cad/palm_bridge_run.py --tag UNIQUE_BRIDGE --name UNIQUE_CAD --topology tower
ulimit -v 4194304
timeout 480 $PY product_prototype/cad/bridge_assembly_audit.py --tag UNIQUE_SERVICE --candidate UNIQUE_CAD
timeout 480 $PY product_prototype/cad/bridge_palm_contact_proof.py --tag UNIQUE_MATING --candidate UNIQUE_CAD
$PY product_prototype/cad/manufacturing_test_run.py --tag UNIQUE_REGRESSION
```

Bridgebuildworker snapshot/command/runtime/hashes:results/product_bridge_backroute764
andproduct_bridge_service767. Oldpartialfailure762 preserved,alloldRawunchanged.
Next independent tasks afterservice:actualtool/assemblysequence andtolerance
budget;rootinletredirect;material/fastenerjoinloads;compactness comparison.
