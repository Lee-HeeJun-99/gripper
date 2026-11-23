# Guide mapping and load-path contrasts1113–1118

Starting HEAD5a32ce1,clean worktree. Original1105 and prior1112 preserved.
No new force/ODE solver,SDK edit,force increase,dt sweep or tolerance change.

## Native component coupon1113/1114

Actual first B3 guide reference frame,three actual attachment coordinates,
same UniformMass vertexMass and frozen332 journal binary. DefaultAnimationLoop,
EulerImplicitSolver,stock ConstantForceField→RigidMapping. No FEM/contact/cable.
Four10us steps each,4GiB/60s guards;actual runtimes0.1203s each,noERROR.

Public mass matrix diagonal:translation1e-5kg,rotation1e-11kg m². This is the
existing research input,NOT measured hardware inertia. Reference translational
load1e-6N and pure couple2e-9Nm produce expected first velocities via
M⁻¹Jᵀf dt,relative error≤9.63e-29. Actual mapped position error≤1.735e-18m.
Predeclared velocity gate0.1%,position1e-12 passed ONLY for this component coupon.
Three-point rigid velocity Jacobian rank6;first-two-point rank5. Reducing the
joint changes moment transmission,not merely its numerical cost. This does not
uniquely explain failed FEM candidate1109 or certify assembled joint dynamics.

## Native load-law isolation1115–1117

Retain entire1105 FEM/Rails/guide bodies/mass/inertia/root/mappings/gravity/
ODE/linearSolver. Remove twoCableConstraints and controller;36stock
LinearForceFields act on the three mapped attachment points of eachguide.
Unit-tension cable reference wrenches reconstructed by minimum-norm anchor
forces;maximum six-component reconstruction residual1.7231e-15 (mixed-unit
norm,NOT a normalized physical qualification gate). Sampled2.5NC2 envelope,
global-direction dead load:NOT evolving cable control. No artificial q/v.

1115 initializationFAIL:MechanicalLoad RequiredPlugin was declared after
Node creation;37errors,nooutputs,guard stopped. Preserve failedScene/producer.
1116 changes plugin declaration to precedeNodes;240steps/0.6s,3.316s,
noERROR,no savedinversion,minratio0.95813845. Maximum nodemotion144.048mm.
No inversion is NOT correct bending/wrapping or CableConstraint repair;
force directions differ strongly at large deformation.

1117 prescribed force history is reconstructed from earlier valid1105 guide
frames/cable positions at each beginning clock. Stop208steps/0.520s so load
inputs precede baselinefirstinversion. UsesNativeLinearForceField only;
NOT closed-loop follower force,NOT identical trajectory replay. Actual2.915s,
208outputs,noERROR,but firstinversion0.2425s,tet553,minratio−6.81703. Reject
postinversion states. CableConstraint is not necessary for inversion under
THIS reconstructed external-load history;do not claim original uniquecause.

1118 compares only shared saved prefixes before either firstinversion.
Firststep position difference1.240e-13m for bothlaws. Recorded-history nodal
displacement-relative error0.0002472% at50ms,0.0032406% at100ms,7.2077% at200ms.
These are NOT time-resolution comparisons or timePASS. Later divergence makes
force-history replay non-equivalent;do not transplant its failuretime to1105.
No floor or interpolation used. Work/energy and physicalhardware loadsNULL.

## Decisions and continuation

Mapping/mass component checks PASS ONLY;fulljoint/FEM/grasp remains unqualified.
Neither deadload nor recorded-load replay is an improved actuator candidate.
No renewed highforce100gHolding/Lift justified. Original50gfunctionalLift and
100gFAIL/time/meshFAILs unchanged. Sixnew evidence-scope regressionsPASS.

Next isolate linearized assembled FEM/guide tangent and force-load transfer at
one VALID deformed1105 state (e.g.100ms),using read-only installed API or an
existing validated tangent observer. Compare constrained versus external-load
direction without feeding invalid states back as checkpoints. If no compatible
Native API exists,mark that diagnosticBLOCKED,then design a separate low-load
Skin-only/bonded-Rail coupon rather than another uncontrolled fullgrasp.
Variable stiffness is still NOT IMPLEMENTED;material/jamming/Jointdata absent.

Reproduction with NEWtag only:
`python product_prototype/sofa/b3_guide_transfer_coupon.py --tag UNIQUE --load couple`
`python product_prototype/sofa/b3_reference_wrench_load.py --tag UNIQUE --history`
Inspect1118 read-only:`python -m json.tool product_prototype/results/b3_load_compare1118/summary.json`.
Per-case preflight records actualcommand,sourceScene/binarySHA,SDK,resourceguard;
producer snapshots and Raw preserved. CurrentCAD remains a separate model.

## Continued valid-prefix strain analysis1119

After feature9fc9a1a,inspected existingNativeElasticMatrixObserver:its matrix
query is only atinitialbwdInit;probePositions privately queries forces but NOT
the deformed tangent. Therefore a100ms assembledtangent is NOT MEASURED with
this existing binary. No invalid state or new checkpoint was installed.

Continued with an independent saved-state kinematic analysis instead:original
1105 Skin maximum absolute principalGreenstrain firstexceeds0.01 at147.5ms
(tet539,materialX88.75mm),0.1 at470ms(tet428,X71.25mm),beforeinversion520ms.
Reference-direction deadload1116 exceeds0.1 at165ms despite NO savedinversion;
this explicitly rejects 'noinversion means valid material response'. Recorded
history1117 matchesfirst0.01crossing butexceeds0.1 at220ms before242.5msinversion.
Unloaded1107 crossesneither. The0.01/0.1levels are descriptive markers,NOT
materialallowables/newPASSgates;materialstrainlimits andfailuredataNULL.
Per-time Skin/Rail strain andvolumeCSV retained;postinversion excluded.

Next minimal improvement must address local large strain/loadpath,not just
eliminate negativevolumes. Build a private-deformed-state read-onlytangent
observer only if its cache/state purity can be independently checked,or use
low-loadSkin/Railcoupon with explicit geometry/mass/load definitions. Do not
claim stiffnessgain/jamming or new100gcapacity fromthese diagnostics.
Seven new scope regressionsPASS;prior6inversionchecksPASS. Fresh tags1120+.
