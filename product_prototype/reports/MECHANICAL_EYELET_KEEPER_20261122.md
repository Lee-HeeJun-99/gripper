# Mechanical Eyelet keeper continuation — 2026-11-22

Baseline3212e14. Old evidence/SDK preserved. ONE second Root guide only.
892 replaces unselected bondline by finite split housing,axial stops,cover and
two screw/nut proxies. Same Eyelet D3/length2mm retained. Connected lower support
and all6new STL bodies valid;FAIL rootwheel overlaps.576637/.132136mm3.
893 moves tabs opposite measured Root direction in composed keeper frame;
tiny positive.000552091mm3 remains:FAIL retained,not rounded toclear.
894 additionally changes physical rootward wall.55→.45mm;no static intersections.
This is a new geometry/strength assumption,NOT tolerance relaxation. Wall strength,
fastener grade/preload/thread/form/process capability remainNULL/unqualified.
Full286parts;oldsecondbond removed ONLY with real mechanical replacement.
FirstRoot unselected bondline and translated Skin attachments still unqualified.

896 actual .45mm wire envelope through second Root/turns/drum:no unresolved
obstacles,25.901s. Originalscope erroneouslysaid282parts;actualhashedrecipe286
was fully evaluated. ExplicitCORRECTION.json preserves originalsummary and
clarifiesmetadata only. Producer now records actualpartcount. No geometry/result
changed or old verdict rewritten.
897 finite service sequence:2exacthexnut−8mm sweeps with screws retained,
2exactsteppedscrew+8mm sweeps after nutsremoved;cover/Eyelet7sampledpositions each.
18records nohits,6.355s. Not continuouscover CCD/actualhand/thread/toolproof.
Unloadactuator/unthreadwire BEFORE Eyeletservice;hardware-only scene.
898 actual CSG axialtranslations:0/±.05mm clear;±.15mm creates~.136mm3
interference perhalf,demonstrating geometric stops only. At±.1mm finiteprecision
face fragments retained. y0drawing lies in splitgap;notcompleteassemblyvisual.

## Actual Native SOFA895 and independent audit899

NEW Native coupon reuses installed FreeMotion/EulerImplicit/BlockGaussSeidel/
MinProximity/FrictionContactConstraint(mu0),not a customsolver. Actual894 keeper
6solids ideallyfixed,actualEyelet freeRigid3,assumeduniform100mg,gravity0,
initialaxialspeed+10mm/s. Sharedrigidframe+COMrecenter preservesrelativeCAD.
80steps×.25ms=20ms,273.135s actualruntime,4GiB/420schildguard. Finite states,
noSOFAERROR,nonzeroactualcontactimpulses. Maximumaxialtravel.100000019704mm.
This is NOT actualfastenerpreload/materialstrength or exactimpactlaw.
Actualscene/SDK/binaryhashes/command/publicmass/journals in895.

899 streamsactual92nonzeroResponseRows across4modelpairs:support/coverTriangle
vsEyeletPoint andLinevsLine. Their totalimpulse matches80accepted mΔv with
maximum1.48108635e-28Ns residual at declared5e-12Ns narrowdiagnostic criterion.
RigidJournal andResponseRow sums differ0. Earlier partial inspection of a
zeroimpulse reststep was NOT a journal/physicsbug;fullaudit resolvesit.
Noangularmomentum/wholeenergy/impactrestitution/time/mesh/realjointqualification.
Opposite-direction Native coupon NOT RUN (CAD stops testedboth directions).
~74MBresponse/~542MBdetector journals retained;do not repeat costly unchangedrun.

Reproduction with NEW outputtags only:
```
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/eyelet_keeper.py --tag UNIQUE --outboard-tabs --rootward-wall .45
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/eyelet_keeper_service.py --tag UNIQUE_SERVICE
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/eyelet_keeper_coupon.py --tag UNIQUE_NATIVE
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/eyelet_keeper_audit.py --tag UNIQUE_AUDIT --case product_eyelet_native895
```
NewNative requires newhypothesis,not automatic repeat. Modelmass/preload are
researchassumptions,not measured data or oldB3adoption. No50g/100g/Lift/STEP/
fabrication/time/meshPASS. Next:complete readable keeperCAD/BOM/servicepack,
then address translated Skin attachment/actualjointandmaterial qualification.
