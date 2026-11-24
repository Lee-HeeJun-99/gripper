# Finite contact-layer hypothesis —2026-11-24

Baseline1298 is100g/1.5N,cable terminal98mm,rail-back joint. It is NOT the
new300partCAD. Terminal-only1326–1333 did not spread material contact.
This candidate adds a separate20×tapered-width×0.5mm layer at80–100mm.
40nodes/72tets,perfect bond at20existing Skin top nodes,20free upper nodes.
E1MPa,nu0.3,rho1000kg/m³ are HYPOTHETICAL sensitivity values,not measured
silicone/PET and NOT a layer-jamming law. Added mass142.493mg/finger;not an
equal-material-volume efficiency comparison. Existing Skin/Rail/hardware
masses,geometry,cable commands,friction0.3 and object0.1kg remain unchanged.

1336 initial limited geometry:pad/object gap0.899644mm,own finite guide proxy
gap15.685mm,signed tet determinants positive. Bottom coordinates match actual
Scene Skin nodes to1e-15m. STL is reference geometry,not accepted deformation
or STEP/fabrication approval. Whole dynamic hardware clearance NOT QUALIFIED.

1337 added separate pad collision models while retaining old Skin/Rail models.
Actual Native abort153.679s,exit−6,`nonfinite native state`,zero saved outputs;
660Null-distance warnings. FAIL,not a successful0.05s run. Forecast30s was too
optimistic;no full grasp expansion. Old scene,logs and producer preserved.

1338 isolated linear fixed-bottom layer coupon:no contact,cable or moving
parent;20steps/0.05s,actual0.136s. Same geometry/material/mapped UniformMass.
Independent CST+BackwardEuler reference:positionerror0,velocityerror2.74e-15m/s,
fixed-bottomerror0. PASS_LINEAR_MAPPED_COUPON_ONLY,NOT B3 qualification.

1339 one-step and1343 twenty-step B3 no-contact CONTROLS remove only collision
pipeline to isolate FEM/mapping.1343 completes0.05s in0.906s,bondpositionerror0,
minimum layer volume ratio0.999808,Skin/Rail0.999909. These are not Holding,
nor proof that contact alone is a unique cause;other coupled paths remain.

1340 export attempt failed BEFORE valid dynamics:VTK plugin was declared after
components.1341 moves declaration first;Native one no-contact step exits0,
but original producer expected`.vtk` whereas actual exporter writes`.vtu`.
Both original FAIL records are retained. VTU declaresFloat32 with limited text
precision;it must not replace STRICT1e-12 State API validation.

1342 frozen1242post-build observer reaches15s bound before any event data.
BLOCKED_NO_FIRST_SYSTEM_DATA,not an accepted state or observer purity PASS.
1344 extends EXISTING Observer with optional`atCollisionEnd` detector-only phase;
default remains old BuildConstraintSystemEnd behavior. New build path and binary,
old1242source snapshot/binary unchanged,SDK untouched,no ForceField/solver added.
1345 on baseline first step:all9journals exactly equal1298,3features.1346 captures
5286first CollisionEnd features,including thousands of own bonded Skin/Rail–pad
pairs. Its15s timeout and zero accepted state remain partial diagnosis,not a
new physicsPASS or proven unique cause. No child Jacobian exists at this phase.

## Exterior-union correction hypothesis

Perfectly bonded material interfaces must not be independent unilateral contacts.
New exterior is derived from the original Skin/Rail AND pad tetrahedra,identical
bond nodes welded by index. Exactly24shared interface triangles cancel.
ALL other original exterior triangles remain;new pad top/side surfaces remain.
All exterior edges must have incidence2. Hardware/object collision unchanged.
This is a physical boundary representation change,not Guide/object collision
deactivation. Material-face labels are retained;combined contact is NOT labelled
bare-Skin load without a face/row provenance analysis.

1347 producer NumPy-int serialization FAIL before Native,retained.1348 repaired
producer starts bounded0.05s test;actual result is in its separate summary.
Native journals/scene/binary hashes and commands are per-case preflight/process.
Run only unique new tags,never reuse these paths.

1348 exterior-union control completes20steps/0.05s in1.516s,all original and
pad saved volumes positive,bonderror0. This supports the internal-interface
correction hypothesis for startup only,NOT unique causality or final contact
qualification.1349 correctly reads1341VTU:coordinates equal six-significant-digit
reference text,absolute errors≤48.73nm;not a strictAPI PASS.1340/1341 original
producer FAIL records retained.1347 has no complete preflight/source snapshot
because producer stopped before writing them;source identityNOTCAPTURED,not a
Native physical experiment. Do not invent the missing artifact.

1350 checks each new pad against ALL Native fingers/layers,all36finiteguide
proxies and36wire-segment capsules:conservative lowerbound margins≥19.405mm
otherfinger,15.685mm guide,10.116mm wire. SameSkin bond intentionally shared.
Missing productionCAD support/clamp/palm solids and dynamicclearance NOTQUALIFIED.
1351 contact-entry0.6s forecast72.756s from actual1348×12×4;child420s unchanged.
Later-duration pilot guard requires same exterior-union/contact-control modes.

## Completed contact entry,withdrawal and mechanism diagnosis

1351 completes0.6s/240outputs in52.489s.1352 completes1.2s/480outputs in75.313s
(forecast209.957s). All saved Skin/Rail/layer volume ratios positive;minimum
layer0.973086,Skin/Rail0.985760. Perfect-bond positionerror0. No ERROR. These
are bounded finite-state observations,not strain-limit/time/mesh qualification.
At0.6s composite Fz0.71853N versus old bareSkin0.68968N;different added mass,
material and exterior,not equal-volume efficiency. At1.2s compositeFz0.66122N,
SupportFz0.219394N,objectspeed137.286mm/s,objectz−77.5581mm. This does NOT show
unsupported100gHolding. Full1.6–2s protocol NOTMEASURED for this candidate;
do not label a partial horizon as full HoldingFAIL/PASS. No100gLift.

1353 frozen1242observer reuse(no rebuild) completes0.6s in50.484s;all9journals
exactly equal1351 over240outputs.1354 unique93normalrow joins.1355 all8active
Point/Line contacts map to the added layer atmaterialstation100mm in sampled
previous-times0.595/0.5975s. No unmapped rows. Line endpoints are matched to a
UNIQUE actual geometric boundary edge at1e-12;Native generated edge ordering is
NOT assumed. No distributedmaterial-contact claim. Pure layer points are NOT
reported as bareSkin force;shared-interface attribution would remainAMBIGUOUS.

1356 new analysis assumedtotalMass but actualsphere usesvertexMass;producer
schemaFAIL before output,source snapshotNOTCAPTURED.1357 corrected analysis
checks actual normalized spherical inertia. Linear/angular momentum residuals
2.17e-18Ns/8.05e-21Nms;responsepartition8.67e-19Ns. Inventory-onlyPASS,not
time/mesh/energy/physicalqualification. Solver reaches1001iterations earlier.
Support load is actualNative response,not a guessed balance residual.

1358 frozen normal-ray diagnostic uses actual pad bottom/top and actualsphere
center at0.6/1.2s,plus manufactured initial clearance budget.40rays intersect;
30rest-equivalent thicknesses exceed initialbudget under the frozen-stretch
assumption. Atstation95mm,1.2s neededrestthickness~3.18/3.42mm versus initial
budget1.706mm. Changing a profile changes mechanics,so this is NOT a global
impossibility proof or fabricated manufactured pad solution. No thickness sweep.

1359 renders/inspects actual unamplified Native projections at0.6/1.2s,with
actualsphere positions;not conceptual Wrapping or contact-area visualization.
1360 width-mean radial-Z decomposition shows finger0tip-angle60.079→51.901deg
while proximalturn−0.656→−8.037deg;about90%of this projected angle loss is in
0–70mm proximalspan. Distal/junction decomposition separately stored. The old
1298model shows similar behavior. This is coarse-model diagnostic evidence,
NOT proof of physical cause,an intrinsic shell-curvature measure or permission
to increase stiffness arbitrarily.

Disposition:finite uniform layer fails the distributed-contact hypothesis in
sampled windows;do not extend this family by force/offset/angle/thickness sweeps.
NextREADY proximal_shape_retention_hypothesis must review prior rail-aspect and
attachment cases,then choose ONE physically explicit bending-retention change
with volume/mass/anchor/collision checks. Existing productionCAD unchanged.

Reproduction (existing tags already completed,do NOT overwrite):
```
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY product_prototype/sofa/b3_contact_layer_geometry.py --tag UNIQUE
$PY product_prototype/sofa/contact_layer_coupon.py --tag UNIQUE
$PY product_prototype/sofa/b3_contact_layer_native.py --tag UNIQUE --exterior-union
$PY product_prototype/sofa/contact_layer_response.py --tag UNIQUE --case b3_contact_layer_union_withdraw1352
$PY product_prototype/sofa/contact_layer_material.py --tag UNIQUE
$PY product_prototype/sofa/contact_layer_profile_feasibility.py --tag UNIQUE
$PY product_prototype/sofa/contact_layer_segment_rotation.py --tag UNIQUE
```
All actual Native launch commands,working source snapshots,scene/compiled-plugin
hashes and runtime limits are in separate result paths. Failure records retained.
Feature7ccf1ea preserves the first completed implementation/diagnostic cycle.

1361 final software regression115testsPASS,history100MBcheckPASS,7SDKhashes
exactly equal1335. `git diff --name-only --diff-filter=MDR dd9b32e --
product_prototype/results` returns no pre-existing result modifications.
All Native children completed;no persistent/background continuation promised.
