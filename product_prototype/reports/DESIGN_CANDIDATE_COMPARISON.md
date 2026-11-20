## Conditional finite union658–659 — 2026-11-20

Previous functional commit3a5844b:actual Native missing-B assembly corrected;
FREE100ms selected0.1% Gate PASS,CONTACT652 still FAIL. No B3 approval.
Independent geometric union implemented and four analytic/objectivity tests PASS.
Eyelet/support overlap2.35284–2.36475mm³;naive mass sum can overcount3.32594%
under SAME uniform material assumption,COM bias≤0.332202mm. Physical density/joint
unknown:actual union mass/inertia BLOCKED. No replacement of B3/checkpoints.
32/64facet geometric sensitivity≤0.080251%;NOT FEM/contact mesh qualification.
Authority:product_prototype/reports/FINITE_UNION_GEOMETRY_20261120.md.
Evidence:evidence_product_union_geometry_v32/manifest.json. STEP NOT GENERATED.
NEXT:contact-entry policy/feature diagnostics from649–651 (current impulse law
still-gap/dt),not more blind dt/alarm sweeps. Material/join/STEP remain separate.
Exact independent reproduction:python product_prototype/sofa/finite_union_run.py --tag UNIQUE_UNION

## Actual Native matrix635–657 — 2026-11-20

Authority:product_prototype/reports/NATIVE_INERTIA_FORCE_TANGENT_20261120.md.
Previous feature5b8bf1 preserved. Missing B found despite callback counts635–639;
new640 installed matrix APIs fix actual assembly,not physics parameters.
644 actual operator isolated tangent relative error2.05e-12;observer purity0.
648 FREE100ms all-common/all3pairs worst0.0753113% PASS selected0.1% Gate.
654 actual world-transform Native strict1e-12 PASS.653 NOT RUN runner error retained.
652 CONTACT time FAIL (surface19.4683%,omega81.4033%,force100%).656 actual
A impulse correction agrees≤2.85e-14;normal target still-gap/dt.657 ten tests PASS.
Evidence:evidence_product_matrix_api_v31/manifest.json;all old immutable Raw retained.
Build:product_prototype/cad/build_b3_inertia_matrix_api_build640 (scoped force),
build_b3_inertia_matrix_api642 (read-only matrix).No SDK/old B3/checkpoint changes.
NEXT:independent eyelet/support overlap-corrected GEOMETRIC union moments;
material/joint mass remains unknown. Contact event/mesh/B3/100g/Lift/STEP unqualified.
Read-only resume:python product_prototype/sofa/inertia_force_contact_audit.py --tag UNIQUE --case b3_inertia_contact_operator655 --reference b3_inertia_matrix_contact649

## Native inertial force/tangent623–634 — 2026-11-20

Authority:NATIVE_INERTIA_FORCE_TANGENT_20261120.md.
Evidence:evidence_product_force_tangent_v30/manifest.json;4628prior immutable hashes unchanged.
-623 scoped gyroscopic ForceField,NOT ODE/contact solver. Actual world-rotation K
 and velocity B derivatives. Native mapped mass retained;no q/v writes or SDK edit.
-624 FAIL preserved:old SparseLUSolver factory moved to optional CSparseSolvers.
 625 uses installed EigenSparseLU (nonsymmetric),NOT symmetric LDL.
-Actual C++ FD relative error:K≤6.65e-11,B≤3.31e-10;K/B assembly calls each40.
-625/626 backward Euler100ms still FAIL0.132861% angular invariant.
-627–632 Native trapezoidal with actual K/B:angular invariant base/half/quarter
 0.0112466%,0.00555120%,0.00276304%. All-common-time/all3pairs worst0.0748267%,
 selected FREE-ring0.1% Gate PASS. First-order observed trend;not generic2nd-order proof.
-633/634 principal-axis reference omega error≤9.01e-14rad/s;strict basis1e-12 PASS.
 No contact/B3/global energy/100g/Lift qualification. Physical hardware mass still assumed.
NEXT:read-only ACTUAL assembled matrix audit (K/B calls alone do not prove matrix),
 world-objectivity,then finite contact using same force law/Native solver.
Reusable build:cad/build_b3_inertia_force_build623,source/binary guarded.
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_inertia_force_trap_time632/summary.json`
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/inertia_force_run.py --tag UNIQUE_FORCE --trapezoidal`

## Inertia/contact continuation600–622 — 2026-11-20

Functional input commit:844afa1. Authority:NATIVE_SAMPLED_INERTIA_20261120.md.
Evidence:evidence_product_long_inertia_v29/manifest.json → contact_inventory_v28 → inertia_v27.
Latest4630files;prior4393immutable paths checked0mismatches. Old Raw/verdicts unchanged.

-600–602 real finite-ring contact with SAME592 input binary passes basis1e-12,
 but604 all-common-time0.1% CONTACT Gate FAIL:surface displacement19.3158%,
 COM6.48978%,angular velocity81.3824%,rotational energy94.5976%,force100%.
-609 actual sampled torque law error≤1.37e-22Nm;M*dv-inertiaImpulse-contactImpulse
 residual≤7.64e-22Ns /9.72e-24Nms;free predictor≤9.60e-14.
 Active Native normal target remains-gap/dt(residual≤3.21e-8m/s).
-606 actual saved mapped finite surfaces show0strict edge/facet crossings and0
 uncertain tests. NOT containment/swept/full hardware clearance or time certification.
-607 analysis omitted contacts after each response group's first block.608/609
 expand ALL actual3-row contacts with ownership/coverage checks;old607 preserved.
 Signed inventory residual≤1.18e-21J,row work≤1.70e-21J. NOT heat/global energy PASS.
-610 cumulative energy/time Gate FAIL,including tiny signed residual192.377%
 (absolute1.63e-21J);NO error floor or residual exclusion.
-611 floating-point test bound failed because cross-product cancellation was
 scaled by output torque instead of operands.612 derives correct operand-based
 bound;6227regressions PASS. No physical tolerance changed.
-613–617100ms free extension:base angular invariant0.133470%,base-quarter
 all-time worst0.100100244%,STRICT FAIL at unchanged0.1%. Do not round to PASS.
-618/619 installed Native trapezoidal option gives EXACT same q/v/impulse as613;
 verified in622. B=K=0 held-input formula is unchanged;stop this branch,not dt sweep.
-620/621 OLD552/550 Raw reanalysis with FULL contact ownership:additional points
 remain on actual mesh≤1.56e-17m;active body-point counts7eyelet/3support,not old6/2.
 Old analysis files retained;counts are NOT area. Native state unchanged.

NEXT:
1.Native retained solver + actual velocity/rotation-dependent inertial-force
 tangent candidate (SparseLU available;do not send nonsymmetric Jacobian to LDL)
 only if independently force/Jacobian/FD/objectivity validated. Current sampled
 ConstantForceField hasZERO within-step Jacobian and is NOT production qualified.
2.Separately validate stock contact's discrete event/stabilization policy using
609 actual rows. Do not assume gyro fix,time smoothing or larger alarm repairs impact.
3.No B3 mass/checkpoint replacement,100g/Lift claim,or fabricated density/union.
Physical material/join/STEP and all original B3 failed time/mesh Gates persist.

Read-only restart:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_inertia_input_100ms_time617/summary.json`
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_inertia_contact_allcontacts609/summary.json`
Reusable build:cad/build_b3_inertia_input_build592 (unchanged);physical332/direct512.
Code regression:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m unittest discover -s product_prototype/sofa -p test_native_inertia.py -v`
No active physics child,no background continuation. Current sampled-input and
trapezoidal directions stop at measured validity limits,NOT OS/resource exhaustion.

## Sampled inertia candidate592–599 — 2026-11-20

Authority:product_prototype/reports/NATIVE_SAMPLED_INERTIA_20261120.md.
Evidence:evidence_product_inertia_v27/manifest.json;3931 prior immutable files unchanged.
Installed SDK unchanged;original B3 and all earlier PASS/FAIL preserved.

-592 scoped input module builds. Native EulerImplicit/ConstantForceField/mapped
 mass retained. Adds ONLY sampled torque=-omega cross(Iworld*omega),not an ODE or
 contact solver. No q/v reset,no implicit gyro Jacobian or B3 adoption.
-593/595/596 real Native10ms off-axis runs:angular invariant error0.0154663%,
 0.00773297%,0.00386646%;baseline0.660162%581 preserved.
-594/597 actual omega vs analytical reference error0.00286461,0.00143227,
 0.000716132rad/s;first-order sampled-input trend,not a universal integration PASS.
-598 principal control state difference≤7.11e-15,strict1e-12 PASS.
-599 all common outputs/all3pairs selected FREE-ring state,shape,L and kinetic
 energy comparison max0.0622731%,below unchanged0.1% Gate. No denominator floor.
 Input zero-power roundoff kept separately;NOT global energy/contact/FEM certification.
-Next finite contact600–602 runs and ALL-output checks;free-spin success does not
 qualify impact,friction,time/mesh,Holding,Lift or fabricated hardware mass.

Reusable build:cad/build_b3_inertia_input_build592;binary/source guards in run tool.
Reproduction(new UNIQUE tags):
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/inertia_input_run.py --tag UNIQUE_GYRO --case b3_finite_com_mapped571`
No old B3 checkpoint reused. Density/join/union still NULL.

## Native composite-acceleration continuation588–591 — 2026-11-19

Feature commits:e85534a,f3869ba;26 archived campaigns565–591 (587 is preliminary build only).
Authority:product_prototype/reports/FINITE_COM_NATIVE_VALIDATION_20261119.md.
Latest evidence:evidence_product_mapping_v26/manifest.json → v25 → v24.
3933 recorded files;3785 prior immutable paths verified0mismatches.

-588 compile FAIL (missing MechanicalParams include) preserved;589 fixed read-only
 observer compiled against INSTALLED SDK only. No SDK/FEM/contact/ODE changes.
 Binary:cad/build_b3_mapping_build589/libReGripMappingAcceleration.so.
-590 observer scene FAIL:RequiredPlugin was placed after child creation.
 591 fixes XML plugin order ONLY;both Native children complete with0SOFA errors.
-Public composite acceleration API called on temporary output at real q/v:
 returned0;expected omega×(omega×r) max0.403523685m/s²,96actual point records.
 Observer q/v/mapped mass points/contact impulse difference EXACT0 vs572.
 Thus current mapped-mass composition lacks this composite acceleration response;
 not a proof that every Native rigid solver is unsupported.
-18 successful short Native children +2 observer-init failures this continuation;
 no full B3 Holding rerun. Independent geometry/Jacobian/reference Gates advance,
 but physical rigid inertia/free-spin/time/mesh and product adoption remain BLOCKED.
-No new50g,100g,Lift/STEP approval. Old B3 functional results/failures unchanged.
 Physical material density and eyelet/support union/join still NOT MEASURED.

NEXT:do not repeat free dt refinements or adopt world-frozen tensor. Verify a stock
Native composition that supplies composite acceleration/gyroscopic response using
581(off-axis negative) and584(principal positive) references. If unavailable,
a narrowly scoped inertial correction requires its own force/Jacobian/reference
validation;do NOT rebuild an ODE/contact solver or silently resume B3 checkpoint.
Only then redo moving finite contact clearance and qualified physical convergence.

Exact read-only resume:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_mapping_acceleration591/summary.json`
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_finite_spin_exact581/summary.json`
Reusable compiled probe589 plus unchanged physical332/direct512;source/binary guards
in observer_identity.py. Probe replay,ONLY with a new hypothesis/unique tag:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/mapping_acceleration_run.py --tag UNIQUE_MAPPING_API`
Regression:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m unittest discover -s product_prototype/sofa -p test_finite_mass.py -v`
No active physics child;no background continuation promised.
This is an adoption/model-capability block,NOT OS memory or480s exhaustion.

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


## Latest native model comparison442–453,2026-11-19

Centered21node native Rail now has limited actual small-load state/force/scaling
PASS,not B3 or spatial qualification. Fine41/81 remain FAIL. Same rigid coordinate
translation,material and load kept;no geometry/stiffness fitting. PRIVATE kinematic
references are not candidates with demonstrated grasping. Native reinforceLength
changes force approximation and was not adopted. Authority:
NATIVE_NONLINEAR_RESIDUAL_AND_CENTERED_RAIL_20261119.md;2dc6afc/fcc7ba5.

## Historical native model comparison432–440,2026-11-19

Geometric rest fixes initial native Rail residual,not loaded failure. Same-state
modern/addDForce blocks agree exactly;do not reuse the spring415 bug diagnosis.
433/435 loaded native alternatives FAIL;no geometry/material/force fitting and
no product model selected.440 PRIVATE linearized Euler agreement is not a loaded
stiffness ratio or B3 performance comparison. Authority:
NATIVE_BEAM_REFERENCE_AND_ASSEMBLY_20261119.md;feature e5d4dae/bc762c1.

## Historical native model comparison407–430,2026-11-19

No new product geometry selected. B3 remains functional research baseline only.
Native shell and rectangular BeamAdapter are separate coupon models,not fair
same-geometry B3 performance comparisons. Shell PCG solves its stored equations,
but mesh/constitutive/stress-free precurve gates FAIL. Rectangular BeamAdapter
retains curved rest positions exactly at zero load,not loaded certification.
Loaded Skin/Rail private matrix references407/425 are NOT accepted states or
certified stiffness ratios. No fitted shell scalar or physical material change.
Authority:`NATIVE_SECTION_BACKWARD_ERROR_AND_ALTERNATIVES_20261119.md`;
feature commits3593421,c487517,127119b,e0d5750.429 directional Rigid3 FD is
diagnostic only;430 raised iteration budget still FAILs.100g/Lift/CAD promotion NOT RUN.

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
