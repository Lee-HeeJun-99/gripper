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
