# Native Guide contact entry and angular inventory — 2026-11-19

Start HEAD:ffd2426e08da4151ff1c1463be64d95d6f933a8f,clean worktree.
Feature commits:985f93e,3ea736c,eeef6a9;unit-label correction0840e2a.
Evidence:evidence_product_angular_v22/manifest.json → evidence_product_entry_v21
→ evidence_product_velocity_v20. Previous results/verdicts/SDK unchanged.

## Scope and hypothesis

The unfinished checkpoint requested actual Native row/velocity/impulse attribution,
not another complete Holding test. Reused frozen375 inputs and controller332.
Each coupon contains two FREE Rigid3 guides extracted at actual375 time2.3875s;
NO FEM,attachments,cables,gravity or object. It is NOT an attached-system restart.
Proxy radius1.802775638mm,mass10mg/body,public isotropic inertia1e-11kg m2,
mu0.3,contactDistance0.2mm. These are inherited research assumptions.
Alarm1/5mm and dt2.5/1.25/0.625ms are the PREVIOUS diagnostic contrasts,
not newly adopted product parameters. Same initial q/v,mass and native ODE.

Installed SOFA only:26.06.00. All physics children used existing4GiB/480s guard;
executed serially. Thirty short children completed,each about0.11–0.21s.
No full B3 re-run,no global-alarm long run,no custom physical solver.
No physical state/force correction or tolerance relaxation.

## Actual implementation503–522

`guide_pair_coupon.py --contact-audit` adds frozen NativeDetectionPairs,
NativeResponseRows and NativeConstraintJournal.503–505 default loop;
508–510 velocity-first.507/511 compare against original483/496/497 and
499/500/501:ALL actual q/v/total impulse values match EXACTLY(error0).
The response metadata API has history-related side effects;these trajectory
comparisons,not an unsupported purity assertion,justify its limited use here.

512 builds a separate read-only `NativePairRows` BaseObject. It reads public
Rigid3 constraintJacobian,Native lambda,freePosition/freeVelocity at AnimateEnd.
It does not call getConstraintInfo or modify physical/solver data. Zero-lambda
rows are recorded directly,not reconstructed by division.513–518 record all
three mapped rows and both bodies with the same binary. Actual q/v/impulse
again match the corresponding uninstrumented reference exactly.

|Audit520|Maximum measured residual|
|---|---:|
|Observer trajectory difference|0|
|Detector coordinates vs PREVIOUS mapped centres|6.9388939e-18m|
|Direct J^T lambda vs existing journal|floating-point roundoff|
|M delta-v vs mapped impulse|5.2939559e-22Ns/Nms|
|J v+ minus(J v- + W lambda)|5.5511151e-16m/s|
|Active normal row vs −buffered-gap/dt,default|1.9392108e-8m/s|
|Same target,velocity-first|1.1090462e-11m/s|

W=sum_i J_i M_i^-1 J_i^T uses ACTUAL public mass matrices. Constant-frame
inertia transport is allowed here ONLY because matrices are verified isotropic.
It is not a general rigid-inertia implementation.507/511 also show equal/opposite
linear impulse error0 and response-row sums exactly match total journals.

Raw519 preserves a WRONG detector-coordinate interpretation:it omitted both
sphere radii and obtained1.44/2.88/5.77m/s target discrepancies. No old file was
rewritten.520 explicitly reconstructs previous mapped centres,verifies their
coordinates,then subtracts BOTH radii plus unchanged0.2mm contactDistance.
506 is a separate failed analysis input path,physics NOT RUN;507 fixes only the
reference case names. Both failures are archived rather than discarded.

## Discrete constraint law,not an explicit continuous impact law

Installed `BaseContactLagrangianConstraint.inl`,getVelocityViolation,contains
`relative_free_velocity + (P-Q)/dt`,then subtracts contactDistance/dt.
Its position branch uses projected free positions. Thus an active discrete row
need not yield zero accepted normal velocity. This is not fixed by simply
setting solveVelocityConstraintFirst. Read-only actual response520 validates
the gap/dt target;it is not a new impulse solver or an event-time theorem.

522 compares all3pairs WITHOUT a relative-error floor. In alarm1 base/half,
first active rows start at the same2.5ms discrete time,normal difference
5.49e-15,gap difference1.73e-18m,previous normal-velocity difference2.22e-15m/s.
Yet accepted normal velocities are+0.467575418/+0.935150827m/s:about50% difference,
consistent with inverse-dt penetration correction. For alarm5 half/quarter,
nearly identical initial row/gap/prevelocity instead give−0.667315650/
−1.334631300m/s. This is also about50%,not0.1% convergence.

Recorded first-response END clocks differ;they are NOT continuous collision
birth times. Equal output clocks do not prove equal event phase. Previous and
accepted velocities are at different discrete times,not same-time v−/v+.
No interpolation,phase shifting or output correction is used to conceal this.
Existing all-time gates498/502 remain FAIL.522 is an additional limited
first-row sensitivity FAIL,not a replacement for those gates.

521 plots actual direct-row velocities/impulses:
`product_prototype/results/b3_entry_plot521/actual_native_entry.png`.
No prescribed deformation or displacement amplification. Impulse axis is nN s,
NOT force. The plot labels SDK,source,binary,dt,mass,inertia and limited scope.
Normal effective inverse mass is~99.5% rotational in this FREE off-centre pair;
do not transfer this ratio to the rail-attached B3 system.
Signed kinetic changes are recorded stably from delta-v. They are NOT heat,
impact dissipation certification or a complete B3 energy inventory.
Raw519/520 key `normal_complementarity_product_Nm_s` has a UNIT LABEL TYPO:
Ns times m/s has units J,not Nm s. Values are unchanged and are not physical
heat. Current producer corrects the key to `normal_complementarity_product_J`;
old immutable Raw remains unedited. This has no effect on measured state/tests.

## Independent angular inventory and stock Native alternative523–531

523/524 add a fixed-origin angular inventory of actual accepted q/v and public
mass. Full ledger includes position-advection term. Closure error≤1.54e-22Nms,
but net INTERNAL angular impulse reaches3.82868023e-11Nms.
Normal-row contribution≤4.14e-25Nms;the tangential rows account for the net couple.
Rigid row lever fit≤4.43e-18m;two reconstructed row application points reproduce
the couple to≤3.88e-25Nms. Ledger closure is NOT conservation PASS.
Application points reconstructed from J are not certified physical surface points.

Installed SphereCollisionModel supports Rigid3d,and RigidMapping supports
Rigid3d,Rigid3d. The Vec3 subset contact mapper uses centre indices;the installed
RigidSphere mapper instead constructs local coordinates from contact positions.
525/527/528 therefore test a concrete stock Native alternative:
same proxy centres/radii,parent q/v,mass/inertia,mu,ODE,solver and alarm;
ONLY mapped collision representation changes from Vec3 to Rigid3 sphere.
This changes rotational contact kinematics,not just instrumentation;it is a NEW
physical-contact approximation,not an identical-results numerical optimization.

All6children run without SOFA errors.526/530/531 report net internal angular
impulse maxima1.4176304e-11/1.7614548e-11/2.2105264e-12Nms respectively.
This does not establish angular conservation or monotonic convergence.
529 all-common-output/all-pair0.1% time gate remains FAIL:
alarm1 worst97.7433321%,alarm5 worst65.8542655%(angular velocity).
At alarm1 coarse dt the−0.968939mm missed-entry gap persists.
The alternative is NOT adopted in B3;no full3-finger experiment is justified by it.
Stop velocity-first/RigidSphere/alarm/solver-parameter retries without a NEW
validated mechanism. These measured failures are not resource exhaustion.

## Product Gates and next research

- Preserved functional50g Skin Holding489/490 and release491;not rerun here.
- Full time/mesh/energy,solid hardware clearance,100g,Lift remain NOT QUALIFIED.
- CAD v10 reference route identity retained;STEP/assembly/fabrication NOT READY.
- No product geometry,force,friction,material or inherited checkpoint was replaced.
- Next independent development:validate the actual finite Guide/Support contact
  geometry and Native contact-point pullback against shared CAD configuration.
  A triangle-surface/finite-eyelet Native candidate must preserve real dimensions,
  keep collision enabled and first pass this FREE-pair angular/entry audit.
  Do not mistake enclosing-sphere overlap or its rotational mapper for exact
  eyelet/support contact. No full B3 or100g/Lift until that reduced gate is justified.
- Separately,if stock Native event-step policy is considered,it must demonstrate
  actual stage timing and same-input time convergence,not a velocity-zero patch,
  undocumented impact law or another unconditional dt-halving sweep.

## Builds,Raw and exact resume commands

Physical332 binary remains3eb202b1e2a25f3ec6cded69e92a9d02bc48c304be14f6ca7123b4d758e5d0e0.
New read-only build:`product_prototype/cad/build_pair_rows512/libReGripPairRows.so`.
Binary SHA256:6a00b4e75ef314f5d92ebc67431ee36cedba02c91e6546ff28a4ffe9d5514527.
Frozen source:`results/b3_direct_rows513/Observer.cpp` under product_prototype.
Source SHA256:2334142b2609a4132f1a96696475d0e527e4246dab22fe92905d9d3cbd25eb99.
`observer_identity.compiled_pair_rows()` checks both. ldd resolved SOFA libraries
ONLY under installed26.06.00;no matched-source SDK used. CMakeCache archived.
Every child keeps actual command/process/log,scene,producer/config identities,
mass,detector,response/direct-row and rigid state files under the Raw paths.
Build512 has no physics verdict;source compatibility deprecation warnings were
not interpreted as runtime failures. Runtime/memory are governed by child guard;
no fabricated peak-memory measurement is claimed.

From repository root,read latest evidence first(no physics repetition):

```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_rigid_time529/summary.json
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_angular_partition524/summary.json
```

Reproduce ONLY for a justified regression,using a fresh unique tag:

```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/guide_pair_coupon.py --tag b3_entry_REPLACE_UNIQUE --contact-audit --dt .00125 --row-binary product_prototype/cad/build_pair_rows512/libReGripPairRows.so
```

Add `--rigid-sphere` only for the explicitly different contact-kinematics candidate.
Actual original commands are in each Raw process/command.json.
No intentionally running physics child,no remote push,no automatic continuation
after session end. This is a reproducible incomplete checkpoint,not product completion.
