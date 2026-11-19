# ReGrip candidate comparison — native product research

All remain candidates,not a final selected product. See AUTONOMOUS_DESIGN_PROGRESS.md
and immutable source/scene/force journals. E250MPa,nu.3,mu.3 and material choices
are research assumptions. Equal prescribed branch commands are NOT a mechanical equalizer.

|Candidate/trial|Main controlled change|Actual result|Decision|
|---|---|---|---|
|187 baseline|outboard4,root0,8mm,centre-Vec3 sphere|Guide.490494N,Skin0;exact row partition|Not Skin grasp|
|188 out24|only lateral guide placement4→24mm|real Skin.03913N,Guide0,support92%|Holding FAIL|
|194 root14|only root0→14deg vs188|Skin mean.49162N,but9.31mm slip and penetration|FAIL|
|201 depth65|only initial depth50→65 vs194|Skin mean.48987N,support0;speed14.55mm/s,cable error6.63mm|FAIL;angular mapping limited|
|205/206/216/220/226 native Rigid3 sphere|proper rotational mapping,then stroke/placement variations|LocalMinDistance lacks mesh intersectors|Invalid collision-completeness comparisons;231 audit|
|211 uniform cross-ribs|physical transverse links + assumed rectangular inertia|240-step large deformation;also missing intersectors|No long-run approval;not a DiagonalMass fix|
|230 valid Min/Rigid3 path|MinProximity/useSphereTriangle,2mm,depth75|real Skin response,consistent sampled.2mm gap and momentum|Limited direct-contact evidence;NOT holding|
|235/236/237|same valid path:full hold and short time refinement|Use final summaries below/checkpoint|No prospective PASS|

Core finger dimensions and volume remain100mm,W24→12,skin.1mm,rails.5mm,
410mm3/finger for these product models. New rib/hardware volume is NOT included
in that core volume. Cross-rib comparison changes inertia and constraints;do not
call it an isolated rail-stiffness contrast. No physical motor/fastener selection.

## Gate ledger (not full product approval)

|Gate|Verified scope|Remaining requirement|
|---|---|---|
|1 Mechanism|3x120deg parametric CAD/STL/BOM candidates|Kernel assembly,hardware strength,motor interface|
|2 Interference|Initial wire/guide checks forv6|Full moving Skin/rail/support/wire/palm clearance|
|3 Cable|Straight and no-contact coupons;actual length journals|Coupled contact shortening/time FAILs remain|
|4 Direct Skin|188/201 legacy mapping;230 correct Rigid3/Min short interval|Full path geometry/response validation|
|5 Wrapping|Curvature/actual states recorded|Continuous contact coverage,not row count|
|6 Holding|Earlier Guide-only observations preserved|Skin-only50g unsupported hold qualification|
|7 Physics|Response partition/momentum/API equality,limited scopes|.1% time,mesh,whole energy/work|
|8 Generalization|NOT RUN for qualified design|100g,R20,cylinder,box|
|9 Lift/release|NOT RUN for qualified design|Verified moving root/pullPoint fixture + gates|
|10 Fabrication|Parametric sources,STLs,drawings/BOM|STEP/assembly,tolerances,supplier/material/actuator data|

No conditional row-force or inventory PASS is promoted to any complete product Gate.
Pressure/contact area/root work remainNULL. No new custom physical solver was added.
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
