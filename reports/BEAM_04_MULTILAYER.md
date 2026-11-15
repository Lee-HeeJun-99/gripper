# BEAM04 — new beam in100mm multilayer structures

Status: **PASS recorded structural equilibrium cases; research assumptions.**
Raw `results/beam_20261115/multilayer`, plans/campaign JSON alongside it.
LayerNetwork force/rotation convention and original code remain unchanged.
Each layer has independent Rigid3 DOFs, same per-layer circular EA/EI, root6DOF
fixed, zero gravity,total tip force1e-6 shared among layers,12s and dt.0005.
All compared runs use mass damping2/stiffness.1 and EigenSparseLU.

|Layers|FREE tip mm|k100 tip mm|Initial ON relative residual|
|---|---:|---:|---:|
|2|.0155868023894037|.00925372386568045|.000278132727|
|4|.00779340134056784|.00236090660095968|.000678742087|
|8|.00389670068851688|.000593995436203677|.001250693341 FAIL|

The8layer standard Euler case remains FAIL, not relabeled. Independent
`tests/test_beam_precision.cpp` verifies translation-only compensated updates
against the NEW beam energy gradient and sub-ULP increments at100mm.
Only then the existing public accumulator component was added to a separate
no-object/no-cable structural scene: tip.000593995436079752mm,
residual2.92195809780e-5 PASS. It changes summation precision, not forces,
tolerances, object positions, rotations or hidden reaction constraints.
Never applied to the free-object grasp or its quaternion DOFs.

8layer follow-ups: `multilayer_followup.json` and their raw metrics.
Halfdt residual2.52378433217e-5,21node residual3.25020801214e-5 PASS.
21node tip.000592264440018427mm; mesh variation≈.2923%, below1% diagnostic.
Extended18s:residual2.63612529720e-5,tip.000593995436417194mm PASS.
Equal-total-material4layer:residual.000792414912152,tip.00943232255308mm PASS.
These are separate cases, not retroactive replacement of the initial8layer FAIL.

The main2/4/8 comparison adds material as layers increase. Equal-total-material
study rescales A∝2/N,I,J∝(2/N)² for circular similar sections and scales mass
using the existing generator. It is NOT the same as fixed film thickness or
fixed stacking thickness. A full same-total-thickness/PET-family study remains
NOT RUN. No real vacuum/material validation follows from these elastic results.

Fair OFF references were independently run with identical numerical/section
conditions:8layer compensatedFREE tip.00389670068851689mm,residual2.86527e-6;
4layer equal-total-materialFREE tip.0311727328986975mm,residual2.59562e-5.
Both PASS. Evidence `matched_structural_ratios.json` computes ratios only from
the matched equilibrium pairs,not from mixed compensation/section conditions.
