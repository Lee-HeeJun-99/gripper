## Latest turn mount873–880 — 2026-11-22

Authority SUPPLIER_TURN_MOUNT_20261122.md. Source baseline6f4d423. Actual
connected3fork/axle branch873 FAIL4.10185mm3;component diagnostic874 identifies
third support cross-member.875 raises that member12mm:no positive solid hits,
zero-volume Palm contact retained. Full287parts,ONE branch only.878 all24pin/
12bore/18driver nominal geometry clear;877 finite .45wire obstacle screen clear;
880 other5LEGACY .5wire paths clear vs changed solids,NOTsupplier qualified.
879 actual CAD sections+287instance BOM. No new SOFA/STEP/physical qualification.
NEXT mass-normalized COM/inertia+material/retention interfaces,then remaining
channels. Full wire law/Root seat/translated Skin/time/mesh/100g/Lift remainopen.

## Supplier bend / real Root CAD cycles855–868 — 2026-11-21

Feature commits:a86f5b4,6b931d1,a4a8fbe. Authority:
SUPPLIER_BEND_AND_ROOT_REDESIGN_20261121.md. No new SOFA run this cycle;
existing B3 functional Holding and all time/contact/FEM mesh failures unchanged.

NEW primary-source supplier facts:0.45mm6x7/6x19 recommendations require groove
rootD18.9/11.25mm;V39 actual rootD3.5 is not pitchD4 or flangeOD6.855 candidate
compatibility FAIL,not a retrospective oldGate change. Facts/URLs/date in
config/wire_bend_supplier_v40.json;not measured fatigue or purchased items.

856 larger U-groove wheel at old centre FAIL Palm/bridge CSG.857 failed fork
STL retained.858 revised exact-CSG bore construction creates3valid STLs in
meshes/b3_supplier_root_module_v41;centre moves4.88572mm,pitchR5.85.859 module
hits first Eyelet/Support.860 shifts SAMEfinite guide+support2mm along existing
incoming branch,removing those two obstacles;old mount stillBLOCKED.
861 physically rebuilds connected Root mount from real bolted compact bridge,
not deleted collisions.862 adds finite seating cavity and UNSELECTED bondline:
meshes/b3_supplier_eyelet_seat_v43/full_assembly_recipe.json,293parts,ONLY f0c0
Root unit updated. Wire full-bore/support/bond CSG no hits. Tiny bond-interface
CSG overlaps retained;actual material/strength/retention/tolerance NULL.
865 actual mesh sections visually inspected;866 drawing/BOM review pack at
drawings/b3_supplier_eyelet_seat_v43. No FreeCAD/OCC/STEP/fabrication release.
867 exact24pin sweeps/12bores/18drivers nominally clear,4.71s. Fixed silent
new-pin-group skip;unknown groups now rejected and coverage verified.
86879software/design regressionsPASS,2.410s;NOT physical/product qualification.

NEXT priority:apply construction-specific bend/finite groove requirements to
remaining5Root+18turn units and firstguide Skin attachment BEFORE fullNative
adoption. Do not blindly mirror an unqualified joint or run invalid Holding.
Resolve finite seat/interface representation and retention/material measurements;
mechanical equalizer,continuous wire law,time/contact/FEMmesh/100g/Lift remainopen.
Repro source entries:cad/supplier_root_module.py,supplier_root_mount.py,
supplier_eyelet_seat.py,complete_drive_service.py;full commands in authorityreport.
For new wire data use a NEW config/candidate;never overwrite current Raw/config
or oldB3checkpoint. No automatically running children or post-session work.
Evidence:evidence_product_supplier_root_v46/manifest.json extendsv45 and includes
all14cases,failedpartialmeshes,catalogfacts and boundaryfragments,not14PASSclaims.

## Finite wire-section / metric-query cycles845–854 — 2026-11-21

Feature commits:253f9c1,15ef7b3. Authority:FINITE_WIRE_SECTION_CONTACT_20261121.md.
845/846 actual Native spherical wire-section proxies against actual finite Root
groove:60finite states each,15ms,8.87/8.77s. NOT complete wire/pulley/B3.
Actual response pairs are wheel Triangle / section Sphere;846 reversal only
changes initial tangential speed. Aggregate response/body impulse mismatch0;
linear momentum residual3.31e-24Ns. No SDK/customSolver/collision removal.

Analysis failure preserved:845/846 original SI-trimesh gaps and847 geometry
are INVALID (unit-sensitive face query). Append-only correction files retained.
848/849 scale geometry+points together to mm,output SI; independent dimensionless
triangle reference agrees<=2.34e-19m. Correct initial gap7.107980um; raw negative
minimum accepted gap~-3.79e-19m retained,not clearancePASS. Geometry conditioning
does NOT alter SOFA physics/tolerances. New metric_mesh_query.py is archived.

851/852:each519 detector sphere centres equal PREVIOUS accepted positions,
not current (difference up to1.007782um). First impulse record3.75ms is NOT
continuous event time. Accepted normal velocity~-2.182mm/s at first contact,
next step~0:position-level contract,NOT instantaneous e=0 impact qualification.
Discrete impulse/work identities only;physical impact loss/Root work/wire energy
NULL.853actual-state plot visually inspected;85470software testsPASS,3.416s.

Next:complete circular wire/connectivity/tangency Native model remains BLOCKED
pending a matched component contract;do NOT relabel spherical proxy as wire.
Actual friction/bendradius/material/retention/force-deflection data NOT MEASURED.
Use ROOT_AXLE_LOAD_MEASUREMENT_PROTOCOL.md for independent physical qualification.
Do not repeat old loop/dt/alarm/offset sweeps or845/846 unchanged. B3 time/contact/
FEMmesh/100g/Lift/STEP Gates unchanged. CAD remains V39,not fabrication-ready.
Evidence:evidence_product_wire_contact_v45/manifest.json. Old immutable data
audited;corrections only affect these newly created analyses,not historicalGates.
Repro new analysis:robot_wsPython product_prototype/sofa/root_wire_work_audit.py
--tag UNIQUE_WORK --cases product_root_wire_section845 product_root_wire_section846
(only for new analysis hypotheses;completed852 need not be repeated).
All Native children completed;no automatic work after session exit.

## Wire/axle continuation836–843 — 2026-11-21

Final regression844:66software/design testsPASS in2.526s;includesactual843
linear-momentum andplugin-order guards. Finalarchivev44extendsv43;v43audited
11363priorimmutablehasheswith0mismatches. Lastfunctionalcommit23c3a81.

Features468b853,e1db691,23c3a81. Authority:ROOT_WIRE_TRANSFER_20261121.md.
Completed NEW Native anchored-wire837/838/free-axle843,10finite states each;
initial J-lambda/angular or linear momentum match analytic impulse.836plugin
creation FAIL preserved. No repeat832/833.839independent circular-arc reference
FDerror5.94e-12,NOTSOFA.841sixCAD76deg root forces1.846984N atASSUMED1.5N/branch,
NOTactual load;blank physical CSV andROOT_AXLE_LOAD_MEASUREMENT_PROTOCOL.md.
84264design/software regressionsPASS,notproductGate.840originalnumeric producer
retained;integer-fixture cast bug fixed explicitly,not physical state correction.
NoCAD geometry changes/noSTEP/noqualifiedsliding/equalizer. NativeRigidMapping
anchors produce torque;balanced2prescribed forces are not physical equalization.
SlidingLagrangianConstraint installed API is point/straight-axis,notcirculararc.
NEXT:matchedNative circularwire/tangency/branch-change contract or keepBLOCKED;
physicalwire bend/friction,axleload-deflection/material/retention data required.
DoNOTreuseoldB3checkpoint or promotecomponentPASS toholding/time/meshPASS.
Repro:robot_wsPython product_prototype/sofa/root_wire_coupon.py --tag UNIQUE
--balanced --free-axle;load841producer:cad/root_load_requirements.py --tag UNIQUE.
Evidence:evidence_product_wire_transfer_v43/manifest.json. All priorRaw preserved.
Noactivephysicschildren/noautomaticexitcontinuation. Full3Finger/100g/Lift/
time0.1%/mesh/STEP/fabrication qualification remainopen.

## Root thrust / actual Native coupons806–835 — 2026-11-21

Finalevidence:evidence_product_thrust_native_v42/manifest.json,27cases/11363
files,11050priorimmutablehasheschecked0mismatches. Includesfailures/corrections
andSOFTWAREfixtures,not27PASSclaims. Lastfunctionalcommitsaff7e9b,f9a3f82.
Nextimplementationentry:sofa/root_bearing_coupon.py+run_native.py andinstalled
SoftRobots/component/constraint/model/CableModel.{h,inl}. DoNOTreruncompleted
832/833asnexttask. Read-onlySDKcontractcommandinROOT_THRUSTreport.

Functionalcommitsaff7e9b,f9a3f82. Authority:ROOT_THRUST_AND_NATIVE_VALIDATION_20261121.md.
V39CAD:meshes/b3_root_thrust_v39/full_assembly_recipe.json,292parts.
6Rootintegralthrustlands+6widergroovewheelscreated;old18turnwheel/shimFAILs
unchanged.806factorial:combinedASSUMEDtolerancealignmentmargin+0.061064mm,
notmeasuredprocessPASS.81324pinsweeps/12bores/18tools0blocked;Palmzero-volume
contactsandintendedwheelprobecontactsretained.820actualCADaxialsections.
ActualNative8attempts:810/811defaultfinite80each;815/816NaN43states/outer
timeoutFAILpreserved;818LineLineJnonfinitewithfinitefreeq/v,undefinednormal
hypothesis.817/819MinProximityfinite80each,~33.6/34.0s,NOTphysics/timePASS.
832idealNativecylindricalbearing80statesfinite;833spin10statesomega_z1exact.
834STRICTDOF/APIscopePASSonly;physicalfriction/clearance/Rootworkunmeasured.
83560design/softwaretestsPASS,notwholeproductGates.827streaminganalysisfix
after822/826failures:280920KiBmaxRSS;825launcherfixturesareNOTSOFAdata.
FutureNativeusesowned-childNaNguard/internal420s,beforeouter480s;noq/vrepair.
NEXTNativeidealwire/pulleyload-transfercontract andactualbearing/wirefriction,
clearance/material/retentionmeasurements;doNOTmapdiscretepointsontoawheel
andclaimverifiedwiresliding. Full3FingeradoptionfromNEWstateafterphysicsGates.
No100g/Lift/time/mesh/STEP/fabricationPASS;noactivechildren/autocontinuation.
Newcoupon:robot_wsPython product_prototype/sofa/root_bearing_coupon.py
--tag UNIQUE_BEARING [--spin-only];guard4GiB/420s. Fullcommands/Rawinreport.

## Compact drive797–805 — 2026-11-21

Featurecommitsa57d9db,31f37d5. Append-onlyarchive:
evidence_product_root_compact_v41/manifest.json,28cases/11050files,
10722priorimmutablehasheschecked0mismatches. IncludesFAIL/corrected/rejected
cases,not28PASSclaims. Noactiveanalysischildrenorautomaticexitcontinuation.

Authority:COMPACT_DRIVE_CONTINUATION_20261121.md. Featurebaselinea57d9db.
V36full292partCAD:meshes/b3_compact_root_v36/full_assembly_recipe.json.
Only6supportshape recipeschange;outerR94.6495->84.2534(-10.9839%),wire0.
6zero-volumePalmBooleancontacts retained,NOTassemblyPASS.803actualcomposed
transform24fullpinsweeps/12bores/18nominaldriverpathsallclear.800unsupported
nestedauditFAILpreserved.791earlier4serviceplacementsREJECTEDbycorrection;
804repairedV34actual6pins/6toolsallclear.80552softwaretestsPASS,notphysics.
ActualCADreview/BOM/sections:results/product_compact_review802.
NEXT:actualRootthread/head/retentionmanufacturingandpullout/preload/fatigue,
frameforce-deflection,existingwheelstacktolerances/friction/wireminimumradius.
NoSOFArun;contact/time/FEMmeshFAILs,100g/Lift/STEP/fabricationGatesremainopen.
Repro:cad/palm_bridge_candidate.py --tag UNIQUE --name UNIQUE_BRIDGE
--topology tower --backbone behind-pulley;thenroot_mount_candidate.py
--tag UNIQUE_ROOT --name UNIQUE_CAD --retention threaded-boss --canonical
--bridge-candidate UNIQUE_BRIDGE (robot_wsPython,4GiB/480s).

## Root mount/retention785–796 — 2026-11-21

Authority:ROOT_MOUNT_AND_RETENTION_20261121.md. Baseline2bf6ab6.
785finitePalm-connectedRootforks/pins/nuts created.786innernuttoolFAIL6/6
vsFingerMount,whileoutwardpinsweepsclear.787bossSTLpartialFAILpreserved;
788canonical-sectorbossalternative12closedpositiveSTLs/292fullparts.
791outward6fullpinsweeps+6nominaldriverpaths0blocked. Noactualthread/strength
qualification.785/788wirehits0,6Palmzero-volumeBooleanresultsretained;
789/792strictleafbounds6/6excludeopenPalminterior,notBReporassemblyPASS.
793OLD4851200framesx6alignmentboundmax0.253936<0.4mm;notnewSOFAdynamics.
790radialcoveragecorrectionpreserved.794sectionlegendcolorrejected;
796correctCAD/BOM/sectionpack.79550softwaretestsPASS,notphysicalGates.
NEXT:compactouterframe(R94.6495stilloversized),actualRootretention/thread
manufacturingandstrength/tolerancequalification,thenNativeadoptionfromNEWstate.
NoSDK/oldRawedits,no100g/Lift/time/mesh/STEP/fabricationPASS.
Candidate:meshes/b3_root_canonical_v34/full_assembly_recipe.json.
Newbuild:cad/root_mount_candidate.py --tag UNIQUE --name UNIQUE_CAD
--retention threaded-boss --canonical (robot_wsPython,4GiB,timeout480).

## Root redirect continuation778–781 — 2026-11-21

Follow-up782–784:inward10mmpinextractioncollideswithFingerMount6/6,preservedFAIL.
Outwarddirection c0:+axis/c1:-axis:6convexsweptpinvolumes overfull10mmtranslation
clearagainst298parts(783). Not retained/mountedassemblyPASS.78448softwaretests.
NextRoot mount/retention must preserveOUTWARDservice,notbidirectionalaccess.
Featureecce74f;laterlocalcommitcontainsserviceauditandcheckpoint.

Authority:ROOT_REDIRECT_CONTINUATION_20261121.md. Six finite Root wheels then
six forks/pin proxies created:meshes/b3_root_fork_v31/assembly_recipe.json.
Actual280-parent/new-module solid screen0intersections; rootwire intendedwheel
contacts516 retained, NOT promoted toclearancePASS. Rootturn76deg and reference
pathchange-0.4722757145mm:oldNativepullpoint isNOT equivalent.78147software
regressionsPASS;noSOFArun/newphysicalPASS. NEXT:finitePalm-to-root-fork mount
andretention,thencompact supportarchitecture/service/strength/tolerance checks.
Raw:results/product_root_redirect778,product_root_reference779,
product_root_fork780,product_root_regression781. Existingfailuresunchanged.
Reproduce NEW candidate with cad/root_redirect_candidate.py --tag UNIQUE
--name UNIQUE_CAD --fork (Pythonrobot_ws;ulimit4GiB;timeout480).

## Palm bridge/retention continuation761–777 — 2026-11-20

Final functional commitsad19a6e,101a17a.777:45design/software regressionsPASS.
Append-onlyevidence:evidence_product_palm_bridge_v40/manifest.json,
19cases/10724files,10134priorimmutablehasheschecked0mismatches. Archiveincludes
FAILED761/762/763/765cases and772visualizationrejection,not19PASSclaims.
CorrectCADfigures/BOM:results/product_bridge_review774/ (committed).
NewestfullCAD:meshes/b3_thrust_shims_v29/full_assembly_recipe.json,280instances.
No intentionally runninganalysis orsession-exitautomaticresearchcontinuation.

Authority:PALM_BRIDGE_AND_AXLE_CONTINUATION_20261120.md. Firstfeaturead19a6e.
761directFAIL18solid/6wirehits;762disconnectedtowerSTLFAILpartialpreserved;
763connectedbutwheel/wirehitsFAIL.764backroutewire0,but3pin10mmsamplesblocked.
767secondturnservice-loop candidate:67closedpositiveSTLs,wire0,6zero-volume
Palm-mating results retained.768same12holes/12drivers/54pinsamples(2/5/10mm)
0blocked.769strictmating envelope proof6/6. Genericintersectionstatusnotchanged.
77136thrustshims reduce NOMINALendplay;770ASSUMED tolerancecase stillFAIL;
16tinypositive wheel/shim CSGseams remainUNRESOLVED,notclearancePASS.
774actualCADreview/BOM:280parts/proxies,outerR94.6495 vs67.8914baseline:
oversizedexperimentalframe,NOT finalproduct.772wrongcaptionimagesrejected,
774correctedandreviewed.776idealizedstiffness sensitivity NOTframeFE/strength.
NEXT:compact supportarchitecture +finiteRootinletredirect,thenframeforce-
deflection/boltretention/tolerance/frictionqualification andNativeadoption.
Material/motorduty/hornfit/wireminbend physicaldata stillmissing;STEPabsent.
OldNativecontact/time/FEMmeshFAILsand100g/Lift remainunchanged. No newSOFA
physics run intheseCADcycles;no completedproduct or backgroundcontinuation.
Read-onlyresume:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/product_bridge_service768/summary.json`
Newcandidate buildonlyafterimplementation:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/palm_bridge_run.py --tag UNIQUE --name UNIQUE_DESIGN --topology tower`

## Deformed wire / drivetrain continuation744–758 — 2026-11-20

Final functional commits3ad4792,af9effb,1c97d82.760:39design/software testsPASS.
Evidence:evidence_product_deformed_wire_v39/manifest.json:19campaigns,
10136files,9811priorimmutablehasheschecked,0mismatches.745isexplicitlyREJECTED
inmanifest as sourceidentityfailure,not19PASSclaims. Snapshot747repair retained.
Figures:results/product_wire_plot750/accepted_state_wire_screen.png and
results/product_pulley_drawing756/pulley_module_views.{svg,png} (committed).
NEXT implementation entry:cad/pulley_fork_candidate.py fork_recipe andcurrent
worldmoduleframes;add actual Palm-to-fork mounting/axleretention asNEWcandidate,
not by relocating or disabling existing obstacles. Nominal conditionalturnload
2.121N at1.5Nwire/90deg,physicalstrength stillUNKNOWN. Rootinletredirect open.
Read-only resume:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/product_pulley_fork754/summary.json`

759supplement:all54finite modules /1431pairs andSTLreadbacks checked,
0nonempty intersections;combined MODULE_BOM.csv retained. 760finalregression.
Feature commits3ad4792,af9effb;finalarchivecommit recorded in gitlog.

Authority:DEFORMED_WIRE_AND_DRIVE_CONTINUATION_20261120.md.
First functional commit3ad479279bee648fc98cb1a895537539b1942f57;later modules
and evidence commits follow. All old Native/SDK/Raw/Gates unchanged.
747frozen-source repair:745producer identity rejected,preserved with annotation.
7461200savedframes/6wires:minimumspheregaplowerbound3.858159mm;hardwareNOTtested.
75322worst/eventframes/132wires:0wire and0interfinger finitehardware intersections;
actual147s,bounded4GiB/480s. NOT continuousCCD or newcandidate SOFA dynamics.
748directmotorleadFAIL18obstaclehits;perimeterroute0,drumcontact retained.
75118finitepulleys +75418forks/18pins created andactualSTL readbackchecked.
754parent/module andwire-envelope intersections0. StillUNMOUNTED:bridge toPalm,
root redirect,axle retention,bearings,tolerances/materialstrength missing.
757conditional1.5N/90degload2.121N;idealstress10.61MPafork/15.13MPapin,
NOT measured strengthPASS. No motor/material approved;STEP absent.
NEXT executable independent task:actual Palm-to-fork mounting/retention CAD,
then finite-route/tool-access review;do not repeat cleared staticwire tests.
Current models:meshes/b3_lead_pulley_modules_v22,b3_pulley_fork_modules_v23.
Bounded replay command (NEWtag):
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/deformed_wire_run.py --tag UNIQUE_EVENT --candidate b3_manufacturing_bore_v21 --include-film --all-event-worst --hardware-pairs`
Old contact0.1%/FEMmesh FAILs;100g/Lift/fullRecovery/STEPstillunqualified.
No intentionally running simulation orautomatic session-exit continuation.

## Wire/Eyelet continuation728–741 — 2026-11-20

Last functional implementation commit529a5c0 (prior32a4825,9d0829b).
Final regression743:30design/software testsPASS,not physical Gates.
Append-only evidence: evidence_product_wire_v37 then evidence_product_wire_v38.
Exact replay command (NEW tag required):
`ulimit -v 4194304; timeout 480 /home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/wire_bore_replay.py --tag UNIQUE_REPLAY --candidate b3_manufacturing_bore_v21`
No active simulation is intentionally left running;no automatic continuation.

Latest further cycle742–743:wire_bore_replay.py mapsNEWCADEyelet centre/axis
through actual485Rigid3 accepted transforms.36sites0failedsavedframes and
0holdfailures;maxrequiredradius0.66934932158mm<0.7. Correct body-to-Eyelet
offset included. This isFROZENMOTIONnecessary-condition screening,NOT newNative
dynamics. Next deform rounded path andscreenfiniteSupport/object/otherhardware
atworstframes,then complete motor lead-in. Code also rejects moving fixtures
without actualpullpointpath. See authority report for all commands andboundary.

Feature commit32a48259996b7efee7746ad94373a3ea76da3ab3; later rounded-path
code/evidence commit follows. Authority:WIRE_EYELET_CONTINUATION_20261120.md.
V20axis-only FAIL6bore sites. V21axis+ID1.4/OD3/L2,wire0.5:36straight
segments vs160parts no intersections. Separate2mm-radius circular-filleted
reference route:740circumscribed tight envelopes no hits;739coarse-box12hits
preserved. Supplier minradius/material/friction unknown,NOT moving-wire PASS.
73212service samplesclear;733six assembledclamp driver paths stillblocked.
734160ASCIISTLs closed/positive;STEP absent;24tiny assembly seam intersections
UNRESOLVED.74129design testsPASS;Native/time/mesh/Holding Gates unchanged.
737motor/material selectionBLOCKED by8missing physical/interface measurements.
Next:deformed B3 accepted-state replay with finite changed Eyelet frames and
wire path,then motor lead-in/horn interface from actual drawings. Do not rerun
known failed Native loop/dt sweeps. No newSOFA or fabrication-ready claim.
Raw:results/product_wire_round740;CAD:meshes/b3_manufacturing_bore_v21_stl_ascii.
Reproduce unique output:
`ulimit -v 4194304; timeout 480 /home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/rounded_wire_path.py --tag UNIQUE_ROUND --candidate b3_manufacturing_bore_v21 --radius-mm 2 --tight-envelope`

## Parallel Track A/B/C continuation704–727 — 2026-11-20

Last implementation commits:901b1cd0d05e283ac96319aef699cbfabb13c09b,
62610d609a34332dc837d6f0c18269bfea5716a5.
Authority:REGRIP_PRODUCT_DESIGN.md,REGRIP_ASSEMBLY_SPEC.md latest sections.
Evidence:evidence_product_manufacturing_v36/manifest.json (8977files,24new cases;
7262prior immutable hashes verified0mismatches). All old Raw/B3/SDK unchanged.

A:713 installed MultiStep actual2Native coupons:free external Newmark discrete
reference<=1e-15 PASS;Cable remains0 FAIL. No qualified constrained-loop contract
found in this tested family;STOP numerical sweeps and continue PRODUCT work.

B:8CAD revisions V12–V19,112then160solids/proxies generated by actualManifold CSG.
Support/Rail andMount/support conflicts,missingholes,fastenercrossings,head seats,
andcartridge removal tracks were implemented and independently checked.
721 twelvewithdrawal samplesclear;NOT continuous service/actuation clearance.
SixClamp driver paths remainblocked whileassembled:bench service sequence needed.
724STL reload FAIL and725partialcleanup FAIL retained.726canonical-module ASCII
STLs:160closedpositive single-body readbacks. Nominal configuration unchanged,
digital/tessellation representation CHANGED;NOT FEMmesh or BRep qualification.
STLs:product_prototype/meshes/b3_manufacturing_service_v19_stl_ascii/.
Assembly recipe,BOM,DXF,SVG,PNG:drawings/b3_manufacturing_service_v19/.
STEP NOT GENERATED (checked FreeCAD/OCC/Python/PATH unavailable).

707 actual344guide paths reanalyzed:peak geometricstroke2.62754–2.90653mm;
internal/geometric mismatch<=.100733mm. NOT hardware measured requiredstroke.
36conditionaldrive scenarios;1.5N/2wire/R8 ->.060–.096Nm atassumedeta.8/.5,SF2.
Motor/wire/material candidates have manufacturer links;cost/stock/continuous
torque/wire stiffness/physical density stayNULL. No purchased component or
mechanical equalizer is approved.3motor/2groove layout is a DIFFERENT control input.

C:718 tenphysicaltest protocols,40NULL fields;hardware tests0.716draft unit-schema
defect retained/corrected.72726DESIGN regressions PASS,not product Gates.
No newHolding/100g/Lift/Recovery/time/mesh/variable-stiffness certification.

NEXT PRODUCT priority:723finitebore audit FAIL12sites at existingaxis/ID1.2/L2.
UNBUILTbisector hypothesis reduces requirement,but6sites stillfail;maxrequired
bore radius.642363mm. Implement separate axis-only andbore/support candidates
in manufacturing_assembly.recipe eyelet basis,NOT randomoffset/stroke sweeps.
Keep real OD/wire andverify Support occlusion,rounded bend radius,assembly/strength.
Native adoption remains separate andblocked by original time/mesh/material Gates.
Read-only resume:
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/product_wire_bore723/summary.json
After a NEW candidate implementation:
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/manufacturing_run.py --tag UNIQUE_CAD --name UNIQUE_DESIGN --config ACTUAL_NEW_CONFIG
Regression after code change:
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/manufacturing_test_run.py --tag UNIQUE_REGRESSION
No automatic background continuation or fabrication-ready claim.

## Native loop / elastic-wire continuation692–703 — 2026-11-20

Feature commit: `6b8d0b64a03e8598a2ece62ce0bf04b83a7c68f0`.
Authority:product_prototype/reports/NATIVE_LOOP_INTERVENTION_AND_ELASTIC_TENDON_20261120.md.
692 loop-only intervention:Default external-force Euler/Newmark STRICT1e-12 PASS;
Default Cable stationary FAIL;deprecated ConstraintAnimationLoop graph segfault.
693–696 Native elastic-wire candidate:old-tangent and nonlinearBE discrete
references PASS,but BOTH full-common-time/all-pair0.1% Gates FAIL. Different
physical model from prescribed-tension Cable;wire properties NOT measured.
697/698 actual Native slack potential/force API inconsistency independently found.
699 potential-only Native subclass:unchanged force/tangent/q/v;potential error
<=8.68e-19J,slack FD gradient0.702 Native Newton journals EXACTLY unchanged.
This scoped API correction does NOT fix time/contact/B3/Holding qualification.
703 fifteen regression checks PASS.27actual Native attempts,one segfault preserved.
Evidence:evidence_product_elastic_tendon_v35 (7264files;6812prior hashes unchanged).
NEXT:new validated Native constrained-loop contract or independently calibrated
elastic-wire physical model;stop blind repeats/promotion under current limits.
Original B3,SDK,Raw/checkpoints preserved;100g/Lift/STEP remain unqualified.
Read-only resume:python -m json.tool product_prototype/results/b3_native_spring_potential_adapter699/summary.json
Regression after specific change:python product_prototype/sofa/contact_policy_test_run.py --tag UNIQUE_REGRESSION

Reusable potential-only build:product_prototype/cad/build_b3_native_spring_potential_adapter699.
Binary SHA81f92e4c50cfa36fe13c2d48260ff8ad54cdaacb6e31d718522a393d583c3963.
Reusable read-only energy build:product_prototype/cad/build_b3_native_spring_energy697.
No new B3 model/CAD/mesh or resumed checkpoint. No product-complete/background claim.
Physical wire stiffness,guide/join density and constrained-loop compatibility
are distinct prerequisites;neither this module nor static CAD supplies them.

## Verified local code checkpoint — 2026-11-20

Last feature commit: `35bee4217b8d0c0dc26b1f945175995f490b8fba`.
Campaigns663–691 preserve 67 actual Native child attempts, including19 with
SOFA errors;691 has nine passing regression checks, NOT nine physical Gates.
Evidence: `evidence_product_native_ode_limits_v34/manifest.json` (6814files;
5831 prior immutable hashes checked without mismatch). No running runSofa child
at handoff. Product qualification remains incomplete. Resume by reading the
authority below; repeat known failed Native loop configurations only after a
specific integration-contract change, not as a new experiment.

## Native compliance/loop limits663–691 — 2026-11-20

Authority:product_prototype/reports/NATIVE_COMPLIANCE_AND_LOOP_20261120.md.
Last prior featurefacd9e2;exact producer/compiled source snapshots authoritative.
Native penalty reference and observer purity implemented;all-common time FAIL.
Native contact metadata resets after evaluation:NOT a force callback journal.
673 frozen-state agreement is rejected by678;partial675/676 rejected by677.
682/684 Native BDF1 discrete equations PASS;tested BDF2 reference mismatch remains.
683 Newmark improves elastic surrogate error,NOT full0.1% Gate.685 actual1N Cable
multiplier correct but Newmark state FAIL;ConstantForceField control also FAIL.
686 factor-only adapter is OPT-IN and REJECTED after687 full-reference FAIL.
688 actual binary loop path forms freePos=pos+dt*freeVel;do NOT patch SDK or states.
690 build-reuse/vdamping cleanup reproduces exact states;691 nine regressions PASS.
Evidence:evidence_product_native_ode_limits_v34. All old Raw/SDK/B3 preserved.
BOUNDARY:stop this candidate family,not a claim of OS resource exhaustion.
NEXT meaningful change needs independently verified Native loop integration
contract/matching source;no blind dt/alarm/parameter repeats or B3 promotion.
Hardware material/join calibration,original mesh/time/interference,100g/Lift/STEP
remain BLOCKED. No final product PASS or automatic background continuation.
Read-only restart:python -m json.tool product_prototype/results/b3_native_plane_ode_reference684/summary.json
Regression after change:python product_prototype/sofa/contact_policy_test_run.py --tag UNIQUE_REGRESSION

## Native contact policy660–662 — 2026-11-20

Last feature:d697a67 conditional union geometry;3a5844b actual inertial matrix fix.
660 actual8active finite contacts start at positive buffered gap;normal target-gap/dt.
661 six actual Native1D sphere/plane runs isolate this WITHOUT FEM,cable or gyro.
Position error≤6.51e-19m/momentum≤5.43e-20Ns,but post-impact velocity error
0.6/.2/.4m/s.662 exact Decimal gap/dt recurrence strict1e-12 PASS;physical
all-common-time0.1%Gate FAIL. Velocity-first option does NOT fix this policy.
Authority:NATIVE_CONTACT_POLICY_20261120.md;evidence_product_contact_policy_v33.
NEXT:independent Native compliant-contact/analytic-reference comparison;different
physical law,not a repair of old hard-contact FAIL. No B3/100g/Lift/STEP promotion.
Reproduce:python product_prototype/sofa/native_plane_policy.py --tag UNIQUE_PLANE

## Conditional finite union658–659 — 2026-11-20

Previous functional commit3a5844b:actual Native missing-B assembly corrected;
FREE100ms selected0.1% Gate PASS,CONTACT652 still FAIL. No B3 approval.
Independent geometric union implemented and four analytic/objectivity tests PASS.
Eyelet/support overlap2.35284–2.36475mm³;naive mass sum can overcount3.32594%
under SAME uniform material assumption,COM bias≤0.332202mm. Physical density/joint
unknown:actual union mass/inertia BLOCKED. No replacement of B3/checkpoints.
32/64facet geometric sensitivity≤0.080251%;NOT FEM/contact mesh qualification.
Authority:product_prototype/reports/FINITE_UNION_GEOMETRY_20261120.md.
Evidence:evidence_product_union_geometry_v32/manifest.json. STEP NOT GENERATED.
NEXT:contact-entry policy/feature diagnostics from649–651 (current impulse law
still-gap/dt),not more blind dt/alarm sweeps. Material/join/STEP remain separate.
Exact independent reproduction:python product_prototype/sofa/finite_union_run.py --tag UNIQUE_UNION

## Actual Native matrix635–657 — 2026-11-20

Authority:product_prototype/reports/NATIVE_INERTIA_FORCE_TANGENT_20261120.md.
Previous feature5b8bf1 preserved. Missing B found despite callback counts635–639;
new640 installed matrix APIs fix actual assembly,not physics parameters.
644 actual operator isolated tangent relative error2.05e-12;observer purity0.
648 FREE100ms all-common/all3pairs worst0.0753113% PASS selected0.1% Gate.
654 actual world-transform Native strict1e-12 PASS.653 NOT RUN runner error retained.
652 CONTACT time FAIL (surface19.4683%,omega81.4033%,force100%).656 actual
A impulse correction agrees≤2.85e-14;normal target still-gap/dt.657 ten tests PASS.
Evidence:evidence_product_matrix_api_v31/manifest.json;all old immutable Raw retained.
Build:product_prototype/cad/build_b3_inertia_matrix_api_build640 (scoped force),
build_b3_inertia_matrix_api642 (read-only matrix).No SDK/old B3/checkpoint changes.
NEXT:independent eyelet/support overlap-corrected GEOMETRIC union moments;
material/joint mass remains unknown. Contact event/mesh/B3/100g/Lift/STEP unqualified.
Read-only resume:python product_prototype/sofa/inertia_force_contact_audit.py --tag UNIQUE --case b3_inertia_contact_operator655 --reference b3_inertia_matrix_contact649

## Native inertial force/tangent623–634 — 2026-11-20

Authority:NATIVE_INERTIA_FORCE_TANGENT_20261120.md.
Evidence:evidence_product_force_tangent_v30/manifest.json;4628prior immutable hashes unchanged.
-623 scoped gyroscopic ForceField,NOT ODE/contact solver. Actual world-rotation K
 and velocity B derivatives. Native mapped mass retained;no q/v writes or SDK edit.
-624 FAIL preserved:old SparseLUSolver factory moved to optional CSparseSolvers.
 625 uses installed EigenSparseLU (nonsymmetric),NOT symmetric LDL.
-Actual C++ FD relative error:K≤6.65e-11,B≤3.31e-10;K/B assembly calls each40.
-625/626 backward Euler100ms still FAIL0.132861% angular invariant.
-627–632 Native trapezoidal with actual K/B:angular invariant base/half/quarter
 0.0112466%,0.00555120%,0.00276304%. All-common-time/all3pairs worst0.0748267%,
 selected FREE-ring0.1% Gate PASS. First-order observed trend;not generic2nd-order proof.
-633/634 principal-axis reference omega error≤9.01e-14rad/s;strict basis1e-12 PASS.
 No contact/B3/global energy/100g/Lift qualification. Physical hardware mass still assumed.
NEXT:read-only ACTUAL assembled matrix audit (K/B calls alone do not prove matrix),
 world-objectivity,then finite contact using same force law/Native solver.
Reusable build:cad/build_b3_inertia_force_build623,source/binary guarded.
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_inertia_force_trap_time632/summary.json`
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/inertia_force_run.py --tag UNIQUE_FORCE --trapezoidal`

## Inertia/contact continuation600–622 — 2026-11-20

Last functional commit:36f6831 (complete contact ownership/energy/validity-limit
audit);input feature commit844afa1. Working branch development/regrip-autonomous-research.
31 new archived campaigns592–622;22 actual Native children completed,all under
4GiB/480s guard. Actual max Native runtime1.13850s;RSS NOT MEASURED.
Current sampled-input/trapezoidal branches are stopped at reproducible validity
limits;no host resource exhaustion claimed. A true inertial-force tangent is a
separate unimplemented candidate,not silently approximated or declared PASS.

Functional input commit:844afa1. Authority:NATIVE_SAMPLED_INERTIA_20261120.md.
Evidence:evidence_product_long_inertia_v29/manifest.json → contact_inventory_v28 → inertia_v27.
Latest4630files;prior4393immutable paths checked0mismatches. Old Raw/verdicts unchanged.

-600–602 real finite-ring contact with SAME592 input binary passes basis1e-12,
 but604 all-common-time0.1% CONTACT Gate FAIL:surface displacement19.3158%,
 COM6.48978%,angular velocity81.3824%,rotational energy94.5976%,force100%.
-609 actual sampled torque law error≤1.37e-22Nm;M*dv-inertiaImpulse-contactImpulse
 residual≤7.64e-22Ns /9.72e-24Nms;free predictor≤9.60e-14.
 Active Native normal target remains-gap/dt(residual≤3.21e-8m/s).
-606 actual saved mapped finite surfaces show0strict edge/facet crossings and0
 uncertain tests. NOT containment/swept/full hardware clearance or time certification.
-607 analysis omitted contacts after each response group's first block.608/609
 expand ALL actual3-row contacts with ownership/coverage checks;old607 preserved.
 Signed inventory residual≤1.18e-21J,row work≤1.70e-21J. NOT heat/global energy PASS.
-610 cumulative energy/time Gate FAIL,including tiny signed residual192.377%
 (absolute1.63e-21J);NO error floor or residual exclusion.
-611 floating-point test bound failed because cross-product cancellation was
 scaled by output torque instead of operands.612 derives correct operand-based
 bound;6227regressions PASS. No physical tolerance changed.
-613–617100ms free extension:base angular invariant0.133470%,base-quarter
 all-time worst0.100100244%,STRICT FAIL at unchanged0.1%. Do not round to PASS.
-618/619 installed Native trapezoidal option gives EXACT same q/v/impulse as613;
 verified in622. B=K=0 held-input formula is unchanged;stop this branch,not dt sweep.
-620/621 OLD552/550 Raw reanalysis with FULL contact ownership:additional points
 remain on actual mesh≤1.56e-17m;active body-point counts7eyelet/3support,not old6/2.
 Old analysis files retained;counts are NOT area. Native state unchanged.

NEXT:
1.Native retained solver + actual velocity/rotation-dependent inertial-force
 tangent candidate (SparseLU available;do not send nonsymmetric Jacobian to LDL)
 only if independently force/Jacobian/FD/objectivity validated. Current sampled
 ConstantForceField hasZERO within-step Jacobian and is NOT production qualified.
2.Separately validate stock contact's discrete event/stabilization policy using
609 actual rows. Do not assume gyro fix,time smoothing or larger alarm repairs impact.
3.No B3 mass/checkpoint replacement,100g/Lift claim,or fabricated density/union.
Physical material/join/STEP and all original B3 failed time/mesh Gates persist.

Read-only restart:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_inertia_input_100ms_time617/summary.json`
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_inertia_contact_allcontacts609/summary.json`
Reusable build:cad/build_b3_inertia_input_build592 (unchanged);physical332/direct512.
Code regression:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m unittest discover -s product_prototype/sofa -p test_native_inertia.py -v`
No active physics child,no background continuation. Current sampled-input and
trapezoidal directions stop at measured validity limits,NOT OS/resource exhaustion.

## Sampled inertia candidate592–599 — 2026-11-20

Authority:product_prototype/reports/NATIVE_SAMPLED_INERTIA_20261120.md.
Evidence:evidence_product_inertia_v27/manifest.json;3931 prior immutable files unchanged.
Installed SDK unchanged;original B3 and all earlier PASS/FAIL preserved.

-592 scoped input module builds. Native EulerImplicit/ConstantForceField/mapped
 mass retained. Adds ONLY sampled torque=-omega cross(Iworld*omega),not an ODE or
 contact solver. No q/v reset,no implicit gyro Jacobian or B3 adoption.
-593/595/596 real Native10ms off-axis runs:angular invariant error0.0154663%,
 0.00773297%,0.00386646%;baseline0.660162%581 preserved.
-594/597 actual omega vs analytical reference error0.00286461,0.00143227,
 0.000716132rad/s;first-order sampled-input trend,not a universal integration PASS.
-598 principal control state difference≤7.11e-15,strict1e-12 PASS.
-599 all common outputs/all3pairs selected FREE-ring state,shape,L and kinetic
 energy comparison max0.0622731%,below unchanged0.1% Gate. No denominator floor.
 Input zero-power roundoff kept separately;NOT global energy/contact/FEM certification.
-Next finite contact600–602 runs and ALL-output checks;free-spin success does not
 qualify impact,friction,time/mesh,Holding,Lift or fabricated hardware mass.

Reusable build:cad/build_b3_inertia_input_build592;binary/source guards in run tool.
Reproduction(new UNIQUE tags):
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/inertia_input_run.py --tag UNIQUE_GYRO --case b3_finite_com_mapped571`
No old B3 checkpoint reused. Density/join/union still NULL.

## Native composite-acceleration continuation588–591 — 2026-11-19

Last functional commit:7c83f9e (read-only public API probe);preceding feature
commits:e85534a (COM/contact),f3869ba (exact/free-spin controls).
Current direction stopped at a reproducible model-capability failure,not because
one test or commit completed. Product is NOT complete. Next inertial capability
work must satisfy off-axis and principal controls before higher-level trials.

Feature commits:e85534a,f3869ba;26 archived campaigns565–591 (587 is preliminary build only).
Authority:product_prototype/reports/FINITE_COM_NATIVE_VALIDATION_20261119.md.
Latest evidence:evidence_product_mapping_v26/manifest.json → v25 → v24.
3933 recorded files;3785 prior immutable paths verified0mismatches.

-588 compile FAIL (missing MechanicalParams include) preserved;589 fixed read-only
 observer compiled against INSTALLED SDK only. No SDK/FEM/contact/ODE changes.
 Binary:cad/build_b3_mapping_build589/libReGripMappingAcceleration.so.
-590 observer scene FAIL:RequiredPlugin was placed after child creation.
 591 fixes XML plugin order ONLY;both Native children complete with0SOFA errors.
-Public composite acceleration API called on temporary output at real q/v:
 returned0;expected omega×(omega×r) max0.403523685m/s²,96actual point records.
 Observer q/v/mapped mass points/contact impulse difference EXACT0 vs572.
 Thus current mapped-mass composition lacks this composite acceleration response;
 not a proof that every Native rigid solver is unsupported.
-18 successful short Native children +2 observer-init failures this continuation;
 no full B3 Holding rerun. Independent geometry/Jacobian/reference Gates advance,
 but physical rigid inertia/free-spin/time/mesh and product adoption remain BLOCKED.
-No new50g,100g,Lift/STEP approval. Old B3 functional results/failures unchanged.
 Physical material density and eyelet/support union/join still NOT MEASURED.

NEXT:do not repeat free dt refinements or adopt world-frozen tensor. Verify a stock
Native composition that supplies composite acceleration/gyroscopic response using
581(off-axis negative) and584(principal positive) references. If unavailable,
a narrowly scoped inertial correction requires its own force/Jacobian/reference
validation;do NOT rebuild an ODE/contact solver or silently resume B3 checkpoint.
Only then redo moving finite contact clearance and qualified physical convergence.

Exact read-only resume:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_mapping_acceleration591/summary.json`
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_finite_spin_exact581/summary.json`
Reusable compiled probe589 plus unchanged physical332/direct512;source/binary guards
in observer_identity.py. Probe replay,ONLY with a new hypothesis/unique tag:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/mapping_acceleration_run.py --tag UNIQUE_MAPPING_API`
Regression:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m unittest discover -s product_prototype/sofa -p test_finite_mass.py -v`
No active physics child;no background continuation promised.
This is an adoption/model-capability block,NOT OS memory or480s exhaustion.

## Free-spin continuation581–586 — 2026-11-19

Feature commit:e85534a (COM/Native contact565–580);this continuation separately committed.
Authority:product_prototype/reports/FINITE_COM_NATIVE_VALIDATION_20261119.md.
Evidence:evidence_product_spin_v25/manifest.json → com_v24;3672 prior immutable files unchanged.

-581 exact axisymmetric torque-free reference:angular invariant relative defect
 ≤2.03e-16,energy≤7.34e-16,Euler-equation FD residual≤9.74e-9rad/s².
 Actual Native off-axis omega error0.122997rad/s and angular error0.660162%
 at10ms persist at all3dt. No interpolation/error floor/new physical solver.
-582 Native principal-axis spin changes ONLY initial angular-velocity direction,
 same magnitude and COM translation.583/584 actual angular invariant PASS:
 point inventory drift3.11e-15,omega vs exact≤6.47e-15rad/s.
 This narrows failed configuration to off-axis rotational dynamics,not a blanket
 failure of Rigid3,geometry/Jacobian or all Native physics.
-585 mathematical regression FAIL preserved:elementwise relative comparison
 mishandled exact-zero tensor entries.586 uses tensor-norm relative error at
 same1e-14 bound (NO floor),5tests PASS. No physical Gate changed.
-New COM/mass candidates remain NOT ADOPTED. No new50g/100g/Lift PASS.
 Actual density,material join/union inertia and CAD STEP remain BLOCKED.

NEXT do NOT repeat565–586 or blind dt/alarm changes. Inspect a STOCK Native
composition supporting composite mapping acceleration/gyroscopic dynamics using
581/584 as negative/positive references. Installed RigidMapping.h declares no
computeAccFromMapping override;Mapping.h default composite-acceleration method
is empty. This is evidence for this composition,not proof all SOFA is incapable.
Do not silently replace old B3 inertia or resume old checkpoints with changed mass.
If no installed stock path is verified,keep adoption blocked and isolate any
minimal inertial correction as a NEW scoped candidate,not a new contact/ODE solver.

Read-only resume:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_finite_spin_exact581/summary.json`
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_finite_spin_principal_exact584/summary.json`
Regression:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m unittest discover -s product_prototype/sofa -p test_finite_mass.py -v`
Guarded fresh control:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/finite_com_native.py --tag UNIQUE_COM_CONTROL --mapped-mass --free --spin-mode principal`
Reusable unchanged332/512 binaries;no new C++ build or SDK edits. No active physics process.

## COM continuation565–580 — 2026-11-19

Authority:product_prototype/reports/FINITE_COM_NATIVE_VALIDATION_20261119.md.
Evidence:evidence_product_com_v24/manifest.json;3354 prior immutable files unchanged.

-565 independent signed-volume COM/inertia cross-check passes;physical density/join/union still NULL.
-566 free Native basis comparison passes,but567 anisotropic body-input contact FAILS:
 maximum mapped position difference1.20949mm. Not adopted into B3.
-568 input WORLD-frozen inertia passes strict1e-12 basis comparison;this is NOT a
 rotating physical tensor.569/570 actual public M and direct J identify convention mismatch.
-571 Native Vec3 mass quadrature + RigidMapping passes basis check with contact.
 572/573 free angular momentum FAIL0.660162%;577–580 half/quarter same drift.
 No custom solver/SDK change;candidate NOT qualified for B3 or physical rigid dynamics.
-575 block-only analysis omitted simultaneous cross-block impulses;preserved.
 576 corrected ALL-row audit on SAME Raw closes row update2.22e-16m/s and shows
 finite-surface active velocity target=-buffered_gap/dt residual2.83e-9m/s.
-Physical calibration,B3 time/mesh/energy,100g/Lift/STEP remain unresolved.
 Next:independent torque-free reference isolates Native rotational dynamics,
 then inspect stock inertial-force/mapped-mass support;do not blind-reduce dt.

## Latest continuation — finite Native hardware532–564,2026-11-19

Feature commits:fcf0282,ea5794a,9e09cc4,ad88042.
Authority:product_prototype/reports/FINITE_GUIDE_AND_SUPPORT_VALIDATION_20261119.md.
Evidence:evidence_product_finite_v23/manifest.json → v22 and older evidence.
Prior immutable2695files audited,0mismatches;new3356files.

-24short Native children;no full B3/Holding rerun.532 MinProximity finite mesh
 yields1001iterations/large residual;alarm5 aborts std::bad_alloc under4GiB limit.
 Actual failure preserved;not host-wide OS exhaustion or a successful run.
-Stock LocalMinDistance tested with all finite eyelet collision models ENABLED.
 16/32/64surface refinements and native compound support scene implemented.
 Fewer rows are a detection-policy change,NOT same-result speed optimization.
-539 detects real saved facet crossings with alarm1.543/5630.1%time and5451%
 contact-mesh Gates FAIL. Compound alarm5 worst~64.6244%;NOT adopted into B3.
-552/555 actual mapped points and Detector feature/edge IDs recorded read-only.
 Observer q/v/impulse difference0.557 mapped API passes strict1e-12.
-534–553 apparent surface discrepancies traced to independent trimesh SI scale
 classification.556 analysis-only nondimensional wrapper passes analytic refs;
 no Native state/force/tolerance changes.557 actual loaded surface-point error
 ≤4.18e-18m;old analysis Raw preserved. Not a physical/time Gate workaround.
-v11 CAD:36finite eyelets+36proposed supports,STL/SCAD/section/BOM/shared config.
 No STEP/kernel/joins/material/strength/whole assembly/fabrication approval.
-548/549 exact convex/envelope SAT screens show no saved support interference
 on OLD485 motion;559 support-object min+0.647705mm. Conditional replay ONLY,
 not dynamics of new hardware or swept clearance.547 sector certificate failed,
 but sector violation was correctly NOT labelled actual solid collision.
-564 partwise COM/normalized inertia audit:eyelet COM offset18.25–25.10mm from
 assumed Native mass origin;support7.61–10.94mm. Actual density/mass/union
 inertia NULL. Existing10mg origin lump is not calibrated fabricated hardware.
-Existing functional50g Skin Holding/release remains limited;full time/mesh/
 energy,100g/Lift/fabrication remain NOT QUALIFIED. SDK/Raw/verdicts preserved.

NEXT:Native COM-frame/shared-Jacobian mini reference using explicit component
mass assumptions supported by564 geometry;do not silently change lumped mass,
invent density,claim numerical repair or reuse old B3 checkpoints.
Separately investigate Native event/step timing on verified finite geometry.
No blind alarm/dt/mesh sweep,collision disable,post-set velocity or custom solver.
Immediate read-only resume:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_finite_hardware_mass564/summary.json`
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_compound_time563/summary.json`
Reusable332/512 and new554 read-only observer;frozen source/binary guards and
exact regression commands in authority. Actual Native plot560 retained.
No active physics child or promised background continuation.


## Latest continuation — Native entry/angular audit503–531,2026-11-19

Feature commits:985f93e,3ea736c,eeef6a9;unit-label correction0840e2a.
Authority:product_prototype/reports/NATIVE_GUIDE_CONTACT_ENTRY_20261119.md.
Evidence:evidence_product_angular_v22/manifest.json → evidence_product_entry_v21
→ evidence_product_velocity_v20. Prior immutable audits0mismatches.

-Actual Native detector/response/direct-J/free-state observers implemented.
 Thirty short Native children completed under4GiB/480s policy;no long B3 rerun.
-503–518 observer comparisons q/v/impulse error0,strict1e-12 preserved.
 Actual mapped impulse,mass-velocity change and effective-mass row update agree.
-506 input-path analysis FAIL and519 wrong sphere-radius interpretation preserved.
 520 verifies detector coordinates are previous mapped CENTRES(error≤6.94e-18m),
 then subtracts both radii. No old Raw or verdict rewritten.
-Native active row follows−gap/dt,NOT necessarily zero normal velocity.
 Same near-identical entry row/gap/prevelocity yields~50%dt sensitivity522.
 Old all-time0.1%FAIL498/502 unchanged;no event-time/impact-law PASS.
-523/524 angular ledger closes,but net internal tangential couple reaches
 3.83e-11Nms. Linear momentum agreement is not angular-conservation certification.
-525/527/528 stock Rigid3 sphere mapping changes contact kinematics only.
 Runs complete,but529 all-output/all-pair time gate FAIL(alarm5 worst65.85%).
 Angular inventories526/530/531 are not conservation PASS. Candidate NOT adopted.
-Functional50g Skin Holding/release485/489–491 preserved;mesh/time/wholeenergy,
 solid hardware clearance,100g/Lift/STEP/fabrication remain NOT QUALIFIED.

NEXT:validate finite Guide/Support Native contact geometry and contact-point
pullback against shared CAD dimensions in a reduced scene BEFORE full B3.
Do not repeat velocity-first/RigidSphere/alarm parameter sweeps without a new
mechanism. No custom physics solver,zero-velocity patch or collision disable.
Exact immediate read-only commands:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_rigid_time529/summary.json`
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_angular_partition524/summary.json`
Reusable read-only build512/source guard:observer_identity.compiled_pair_rows().
Raw paths,SDK/binary/source hashes,actual commands and scope in authority.
No physics child intentionally running;no automatic background continuation.


## Latest continuation — B3 moving clearance472–502,2026-11-19

Feature commits:ea03025,83da78d,18bd3eb,bd43763,3b7a4c5.
Authority:`product_prototype/reports/B3_GUIDE_RELEASE_AND_DETECTION_20261119.md`.
Final evidence:`product_prototype/reports/evidence_product_velocity_v20/manifest.json`
(linked to v19 and all old immutable evidence).

-472/475 locate375 overlap at2.390s,98mm adjacent Guide pair:one negative frame.
 Detector output follows at2.3925s;small solver residual is not accepted clearance.
-474 changes ONLY sector margin0.5→1mm,completes3s/221.356s. Holding functionality
 remains,but Guide overlap worsens to−1.102mm. Candidate NOT adopted.
-480 global5mm alarm is CANCELLED for measured cost forecast(4partial frames);
 NOT timeout,OS exhaustion,completed physics or a remedy.
-483 Native free-pair reference supports alarm-range cause.484/485 scheduled
 native alarm window changes no force/state solver;3s completes133.319s.
-488 saved Guide spheres show no overlap(min+0.194739mm).492 first954frames
 finger/Guide/object q/v and cable force match375 EXACTLY;4wide-alarm frames.
 Skin-only functional50g Holding and release retained489–491. NOT final grasp PASS.
-493 positive chord gaps are NOT actual swept CCD. Solid supports remain unverified.
-498 free-pair0.1%all-common/all-pair time gate FAIL. Native velocity-first499–502
 also FAIL(5mm worst~63.8%);not applied to B3. Prior mesh/time/energy FAIL preserved.
-481/487 new baseline route drawing/STL/SCAD coordinate audit:all6Native routes
 error0. STEP/assembly/fabrication NOT READY. No100g/Lift expansion.
-v19/v20 prior hash audits0mismatches;final2087files. No old results rewritten.

NEXT:read-only Native free-pair row/normal/tangential velocity/impulse recording
around contact entry;compare modes at same physical event phase using existing
verified mass/Jacobian references. No new solver,margin sweep,global alarm full
run,or unvalidated100g/Lift. Read exact restart commands in authority.
Immediate read-only commands:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_pair_velocity_time502/summary.json`
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_comparison492/summary.json`
Reusable physical build332 and separate alarm build484 have frozen hash guards.
ActualRaw,source/binary,applied alarm clocks and commands are preserved.
All launched sessions ended;480child final report absent/NULL,not fabricated.
No background continuation promised.


## Latest continuation — Native axial strain468–471,2026-11-19

Feature commit7701d5b. Authority:
`product_prototype/reports/NATIVE_AXIAL_STRAIN_PATH_20261119.md`.
Evidence:`product_prototype/reports/evidence_native_strain_v18/manifest.json`.

-Actual installed force path inspected:default axial strain uses spline-midpoint
 local/rest endpoint transforms,not chord length. SDK remains unchanged.
-468 build/API constness failure is preserved;physics NOT RUN. New build469
 fixes observer temporary qualification only;470 completes6native PRIVATE queries.
-Native force reproduces455 exactly. Reconstructed axial changes explain
 1ULP force changes1.70e-12/3.40e-12N to≤4.16e-18N. Actual unloaded q unchanged.
-47170digit projection contrast supports representation sensitivity but is not a
 complete high-precision spline reference,force correction or accepted equilibrium.
-Strict fine-mesh equilibrium remains FAIL. Stop further unit/origin/FD/precision
 sweeps without a new remedy hypothesis. No Gate waived;no B3/100g/Lift approval.
-Prior immutable1258files verified,0mismatches;new manifest1351files.

NEXT independent product task:read-only actual-state Guide interference audit
using saved375. Identify offending physical Guide/support pairs before proposing
new geometry;do not disable collisions or promote prescribed geometry.
Fine-mesh physics qualification remains blocked separately.
Exact read-only restart:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/native_beam_strain_assess471/summary.json`
`rg -n '375|Guide|gap|interference' product_prototype/reports/SKIN_ROUTING_AND_PRECURVATURE_20261119.md`
Reuse frozen strain observer469 and force observer451 only for justified new
diagnostics. Full commands/source/binary/SDK identity are in authority/Raw.
No physics child intentionally running;no automatic continuation promise.


## Latest continuation — loaded tangent459–466,2026-11-19

Feature commits1c20109,b19f839. Authority:
`product_prototype/reports/NATIVE_LOADED_TANGENT_VALIDATION_20261119.md`.
Evidence:`product_prototype/reports/evidence_native_loaded_fd_v17/manifest.json`.
-459 corrects diagnostic root mask(3/5nodes);mixed-direction force derivatives
 agree to best1.30e-9/7.40e-10 relative.460 old-default FD byte regression PASS.
-462 observer input registration FAIL is preserved. New build463 fixes it;
 464/465 test a soft bending direction without changing actual q/v.
-Soft-direction force agreement is much less precise(best1.65e-4/2.04e-4 relative);
 torque derivatives near zero remain unresolved. No complete tangent/mesh PASS.
-466 records the comparison and actual-query plot. Actual unloaded positions
 unchanged(error0). Prior immutable1119files verified;0mismatches.
-Strict static41/81 residuals remain FAIL. No B3/full time/energy/hardware,
 100g,Lift or fabrication approval. No tolerance or model change adopted.

NEXT:read the actual native axial strain/length force path,then quantify
represented segment-length/axial-force sensitivity at frozen PRIVATE states.
Do not assume chord length equals the implementation's internal strain.
No more blind FD-step/unit/origin sweeps;no new custom physics solver.
Read-only restart:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/native_beam_fd_assess466/summary.json`
Reuse frozen builds458(root ladder),463(explicit direction);source/binary guards
and complete reproduction commands are in the authority. All prior results kept.
No physics child intentionally left running;no background continuation promised.


## Latest continuation — refined Rail454–457, 2026-11-19

Feature commit:c50516b. Authority:
`product_prototype/reports/NATIVE_FINE_RAIL_PRECISION_20261119.md`.
Evidence:`product_prototype/reports/evidence_native_refined_v16/manifest.json`.

-454 per-node failed-state diagnostics and455 PRIVATE ±1ULP force queries are
 complete. Baseline queries reproduce actual failed-frame forces exactly;
 actual unloaded q is unchanged. These are NOT accepted equilibrium states.
-41/81 axial residuals1.34812e-12/2.59047e-12N; one-coordinate ULP perturbations
 change force by1.69967e-12/3.39935e-12N. Sensitivity is not an error floor,
 proof of impossible equilibrium, or permission to correct actual coordinates.
-456 read-only observer exports SI positions/torques for static unit tests.
-457 equivalent N-mm-s static representation passes coarse21 force/state checks,
 but41/81 remain native solve FAIL. No mesh, time, B3,100g or Lift approval.
 Previous B3 functional Holding and all historical failures remain preserved.
-Old immutable evidence audit:980 files checked,0 mismatches; new manifest1122
 files. Original SDK, Golden, Raw and Checkpoints are not modified.

NEXT:compare loaded-state native tangent/directional force derivative with
symmetric FD over a documented perturbation ladder at frozen PRIVATE41/81
failed states. Initial-reference matrix equivalence432/439 is DONE;do not repeat.
First inspect exact preserved inputs:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/native_beam_refined_diagnostic454/summary.json`
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/native_beam_units457/summary.json`
Reusable frozen observer451 for SI PRIVATE queries,456 for SI unit exports.
Actual reproduction scenes/commands are in each Raw process record and authority.
Stop blind unit/origin/parameter sweeps. No tolerance waiver, custom solver,
failed-frame promotion or new product candidate is justified by these results.
No physics child intentionally running; no automatic session continuation.


## Latest checkpoint — native residual/centered Rail442–453,2026-11-19

Feature commits2dc6afc,fcc7ba5. Authority:
`product_prototype/reports/NATIVE_NONLINEAR_RESIDUAL_AND_CENTERED_RAIL_20261119.md`.
Evidence:`product_prototype/reports/evidence_native_centered_v15/manifest.json`.

-442 completes the previous next task:PRIVATE native axial residual scales with
  amplitude^2,transverse^3.444 second-order PRIVATE kinematics reduces axial error,
  but is NEVER installed into actual state. No need to repeat these diagnoses.
-443 full-step-like native budget0 and445 smaller load FAIL strict solver gates.
 447 native reinforceLength is a DIFFERENT force approximation,not adopted.
-448/450 translate complete geometry/root by−50mm;21node actual small-load static
  solves now complete WITHOUT gate relaxation.452 directly measures free force
  residuals6.17e-13/2.30e-13N,torque criterion passes,and observer/control q/v error0.
  This is only centered21node Rail at1e-8/5e-9N,NOT B3,mesh/time or grasp PASS.
-453 actual load scaling error9.50233e-13m passes absolute1e-12m only.449 centered
  41/81node solves FAIL;no full mesh certification and no partial-state promotion.
-Reusable read-only builds441/451,frozen source/binary guards and actual/private
  plots are preserved. All old B3/raw/Golden/verdicts remain unchanged.

NEXT:per-node native force/torque and coordinate representation diagnosis of
centered41/81 failures449. Full Rigid3 failed frames must be marked diagnostic,
NOT accepted states. No tolerance waiver or repeated parameter sweep.
Exact read-only restart:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/native_beam_accepted452/summary.json`
Then inspect453 and449;source/build/raw/reproduction commands are in authority.
Full wrapping,mesh/time,energy,hardware clearance,100g,Lift and fabrication stay
unqualified. No physics child intentionally running;no automatic restart promise.

## Historical checkpoint — native reference/assembly432–440,2026-11-19

Feature commits:e5d4dae,bc762c1. Authority:
`product_prototype/reports/NATIVE_BEAM_REFERENCE_AND_ASSEMBLY_20261119.md`.
Evidence:`product_prototype/reports/evidence_native_reference_v13/manifest.json`.

-432/439 initial native modern assembly and full addDForce agree EXACTLY in all
  four translation/rotation blocks. This next task is DONE,not to be repeated.
-Flat straight=true starts with1.01244e-12N free force and strict rest FAIL.
  Actual geometric rest transforms remove initial force/torque;rest q/v control
  differences0.439 exports native lengths at17digits;432 generic string was rounded.
-433 loaded21/41/81 geometric-rest cases FAIL.435 corrected native20-stage load
  continuation also FAILs.434 unsupported fields caused zero load:EXCLUDED,not PASS;
  original records retained. Runner now rejects unused attributes.
-440 measured initial tangent PRIVATE linear reference matches Euler to9.04e-13
  relative;not an actual accepted state,loaded bending or full energy certification.
-New431/438 read-only builds and frozen source/binary guards are reusable.
  Precision-only changes retain nine initial force/matrix CSVs exactly and actual
  zero-load mapped-center q/v exactly. All old B3/raw/verdicts remain preserved.

NEXT:read439/440,then query native FORCE at PRIVATE linear reference,partition
axial/transverse/rotational residual and representation error. Do NOT install
private coordinates as accepted state or repeat cap/ramp sweeps without evidence.
Immediate command:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/native_beam_precision_assess440/summary.json`
B3 full wrapping/mesh/time/energy/hardware-clearance/fabrication remain open;
100g/Lift NOT RUN. No physical process intentionally left running;no automatic
restart promised. Exact reproduction/build/raw identities are in the authority.

## Historical checkpoint — native backward error/alternatives407–430,2026-11-19

Feature commits:3593421,c487517,127119b,e0d5750. Authority:
`product_prototype/reports/NATIVE_SECTION_BACKWARD_ERROR_AND_ALTERNATIVES_20261119.md`.
New evidence:`product_prototype/reports/evidence_native_alternatives_v11/manifest.json`.

-407 actually tests loaded Skin/one-Rail/two-Rail. All loaded native trials FAIL;
  PRIVATE matrix equilibria are NOT accepted states. Coordinate representation
  amplifies residual from~1e-14N to~4e-9N; native force agrees with this diagnosis.
-425 rigid coordinate translation preserves K to3.23e-15 relative, reduces but
  does not cure residual. Both translated loaded trials remain FAIL1e-12N.
-415 actual native bending derivative paths differ34.7062%; SDK NOT patched.
  Stock matrix-free PCG416/417 works numerically, but mesh and constitutive
  qualification421 FAIL; manufactured precurve419 is not stress-free. No B3 use.
-423 native rectangular BeamAdapter curved zero-load state is exactly retained;
  loaded422/424 FAIL. This is not loaded Rail/attachment certification.
-429 Rigid3 directional native addDForce FD is DONE:force~.00312%,torque~.0890%;
  curved observed/control rest positions exactly agree.427 scalar-API comparison
  is an observer failure,excluded;not a native bug.430 raises only iteration cap
  to120 and still FAILs actual Line Search at58. Do not repeat cap sweeps.
-v8 verifies764 prior-v7 immutable files;v9 verifies395 prior-v8 immutable files;
  zero mismatches. Historical evidence and all old PASS/FAIL retained.
-B3 functional50g holding/release unchanged. Full wrapping,mesh/time,energy,
  moving solid clearance,100g,Lift and fabrication remain unqualified/NOT RUN.

Reusable read-only builds:cad/build_elastic_probe406,
cad/build_assembled_observer410,cad/build_rigid_observer428;
frozen identities in sofa/observer_identity.py.
Raw:product_prototype/results/native_*407–430 (exact names in v11 manifest).
No physics process is left intentionally running. No background restart promise.

Next:429 directional FD is DONE. Read429/430,then inventory native rectangular
BeamAdapter reference lengths/initial force and compare actual modern assembled
matrix versus addDForce at the SAME state. No custom force law or cap sweep.
Immediate exact restart:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/native_rigid_tangent429/summary.json`
Reproduction commands/frozen sources/build hashes and explicit scope are in
the authority. A unique tag is mandatory for any new physics run.

## Historical continuation — native elastic validation380–405,2026-11-19

Latest feature commits:73e431e,e1dc3ea,19432e5. B3 functional holding/release
and ALL prior failures remain unchanged;no product promotion,100g or Lift run.
Authority:product_prototype/reports/NATIVE_ELASTIC_MODEL_VALIDATION_20261119.md.
Evidence:product_prototype/reports/evidence_native_elastic_v7/manifest.json.

- Actual native tetra/hexa exact axial patch393 passes all-node1e-12m.
- Actual pure-bending396/398 and independent force/strain/energy397/399 are
  recorded;thin section and ALL-PAIR mesh gates still FAIL. Time.1% unchanged.
- Native K/force observer402 changes solid q/v by EXACTLY0. Thin projected
  condition~2.96e9;force/K FD checked. NO new FEM/contact/ODE solver.
-405 verified material volumes210/310/410mm³ and zero-load state identity;
  initial Skin-only condition~4.10e9 already precedes Rail/Guide attachment.
  This is NOT loaded component bending certification.404 wrong material labels,
  401 scene plugin ordering failure and383 CSV parser failure are retained/excluded.
- Prior10613 immutable files byte-verified with zero mismatches. B3 moving
  hardware clearance,full wrapping,whole energy,mesh/time and fabrication remain
  unqualified. STEP/CAD geometry was not changed to conceal failed physics.

NEXT:loaded Skin/one-rail/two-rail reference and native element/arithmetic
diagnostics,then incremental Guide attachment. Initial spectra405 are DONE.
Do not rerun failed372 unchanged or expand unqualified B3 to100g/Lift.
Exact read-only restart:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/native_section_spectrum405/summary.json`
Full commands/build hashes/raw paths are in the authority above.
No physics child is intentionally left running;no automatic restart is promised.


## Latest product checkpoint — 2026-11-19, native trials259–379

Last functional checkpoint commit:d215185 (routing8f1cbc7/1de4288,force input81640fe,
mesh/time isolation4d7d4e9). Detailed authority:
product_prototype/reports/SKIN_ROUTING_AND_PRECURVATURE_20261119.md.
Historical bodies,Raw,Golden,SDK and prior verdicts below are preserved.

- A/B/C distributed routing/stress-free precurve candidates were implemented and
  actually tested first in SINGLE fingers. Initial3-finger guide-proxy overlap was
  discovered287,not hidden;293 now rejects it before physics. v8 sector routes retain
  real wire/guide dimensions and all hardware collision.
- B3=40deg manufactured distal curve70–100mm,1.5N/cable NATIVE force input.
  330/331 calibrate native value=T*dt;334/335 C2 input and discrete BE reference pass
  STRICT1e-12. New default displacement branch333 q/v difference0 for200 contact
  steps. This is input/controller work,NOT new FEM/contact/ODE solver.
- 344/348 ACTUAL Skin-source50g holding:slip.032359mm,speed.272144mm/s,
  support gap41.599746mm,Support/Guide/Rail hold force0,Skin Fz.490513N.
  Half-dt351/368/373 also meets FUNCTIONAL hold protocol,with Skin Fz.490480N.
  SAME-geometry zero-force345/349 FAILs (40.00054mm slip):not passive-curvature
  holding alone. This is limited SIMULATION evidence,NOT full physical certification.
- Matched constant-route308 ALSO meets functional holding;do not claim routing
  uniquely creates holding. Its cable errors/settling are worse;force and displacement
  inputs are different physical models,not a relabelled numerical fix.
- 375 completes3s in172.152s:after the SAME0–2s hold,the support ONLY exits laterally
  120mm2–2.2s (NEW post-hold fixture input);object remains free under gravity.
  377 first800 q/v states match344 EXACTLY.376 last Skin contact2.3875s;late Skin/
  Guide-object/support forces0;support and Guide-object forces after2s also0.
  Actual force unload reaches0N. Tip rest-reference error.150984mm under gravity;
  full recovery to validated gravity equilibrium NOT QUALIFIED. Old325 separation
  failure and residual cable tension are retained,not converted to PASS.
- Wrapping NOT QUALIFIED:48deg tip angle is not broad contact coverage;area/pressure
  remainNULL. Full moving hardware clearance FAIL/UNQUALIFIED (e.g.375 guide-proxy
  gap−.864mm);exact supports/solid sweep/self-collision/thickness remain unfinished.
- Physical gates FAIL:315/366 all-pair.6s,367 full2s pair,276/346 single full2s
  refinement retain.1% gate with NO floors. Loaded41-node360 has inverted tets;
 365 no-object also inverts;364 quarter-dt avoids inversion through.5s but differs
  strongly from coarse spatial response.363 zero-input reference is exact.
  These isolate causes,NOT prove locking or a unique solver bug. No production3-finger
 41-node expansion. Static native bending372 stops on actual Newton failures;
  missing static pairs areNOTMEASURED/BLOCKED,not measured zero errors.
- No100g,Lift,12-Wrench,Optuna,whole energy,final design or fabrication PASS.
  Native velocity-first Cable coupon322 FAILs;323 control PASS. Do not enable that
  combination in product scenes. General friction/energy certification remains open.

Reusable calibrated controller:product_prototype/cad/build_default_control332/
libReGripProductSequence.so
SHA2563eb202b1e2a25f3ec6cded69e92a9d02bc48c304be14f6ca7123b4d758e5d0e0.
Historical displacement build187 remains immutable;current runner source guard
requires the new332 build. Actual source snapshots/hash identities,not just a
possibly dirty parent source_commit,define each experiment.

CAD references:meshes/drawings distal_A_sector_v8,precurve_B_sector_v8,
hybrid_C_sector_v8,precurve_distal40_v9. STEP/OCC/FreeCAD assembly NOT GENERATED.
Actual figures:results/release_figures379/ and final_actual370/ (NOT QUALIFIED).
Frozen native scene:product_prototype/sofa/scenes/native_force_hold_release_v9/
(journals redirected;export-only is not an extra replay PASS).

Next priority:well-conditioned NATIVE small-load bending/attachment validation,
then moving-clearance and mesh/time gates. Do not continue stroke/offset/force sweeps
or repeat failed372 unchanged. Inspect its real residual/line-search logs before
changing any numerical scheme;do not waive tolerances or resume custom solver work.
The current family is checkpointed after repeated physical-gate failures,not declared
complete. All launched children finished;no automatic background continuation.
Actual275 hit480s policy timeout;no OS/RAM exhaustion is claimed.

Exact review/reproduction commands (use NEW tags;do not overwrite existing outputs):
```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY -m json.tool product_prototype/results/mesh_isolation369/summary.json
$PY -m json.tool product_prototype/results/force_three_time366/summary.json
$PY product_prototype/sofa/release_assess.py --case force_release_clear_support375 --tag NEXT_UNIQUE_RELEASE_AUDIT
$PY product_prototype/sofa/response_load_assess.py --case precurve40_force_three344 --tag NEXT_UNIQUE_SKIN_AUDIT
```
Actual simulation commands are preserved in each case launch_command.json and
process/command.json;full-quarter2s cost exceeds480s and was NOT RUN.

## Latest Skin-contact continuation — 2026-11-19

Source commits fbc9754,0ec92f0; details: product_prototype/reports/SKIN_CONTACT_CONTINUATION_20261119.md.
Trials147–175 use unique Raw paths; legacy and earlier FAILs unchanged.

-150/152: first finger impulse1.07s coincides with−.214888mm cable error.
 Assembled J matches previous geometry (~1.25e-16),not current geometry;
 reported linear error3.33e-9 does not certify geometric shortening.
-Backside guide149/151 (normal−3mm,unchanged hardware size) fails:no finger load,
 object follows support40mm. This routing is not selected.
-Outboard4 candidate155 initially meets functional holding and child-J row-load
 criteria, but these are NOT physical Skin holding. Geometry168 FAIL:
 Skin gap>=3.394mm despite active row influence;child/FEM coordinates match0.
 Detector173 confirms object–GUIDE pairs and NO object–Skin pairs through.4s.
 Child Jacobian influence is NOT direct contact provenance;169 is not grasp PASS.
-Read-only mapping logger171 and native detector174 give EXACT state equality
 (STRICT1e-12) over their respective2s/.4s scopes. Split-vs-unsplit172 FAIL:
 contact partition changes dynamics and is not a passive observer substitution.
-Base/Half/Quarter155/162/163 all completed2s;all-pair/all-common-time167 FAIL at
 unchanged.1% gate. No100g/Lift or final CAD selection is authorized by these results.
-Minimal Rigid3/DiagonalMass158 FAILs factory/state/topology initialization;
 not proof the entire SOFA capability is unsupported. Full bridge remains BLOCKED.
-CADv5 retained;STEP/assembly kernel/moving hardware/wire swept clearance,
 full energy/contact area/pressure remain NOT QUALIFIED/NOT MEASURED.

Next:bind actual Contact collision-model pair and response Constraint row identity,
 not mechanical-J influence. Use public detector provenance first,then eliminate
 Guide-first contact without disabling hardware collision. No custom solver rewrite.
Exact commands/Raw/Build identities are in the new detailed report.
All launched physics children completed;no automatic continuation is promised.


## Native continuation checkpoint — 2026-11-19 (supersedes priorities below, not historical results)

Functional commit: `ff21719` (preceded by 3f600b7, af356fb, e29719f, 956d6c3).
Detailed evidence: `product_prototype/reports/NATIVE_CABLE_COUPLING_AND_HOLDING_20261119.md`.
New native trials051–146 are separate from legacy Campaign numbering.

- Cable error isolated: exterior lateral Barycentric extrapolation (weights −29..37,
  amplification73) plus lagged native cable linearization produces a two-state cycle.
  Mapping/Jacobian arithmetic is consistent; straight/surface coupons pass. Existing044 FAIL retained.
- Stock RigidMapping/SubsetMultiMapping guide hardware replaces extrapolated guide mechanics
  in opt-in scenes. No custom force/contact/ODE solver added. No-contact131 hold shortening
  error ≤2.33e-10mm; transient error .00365mm means NOT whole-time cable certification.
- R30/50g conditional holding124: support force0, support clearance about44mm,
  low measured speed. Weight is borne by GUIDE HARDWARE, not Skin. This is
  experimental hardware-only holding, NOT film wrapping or final grasp PASS.
  Matched100g132 FAIL. No maximum holding capacity or fabrication claim.
- End-clock support adapter124/127: declared versus actual path error0m.
  Half/quarter-dt assessment133 retains0.1% gate: FAIL, including substantive object-motion
  differences (~1.44mm), not only tiny-value relative errors. Contact cable errors at
  base/half/quarter remain .21489/.09091/.05674mm.
- Public initial mass API140 PASS; opt-in query purity four steps difference0.
  Frozen scene replay141: all1200 steps q/v/quaternion/support differences0, STRICT1e-12 PASS.
  Repeatability is not physical accuracy. Input guards146 PASS (no physical trial).
- Cross-guide bridge136–138 current DiagonalMass configuration fails initialization;
  only that candidate BLOCKED, not proof all native diagonal mass is unsupported.
- CAD sources/STL/drawings/BOM: native_guides_v5. FreeCAD/OCC unavailable;
  STEP/kernel assembly NOT GENERATED. Moving full hardware interference NOT qualified.
- Lift BLOCKED by contact/time gates and mapped-root actuation path; no Lift run.
  Skin wrapping, general friction, self-collision, full energy/pressure/area and fabrication
  readiness remain unverified. Legacy results/SDK preserved; no push.

Next implementation: isolate native contact-transition cable linearization on a short
recorded failure interval, then revise guides so Skin, not hardware, bears load.
Before bridge dynamics, reproduce its native Rigid3 DiagonalMass initialization in a
minimal scene. Before Lift, implement a verified free-subset root fixture and pullPoint
motion; do not bypass current guards. Existing tests should be reused, not blindly repeated.

Reproduction commands and exact Raw/Build identities are in the detailed report and
`product_prototype/reports/evidence_native_coupling_v2/manifest.json` (once published).
All trials are stopped; no automatic continuation is configured. This is an incomplete
product-development checkpoint, not OS resource exhaustion or project completion.


# Product/native checkpoint — 2026-11-19

방향 전환 시작 b63ac48. 초기 제품 commit e5675c9,주요 기능 commit d6c4580.
이후 coupon050,메타데이터 수정,추종/지지대 진단과 문서를 별도 커밋한다.
정확한 최종 커밋은 `git log -3 --oneline`으로 확인한다.

## 구현/증거

- cad/generate.py,export_freecad.py,publish.py;drawings/candidate_v3/에 치수도,
  부분 분해도,BOM,SCAD,검사 JSON. meshes/product_outboard14_v3/에4종 폐곡면 STL.
- 실제 실행 Scene:sofa/scenes/native_three_finger_v1/,800스텝 exit0.
- 모든 고유 trial:results/native_*/,분석:results/analysis_*.
- 재사용 가능 입력/로깅 DSO:
  cad/build_native_single_generic_045/libReGripProductSequence.so.
  이 빌드는 정상이나045의 제거된 GenericConstraintSolver Scene은 FAIL이다.
  같은 DSO의050 수정 BlockGaussSeidel 직선 coupon은 실제800스텝 PASS.
- product 결과는 기존 자체 Solver/SDK와 분리. legacy Checkpoint 재사용하지 않음.
- 044 support withdrawal,048 분석:Holding FAIL,종료 objectdrop40.2mm.
  지지대 중간 시각 API 경로 오차.2mm로 STRICT시험도 FAIL;원인 미확정.
- 050 straight cable 실제 경로 추종 PASS,max1.77809e-17m. FEM/외측 매핑/두케이블
  조건에서는8mm 명령을 추종하지 못한다. 다음 개발 병목이다.
- 010/011/012 전체 출력 Time Gate0.1% FAIL,021 Lift FAIL,
  pressure/area/root reaction/full energy NULL. 모터/실측 재료/Equalizer 미정.
- FreeCAD/OpenSCAD/OCC 미발견으로 STEP/전체 어셈블리 검증 미실행.

## 다음 정확한 명령

```bash
cd /media/ubuntu/99419895-2058-45b4-b746-b36ea7112e4e/research/LHJ/ReGrip
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
git status --short
git log -3 --oneline
$PY product_prototype/sofa/cable_coupon.py --tag UNIQUE_STRAIGHT_CHECK
$PY product_prototype/sofa/run_native.py --tag UNIQUE_FEM_BASELINE
$PY product_prototype/sofa/analyse.py --tag UNIQUE_FEM_AUDIT --cases UNIQUE_FEM_BASELINE
```

050 재현은 원리 시험이다. 다음 **새 개발**은 단일 케이블과 쌍 케이블을
동일 FEM에서 비교하는 opt-in 장면을 추가하고,외측 Barycentric 경로와 표면상
경로를 한 변수씩 비교하는 것이다. 실제 Guide 길이/명령/반력/단계 선형화 오차를
기록한다. 물리 장력/마찰/허용오차를 바꾸어 기존 FAIL을 PASS로 변경하지 않는다.
기존 기본 단일 Scene은 지오메트리6개 Guide/케이블,C2/5mm 명령이다.
기존 CSV가 guide로그를 갖지 않으면 길이 측정은 NULL이며 0으로 채우지 않는다.

독립 Holding 재현(지지대 실제 구동,물체와 핑거 형상은 처방하지 않음):

```bash
$PY product_prototype/sofa/run_native.py --tag UNIQUE_HOLD --fingers 3 --object free --radius 20 --gravity --floor --outboard 14 --intersection LocalMinDistance --stroke 8 --center-z -80 --support-shape sphere --support-gap .4 --withdraw-support
```

재개는 기록된 물리 checkpoint가 아니라 **새 Native 초기 상태의 신규 trial**이다.
개별 프로세스4GiB/480초,동시 장시간4개 이하. 모든 실행은 종료되었으며
세션 이후 자동 재시작은 설정하지 않았다. OS 자원 고갈을 주장하지 않는다.
제품 완성은 미달성이다. 현재 산출물은 다음 개발로 이어갈 구현 체크포인트이다.
## Latest native Skin-contact checkpoint — 2026-11-19 (trials179–258)

Latest functional commit: b5e99ee; preceding commits9298860,427c124,ba0657f,c17f99a.
See product_prototype/reports/AUTONOMOUS_DESIGN_PROGRESS.md and
DESIGN_CANDIDATE_COMPARISON.md. Historical verdicts/Raw are preserved.

Actual Contact model pairs now bind to public response ConstraintBlockInfo rows.
Object impulse partition is verified;190 physical q/v/quaternion equality is0
at STRICT1e-12. getConstraintInfo changes yetIntegrated metadata: internal-history
query purity is NOT claimed. Child-J influence alone is not direct Skin contact.

Native Rigid3 sphere requires supported MinProximityIntersection/useSphereTriangle.
231 audits missing LocalMinDistance RigidSphere/mesh intersectors in205/206/211/
216/220/226; those are INVALID collision-completeness comparisons,not evidence
that their Skin mechanisms cannot work. New unsupported combinations are rejected.

Valid R30/50g,mu.3,gravity,3-finger trials235(2mm) and247(4mm) finish2s:
real Skin response,Guide/Rail load0,but unsupported Holding FAIL.
247 downward slip40.242309mm;Skin mean Fz−.3244778N,support+.8149382N.
256 late Skin Coulomb cones all have negative maximum vertical coefficient:
increasing normal force alone cannot support gravity at those measured normals.
Early upward normals245 did not persist through support withdrawal.
257 accepted-state gap/active-response consistency FAIL (max active gap.202431mm
versus declared.2mm);this is not per-row or swept-clearance certification.
258 linear/angular momentum inventory passes only its narrow balance scope.
251 body/collision Rigid3 identity mapping q/v/time difference0 over800steps.

236/237 complete.6s half/quarter refinement;243 all-common-time/all-pair comparison
FAIL at unchanged.1% gate. Base/quarter finger-motion difference.245452mm at.05s.
239 assumed-radial reconstructed Jacobian FD FAIL;actual native contact-point
Jacobian FD remains unqualified,not conclusively a native force implementation bug.
Full2s quarter run forecast~950s exceeds480s child policy:NOT RUN,not OS exhaustion.
No Skin Wrapping/Holding/100g/Lift/whole-energy or final-product PASS.
Area,pressure,root work remainNULL. CADv6 sources/STL/SVG/BOM exist;STEP/kernel
assembly,full moving interference,measured materials and fabrication readiness BLOCKED.

Stop this constant-offset routing family after measured2/4mm failures;do not blindly
increase stroke/force. Next independent hypothesis:distributed distal routing or
precurvature must preserve upward Skin contact normals during withdrawal. First
validate native Cable/FEM bending and actual contact-point logging in a short coupon;
keep real hardware collision enabled and shared CAD/SOFA configuration.
Thin tetrahedral bending/locking and native animation-loop alternatives are hypotheses,
not established causes. No custom solver redevelopment or old checkpoint reuse.

Reusable build:product_prototype/cad/build_response_public_187/libReGripProductSequence.so
SHA256:33baec3658a718b7bff6f472f6701f6f75c02a70507bbe5a4ea4260fa478e1c2.
Raw:product_prototype/results/rigid_min_stroke4_hold_247/
Actual-state PNGs:product_prototype/results/native_min_actual_255/
Reproduce analysis with a NEW unique tag,not existing directories:
```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/response_load_assess.py --case rigid_min_stroke4_hold_247 --tag NEXT_UNIQUE_SOURCE
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/skin_contact_direction.py --case rigid_min_stroke4_hold_247 --tag NEXT_UNIQUE_DIRECTION
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/wrapping_geometry.py --case rigid_min_stroke4_hold_247 --tag NEXT_UNIQUE_GEOMETRY
```
All launched children completed. This is a bounded failed design-family checkpoint,
not project completion or a claim of background continuation. No SDK/legacy solver
changes,remote push or old evidence overwrite.
## 2026-11-22 — whole-path supplier CAD869–872

Read SUPPLIER_WHOLE_PATH_20261122.md. Six lead tangent budgets clear only;
5oldRoots+18turns fail candidate wire bend diameter. Actual3wheel retrofit871
FAILS wheel/wheel and retained hardware interference. Single-variable outer
route x74 candidate872 removes wheel/wheel overlap but retained bridge/pins
still FAIL. Do NOT repeat unchanged runs or promote to Native/product PASS.
NEXT reconstruct connected finite turn mount/axle at872 centres, then full
wire/channel/service clearance. No approved wire/material/STEP/wholewire law.
Old physical Gates preserved; no new SOFA run or automatic background work.
