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


## Latest validation442–453,2026-11-19

Actual native21node centered Rail448/450 independently measured452:force residual
6.17e-13/2.30e-13N,torque<=1e-12Nm,observer/control mapped q/v EXACT0.453 absolute
load scaling9.50233e-13m. These narrow checks PASS,not mesh/time/Skin/attachment/
B3/grasp. Fine41/81 native449 FAIL. PRIVATE442/444 expose nonlinear axial residual
and representation effects without accepted-state injection.443/445 FAIL;447 is
unadopted different native force model. Source/build/Raw preserved;SDK unchanged.
Authority:NATIVE_NONLINEAR_RESIDUAL_AND_CENTERED_RAIL_20261119.md;v15 evidence.

## Historical validation432–440,2026-11-19

Initial native BeamAdapter assembly/addDForce exact agreement and geometric-rest
zero force/torque confirmed.439 precision regression retains nine force/matrix
files exactly;actual valid control/observer mapped-center q/v difference0.
Loaded433/435 still FAIL.434 zero load from unused API fields EXCLUDED;not bending
evidence.440 is PRIVATE initial linearized reference only. No time/mesh/contact/
whole-energy/grasp promotion. SDK unchanged;feature e5d4dae/bc762c1.
Authority:NATIVE_BEAM_REFERENCE_AND_ASSEMBLY_20261119.md;evidence v13.

## Historical validation407–430,2026-11-19

Feature commits3593421,c487517,127119b,e0d5750;authority:
`NATIVE_SECTION_BACKWARD_ERROR_AND_ALTERNATIVES_20261119.md`.
All loaded thin-section tests407/425 FAIL strict equilibrium. Read-only probes
separate coordinate rounding from native force/K differences;no accepted-state
replacement. Actual native modern/legacy spring matrices415 differ34.7062%.
Native matrix-free PCG is runnable416/417;mesh/constitutive421 and curved
stress-free419 FAIL.423 passes exact zero-load position identity only;loaded
BeamAdapter422/424 FAIL. None qualifies B3 mesh/time/contact/energy.
Observer420 states exactly match417. Frozen source/binary guards protect400/406/410.
Evidence v8/v9 verifies764/395 prior immutable files with no mismatches.
429 actual native addDForce directional FD completed with separate force/torque
errors and exact curved rest-position control identity.427 scalar-API comparison
is EXCLUDED as observer failure.430 raises only iteration cap but Line Search58
FAILs. v11 archives all21 cases. No SDK modification,new force law,gate relaxation,
100g or Lift.

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


# Native SOFA product validation — 2026-11-19

## 판정

|요청 항목|실제 상태|
|---|---|
|CAD CREATED|PARTIAL: 파라메트릭 SCAD/FreeCAD 소스,개별 Skin/Rail/결합 Finger STL|
|ASSEMBLY VERIFIED|NOT VERIFIED: CAD kernel 미설치,전체 간섭 미검증|
|SOFA SCENE RUNNABLE|PASS: 저장 Scene을 실제800스텝 재실행,10.424초|
|SINGLE-FINGER ACTUATION PASS|구동·복원 OBSERVED;변위 추종/전체 시간 수렴 NOT QUALIFIED|
|THREE-FINGER CONTACT PASS|실제 자유 물체 접촉 OBSERVED EXPERIMENTAL;물리 인증 미완료|
|WRAPPING PASS|NOT PROVEN:연속 하중 지지 접촉 범위/면적 미검증|
|HOLDING PASS|FAIL:044 지지대 제거 시 물체가40.2mm 내려감|
|LIFT PASS|FAIL:021 Root20mm 상승 시 물체가 따라오지 않음|
|PHYSICAL FABRICATION READY|BLOCKED:STEP/전체 간섭/구동부/재료/성능 미확정|

## 실제 모델

설치된 SOFA v26.06.00와 SoftRobots만 사용. SI m/kg/s/N/Pa.
EulerImplicitSolver,SparseLDLSolver,TetrahedronFEMForceField(large),
CableConstraint,BarycentricMapping,기본 충돌 및 BlockGaussSeidelConstraintSolver.
Controller.cpp는 입력과 공개 API 상태 기록만 담당한다. 새 FEM/적분/접촉 Solver 없음.
Single Skin+두 Rails는 공유 Tetra 노드를 통한 연속 접합이다. 독립 적층/재밍이 아니다.
형상은100mm,24→12mm,단층0.1mm,Rails2×0.5mm,체적410mm³/핑거.
E250MPa,nu.3,질량1g/핑거,구체100g은 연구용 가정값이다.
주기0-.5/ .5-1/1-1.5/1.5-2초,각 케이블 독립 변위 명령이다.
동일 명령은 Mechanical Equalizer가 아니다. 모터 토크/스트로크 사양 미정.

## 실행 및 실패 증거

Raw/소스 스냅샷/바이너리 해시/명령/SDK/실행시간은 ../results/<case>/.
결과를 끝까지 실행한 것과 물리 PASS를 구분한다.

- 010 단일 핑거:800스텝2초,tip 최대41.593mm,마지막2.53e-12mm.
  최소 Tetra 체적비.98086. 단순 구동·복원 관찰이지 시간/물성 인증 아님.
- 010/011/012 동일 바이너리,dt2.5/1.25/.625ms,모든 공통 시점 비교:
  기존0.1% Gate **FAIL**,최대194.582544%(속도,절대차1.22636e-4m/s).
  작은 값에 floor를 더하지 않았다. 끝단 상태만으로 전체 PASS 처리하지 않음.
- 013/015/018 기존/Outboard10:실제 유한 와이어–구체 간섭 FAIL.
- 020 Outboard14,5mm명령:와이어 여유+2.678mm이지만 Skin 접촉 없음.
- 023/024 6/8mm명령:접촉 증가와 동시에 와이어 간섭 발생. 최종 선정 불가.
- 025 원통:비유한 상태로 실패. SIGABRT는 OS 메모리 고갈이 아니다.
  후속028 초기 지지대 여유.4mm 조건은 별도 물리 배치이며 기존 실패를 대체하지 않음.
- 033/036/037:올바른 우수 좌표계,경계 삼각형 전용 충돌 Child,
  R30 구체/원통/Box 실제 자유 강체 접촉. 모두 최종 파지 미인증.
- 039 느린4초 주기도 R20 유지 실패. 구동 시간 증가만으로 해결되지 않음.
- 041 R20 둥근 지지대:물체가 남아 있어도 지지대 지지이므로 Holding 아님.
- 042 조밀한10개 Guide/와이어:와이어 간섭−.79mm,Skin 침투 약−1.2mm.
  구조 변경의 개선이 확인되지 않아 기각. 기본6개 Guide와 별도 조건.
- 044 지지대를1–1.5초 사이40mm 내린 실제 중력 시험:
  물체가 함께 내려가므로 독립 Holding **FAIL**. 물체/핑거 형상은 지정하지 않았다.
  실제 support.csv로 지지대 운동을 검증한다. 지지대 구동 일 미측정.
- 045 GenericConstraintSolver 비교는 실제 factory 오류로 **FAIL**.
  v26.06에서 제거된 이름이었다. 헤더 존재는 factory 등록을 보장하지 않는다.
  BlockGaussSeidelConstraintSolver를 유지하며 미래 CLI는 해당 제거 이름을 거부한다.

## 와이어 추종 결함

050 독립 직선 Cable–Spring–Mass 시험은 실제800스텝/2초에서 모든 경로 단축 명령
오차 최대1.77809e-17m,STRICT1e-12 기준 PASS(실행.267초).
049는 SubsetMapping topology 옵션 누락으로 실패했고 보존했다.
050은 handleTopologyChange=0을 명시한 수정 시험이다. 단순 Cable 입력 자체보다
외측 Barycentric Guide/FEM/두 Cable 결합 조건을 다음 조사 대상으로 좁힌다.
이는 Finger FEM/접촉/파지 검증이 아니다.

044에서 실제 mapped Guide와 PullPoint의 전 경로 길이를 합산했다.
Hold 끝2초:명령8mm,실제 단축5.36008/5.79309mm(두 케이블).
명령과의 오차−2.63992/−2.20691mm. 단순히 tip이 움직였다고 Cable 명령
구현 PASS를 부여하면 안 된다. CableModel displacement는 단계 중 기록값이므로
최종 실제 경로 길이와 별도 기록한다. 원인은 미확정이다.
다음 작업은 stock CableConstraint의 작은 단일 경로에서 명령/실제 길이/선형화/
제약 오차를 분리하는 것이다. 허용오차 완화나 자체 Solver 재개발로 우회하지 않는다.

044 지지대의 종료40mm 이동은 확인됐지만,중간 시점 예상 경로와 공개 API 사이
최대.2mm 차이로 별도 STRICT1e-12 지지대 시간 동기화 시험은 FAIL이다.
물체가 지지대에 의존한다는 관찰과 지지대 API 시점 정확도는 구분한다.

## 접촉·에너지 측정 범위

구체에 대한 전체 저장 삼각형 최근접 거리와 와이어 유한 반지름 간격을 검사했다.
이는 저장 시점 검사이며 연속 시간 swept clearance 인증이 아니다.
근접 삼각형 수/접촉 Row 수는 실제 Contact Area/Pressure가 아니다.
물체 Jᵀλ는 지지대 접촉도 포함한다. 고정 물체의 투영된0을 반력0으로 해석하지 않음.
CableModel.force는 설치 헤더상 충격량 Ns이므로 **실제 dt로 나누어 N**을 계산한다.
Root Reaction,압력,접촉면적,전체 에너지/일 인증은 NULL/NOT MEASURED.
SOFA 기본 마찰계수는 연구용 가정이며 Changing-normal friction 인증을 대신하지 않는다.
기존 자체 모델과는 Geometry/재료/접합/접촉/적분이 달라 직접 성능 비교를 보류한다.

## 재현

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY product_prototype/sofa/run_native.py --tag UNIQUE_NATIVE_SINGLE
$PY product_prototype/sofa/run_native.py --tag UNIQUE_HOLD --fingers 3 --object free --radius 20 --gravity --floor --outboard 14 --intersection LocalMinDistance --stroke 8 --center-z -80 --support-shape sphere --support-gap .4 --withdraw-support
$PY product_prototype/sofa/analyse.py --tag UNIQUE_ANALYSIS --cases UNIQUE_HOLD
```

기존 results는 덮어쓰기를 거부한다.4GiB/480초,SDK 변경 없음.800스텝 실행한 Scene은
../sofa/scenes/native_three_finger_v1/scene.scn.절대 로컬 경로를 포함하므로 다른 환경에서는
run_native.py로 새로 생성한다.기존 기록에 재실행하지 않는다.
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
