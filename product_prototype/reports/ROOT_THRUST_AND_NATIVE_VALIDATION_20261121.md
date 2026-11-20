# Root thrust geometry and Native coupon continuation806–830

Finalfunctionalcommitsaff7e9b,f9a3f82.835:60design/softwaretestsPASS2.410s.
Append-onlyevidence:evidence_product_thrust_native_v42/manifest.json,
27newcases/11363files,11050priorimmutablehashesverified0mismatches.
IncludesNaN/timeout,analysisfailures/corrections andlauncherSOFTWAREfixtures;
NOT27physicalPASSclaims. Noactivechildrenorautomaticbackgroundcontinuation.

Baseline2a81fb044200531e52ba51ac2f9fca946b6c7888;oldRaw/SDK/Golden unchanged.
No fullgripper Holding/Lift/time/mesh/energy/productqualification added.

## 1. Root axial stack:physical question and geometry

V36Rootwheelwidth1.8mm insideforkspan2.8mm allowsnominalcenteredwander+/-0.5mm.
Groove0.8mm/wireD0.5mm givesonly0.15mm centeredsidegap. OLD793motion adds a
conservative0.00393598mm axialoffset term. Therefore referencewire clearance
without wheelwander is insufficient;806factorial math keeps effects separate:

|Candidate|Nominal alignment margin mm|ASSUMED error-case margin mm|
|---|---:|---:|
|V36baseline|−0.353936|−0.438936|
|Integral lands only|+0.046064|−0.038936|
|Groove width only|−0.253936|−0.338936|
|Combined|+0.146064|+0.061064|

Error-case bounds are ASSUMED,not measured shop capability:span/wheel/groove
each+/-0.05mm,wireD+/-0.02mm. Combinedminimumaxialgap0.1mm underthese assumptions.
Actualendplay/friction/tolerances/material remainNULL. Old770toleranceFAIL stays.

Config:config/root_thrust_v37.json. Integralannularlands OD2.5/ID1.2 reach
axial+/-1mm and overlaporiginalfork0.05mm. Groove widens0.8->1.0mm;wheelwidth
1.8/OD6/pitchR2 remainunchanged. Thinner flanges introduce an UNVERIFIED strength/
wear tradeoff. Rootthread/head material/retention are stillunqualifiedproxies.

807lands-only6STLs,40.291s;808wide-only6STLs,10.842s;809combined12STLs,42.478s.
Allreadbacksclosedpositive. Same292parts,old18turnpulley/shim assemblies unchanged.
Newwireobstaclehits0;intendedwheelprobecontacts522retained,notclearancePASS.
SixPalmzero-volumeBooleanresults retained.813full24pinsweeps/12bores/18tools
allclear,5.773s. ActualaxialsectionPNG/SVG:results/product_root_thrust_drawing820.
CAD:meshes/b3_root_lands_v37,b3_root_wide_v38,b3_root_thrust_v39.

## 2. Actual Native SOFA:finite wheel–land end stop

New isolatedNativecoupon reuses finiteRootwheel/land subgeometry inSIunits.
Fixedlands,onefreeRigid3wheel;mass0.1g andhomogeneousinertia areRESEARCH
ASSUMPTIONS,not selectedmaterial. Gravity0,mu0,initialaxialspeed+/-10mm/s,
dt0.25ms,duration20ms. No fork/frame/axle/wire/Cable/fullgripper simulated.
NativeEulerImplicit/FreeMotion/BlockGaussSeidel and allTriangle/Line/Point
collisionmodels remainenabled. Existingpassivejournalbinaries reused;NO new
physicsSolverorSDKchange. ActualBinary/SDK/scenehashes inrunmetadata.

810/811:80states each,0SOFAERROR;4.715/4.193s. Actualwheel displacement reaches
~0.1mm stop. Linearimpulse/momentumresidual<=2.43e-27Ns. Publicmass/inertia
matchspecifiedinputexactly (API identity,not materialcalibration). Actual
responseRowimpulses sumexactly tobodyjournal. Contactsource is wheel–lands
inbothmodelorders. Detectoralarm starts0.25ms,firstpositiveresponse10.25ms;
neither isautomaticallycontinuousbirthtime. Nominale=0 referenceevent10ms is
aSEPARATElawassumption;velocityerroratevent0.01m/s remains. No impact/timePASS.

Smallresidualspin andsamplednonemptyCSGresults remain:814endvolumes~4.70e-8 /
3.61e-8mm3. Conservativeglobalplane gap can be pessimisticoutsideannularland.
DoNOTround away tiny intersections or callnumericalresidualphysicalheat.
Full energy/work certificationFALSE.812orderedpaircheck false-negative is
preservedwithcorrection;814unorderedphysicalpairpredicate fixesattribution.

## 3. Failure analysis and installed Native alternative

InstalledGenericConstraintSolverheader exposes scaleTolerance/allVerified.
815/816 explicitlysetscaleTolerance0/allVerified1,same1e-10tolerance. BothFAIL:
43recordedstates,firstNaNat10.75ms.818read-onlyprefixdiagnosis finds one
Line–LineJrownonfinite whilefreeq/vfinite;matchingdetectorpairhascoincident
points. Undefinedcontactnormal is a CAUSEHYPOTHESIS,not directnormalmeasurement
or proofthatiterativeSolveralonecausedfailure. Do notrepeatthissetting sweep.

Bothinvalidchildrenreachedouter480stimeout(exit124)beforeinner480sguard could
writefinalsummary;actualruntimeNULL,partialRawpreserved.823retrospectively
recordsactualfailure,notcompleted80states. HostprocesschecklaterfoundtrialPIDs
gone;requestedkillreturnedNoSuchProcess. Nativefinite_guard.py nowstopsONLYits
verifiedchildafteractualNaN anduses420s internaldeadline,leavingoutermargin.
825finite/nonfiniteCSVfixtures pass launchercontrolchecks;these areEXPLICIT
SOFTWAREFIXTURES,notSOFA/physicalmeasurements. No q/v orforces arecorrected.

817/819 changeONLY installedintersectorLocalMinDistance->MinProximityIntersection
on same strictinitialscene. Allfinitecollisiongeometry retained;nohardware
collision disabled. Both80statesfinite,33.593/33.986s;notuniversalrobustnessPASS.
828exactXMLauditconfirms isolatedclassintervention;actualpositivecaseruntime
7.124xdefaultcoupon. Candidatecounts/data costsincrease;notfreeperformancegain.
827diagnostics showmomentum/API/provenanceconsistent but residualmotion,
reflectiondifferences andnegative conservativegapbounds remain. Negativecase
lastsampleCSG~6.96e-8mm3. No time/mesh/fullenergy/holdingPASS inferred.

822analysisfailedbecauseclonehadembeddedscenegeometry,noseparateSTL.826then
hitMemoryErrorunder4GiBloadinglargeCSVlists (NOTOSglobalexhaustion).827streams
responseaggregationandfirstdetectorrecordfromactualscene geometry:2.94s,
maxRSS280920KiB,exit0. Failures/sourceversionsretained;noinputdatachanged.

ActualNativejournalplot:results/product_root_native_plot821/native_thrust_policy.png;
redline marksNaNprefix,notrepairedstates.830:58design/softwaretestsPASS3.350s,
NOTphysicalqualification. FreeCADCmd/freecadcmd/OpenSCAD andPythonFreeCAD/OCP/
OCC/cadquery recheckedabsent;STEP NOT GENERATED.

## 4. Reproduction and next work

### Independent follow-up832–835:ideal bearing

Afterfunctionalfeatureaff7e9b,installedPartialFixedProjectiveConstraint<Rigid3d>
was actuallyrun withfixedDirections1 1 0 1 1 0. Thisis a NEWideal cylindrical
joint assumption,not a correctiontofreeRigidstates or measuredbearingfriction.
832axialendstop:80statesfinite,21.118s,lockedvelocity/positioncomponents0.
833free-spin:10statesfinite,3.887s,actualomega_z=1rad/s,uncommandedcomponents0.
834independentDOF/APIcheck:analyticalspin quaternionerror3.33e-16,
quaternionnormerror<=2.22e-16,unrestrictedz/spin impulsebalance<=9.41e-38
Ns/Nms. LoadedobserverDLLhashes matchthe frozen332/512binaries. Thispasses
ONLYidealjointDOF/API scope,not material/clearance/friction/physicalbearingPASS.
Projectivereactionwork staysNULL. Bothuse420sfiniteguard;NaNfailure815/816
wasNOTrepeated.835finalregressions include integration-margin/source guards.

Raw:results/product_root_bearing832,product_root_bearing_spin833,
product_root_bearing_assess834,product_root_bearing_regression835.
ReproduceNEWcoupon:

```bash
timeout 480 /home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/root_bearing_coupon.py --tag UNIQUE_BEARING
timeout 480 /home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/root_bearing_coupon.py --tag UNIQUE_SPIN --spin-only
```

NEXT:defineNativeidealwire/pulleyforce-transfer contract and actualbearing/
wirefriction/clearance/material measurements;doNOTsubstitutea body-fixed discrete
guidepointpath for verifiedwire slidingaround a rotatingpulley. V39CAD still
doesnotverifythread/headretention,other18wheelstacktolerances or fullhardware
actuationCCD. Full3Finger adoption andnewHolding requireseparatephysicsGates.

Do NOTstartnextsessionbyrerunning832/833. Implementationentry:
product_prototype/sofa/root_bearing_coupon.py (jointbasis) andrun_native.py
(existingCablegraph),plusinstalledSoftRobotsCableModel. Read-onlyresume:

```bash
rg -n 'pullPoint|cableLength|indices|valueType' /home/ubuntu/SOFA/v26.06.00/plugins/SoftRobots/include/SoftRobots/component/constraint/model/CableModel.h /home/ubuntu/SOFA/v26.06.00/plugins/SoftRobots/include/SoftRobots/component/constraint/model/CableModel.inl
```

Everynew outputusesunique path;source/scene/binary hashes andcommands inRaw.
KeyNativecommands (NEWtags):

```bash
ulimit -v 4194304
timeout 480 /home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/root_thrust_candidate.py --tag UNIQUE_CAD --name UNIQUE_ROOT --mode combined
timeout 480 /home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/root_intersection_probe.py --tag UNIQUE_NATIVE
```

Do not rerun815/816merelytotightentolerances. NextindependentNative task:
idealbearingDOFcontract usinginstalledPartialFixedProjectiveConstraint,
explicitly a NEWjointassumption,not actualradialclearance/friction data.
Then qualificationrequiresrealRootretention/thread/head/material/pullout,
actualwheel/shaft/landcontactfrictionandwear,wireminimumradius,fullframe
force-deflection andnewmechanism adoptionfromNEWinitialstate. Old B3time/mesh
FAILs,50gfinalqualification,100g/Lift/STEPremainopen. Noexitbackgroundpromise.
