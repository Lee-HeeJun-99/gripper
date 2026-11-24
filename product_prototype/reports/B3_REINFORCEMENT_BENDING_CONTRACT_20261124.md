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
Child4GiB/30s;forecast5s perNativecoupon. No newphysicalmaterialmeasurement,
time/meshconvergence,100gHolding,Lift,jammingorhardwarePASS.
