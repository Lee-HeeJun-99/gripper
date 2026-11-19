## Free-spin continuation581–586 — 2026-11-19

Feature commit:e85534a (COM/Native contact565–580);this continuation separately committed.
Authority:product_prototype/reports/FINITE_COM_NATIVE_VALIDATION_20261119.md.
Evidence:evidence_product_spin_v25/manifest.json → com_v24;3672 prior immutable files unchanged.

-581 exact axisymmetric torque-free reference:angular invariant relative defect
 ≤2.03e-16,energy≤7.34e-16,Euler-equation FD residual≤9.74e-9rad/s².
 Actual Native off-axis omega error0.122997rad/s and angular error0.660162%
 at10ms persist at all3dt. No interpolation/error floor/new physical solver.
-582 Native principal-axis spin changes ONLY initial angular-velocity direction,
 same magnitude and COM translation.583/584 actual angular invariant PASS:
 point inventory drift3.11e-15,omega vs exact≤6.47e-15rad/s.
 This narrows failed configuration to off-axis rotational dynamics,not a blanket
 failure of Rigid3,geometry/Jacobian or all Native physics.
-585 mathematical regression FAIL preserved:elementwise relative comparison
 mishandled exact-zero tensor entries.586 uses tensor-norm relative error at
 same1e-14 bound (NO floor),5tests PASS. No physical Gate changed.
-New COM/mass candidates remain NOT ADOPTED. No new50g/100g/Lift PASS.
 Actual density,material join/union inertia and CAD STEP remain BLOCKED.

NEXT do NOT repeat565–586 or blind dt/alarm changes. Inspect a STOCK Native
composition supporting composite mapping acceleration/gyroscopic dynamics using
581/584 as negative/positive references. Installed RigidMapping.h declares no
computeAccFromMapping override;Mapping.h default composite-acceleration method
is empty. This is evidence for this composition,not proof all SOFA is incapable.
Do not silently replace old B3 inertia or resume old checkpoints with changed mass.
If no installed stock path is verified,keep adoption blocked and isolate any
minimal inertial correction as a NEW scoped candidate,not a new contact/ODE solver.

Read-only resume:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_finite_spin_exact581/summary.json`
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_finite_spin_principal_exact584/summary.json`
Regression:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m unittest discover -s product_prototype/sofa -p test_finite_mass.py -v`
Guarded fresh control:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/finite_com_native.py --tag UNIQUE_COM_CONTROL --mapped-mass --free --spin-mode principal`
Reusable unchanged332/512 binaries;no new C++ build or SDK edits. No active physics process.

## COM continuation565–580 — 2026-11-19

Authority:product_prototype/reports/FINITE_COM_NATIVE_VALIDATION_20261119.md.
Evidence:evidence_product_com_v24/manifest.json;3354 prior immutable files unchanged.

-565 independent signed-volume COM/inertia cross-check passes;physical density/join/union still NULL.
-566 free Native basis comparison passes,but567 anisotropic body-input contact FAILS:
 maximum mapped position difference1.20949mm. Not adopted into B3.
-568 input WORLD-frozen inertia passes strict1e-12 basis comparison;this is NOT a
 rotating physical tensor.569/570 actual public M and direct J identify convention mismatch.
-571 Native Vec3 mass quadrature + RigidMapping passes basis check with contact.
 572/573 free angular momentum FAIL0.660162%;577–580 half/quarter same drift.
 No custom solver/SDK change;candidate NOT qualified for B3 or physical rigid dynamics.
-575 block-only analysis omitted simultaneous cross-block impulses;preserved.
 576 corrected ALL-row audit on SAME Raw closes row update2.22e-16m/s and shows
 finite-surface active velocity target=-buffered_gap/dt residual2.83e-9m/s.
-Physical calibration,B3 time/mesh/energy,100g/Lift/STEP remain unresolved.
 Next:independent torque-free reference isolates Native rotational dynamics,
 then inspect stock inertial-force/mapped-mass support;do not blind-reduce dt.

## Latest continuation — finite Native hardware532–564,2026-11-19

Feature commits:fcf0282,ea5794a,9e09cc4,ad88042.
Authority:product_prototype/reports/FINITE_GUIDE_AND_SUPPORT_VALIDATION_20261119.md.
Evidence:evidence_product_finite_v23/manifest.json → v22 and older evidence.
Prior immutable2695files audited,0mismatches;new3356files.

-24short Native children;no full B3/Holding rerun.532 MinProximity finite mesh
 yields1001iterations/large residual;alarm5 aborts std::bad_alloc under4GiB limit.
 Actual failure preserved;not host-wide OS exhaustion or a successful run.
-Stock LocalMinDistance tested with all finite eyelet collision models ENABLED.
 16/32/64surface refinements and native compound support scene implemented.
 Fewer rows are a detection-policy change,NOT same-result speed optimization.
-539 detects real saved facet crossings with alarm1.543/5630.1%time and5451%
 contact-mesh Gates FAIL. Compound alarm5 worst~64.6244%;NOT adopted into B3.
-552/555 actual mapped points and Detector feature/edge IDs recorded read-only.
 Observer q/v/impulse difference0.557 mapped API passes strict1e-12.
-534–553 apparent surface discrepancies traced to independent trimesh SI scale
 classification.556 analysis-only nondimensional wrapper passes analytic refs;
 no Native state/force/tolerance changes.557 actual loaded surface-point error
 ≤4.18e-18m;old analysis Raw preserved. Not a physical/time Gate workaround.
-v11 CAD:36finite eyelets+36proposed supports,STL/SCAD/section/BOM/shared config.
 No STEP/kernel/joins/material/strength/whole assembly/fabrication approval.
-548/549 exact convex/envelope SAT screens show no saved support interference
 on OLD485 motion;559 support-object min+0.647705mm. Conditional replay ONLY,
 not dynamics of new hardware or swept clearance.547 sector certificate failed,
 but sector violation was correctly NOT labelled actual solid collision.
-564 partwise COM/normalized inertia audit:eyelet COM offset18.25–25.10mm from
 assumed Native mass origin;support7.61–10.94mm. Actual density/mass/union
 inertia NULL. Existing10mg origin lump is not calibrated fabricated hardware.
-Existing functional50g Skin Holding/release remains limited;full time/mesh/
 energy,100g/Lift/fabrication remain NOT QUALIFIED. SDK/Raw/verdicts preserved.

NEXT:Native COM-frame/shared-Jacobian mini reference using explicit component
mass assumptions supported by564 geometry;do not silently change lumped mass,
invent density,claim numerical repair or reuse old B3 checkpoints.
Separately investigate Native event/step timing on verified finite geometry.
No blind alarm/dt/mesh sweep,collision disable,post-set velocity or custom solver.
Immediate read-only resume:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_finite_hardware_mass564/summary.json`
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_compound_time563/summary.json`
Reusable332/512 and new554 read-only observer;frozen source/binary guards and
exact regression commands in authority. Actual Native plot560 retained.
No active physics child or promised background continuation.


## Latest continuation — Native entry/angular audit503–531,2026-11-19

Feature commits:985f93e,3ea736c,eeef6a9;unit-label correction0840e2a.
Authority:product_prototype/reports/NATIVE_GUIDE_CONTACT_ENTRY_20261119.md.
Evidence:evidence_product_angular_v22/manifest.json → evidence_product_entry_v21
→ evidence_product_velocity_v20. Prior immutable audits0mismatches.

-Actual Native detector/response/direct-J/free-state observers implemented.
 Thirty short Native children completed under4GiB/480s policy;no long B3 rerun.
-503–518 observer comparisons q/v/impulse error0,strict1e-12 preserved.
 Actual mapped impulse,mass-velocity change and effective-mass row update agree.
-506 input-path analysis FAIL and519 wrong sphere-radius interpretation preserved.
 520 verifies detector coordinates are previous mapped CENTRES(error≤6.94e-18m),
 then subtracts both radii. No old Raw or verdict rewritten.
-Native active row follows−gap/dt,NOT necessarily zero normal velocity.
 Same near-identical entry row/gap/prevelocity yields~50%dt sensitivity522.
 Old all-time0.1%FAIL498/502 unchanged;no event-time/impact-law PASS.
-523/524 angular ledger closes,but net internal tangential couple reaches
 3.83e-11Nms. Linear momentum agreement is not angular-conservation certification.
-525/527/528 stock Rigid3 sphere mapping changes contact kinematics only.
 Runs complete,but529 all-output/all-pair time gate FAIL(alarm5 worst65.85%).
 Angular inventories526/530/531 are not conservation PASS. Candidate NOT adopted.
-Functional50g Skin Holding/release485/489–491 preserved;mesh/time/wholeenergy,
 solid hardware clearance,100g/Lift/STEP/fabrication remain NOT QUALIFIED.

NEXT:validate finite Guide/Support Native contact geometry and contact-point
pullback against shared CAD dimensions in a reduced scene BEFORE full B3.
Do not repeat velocity-first/RigidSphere/alarm parameter sweeps without a new
mechanism. No custom physics solver,zero-velocity patch or collision disable.
Exact immediate read-only commands:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_rigid_time529/summary.json`
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_angular_partition524/summary.json`
Reusable read-only build512/source guard:observer_identity.compiled_pair_rows().
Raw paths,SDK/binary/source hashes,actual commands and scope in authority.
No physics child intentionally running;no automatic background continuation.


## Latest continuation — B3 moving clearance472–502,2026-11-19

Feature commits:ea03025,83da78d,18bd3eb,bd43763,3b7a4c5.
Authority:`product_prototype/reports/B3_GUIDE_RELEASE_AND_DETECTION_20261119.md`.
Final evidence:`product_prototype/reports/evidence_product_velocity_v20/manifest.json`
(linked to v19 and all old immutable evidence).

-472/475 locate375 overlap at2.390s,98mm adjacent Guide pair:one negative frame.
 Detector output follows at2.3925s;small solver residual is not accepted clearance.
-474 changes ONLY sector margin0.5→1mm,completes3s/221.356s. Holding functionality
 remains,but Guide overlap worsens to−1.102mm. Candidate NOT adopted.
-480 global5mm alarm is CANCELLED for measured cost forecast(4partial frames);
 NOT timeout,OS exhaustion,completed physics or a remedy.
-483 Native free-pair reference supports alarm-range cause.484/485 scheduled
 native alarm window changes no force/state solver;3s completes133.319s.
-488 saved Guide spheres show no overlap(min+0.194739mm).492 first954frames
 finger/Guide/object q/v and cable force match375 EXACTLY;4wide-alarm frames.
 Skin-only functional50g Holding and release retained489–491. NOT final grasp PASS.
-493 positive chord gaps are NOT actual swept CCD. Solid supports remain unverified.
-498 free-pair0.1%all-common/all-pair time gate FAIL. Native velocity-first499–502
 also FAIL(5mm worst~63.8%);not applied to B3. Prior mesh/time/energy FAIL preserved.
-481/487 new baseline route drawing/STL/SCAD coordinate audit:all6Native routes
 error0. STEP/assembly/fabrication NOT READY. No100g/Lift expansion.
-v19/v20 prior hash audits0mismatches;final2087files. No old results rewritten.

NEXT:read-only Native free-pair row/normal/tangential velocity/impulse recording
around contact entry;compare modes at same physical event phase using existing
verified mass/Jacobian references. No new solver,margin sweep,global alarm full
run,or unvalidated100g/Lift. Read exact restart commands in authority.
Immediate read-only commands:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_pair_velocity_time502/summary.json`
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_comparison492/summary.json`
Reusable physical build332 and separate alarm build484 have frozen hash guards.
ActualRaw,source/binary,applied alarm clocks and commands are preserved.
All launched sessions ended;480child final report absent/NULL,not fabricated.
No background continuation promised.


## Latest continuation — Native axial strain468–471,2026-11-19

Feature commit7701d5b. Authority:
`product_prototype/reports/NATIVE_AXIAL_STRAIN_PATH_20261119.md`.
Evidence:`product_prototype/reports/evidence_native_strain_v18/manifest.json`.

-Actual installed force path inspected:default axial strain uses spline-midpoint
 local/rest endpoint transforms,not chord length. SDK remains unchanged.
-468 build/API constness failure is preserved;physics NOT RUN. New build469
 fixes observer temporary qualification only;470 completes6native PRIVATE queries.
-Native force reproduces455 exactly. Reconstructed axial changes explain
 1ULP force changes1.70e-12/3.40e-12N to≤4.16e-18N. Actual unloaded q unchanged.
-47170digit projection contrast supports representation sensitivity but is not a
 complete high-precision spline reference,force correction or accepted equilibrium.
-Strict fine-mesh equilibrium remains FAIL. Stop further unit/origin/FD/precision
 sweeps without a new remedy hypothesis. No Gate waived;no B3/100g/Lift approval.
-Prior immutable1258files verified,0mismatches;new manifest1351files.

NEXT independent product task:read-only actual-state Guide interference audit
using saved375. Identify offending physical Guide/support pairs before proposing
new geometry;do not disable collisions or promote prescribed geometry.
Fine-mesh physics qualification remains blocked separately.
Exact read-only restart:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/native_beam_strain_assess471/summary.json`
`rg -n '375|Guide|gap|interference' product_prototype/reports/SKIN_ROUTING_AND_PRECURVATURE_20261119.md`
Reuse frozen strain observer469 and force observer451 only for justified new
diagnostics. Full commands/source/binary/SDK identity are in authority/Raw.
No physics child intentionally running;no automatic continuation promise.


## Latest continuation — loaded tangent459–466,2026-11-19

Feature commits1c20109,b19f839. Authority:
`product_prototype/reports/NATIVE_LOADED_TANGENT_VALIDATION_20261119.md`.
Evidence:`product_prototype/reports/evidence_native_loaded_fd_v17/manifest.json`.
-459 corrects diagnostic root mask(3/5nodes);mixed-direction force derivatives
 agree to best1.30e-9/7.40e-10 relative.460 old-default FD byte regression PASS.
-462 observer input registration FAIL is preserved. New build463 fixes it;
 464/465 test a soft bending direction without changing actual q/v.
-Soft-direction force agreement is much less precise(best1.65e-4/2.04e-4 relative);
 torque derivatives near zero remain unresolved. No complete tangent/mesh PASS.
-466 records the comparison and actual-query plot. Actual unloaded positions
 unchanged(error0). Prior immutable1119files verified;0mismatches.
-Strict static41/81 residuals remain FAIL. No B3/full time/energy/hardware,
 100g,Lift or fabrication approval. No tolerance or model change adopted.

NEXT:read the actual native axial strain/length force path,then quantify
represented segment-length/axial-force sensitivity at frozen PRIVATE states.
Do not assume chord length equals the implementation's internal strain.
No more blind FD-step/unit/origin sweeps;no new custom physics solver.
Read-only restart:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/native_beam_fd_assess466/summary.json`
Reuse frozen builds458(root ladder),463(explicit direction);source/binary guards
and complete reproduction commands are in the authority. All prior results kept.
No physics child intentionally left running;no background continuation promised.


## Latest continuation — refined Rail454–457, 2026-11-19

Feature commit:c50516b. Authority:
`product_prototype/reports/NATIVE_FINE_RAIL_PRECISION_20261119.md`.
Evidence:`product_prototype/reports/evidence_native_refined_v16/manifest.json`.

-454 per-node failed-state diagnostics and455 PRIVATE ±1ULP force queries are
 complete. Baseline queries reproduce actual failed-frame forces exactly;
 actual unloaded q is unchanged. These are NOT accepted equilibrium states.
-41/81 axial residuals1.34812e-12/2.59047e-12N; one-coordinate ULP perturbations
 change force by1.69967e-12/3.39935e-12N. Sensitivity is not an error floor,
 proof of impossible equilibrium, or permission to correct actual coordinates.
-456 read-only observer exports SI positions/torques for static unit tests.
-457 equivalent N-mm-s static representation passes coarse21 force/state checks,
 but41/81 remain native solve FAIL. No mesh, time, B3,100g or Lift approval.
 Previous B3 functional Holding and all historical failures remain preserved.
-Old immutable evidence audit:980 files checked,0 mismatches; new manifest1122
 files. Original SDK, Golden, Raw and Checkpoints are not modified.

NEXT:compare loaded-state native tangent/directional force derivative with
symmetric FD over a documented perturbation ladder at frozen PRIVATE41/81
failed states. Initial-reference matrix equivalence432/439 is DONE;do not repeat.
First inspect exact preserved inputs:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/native_beam_refined_diagnostic454/summary.json`
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/native_beam_units457/summary.json`
Reusable frozen observer451 for SI PRIVATE queries,456 for SI unit exports.
Actual reproduction scenes/commands are in each Raw process record and authority.
Stop blind unit/origin/parameter sweeps. No tolerance waiver, custom solver,
failed-frame promotion or new product candidate is justified by these results.
No physics child intentionally running; no automatic session continuation.


## Latest product status after native442–453,2026-11-19

Centered21node native Rail small-load validation is limited;no B3 geometry or
product acceptance change. Fine mesh,attachment,time/energy,clearance and fabrication
remain open. No new100g/Lift/STEP claim. Authority:
NATIVE_NONLINEAR_RESIDUAL_AND_CENTERED_RAIL_20261119.md.

## Historical product status after native432–440,2026-11-19

No B3 geometry or product acceptance change. Initial native Rail rest/assembly
diagnosis is complete,but loaded model still fails;no replacement selected.
100g/Lift/CAD/STEP/fabrication claims remain unchanged and unqualified.
See NATIVE_BEAM_REFERENCE_AND_ASSEMBLY_20261119.md.

## Historical product status after native coupons407–430,2026-11-19

B3 CAD/functional holding baseline preserved;NO alternative model or geometry
is approved for production. Native shell fails continuum/mesh/precurve checks;
native rectangular BeamAdapter has only zero-load rest-position validation.
Loaded thin-section equilibrium and whole product time/mesh gates remain FAIL.
No motor/material measurement,100g,Lift,STEP assembly or fabrication-ready claim.
Authority:`NATIVE_SECTION_BACKWARD_ERROR_AND_ALTERNATIVES_20261119.md`.

## Historical continuation — native elastic validation380–405,2026-11-19

Latest feature commits:73e431e,e1dc3ea,19432e5. B3 functional holding/release
and ALL prior failures remain unchanged;no product promotion,100g or Lift run.
Authority:product_prototype/reports/NATIVE_ELASTIC_MODEL_VALIDATION_20261119.md.
Evidence:product_prototype/reports/evidence_native_elastic_v7/manifest.json.

- Actual native tetra/hexa exact axial patch393 passes all-node1e-12m.
- Actual pure-bending396/398 and independent force/strain/energy397/399 are
  recorded;thin section and ALL-PAIR mesh gates still FAIL. Time.1% unchanged.
- Native K/force observer402 changes solid q/v by EXACTLY0. Thin projected
  condition~2.96e9;force/K FD checked. NO new FEM/contact/ODE solver.
-405 verified material volumes210/310/410mm³ and zero-load state identity;
  initial Skin-only condition~4.10e9 already precedes Rail/Guide attachment.
  This is NOT loaded component bending certification.404 wrong material labels,
  401 scene plugin ordering failure and383 CSV parser failure are retained/excluded.
- Prior10613 immutable files byte-verified with zero mismatches. B3 moving
  hardware clearance,full wrapping,whole energy,mesh/time and fabrication remain
  unqualified. STEP/CAD geometry was not changed to conceal failed physics.

NEXT:loaded Skin/one-rail/two-rail reference and native element/arithmetic
diagnostics,then incremental Guide attachment. Initial spectra405 are DONE.
Do not rerun failed372 unchanged or expand unqualified B3 to100g/Lift.
Exact read-only restart:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/native_section_spectrum405/summary.json`
Full commands/build hashes/raw paths are in the authority above.
No physics child is intentionally left running;no automatic restart is promised.


## Latest product checkpoint — 2026-11-19, native trials259–379

Last functional checkpoint commit:d215185 (routing8f1cbc7/1de4288,force input81640fe,
mesh/time isolation4d7d4e9). Detailed authority:
product_prototype/reports/SKIN_ROUTING_AND_PRECURVATURE_20261119.md.
Historical bodies,Raw,Golden,SDK and prior verdicts below are preserved.

- A/B/C distributed routing/stress-free precurve candidates were implemented and
  actually tested first in SINGLE fingers. Initial3-finger guide-proxy overlap was
  discovered287,not hidden;293 now rejects it before physics. v8 sector routes retain
  real wire/guide dimensions and all hardware collision.
- B3=40deg manufactured distal curve70–100mm,1.5N/cable NATIVE force input.
  330/331 calibrate native value=T*dt;334/335 C2 input and discrete BE reference pass
  STRICT1e-12. New default displacement branch333 q/v difference0 for200 contact
  steps. This is input/controller work,NOT new FEM/contact/ODE solver.
- 344/348 ACTUAL Skin-source50g holding:slip.032359mm,speed.272144mm/s,
  support gap41.599746mm,Support/Guide/Rail hold force0,Skin Fz.490513N.
  Half-dt351/368/373 also meets FUNCTIONAL hold protocol,with Skin Fz.490480N.
  SAME-geometry zero-force345/349 FAILs (40.00054mm slip):not passive-curvature
  holding alone. This is limited SIMULATION evidence,NOT full physical certification.
- Matched constant-route308 ALSO meets functional holding;do not claim routing
  uniquely creates holding. Its cable errors/settling are worse;force and displacement
  inputs are different physical models,not a relabelled numerical fix.
- 375 completes3s in172.152s:after the SAME0–2s hold,the support ONLY exits laterally
  120mm2–2.2s (NEW post-hold fixture input);object remains free under gravity.
  377 first800 q/v states match344 EXACTLY.376 last Skin contact2.3875s;late Skin/
  Guide-object/support forces0;support and Guide-object forces after2s also0.
  Actual force unload reaches0N. Tip rest-reference error.150984mm under gravity;
  full recovery to validated gravity equilibrium NOT QUALIFIED. Old325 separation
  failure and residual cable tension are retained,not converted to PASS.
- Wrapping NOT QUALIFIED:48deg tip angle is not broad contact coverage;area/pressure
  remainNULL. Full moving hardware clearance FAIL/UNQUALIFIED (e.g.375 guide-proxy
  gap−.864mm);exact supports/solid sweep/self-collision/thickness remain unfinished.
- Physical gates FAIL:315/366 all-pair.6s,367 full2s pair,276/346 single full2s
  refinement retain.1% gate with NO floors. Loaded41-node360 has inverted tets;
 365 no-object also inverts;364 quarter-dt avoids inversion through.5s but differs
  strongly from coarse spatial response.363 zero-input reference is exact.
  These isolate causes,NOT prove locking or a unique solver bug. No production3-finger
 41-node expansion. Static native bending372 stops on actual Newton failures;
  missing static pairs areNOTMEASURED/BLOCKED,not measured zero errors.
- No100g,Lift,12-Wrench,Optuna,whole energy,final design or fabrication PASS.
  Native velocity-first Cable coupon322 FAILs;323 control PASS. Do not enable that
  combination in product scenes. General friction/energy certification remains open.

Reusable calibrated controller:product_prototype/cad/build_default_control332/
libReGripProductSequence.so
SHA2563eb202b1e2a25f3ec6cded69e92a9d02bc48c304be14f6ca7123b4d758e5d0e0.
Historical displacement build187 remains immutable;current runner source guard
requires the new332 build. Actual source snapshots/hash identities,not just a
possibly dirty parent source_commit,define each experiment.

CAD references:meshes/drawings distal_A_sector_v8,precurve_B_sector_v8,
hybrid_C_sector_v8,precurve_distal40_v9. STEP/OCC/FreeCAD assembly NOT GENERATED.
Actual figures:results/release_figures379/ and final_actual370/ (NOT QUALIFIED).
Frozen native scene:product_prototype/sofa/scenes/native_force_hold_release_v9/
(journals redirected;export-only is not an extra replay PASS).

Next priority:well-conditioned NATIVE small-load bending/attachment validation,
then moving-clearance and mesh/time gates. Do not continue stroke/offset/force sweeps
or repeat failed372 unchanged. Inspect its real residual/line-search logs before
changing any numerical scheme;do not waive tolerances or resume custom solver work.
The current family is checkpointed after repeated physical-gate failures,not declared
complete. All launched children finished;no automatic background continuation.
Actual275 hit480s policy timeout;no OS/RAM exhaustion is claimed.

Exact review/reproduction commands (use NEW tags;do not overwrite existing outputs):
```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY -m json.tool product_prototype/results/mesh_isolation369/summary.json
$PY -m json.tool product_prototype/results/force_three_time366/summary.json
$PY product_prototype/sofa/release_assess.py --case force_release_clear_support375 --tag NEXT_UNIQUE_RELEASE_AUDIT
$PY product_prototype/sofa/response_load_assess.py --case precurve40_force_three344 --tag NEXT_UNIQUE_SKIN_AUDIT
```
Actual simulation commands are preserved in each case launch_command.json and
process/command.json;full-quarter2s cost exceeds480s and was NOT RUN.

## Latest Skin-contact continuation — 2026-11-19

Source commits fbc9754,0ec92f0; details: product_prototype/reports/SKIN_CONTACT_CONTINUATION_20261119.md.
Trials147–175 use unique Raw paths; legacy and earlier FAILs unchanged.

-150/152: first finger impulse1.07s coincides with−.214888mm cable error.
 Assembled J matches previous geometry (~1.25e-16),not current geometry;
 reported linear error3.33e-9 does not certify geometric shortening.
-Backside guide149/151 (normal−3mm,unchanged hardware size) fails:no finger load,
 object follows support40mm. This routing is not selected.
-Outboard4 candidate155 initially meets functional holding and child-J row-load
 criteria, but these are NOT physical Skin holding. Geometry168 FAIL:
 Skin gap>=3.394mm despite active row influence;child/FEM coordinates match0.
 Detector173 confirms object–GUIDE pairs and NO object–Skin pairs through.4s.
 Child Jacobian influence is NOT direct contact provenance;169 is not grasp PASS.
-Read-only mapping logger171 and native detector174 give EXACT state equality
 (STRICT1e-12) over their respective2s/.4s scopes. Split-vs-unsplit172 FAIL:
 contact partition changes dynamics and is not a passive observer substitution.
-Base/Half/Quarter155/162/163 all completed2s;all-pair/all-common-time167 FAIL at
 unchanged.1% gate. No100g/Lift or final CAD selection is authorized by these results.
-Minimal Rigid3/DiagonalMass158 FAILs factory/state/topology initialization;
 not proof the entire SOFA capability is unsupported. Full bridge remains BLOCKED.
-CADv5 retained;STEP/assembly kernel/moving hardware/wire swept clearance,
 full energy/contact area/pressure remain NOT QUALIFIED/NOT MEASURED.

Next:bind actual Contact collision-model pair and response Constraint row identity,
 not mechanical-J influence. Use public detector provenance first,then eliminate
 Guide-first contact without disabling hardware collision. No custom solver rewrite.
Exact commands/Raw/Build identities are in the new detailed report.
All launched physics children completed;no automatic continuation is promised.


## Native continuation checkpoint — 2026-11-19 (supersedes priorities below, not historical results)

Functional commit: `ff21719` (preceded by 3f600b7, af356fb, e29719f, 956d6c3).
Detailed evidence: `product_prototype/reports/NATIVE_CABLE_COUPLING_AND_HOLDING_20261119.md`.
New native trials051–146 are separate from legacy Campaign numbering.

- Cable error isolated: exterior lateral Barycentric extrapolation (weights −29..37,
  amplification73) plus lagged native cable linearization produces a two-state cycle.
  Mapping/Jacobian arithmetic is consistent; straight/surface coupons pass. Existing044 FAIL retained.
- Stock RigidMapping/SubsetMultiMapping guide hardware replaces extrapolated guide mechanics
  in opt-in scenes. No custom force/contact/ODE solver added. No-contact131 hold shortening
  error ≤2.33e-10mm; transient error .00365mm means NOT whole-time cable certification.
- R30/50g conditional holding124: support force0, support clearance about44mm,
  low measured speed. Weight is borne by GUIDE HARDWARE, not Skin. This is
  experimental hardware-only holding, NOT film wrapping or final grasp PASS.
  Matched100g132 FAIL. No maximum holding capacity or fabrication claim.
- End-clock support adapter124/127: declared versus actual path error0m.
  Half/quarter-dt assessment133 retains0.1% gate: FAIL, including substantive object-motion
  differences (~1.44mm), not only tiny-value relative errors. Contact cable errors at
  base/half/quarter remain .21489/.09091/.05674mm.
- Public initial mass API140 PASS; opt-in query purity four steps difference0.
  Frozen scene replay141: all1200 steps q/v/quaternion/support differences0, STRICT1e-12 PASS.
  Repeatability is not physical accuracy. Input guards146 PASS (no physical trial).
- Cross-guide bridge136–138 current DiagonalMass configuration fails initialization;
  only that candidate BLOCKED, not proof all native diagonal mass is unsupported.
- CAD sources/STL/drawings/BOM: native_guides_v5. FreeCAD/OCC unavailable;
  STEP/kernel assembly NOT GENERATED. Moving full hardware interference NOT qualified.
- Lift BLOCKED by contact/time gates and mapped-root actuation path; no Lift run.
  Skin wrapping, general friction, self-collision, full energy/pressure/area and fabrication
  readiness remain unverified. Legacy results/SDK preserved; no push.

Next implementation: isolate native contact-transition cable linearization on a short
recorded failure interval, then revise guides so Skin, not hardware, bears load.
Before bridge dynamics, reproduce its native Rigid3 DiagonalMass initialization in a
minimal scene. Before Lift, implement a verified free-subset root fixture and pullPoint
motion; do not bypass current guards. Existing tests should be reused, not blindly repeated.

Reproduction commands and exact Raw/Build identities are in the detailed report and
`product_prototype/reports/evidence_native_coupling_v2/manifest.json` (once published).
All trials are stopped; no automatic continuation is configured. This is an incomplete
product-development checkpoint, not OS resource exhaustion or project completion.


# ReGrip product prototype — 2026-11-19

제품 우선 방향 전환에 따라 별도 구현했다. 기존 models/,Golden,Raw,
Checkpoint1644,자체 Solver와 검증 결과는 수정하지 않았다.

## 생성한 기준 후보

Single Skin + two bonded Rails + two edge cables,100mm 길이,폭24→12mm,
테이퍼 시작50mm,Root-centre radius50mm,0/120/240도 배치.
설정 원본은 config/design_v1.json. product_outboard14_v3는 동일 재료 단면의
Outboard14mm 비교 후보다. 최종 선정은 아니다.

제작 취급성을 검토하기 위해 Skin0.1mm/Rail0.5mm×2mm를 잠정 입력했다.
기존 연구의0.05mm/0.1mm나8층 ConceptV2와 다른 설계다. 물성은 미측정:
Native FEM E250MPa,nu0.3,핑거당 질량1g 가정. 실제 PET/TPU 인증값 아님.
코어 체적410mm³/핑거,1230mm³/3핑거. 기존439.34mm³와 동일 재료량이
아니므로 기존 모델 대비 성능 우위를 주장하지 않는다. 하드웨어 질량 미포함.

## 실제 산출물

- cad/generate.py:공유 형상에서 SCAD,양의 체적 Tetra 메시,STL,SVG,BOM 생성.
- meshes/product_outboard14_v3/:최신 파라메트릭 CAD 소스와 개별 Skin/Rail STL.
- drawings/candidate_v3/:치수도,부분 분해도,조립 SCAD,권위 BOM,기하 검사.
- cad/export_freecad.py:실제 BRep/STEP/STL/FCStd 생성용 FreeCAD 스크립트.
  문법 검사만 실행했다. FreeCAD/OCC/OpenSCAD가 시험 환경에서 발견되지
  않아 CAD kernel 실행·STEP·Assembly STEP·전체 Assembly STL은 미생성.
- sofa/run_native.py:SOFA 기본 FEM/CableConstraint/접촉/적분 Scene 생성·실행.
- sofa/scenes/native_three_finger_v1/:실제로800스텝 재실행한3핑거 Scene.
- results/:실제 CSV,Source/Binary/SDK 해시,로그,실패 증거,Accepted-state PNG.

STL 검증:Skin210mm³,각 Rail100mm³,합체410mm³. 모두 watertight,
consistent winding,양의 체적.3개 좌표계 determinant1,직교 오차<=1.62e-16.
이는 전체 어셈블리 간섭·가공 공차 검증이 아니다.

## 기구 관측과 변경

기본 가이드 normal3/outboard4mm,5mm Stroke에서는 실제 변형 중 와이어가
R30 물체와 약2.55mm 간섭했다. Outboard10mm도 약0.82mm 간섭.
Outboard14mm/5mm Stroke는 샘플 간섭 여유 약2.68mm지만 접촉 부족.
6mm Stroke에서는 접촉이 증가하나 약0.36mm 와이어 간섭이 다시 발생.
한 변수 변경 시험이며,동일 Stroke이지 동일 장력/Work 비교는 아니다.
가이드 질량,지지대,실제 가이드 마찰/마모,전 시간 CCD는 미검증.

Object 중심 깊이65mm,R30이면 지지면 깊이95mm가100mm 핑거보다 높아
닫힘을 방해한다.75mm 깊이 배치로 별도 시험했다. R20은80mm 배치.
초기 좌표를 바꾼 실제 물리 시험이지 저장 형상을 렌더링에서 옮긴 것이 아니다.

## 결정

초기 제작 후보만 유지한다. 실제 wrapping,독립 holding,lift와 제작 준비
완료는 승인하지 않는다. 다음은 와이어를 접촉면 밖으로 유지하면서 필요한
곡률을 만드는 가이드/앵커/Root angle의 단일 변수 기구 비교다.
자체 Solver 신규 개발보다 이 기구 문제와 Native 접촉 설정을 우선한다.
8층 필름/진공/Selective Jamming은 기본 파지 기능 이후의 교체형 확장안.
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
