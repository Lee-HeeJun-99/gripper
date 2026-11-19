# Native refined Rail precision diagnosis — 2026-11-19

Feature commit: c50516b. Source before experiments: ba026aa87264b5bd431573fa82d4a75c1baae172.
Scope: installed SOFA BeamAdapter static straight Rail, E=250MPa, rectangular
2mm × 0.5mm, length100mm, centered coordinates, load1e-8N. No contact,
Cable, Skin, mass integration or B3 qualification. Existing results remain unchanged.

## Implementation and actual experiments

454 adds read-only per-node native force/torque and initial tangent diagnostics
to the failed41/81node cases449. FAILED filenames explicitly prohibit accepting
these frames as equilibrium states. Frozen observer451 is reused.

455 queries the actual native force at PRIVATE copies of those failed frames
and at one-coordinate ±1ULP perturbations. These poses are never installed into
MechanicalObject. Actual unloaded geometry is unchanged (error0); baseline
queried forces exactly reproduce454. This is force-query evidence, not a solver.

456 adds lengthToM to the read-only accepted-state observer. Positions and torques
are exported in SI; native forces and actual states are not changed.
Frozen binary SHA:16fa6e24f192a46779eea712fa1381eb1adbbb3143b200cdf6e1e7f9ba782bd1.
Frozen C++ SHA:831fd04b007973d2554f661ba6ff65c406713591409fbb55c64f5c61768b9a3f.
Build:product_prototype/cad/build_unit_observer456.
SDK:/home/ubuntu/SOFA/v26.06.00; no SDK files edited.

457 changes only static length-unit representation to N-mm-s: geometry ×1000,
Young modulus /1e6; force and physical dimensions unchanged. Native mixed
force/torque stopping norms are not unit invariant. Independent SI force1e-12N,
torque1e-12Nm and state1e-12m gates remain unchanged. This is NOT dynamic equivalence.

| Nodes |454 failed-frame axial residual N|455 one-ULP force change N|457 SI force residual N|457 verdict|
|---|---:|---:|---:|---|
|21|NOT MEASURED|NOT MEASURED|6.64363e-13|PASS static force only|
|41|1.34812e-12|1.69967e-12|1.29701e-12|FAIL native solve|
|81|2.59047e-12|3.39935e-12|2.70981e-12|FAIL native solve|

The axial coordinate perturbation is6.938893903907228e-18m. It produces changes
larger than the force gate. This supports representation sensitivity, but does
NOT prove that no representable equilibrium exists. Initial-tangent half-ULP
envelopes are estimates, not error floors or bounds on nonlinear equilibrium.
No coordinate correction is adopted.

457 coarse21node SI-control position difference3.469446951953614e-17m,
velocity difference0. Fine41 native line search/nonconvergence remains FAIL;
81 process was stopped by the nonlinear-failure guard (exit−9), not evidence
of OS memory exhaustion. Failed diagnostic output is never promoted to PASS.

## Decision and next hypothesis

Unit scaling alone does not resolve fine-mesh force residuals. Stop this direction:
no arbitrary origins, tolerances, loads or unit sweeps. Mesh qualification remains
FAIL. Previous B3 functional50g Holding344/351 and release375 remain narrow
functional observations, NOT validated mesh/time/grasp performance.

Next independent check: at the frozen failed41/81 PRIVATE states, compare the
native current tangent/directional derivative with symmetric finite differences
using a documented perturbation ladder and SI translation/rotation units.
Separate the initial tangent (already verified432/439) from the loaded tangent.
Reject cancellation-dominated FD values explicitly. Do not alter actual q or
create a new ForceField/solver. Only pursue a stock component remedy if that
test establishes a discrepancy; otherwise retain the model as unqualified.

## Reproduction and evidence

Run from repository root; unique tags required:

```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/native_beam_refined_diagnostic.py --help
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/native_beam_ulp_probe.py --help
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/native_beam_unit_scale.py --help
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/native_beam_units457/summary.json
```

Exact executed scenes, process commands, producer snapshots, source/binary hashes,
SDK linkage, limits and measurements are in:
product_prototype/results/native_beam_refined_diagnostic454,
product_prototype/results/native_beam_ulp_probe455,
product_prototype/results/native_beam_units457.
Immutable evidence:product_prototype/reports/evidence_native_refined_v16/manifest.json.
Root work, full energy, friction grasp, CAD STEP,100g and Lift:NOT MEASURED/NOT RUN.
No physical child is intentionally left running; no automatic continuation promised.

