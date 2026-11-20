# Native loop intervention and elastic-wire alternative — 2026-11-20

## Scope and preservation

Continuation from c0ca121/35bee42. Campaigns692–703 are NEW causal interventions,
independent references, actual API probes and regression checks. Old Raw,
verdicts, B3 scenes/checkpoints and installed SOFA SDK are unchanged. No new ODE,
contact, FEM or force algorithm was implemented. No B3/100g/Lift/STEP PASS.

Source SHA is the parent of a working snapshot. Each producer.py, generated scene,
compiled C++ snapshot, binary and SDK hash is authoritative, not parent SHA alone.
Archive: `evidence_product_elastic_tendon_v35/manifest.json`:7264files,12cases;
6812previous immutable hashes checked without mismatch.

## Cycle A: actual loop intervention692

Same685 two1g points,1000N/m rest springs,1N/point,dt250us,20ms. Change ONLY loop
in existing graph. Existing685 FreeMotion results reused, not re-executed.

- DefaultAnimationLoop + Native Euler + external force agrees with independent
  discrete BE: position6.51e-19m,velocity4.45e-16m/s maximum error.
- DefaultAnimationLoop + Native Newmark + external force agrees with independent
  average-acceleration scheme: position9.90e-19m,velocity1.00e-15m/s.
- DefaultAnimationLoop + CableConstraint: positions/velocities remain0; FAIL,
  despite no Native ERROR messages. This loop is NOT a proposed Cable solution.
- Installed deprecated ConstraintAnimationLoop in this graph segfaults(-11),
  with partial trace retained. No physics conclusion from partial outputs.

Together with685/688 this causal contrast localizes the Newmark state mismatch
to the constrained-loop path, not Native Newmark free integration alone. This
does NOT validate DefaultAnimationLoop for Lagrange Cable/contact processing.

## Cycle B: separate Native elastic-wire physical candidate693–696

Native SpringForceField `elongationOnly=1`,zero damping,FixedProjectiveConstraint
on anchor,DefaultAnimationLoop,NativeEigenSparseLU. One free1g Vec3 point;fixed
anchor has another1g but no motion. Assumed k100N/m,initial length100mm,rest90mm,
initial stretch10mm and tension1N. These are research assumptions,NOT measured
wire properties or an equivalent prescribed-tension CableConstraint model.
Initially slack control uses rest110mm. No gravity/contact/guide/pulley/sliding.

Exact reference,omega=sqrt(k/m),e0=.01m:

    taut: z=e0(1-cos(omega*t)), v=e0*omega*sin(omega*t)
    release: t*=pi/(2*omega)=4.96729413289805ms
    slack: z=e0+e0*omega*(t-t*), v=e0*omega

This is a mathematical reference, not a prescribed Native trajectory. Actual
Native states are saved at250/125/62.5us through8ms. Anchor displacement0 in all.

693 Native Newmark runs;initially slack control has EXACT zero motion. Actual
moving-point displacement error12.0798/4.40842/1.97355um,velocity error
.00133324/.000795995/.000489039m/s. Reconstructed energy defect4.21520/2.51684/
1.54636uJ from initial.005J,NOT physical heat or global energy qualification.

694 independently reproduces the old-state-tangent Newmark recurrence:

    f_n=k*max(e0-z_n,0); K_n=-k if z_n<e0 else0
    a_next=[f_n+K_n(h*v_n+h²*a_n/4)]/[m-h²*K_n/4]

Position agreement<=5.56e-17m,velocity<=3.56e-15m/s,STRICT1e-12 PASS for this
discrete reference. At first sampled slack state5ms,extrapolated acceleration
is -9.52/-10.14/-10.29m/s² while physical slack acceleration is0. This is NOT
a claim of an accepted-state Native force callback evaluating compression.
All-time/all-pair0.1% Gate FAIL: worst base-quarter tension1.052646% at4.75ms.

693's preliminary full-q relative metric contains the fixed anchor;694 explicitly
compares MOVING-POINT DISPLACEMENT,velocity,tension,energy,with no relative floor.
Use694 for the authoritative moving-point time comparison. Original693 is kept.

695 changes only the Native ODE configuration: BDF1 + Native Newton,50iterations,
1e-12 relative/1e-14 absolute residual thresholds.696 proves agreement with exact
piecewise nonlinear BE equations:position<=6.87e-16m,velocity<=1.54e-13m/s.
Discrete slack acceleration0. Initial slack control remains exactly stationary.
Nevertheless physical velocity error.189430/.0962038/.0485533m/s, and energy
defect.581089/.299596/.152360mJ. All-pair0.1% Gate FAIL; moving displacement
base-quarter first-common-time relative difference37.1953%. No floors/exclusions.
Nonlinear branch consistency does NOT eliminate first-order integration error.

## Cycle C: actual Native potential API mismatch697–698

Read-only NativeSpringEnergyJournal calls the actual virtual potential API at
accepted states.697 q/v/force-slot output equals693 EXACTLY with observer on/off.
Initially slack wire has zero velocity and zero actual force slot, but stock
Native potential returns.005J. Taut-release potential disagreement reaches
.00458707J. This is an API mismatch, not real stored slack-wire elastic energy.

698 independently perturbs INITIAL free-point z by±1um. These are mathematical
probes,NOT driven motion. Actual Native potential .00499900005/.00500100005J
gives dU/dz=1.000000000001N; actual free motion and force slot both0.
Native installed SpringForceField.inl getPotentialEnergy sums squared elongation
without the force routine's elongationOnly/activation test. Installed code/library
hashes are preserved. No SDK modification or subtraction of residual as heat.

## Cycle D: potential-only compatibility module699/702

After the Native deficiency was independently demonstrated, added OPT-IN
`ReGripTensionSpringPotential`, a NativeSpring subclass overriding ONLY the
potential API. Native addForce,addDForce,matrix assembly and integration are
INHERITED UNCHANGED. No new force law or state writes. Native input parameters,
states and dynamical evolution are not replaced.

For enabled springs: U=.5*k*extension²,with extension clipped at0 only for
elongationOnly springs;disabled springs contribute0. The actual validation scope
is enabled,nondegenerate,zero-damping,tension-only Vec3 coupons,NOT all possible
Native spring configurations or coincident endpoints.

699 four actual Native cases:taut-release,initial slack,slack±1um. Entire saved
q/v/force-slot journals equal unmodified Native EXACTLY. Actual potential error
<=8.68e-19J;slack API FD gradient0. PASS POTENTIAL-ONLY SCOPE.

702 tests the separate Native BDF1/Newton graph because line search might consult
potential:entire saved states,force-slot,Newton status AND residualGraph are
EXACTLY unchanged;actual potential reference error<=8.68e-19J. No rebuild/retry
of697/699 binaries. This is not a general Newton-graph purity theorem.

The adapter is NOT applied to B3 or to old checkpoints. It fixes an energy API,
NOT the693/695 time Gate, contact-loop contract,wire-material calibration or grasp.

## Evidence, runtime and visualization

700 fourteen regression tests PASS;703 fifteen PASS,including actual Newton API
purity and old failures. These are validity regressions,not15physical Gates.
692–702 contain27actual Native child attempts;one segfault preserved. All other
26completed without SOFA ERROR,not automatically physics PASS. Max Native runtime
.269787s;C++ builds<=5.74s. Each build/Native child4GiB/480s,executed sequentially;
RSS NOT MEASURED. No background physics process is promised.

701 actual Native plot:
`results/b3_native_elastic_visualization701/actual_native_elastic_tendon.png`.
It distinguishes actual states/API,analytic reference and energy reconstruction.
3D matplotlib import warning does not affect the inspected2D figure.
Root reaction/work,contact work/pressure/area and physical wire data NOT MEASURED.

## Decision and next meaningful work

Stop promoting this elastic alternative into B3:time Gate fails even without
contact,and wire axial stiffness/density/preload/sliding are not calibrated.
Stop the old constrained Newmark candidate without a validated loop contract.
No blind dt/alarm/stroke/parameter repeats or unvalidated custom loop development.
These are reproducible technical/model-validity limits,NOT OS resource exhaustion.

The potential-only module is reusable for independent tests,not a production
grasp model. A meaningful next change is a validated Native constrained-loop
integration contract using matching source/upstream-compatible correction,or
measured elastic-wire parameters defining a distinct physical prototype. Neither
is supplied by the present coupons. Physical guide/join mass,original FEM/contact
mesh/time Gates,interference,100g/Lift/recovery/STEP remain open.

Read-only resume:

```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_native_loop_intervention692/summary.json
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_native_spring_potential_adapter699/summary.json
```

After a SPECIFIC new implementation/physical hypothesis only:

```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/contact_policy_test_run.py --tag UNIQUE_REGRESSION
```

Known reproduced Native reference,not a new hypothesis on its own:

```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/native_elastic_tendon.py --tag UNIQUE_ELASTIC --ode bdf1
```
