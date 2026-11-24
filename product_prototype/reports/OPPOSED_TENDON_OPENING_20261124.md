# Opposite-side route1390–1395 — exploratory no-object opening

StartingHEADa18771f. One new causal change:guide cable point/pullpointnormal
offset+3→−3mm,keeping actualoutboardcoordinates,12Rigidguide frames/masses,
36Railbackfoot anchors,NativeFEM/C2/root/gravity/solver. This replaces thetwo
closingroutes for a matched diagnostic,NOT a simultaneous4cable antagonistic
assembly. OriginalB3/300partCAD unchanged. No object/support/other2fingers in
Nativecoupon;originalcollisionpipeline and retainedSkin/Rail/guidecollision
models stay present. Samegroup selfcollisionpolicy unchanged,NOT certified.

Finiteproxy assumptions:wireR.25mm,guide enclosingR=hypot(1.5,1)mm,solid
supportrodOD.5mm fromRailfootcentroidtoeyelet. Sampled distance plusLipschitz
halfspacing gives initial Skin lowerbounds1390:wire17.1152mm,guide15.8096mm,
support.199427mm. OwnRail joint/bond overlap,eyeletbore/wirebend,assembly and
dynamic interference NOTQUALIFIED. Rodstrength/guideCOM/inertia notmeasured;
oldRigidmass/COM/inertia intentionallyheld as controlled idealbody assumption,
NOT claimed massproperties of a manufacturedbackside support.

1391front/1392back .05s/20outputs complete in.471/.418s. Costforecastfor.6s
uses actualpilot×12×5<120s;child4GiB/120s.1393front/1394back.6s/240outputs
complete3.320/3.219s,mincorevolume ratios.983561/.989130,finite,noSOFAERROR.
Actual1.5N/cable NativeC2 input andlambda=Tdt journalidentityerror0Ns1395.
Geometricshortening reconstructed from actualRigid3 acceptedframes,localwire
coordinatesandfixedpullpoint;not command/internalvalue substituted forlength.
Backendpoint2.00252/2.13589mm;maxinternal-geometricdifference19.3541µm.
Front4.53878/4.84465mm,difference46.7365µm. No newCable/timeconvergencePASS.

1395restunit-force momentalgebra eachcable aboutSkinsection0/30/50mm:
front+3Nmm/N,back−3Nmm/N. Algebra reference,NOT Native measuredmoment.
Native widthmean topSkin endpoint tangent50.6667°rest→83.7657°front vs
34.5011°back. Back outwardTipX+15.4163mm;front−17.9414mm. Actualopening
direction observed inexisting circularrest singlefinger,not prestatedpose.
No actualcontact/100gHolding/Lift/jamming/hardwarequalification claimed.

Nextactualcycle:apply SAME opposedroute to rejected1388nonuniformmanufactured
restshape in NO-OBJECT coupon. Rebuild Native stress-free FEM/Guide-foot/wire
references consistently. ComputevirtualR30insertiongap fromacceptedstate:
noobjectexistsinNative,so gaptestONLY answersgeometricclearance for future
insertion,not contactorHolding. Do notinitializepenetratingactualsphere or
reuse old50gresult. Simultaneousclosing+openingactuators requireseparatefinite
guide/anchor/support/mass checks beforegraspintegration.

Reproduce(newuniquetags only),Pythonrobot_ws:
```
product_prototype/sofa/opposed_tendon_coupon.py --tag NEW_GEOMETRY
product_prototype/sofa/opposed_tendon_coupon.py --native --opposed --tag NEW_PILOT
product_prototype/sofa/opposed_tendon_coupon.py --native --opposed --duration .6 --pilot opposed_pilot1392 --tag NEW_MID
product_prototype/sofa/opposed_tendon_assess.py --tag NEW_ASSESS
```
## Nonuniform manufactured-reference continuation1396–1400

After59b73b7,actually rebuilt1388referenceinaseparateno-objectNative:allFEM
rest/Mechanical/freeSubset/collisionpositions,36guidefoot positions,12body
centroidsandwirepoints/pullpointsupdated consistently. Identitybodyorientation
andoldmass/inertia are explicitidealized assumptions,not a fabricationmodel.
Localmaterialconnectivity/root/nominalthickness unchanged;referencevolume
changesas1388,not exactequalvolume.1396sameinitialSkinproxyclearancePASS;
this doesNOT erase1388sphereinitialoverlapFAIL:noactualsphereexists here.

1397.05s.426s/20outputs;1398.6s3.220s/240outputs,mincorevolume.989995,
finite,noERROR.1400actualresttiptangent53.6297°→39.6107°,outwardtip14.0028mm,
actualshortening2.24033/2.36474mm,Tdtjournalerror0,internal/geometricdifference
21.3843µm. No strictCable/timeconvergencePASS.

1399virtualR30atoldcentre(0,0,−65mm) is GEOMETRYONLY,notNativecontact. Actual
openedSkin trajectory firstclears.2mmenvelopeat.1375s. ALL41savedstates.5–.6s
Skinmargin≥10.7394mm,endpointguideproxy16.8258mm/wire18.3786mm. This shows
singlefingeropeningcreates aninsertionenvelope inactualactuation,not3Finger
synchronization,insertion/Holding orfuturecontactforce. Realfourcableassembly,
wire/supportbores,COM/inertiaanddynamicselfclearance still required.

Nextactualcycle:openingforce release and recovery vs independentzero-force
samegravity reference. ExistingNativeCableSequence hold/release parameters
driveINPUTONLY,not forcedSkinstate. Separatefullruns,no checkpoint transfer.
Do not initialize sphere inmanufacturedrestoverlap orlabelvirtualsphere as
contact. Delayedclosing/fourcableintegration remains aseparatehardware gate.

## Unload/reference-return continuation1401–1404

Afterb11afdd,actually executed NativeC2openingholdtill.6s,release.6–.9s,
observeuntil1.2s.1401actual480outputs4.879s,mincorevolume.989995. Separate
zero-force samegravity/reference1402pilot.338s,1403full480outputs4.715s,
mincorevolume.999967. No statecorrection orcheckpointtransfer.1402preflight
inheritedinputtext says1.5Nbutexplicitforce_N_per_cable=0,zero_force=trueand
actualScene/journals0 authoritative;producertext correctedbefore1403. Preserved
originalmetadata,not retroactivelyedited. Zero-force isreferencecondition,
NOT a fitted material/forcechange to passgrasp.

1404first240rows match1398 EXACT in4film/guide/Skin/Railjournals. This is
same-dtreproducibility,NOTtimeconvergence. Afterrelease121outputsactualCable
impulse0Ns;floatC2commandresidual≤1.67e-15N. At1.2s maxq−same-time-gravity
reference9.48957e-11m,maxv difference5.99516e-8m/s,maxnodespeed6.62278e-8m/s.
Relative displacementdifference6.63076e-7,withoutartificialfloor. Measured
limitedno-objectelasticreturn,NOT materialfatigue/fullRecovery/hardwarePASS.
No objectinsertion/contact/Holding performed. Nextmeasure actualelement
strain/stretches;positivevolumesalone doNOT establishmaterialvalidity.

All commands/source/binary/scene hashes/limits inpreflight,Raw preserved;
actualforcework/rootreaction/wholeenergy NOTMEASURED. SDKunchanged,nopush.
