# Native tetra handedness and 100g grasp — 2026-11-24

Continuing347c858,not a newSolver/SDK or physicalcertification.
Actualsource/binary/scene/generator hashes andcommands in eachuniquepreflight.
All oldRaw/FAILs preserved;4GiB/120s smallcoupons,420s graspchildren.

## Actual failures before diagnosis

1506untaperedwidthfull2s123.927s/800each:1509FAILspeed29.7741mm/s despite
slip.9790mm/SkinFz.98542N/GuideRailSupport0.1513samegeometry,ONEC2input
closing.5→1s(actualSupportwithdrawalstart),full2s108.008s/800each:1515FAIL
speed26.82659mm/s despite slip.180669mm/SkinFz.980542N/GuideRailSupport0,
gap42.0275mm.1516allthree800actualC2commandsmatchanalytic≤4.44e−16N and
Nativeimpulsecommanderror0;normalizedScenesEXACTexceptclosing. Not a solver
repair;do not keep changingrampduration.1518actualRawcomparisonPNG.

1519independentoldlatchauditrulesoutbenignzero-tensionslack explanation:
1458worstlonger-path2.992797mm atpositive1.782062N,zeroexactslacksamples.
1451worst5.979µm at1.655114N. Oldstrict1e−12 andfunctionalFAILs unchanged;
do not blindlyreusefailedfixed-spoolcontract as a100g repair.

1520actualobjectangularmomentum residual1.58e−20Nms/sourcepartition8.67e−19,
discretekineticmidpointidentity3.07e−19J. Theseareobject-onlyidentities,NOT
globalstoredenergy orfrictionloss. All3SkinmeanZtorquesnegative duringhold:
−.242948/−.172306/−.086946mNm. Objectomega up to7.48977rad/s. No hidden
Guide/Rail/Supporttorque;need originofsame-handedSkinmotion,notmoretension.

## New minimal Native reflection experiment1521–1523

CloneINITIALScene1506,notacceptedstate/checkpoint. Removeobject/support/two
fingers andtheirread-onlyobservers;retain all remainingGuidecollisionmodels.
Onlytetconnectivity differs:reflectnodeindices acrosslocalwidth andswap0/1
to retainpositivevolume. Actual.6s/240outputs,3.282/3.180s,bothminvol.984187,
exactly2Cableconstraintrows (no contactconstraints). OthernormalizedScene
data identical. Originaltip lateral−1.423703mm vsreflected+1.423703mm;
crosswidthnormaldifference+1.316038mm vs−1.316038mm. Fullmirrorprediction
qerror1.98e−13m/v3.43e−11m/s;unreflectedqdiff2.849449mm. This isolates
meshhandedness inthisno-objecttrial,NOTuniqueproof ofallcontacttimefailure.

## Conforming matched centreline meshes1524–1528

Addcentreliney0nodes,removeunusedvoidnodes:294vsold252nodes,720tets.
No doubledmaterial/half-Efields. Exactmaterialvolume,existingreferencepoints,
36mappedrailbackanchors,Rootarea,Guidehardware/cables/totalMass preserved.
NativeUniformMass nodaldistribution necessarilychanges vs252nodes;paired294
nodecaseshave identicaldistribution. RebuildSkin/Rail collisionboundaries
fromactualFEM exteriorfaces;everyboundaryedgehasincidence2,nohangingcracks.

1524matchedasymmetricdiagonals:tipy−2.280564mm.1525reflectedtetSET reduces
to+.011341mm butqreflection22.77µm/v.00011216m/s:1526strict1e−12FAIL.
NativecorotationalQR referenceframe depends onorientedvertexorder,not just
unorderedtetset. Pairedswap0/1reversesABwhilepreservingABCplane,soframeunder
reflectiondiffersbyfixedlocalparity;swap1/2changesaxisABtoAC instead.
1527actualnewpaired-ordercoupon.6s3.210s/positiveFEM/twoCable rows;tipy end
−3.41e−13mm,fullqreflection4.13e−15m. vreflection1.444891e−12m/s still
FAILS unchanged1e−12:1528 remainsFAIL,not roundedtoPASS orfloor-relaxed.

## Functional candidate,NOT numerical promotion

Positionbiaselimination/closedmesh/positiveactualFEM justify a separate
EXPLORATORY functionalpilot,as permitted for100g despiteunresolvednumerical
gates. Do not callmirror/time/mesh/physicalPASS. Source1506T1.5/mu.3/R30/.1kg,
physicaluntaperedreference,Root/Guides/foot/material/ODEunchanged. Surface
triangulationandnodalmassquadrature differ vsold252nodeB3,explicitly not an
isolatedtopology-onlyfullgraspcomparison. NewconsistentFEMSkin/Railboundaries,
samefiniteGuidecollisions.1529fixedsphere single.25spilot nowactualNative;
fixedobjectprojectedJ isNOTtotalreaction. Inspectsummarybeforefree3pilot.
Thenoriginal100ggoal1.6–2s/slip2mm/speed5mm/s/supportgap5mm/nohardwareloads.

Reproduce ONLYfresh tags:

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY product_prototype/sofa/mirror_tet_coupon.py --tag UNIQUE --reflect
$PY product_prototype/sofa/run_mirror_mesh_coupon.py --tag UNIQUE --symmetric --paired-order
$PY product_prototype/sofa/run_mirror_mesh_grasp.py --tag UNIQUE --single
```

Actualwire/material/hardwaremass/allowables/energyclosure NOTMEASURED;
oldtime0.1%/mesh1%FAILs unchanged. Latest300partCAD isdifferentmodel.

1529completedfixedsingle.25s4.139s/100states/minvol.995513.1530actualfree3
.6s74.160s/240each/minvol>.98995;endobjectspeed4.46mm/s,omegaZ.01661rad/s,
notfinalHolding.1532actualwithdrawal1.2sRUNNING after296.64sforecast/hard420s.
Inspectsummarythenoriginalfull2sgoal.1531software16tests+7SDKhashesunchanged.
No100gfunctionalPASSyet;componentbiasreduction isnotwholephysicalvalidation.
