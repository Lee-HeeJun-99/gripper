# Actual finite wire contact and100g goal continuation

Start41f15b0 clean. No old Raw/SDK changes. Initial target:100g/R30/gravity9.81,
mu.3,1.6–2s slip≤2mm,speed≤5mm/s,supportgap≥5mm,force≤1e−5N,Guide/Rail
load excluded and positive savedFEM elements. Existing time/mesh FAIL unchanged.

## Finite wire component cycle1426–1432,1436–1437

Implemented `native_wire_eyelet.py`:stockBeamAdapter,Euler/FreeMotion/BTD,
actual0.25mm-radius16-sided tube and actual eccentric eyelet1416. E2GPa/rho1000
ASSUMED. Zero friction isolates sliding availability,not realfriction performance.
1426missing plugin load orderingFAIL;1427obsolete Collision factory aliasesFAIL.
Correct aliases1428executes,but surface collapses to x0;not contactPASS.
Explicitcurvilinearpoints1429stillcollapses.1430beam-index coordinates produce
correct20mm surface;no contact at earlier small load. Actual SDK base mapping
coordinate behavior is not proof all BeamAdapter mappings are unsupported.

1431 uses outward surface winding and0.4mN transverse load:independent Euler
midpoint54µm versus initial42µm gap motivates actualcontact loading;not gripper
tension tuning.20ms/200states,2.616s runtime,186activeconstraint outputs.
1432 axialfree-root+0.1mN axialtraction adds sliding;both boundary/load changes
explicit,not a one-variable performance claim.200states,2.719s,119activeoutputs.
1436 actual existing read-only provenance observers repeat1432:states.csv EXACT
before/after observer. Actualpairs finiteEyeletLine–wireLine and finiteEyelet
Triangle–wirePoint;responseimpulse partitionerror0. OriginalNativeλ Ns divided
by100µs for force;maximumresultant1.8918mN. Rootaxialmotion5.224993mm.
1437 initialvertexsolidgap.041607mm,minimumsavedvertexgap.002039mm in sliding
trial. Positive VERTEX gaps do not certify continuousfacets/wholewire clearance.
No physicalfriction/material/mesh/time/energy or wholefinger/graspPASS.

## New100g exploratory candidate1433–1439

P1 does not block P0. Implemented `nonuniform_grasp_candidate.py` on old1298
idealjoint Native model (NOT latest finitehardware). Newstress-free manufactured
phi=40deg*(2u−u²) on70–100mm. Preserve1388initialoverlap−1.58315mm atroot50.
Derive necessary rootradius by initialgap solve,not randomradius performance
sweep:53.175623656mm yields≥.30mm Skin/wireR.25/actualguidesphere clearance.
Root14deg,original1.5N/cable/gravity/mu/100g/sphere/support unchanged. Coupled
profile+requiredplacement change,not isolated profile efficiency proof. Guide
anchors/freeDOFs/collisionrefs/tendonroutes allrebuilt;original assigned masses
and idealguideinertias retained research assumptions,not measured newhardware.

1433serializationFAIL beforeNative retained.1434 actual.25s27.672s,100outputs
eachfinger,positiveelements.1435 actual.6s49.164s,240outputs,positiveelements.
Measuredforecast327.76s permits2s under420s/4GiB.1438 actual2s125.205s,800outputs
each,minvolumeratios.984871/.984985/.985568. No error/no inverted savedtet.
Original protocol plusGuide/Rail exclusion and1e−10Ns momentumcheck stored
BEFORE fullrun.1439 actualfullfunctionalFAIL:slip40.04035mm,speed.323115mm/s,
supportgap.200000mm,meanSkinFz−.167911N,Support+1.148908N,Guide/Rail0.
Partitionerror8.67e−19Ns/Nms,holdmomentum residual4.34e−19Ns. ActualSkin
detector outputs exist but wrong supportingforce;no success from immobility on
support. Solvermax1001. This coupledrest-profile candidate is REJECTED;no rerun.

Next independent P0 hypothesis:form contact with calibrated force input then
hold actual geometric cable length using Native displacement input. Motor-like
length retention,not increased prescribedtension. Needs input-only controller,
small coupon transition/geometry verification and no q/v resets before100g.
No promise that this will solve contact/FEM/time failures.

Commands (unique NEW tags,do not rerun unchanged failed settings):
```
python product_prototype/sofa/native_wire_eyelet.py --tag NEW_WIRE --slide --audit
python product_prototype/sofa/wire_eyelet_assess.py --tag NEW_INVENTORY
python product_prototype/sofa/nonuniform_grasp_candidate.py --tag NEW --native --duration 2 --pilot nonuniform_contact1435
python product_prototype/sofa/grasp_goal_assess.py --tag NEW_ASSESS --case nonuniform_hold1001438
```
Per-case source/Scene/binary hashes,commands,Native q/v andprocess limits retained.
Pressure/contactarea/realmaterial/joints/hardwarestrength NOTMEASURED.

## Input-only motor-length experiments1441–1460

New separate plugin source `sofa/cable_latch/` only reads accepted guide positions
and writes public CableConstraint.value/valueType. No q/v/forcefield/ODE writes.
Unique builds1441/1447/1454;all older binaries unchanged,actual compiledsource
snapshots in Nativecases.1443/1444straight80steps:heldgeometryerror0.1446cross-
sibling earlybwdInit check FAIL. Same strict1e−12 check moved to FIRSTBegin
before any dynamics;1449straighterror0,not tolerance change.

1450singleFingeractual.8s320states3.312s,minvolume.98356.1452all4journals first
240rows EXACT vs1393;straight39rows EXACT vs1443. Firstlatch.6025s captures
previousaccepted.6s actualpath (floating publicclock,not shiftedafterward).
SingleFEM geometricerror6.4374e−11m FAILS1e−12 inventory;not a newstrictPASS.
1451actual3Finger1.2s59.837s,positiveelements;holding beyond1.2 NOTMEASURED.
1453endpointdownward12.356mm from1s,speed137.512mm/s,SkinFz.734029N,
Support.146570N,maxemergentCable1.788953N. Poorwithdrawal,not fullHoldingFAIL.

One further input hypothesis uses actual no-object1393/.6s closure targets
4.538775/4.844649mm from1452,not a randomstroke scan. OptionalC2 input from
.6to1s andthenhold;coupon1456error1.735e−17m.1457singlepositive,same max
no-object posture. Its inheritedpreflighttext lacks ramp flag;actualScene is
authoritative,producerfixed BEFORE1458.1458actual1.2s60.338s,positive minvolume
.97585 butactualgeometriccommanderror2.992797mm,peakemergentCable2.127902N.
1459endpointdownward12.0337mm,speed169.640mm/s,SkinFz.724651N,Support0.
1460first240rows4journals EXACT baseline1298. Contact/unresolvedcoupledCable
contract remains;do not blame a unique cause or promote command as actualmotion.
REJECT this heldlength/ramp family rather than run costly2s with unqualified
actuation. Full1.6–2sHoldingNOTMEASURED,not fabricated asFAIL/PASS.

## Next independent approach-pose hypothesis1461–1462

No material/force/friction/pitch changes. Original1298 shape,100gobject/support
stay fixed. Derive initialgripper z shift so90mmSkin centre is at spherecentre
z−.85R;90mm is the existing penultimateguide station,leaving distal tail for
potential lowerhemisphere wrapping. .85 is declared design direction inspired
byold50g favourable normals,not a new measurednormal. Shift−5.037385900mm.
All three root/free/guide/collisionreference coordinates andpullpoints translate
equally,not object q/v. Relativegeometry/mass/Rootradius50/angle14 unchanged.
InitialSkin/wire/guide gaps3.835010/10.453746/8.900971mm.1461actual.25s3.431s,
positiveelements;1462actual2s launchedunder420s/4GiB after137.23sforecast.
Assessactualcompletion andoriginalfunctionalprotocol before claiming outcome.

1462 completed actual2s143.334s,all800/fingerpositive/minvolume.98466.1463
HoldingFAIL:slip40.01205mm,SkinmeanFz+.076490N,Support+.904511N,Guide/Rail0,
gap.2mm;momentumerror4.34e−19Ns. Finite contactdirectionnot sufficientforce.
Do not search neighbouringinitialheights.1464eightsoftwaretests+7SDKhashesPASS.

## One measured-load-sizing hypothesis1465–1467

After two structural/pose hypotheses and two length-control hypotheses failed,
explicitly separated actuation capacity from mechanism improvement. Reused1298/
1306actualSkinresponse in SAME.55–.65s prewithdrawalwindow(41samples):mean
SkinFz.692369855N at1.5N and.937472988N at2N,both below.981Nweight. Local
secant.490206267N/N and declaredengineering reserve10%(assumed,not calibrated)
giveONE preregistered2.2889130997N/cable candidate for1.0791NearlySkin support.
Distinct dynamic shapes mean this is ONLY a hypothesis,not a linearity proof.
Old2NFAIL,original2.5Ninterfaceinversion andstop-force-search evidence preserved;
this experiment is load-sizing under railback joint with independent2.5N
no-object1129positivevolume evidence,NOT that old invalid interface model.
No additionalincrements if rejected;not structural efficiency or motor spec.

1466actualsingle.8s3.174s/320outputs,minvolume.853221,Nativeforcecommandimpulse
error0. This is a real safetyPilot,not monotonic-stability inference from1129.
1467actual3Finger1.2scontacttrial started after conservative190.43sforecast;
readactualsummary beforeanyfull2srun. All originalgeometry/1.5Ncomparators and
physicalFAILs preserved. No100gPASS yet.

## Actual load-sizing failure and new conformal mechanism1468–1482

1468 full2s263.546s/800states each,forcecommanderror0,positive savedtets
(minratio .61650/.84331/.72628).1469actual HoldingFAIL:slip205.847mm,
speed1735.522mm/s,Guide/Railpeak .846/.973N;Supportloaddominates. Stop old
geometry force-sizing family;no additional force increments.

1470 new manufactured stress-free distal circle: innerSkincentreline radius
30.5mm aroundR30,70–100mm span gives56.172333deg. Rootradius46.625582mm and
zshift−4.482109mm follow circle tangency at unchanged14deg rootangle.
All FEM/reference/collision/free/36footanchors/cablepath coordinates rebuilt,
not prescribed dynamic wrapping or object relocation. Discretevolume ratio
.9997168,assignedmass/idealGuideinertia retained and explicitly NOT realdensity
or bodyCOMqualification. FiniteWireR.25/GuideproxyR1.802776 retained. Shared
120deg eroded-sector lateralcap givespositiveinitialinterfingergap;not dynamic
fullhardwareclearance. InitialSkintriangle gap.398266mm,not penetration.

1471/1472actualfixedsingle .25/.6s showedGuide-first collision,lateSkincontact
lost. Rejected minimalroute. Dorsalterminalcorrective design places98mmanchor
on existingrailbackplane−.5mm;all collisionradii,bodyDOFs andFootattachment
retained.1473/1474 fixedsingle .25/.6s keep realSkinresponse,positiveFEM.
FixedobjectprojectedJacobian isNOT totalreaction:reaction NOT MEASURED.

1475 actual3Finger1.5N .6s118.731s,240states each,minvol>.98893. Endpoint
SkinFz .947838N,Support .033382N,Guide/Rail0,not finalHolding. Runtimeforecast
blocks immediate2s under420s,so1479actuallyruns1swithdrawalpilot instead.

ONE hybrid reuses EXACT frozen1465 input2.2889130997N with new conformalshape;
not another forceincrement or isolatedstructural-efficiencyclaim.1477single
.25s4.113s/minvol.992179.1478free3 .6s98.392s/240each,minvol>.97664.
1482 actualendpointSkinFz1.070200N,Support/Guide/Rail0;allthreeSkincontribute
.328891/.396638/.344671N. Objectspeed42.254mm/s soNOTHoldingPASS. Nativeforce
impulsecommanderror0,partition4.34e−19Ns,momentum8.67e−19Ns.1481actual1.2s
withdrawalpilot RUNNING,forecast393.57s/hard420s/4GiB;inspectsummary beforeany
fulltest. No100gPASS yet.1480twelve softwaretests+7SDKhashesPASS,notphysics.
Newtestfixture first failed(nonexistentcentrelinenode/wrongresultbasename);
fixed test to actualwidthmeans andactual1469path,not alteredmodel/tolerance.

## Full conformal results and equatorial-entry follow-up1483–1491

1479actual1s159.698s/400states each,positiveFEM. Comparedcompleted1475 .6s
with1479:fouracceptedstateprefixjournals EXACT. Startup/fullprefixcost paid
once plus2x measuredmarginalcost(.6→1s) predicts364.534s for2s,hard420s
unchanged.1483actuallycompleted2s225.528s/800each,minvol>.98878.
1488 originalgoal FAIL:slip3.627230mm/speed58.371070mm/s exceeds2/5 limits;
gap37.02758mm,Support/Guide/Rail0,SkinmeanFz.972520N(weight.981). Noinversion.
Nearly balancedverticalsupport isNOT stableHolding.

1481hybrid1.2s124.382s/positiveFEM;1485inventory,notHolding.1484full2s
163.064s/800each completed.1487FAIL:slip.767901mm passes butspeed82.288622
mm/s fails;Guidepeak.875138N supportsmeanFz.201151N,soalsohardwareexclusion
FAIL. SkinmeanFz.785012N,Support0,gap43.79394mm,positiveFEM;Nativeforceinput
error0,momentum6.78e−19Ns. Maxobjectangularspeed19.361rad/s/rotation179.86deg
from1s reported,not hidden. Reject both theseconformalvariants,notmoretension.
1490actualRaw scientificcomparisonPNG(source/Rawhashes),not conceptualwrap.

Newequatorialentry hypothesis preserves EXACT distalspatialpositions70–100mm
(test<=1e−10mm) and1.5N input,butadds side-facing proximalSkin. Replace14deg
tangent byvertical0deg tangent,derivecurveonset70−30.6*radians14=62.5230095mm;
terminalangle70.172333deg unchanged. Rootradius30.6mm,z−2.4769905mm follow
circle,not a randompitch sweep and not strongerfriction/material. InitialSkin/
wire/Guidegaps.398266/5.162524/3.609748mm,interfingerGuidegap1mm. Allfoot/
free/collisionreference/cablepositions consistent. Initialobjects never moved.
Referencevolume .99966937xold,assignedmasses retained as explicitidealization.
1489actualfixedsingle.25s6.126s/100states,minvol.994828. It is NOT Holding or
totalfixedreaction measurement.1491actualfree3 .6sPilot RUNNING;readsummary
beforepromotion,uniqueoutputpath. Originaltime/meshFAILs andoldRawunchanged.

## Actual equatorial result and width mechanism1492–1505

1491actual.6s148.384s;1492actual.8s164.480s/320each/minvolume>.98709.
Fouracceptedprefixjournals EXACT,marginalcostforecast357.63s/hard420s.
1496actuallycompleted2s274.555s/800each/minvol>.98709.1502goalFAIL solely
speed69.04364mm/s;slip.795230mm,gap41.81805mm,SkinFz.984012N,Guide/Rail/
Support0,actualinputerror0,finite/normalcompletion. This improvesvertical
retention butNOTstableHolding.1500NativeDetectorpoints nearestacceptedSkin
material inventory(.5–.6s):below70mm193/2642old vs635/2771equatorial,minimum
materialx65→55mm. Stagemismatchsurfacegapmax.2168/.2848mm explicit:NOTexact
load-bearingfraction/contactarea or forceassignedtodetectedsamples.

1493/94/95/98workinventory usesactualforceNs/dt andacceptedgeometriclengths;
previous-chordwork isindependentlyreconstructed,NOT observedSDKstagework.
Hybrid1495maxsavedGuidepointjump10.5865mm/2.5ms,previouschord-vs-geometric
cumulativeworkdifference182.982J;1501actualRigid3maxomega~159.94rad/s atbody8.
This isconcretehigh-inputmechanism/couplingwarning,not uniqueenergycausalproof.
Base1.5Nworkdiff.00046568J,Guideomega~5rad/s. FEMstrainenergy/frictionloss/
globalenergyresidual remainNULL. Prior1152criticalFootspan5→10mmalreadyfailed;
reviewed1152–55anddidNOTrepeatit.1499software12+SDK7identityPASS,notphysics.

Nextone-variablewidthhypothesis:REMOVE24→12taper,retain24mmwidththroughout,
sameequatorialcentreline/railwidth/thickness/material/T1.5/mu. Motive:increase
transverseSkinspan andrail torsionallever,notforce/Young/damping search.
CorrespondingrailbottomfootcoordinatesandGuides remainconsistent. Actual
newcorevolume/mappedUniformMassratio1.072776088 vs SAME taperedcircle;
not equalmaterial/mass efficiency. Hardwaremasses/inertias unchanged. Generic
geometryscope's retainedmass clause isoverriddenbyexplicituntaperedrecord and
actualSceneUniformMass=.001072776088kg;not freeNode.1503producerincorrectmass
NodelookupFAILED beforeNative;originalproducer/failurepreserved.1504fixedonly
Nodelookup,actualsingle.25s3.052s/100states,minvol.99524. Coreinitialsector
margin2.95935mm positive;allGuidecollisions retained.1505free3 .6sNative
RUNNING,inspectsummary beforepromotion. No100gPASS. NooldRaw/SDKchanges.

1505completed.6s57.331s/240each,minvol>.98851.1507actualendpointSkinFz
.995004N,Guide/Rail/Support0,speed19.0294mm/s;NOTfullHolding.1506actual2s
launched after382.20sforecast/hard420s,4GiB.1508software12+SDK7identityPASS.
Readactual1506summary thenrunnewgoalassessment. Sceneanduntaperedrecord
explicitlyoverride generic retainedmass clause;coremappedUniformMassscaled,
allGuidehardwaremasses retained. Nootherpropertyorinput changes.

## Width fullresult and deterministic actuator sequencing1506–1512

1506actuallycompleted2s123.927s/800each,minvol>.98851.1509goalFAIL solely
speed29.774142mm/s,improvedfromequatorial69.04364. Slip.979002mm,SkinFz
.985416N,Guide/Rail/Support0,gap41.11804mm. Retainmechanismimprovement but
NOTHoldingPASS or equalmass efficiency;corevolume/mass increased7.2776%.

Next independent hypothesis changesONLY input timing:finish originalquinticC2
force ramp atactualSupportwithdrawalstart1s(keyTimesfirstmoving−previoushold
end plusdt) insteadNativeCableSequence default.5s. Same1.5Npeak,hold2/release2.5,
Supporttrajectory/hold1.6–2/geometry/material/constraints/solverunchanged.
Maximumforce slew5.625→2.8125N/s iscommanddesign,NOT measuredmotorlimit.
Motive:limitinitialbendingexcitation,not anotherforce/dt/damping sweep;ONE
preregisteredtimingcase,notadoptednumericalrepair. FinalholdingTunchanged,
preclosureinputworkdifferssoNOTisolatedstructure-efficiencycomparison.
1510single.25s2.310s/minvol.99900.1512normalizedScenes vs1504EXACT except
closing(.5→1),analyticC2commanderror2.78e−17N/Nativeimpulsecommanderror0.
Only100sampleinputcouponPASS,notgrasp.1511actualfree3.6sRUNNING;readsummary
beforepromoting. NoSDK/sourcebinaryupdate needed(publicNativeinputDataonly).
