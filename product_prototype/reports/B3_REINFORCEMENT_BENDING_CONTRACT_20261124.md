# Matched composite bending diagnostic1379–1381

StartingHEAD31c0512;immutable baseline1298,reinforcement1364. Same curved
originalreference,root material0–5mm fixed,−X total10µN on original100mm
Skin-top nodes,E250MPa/nu.3. No gravity/cable/contact/Guide in BOTH diagnostic
coupons. Important limitation:fullRigidGuide Mapping is NOT certified here;
removed identically to isolate material bending,not hidden as fullB3 test.
Linear methodsmall chosen explicitly for independent CST reference. Baseline
252nodes600tets1g;reinforced312nodes768tets1.085354939g. Added attached-node
mass correctly accumulates at shared parents;not equalmass/volume comparison.

## Actual executions and failures

1379 requests unsupported DiagonalMass templateVec3d;installedNativeERROR
states actualtemplateVec3d,Vec3d. Partialoutputs invalid;FAIL preserved.1380
uses actualsupportedtemplate and canonicalvertexMass data;bothNative20steps
completewithoutERROR in~.24s each. qmaxerrors~2.68e-14/1.60e-14m, vmaxerrors
3.12674e-12/2.14248e-12m/s. STRICT1e-12velocityFAIL unchanged;no tolerance
relaxation or Native equilibrium claim. Independent BE reference is NOT anew
SOFA integrator. Solver/SDK unchanged. Inputs/snapshots/preflight/NPZ percase.

Independent staticcompliance.1049804131→.09279565927m/N;effective stiffness
ratio1.131307368. StaticTip−1.04980413→−.92795659µm. Addedmaterial+8.5355%.
This differs from the1.717–1.722local composite-sectionI algebra and1.953
rail-onlyI;whole taperedcurved cantilever and discreteFEM are different from
a single uniformsection. Do not infer fullgrasp stiffness or normalizedmerit.

1381 read-onlyinventory:reference energies5.24902e-12/4.63978e-12J;halfwork
errors≤4.33e-20J,rootforce~10µN;staticstrain≤1.21e-6,positivevolume ratios.
Shearenergyfractions.70627/.70860 are diagnostics,not proof of uniquelocking.
Native firstvelocityfailure10/12.5ms;earlyfirststep≤2.12e-13. Small accumulated
Native/reference discrepancy is not evidence ofphysicalheat orgraspfailure.
Actual Native energy API,wholeenergy,dampingwork NOTMEASURED.

Dynamic1370 mixed3fingerresponse and persistent100mmcontact are compatible
with modestreference stiffnessgain not guaranteeing usefulcontactgeometry.
No newforce/pad/width sweep orfullgrasp launched from thislinear diagnostic.
Next independenthypothesis:coordinate-origin sensitivity of smallNative
linearresponse,physicalsamecoupon translatedasawhole. This isNOT a proposed
objectstate correction or productiongrasp fix. KeepstrictcomparisonFAILs.

Reproduce withunique tags only,Pythonrobot_ws:
```
product_prototype/sofa/reinforcement_bending_contract.py --tag NEW
product_prototype/sofa/reinforcement_bending_inventory.py --tag NEW_INVENTORY
```
Inventorycurrentlyreads1380explicitly;inspectbeforeusingnewsource.
## Follow-on actual cycles after15ccb67

1382 translates BOTH entirelinear coupons bytheoriginalcorecentroid,no object
or productionstate correction. Nativepositionerrors9.12e-15/4.59e-15m;
velocity1.32662e-12/7.78144e-13m/s. CombinedSTRICTFAIL persists. Coordinate
origin influences tinyroundoff;not a demonstrated generalphysicalfix. Stop
originparametersearch,do not alter actualB3position or productiontolerance.

1383preserves actual guides/freeSubset/root and addsConstantForce. Missing
MechanicalLoad factory causesFAIL;partialstate notperformance.1384 declares
installedplugin explicitly and completes20steps forBOTH. Same originalguide
XML asserted exactly. No object/cable/contact/gravity,smallFEM only. Positive
savedcorevolumes;transienttiposcillation,NOTequilibrium stiffness ratio.
Unlikeguide-free1380,1384retains originalmass/stiffnessRayleighcontract.
Thus do not compare those timehistories as a pureGuide-only physicalcontrast.

1385 independent pullbackJ=[I,−cross(r)] fromactual12Rigidguide owners and
originalSubsetindexPairs;root72DOFs plus24newrootDOFs retained. Mappedstatic
referencegain1.126480537,Tip−1.02730137→−.91195661µm. Virtualworkerror2.02e-28J,
energy-halfworkerror≤3.58e-20J. Infinitesimalworldrotation only,NOT Native
nonlinear tangent/geometricstiffness or NativeenergyAPIqualification.

1386actualstockStaticSolver ontheexactsmalllinear1380coupon,2requestedsteps,
25Newtonmax andstrict1e-12unchanged. BothstopatactualLineSearchfailure,one
savedoutputonly. Lastqclosetoreference(~9e-15m)BUTfreeforceresidual~1e-9N.
BaselineNativeNewtonresidual4.83521e-9N atiteration11;lineSearchFAIL. Do not
certifyequilibriumorNativeEIfromthis. No Solverparametersearch performed.
New shape/grasp candidate isdeferred:thelimitedreference stiffnessgain does
not establish a reliablemapping fromsectionI todynamiccontactdistribution.

Transitiontoindependentvariable-stiffnessmeasurementingest/protocol tooling;
actualpressure/friction/material/hardware data remainNOTMEASURED. This avoids
repeatingNativeprecisionfailures withoutanewcausalhypothesis.

## Next-mechanism actual implementation afterbc17cc2

1388implementedone nonuniformcurvaturecandidate,not anotheruniformangle/start
sweep:phi(u)=40deg*(2u−u²),same70–100mmspan,total40deg,root14deg/radius50,
samewidth/thickness. Earlierinwardtangent intended toadvance contactawayfrom
100mmtip. Existinggenerator exactlymatches originalNativecoordinatesbefore
newlaw. Actualtriangle/spheregate:all3fingers−1.5831497mm initialgap atmaterial
96.278mm. Reference tetspositive,volumechanges−.02414%explicit,notexactequal
volume. REJECT beforeGuide/Wiretransform orNative;STLsreferencecandidateonly,
notobserveddeformation. No oldgeometrychanged. Tightermanufacturedrestshape
needs a realopeningmechanism beforeinitialR30placement. Do notdisablecollision,
prescribeopenSkinorforceobjectmotion. NextREADY opposed_tendon_opening_feasibility
inno-objectsingleFinger;current2edgeclosingtendonsarenotopenactuatorproof.
Actualhardware/pressuremeasurementsremainBLOCKED.1389finalregression44tests
PASS/7SDKhashesunchanged supersedes1387softwarecount,notphysicalcertification.

Child4GiB/30s;forecast5s perNativecoupon. No newphysicalmaterialmeasurement,
time/meshconvergence,100gHolding,Lift,jammingorhardwarePASS.
