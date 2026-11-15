# Actual Beam force: energy-potential obstruction

Status: closed-work experiment **PASS**; exact inherited Beam potential **FAIL**;
complete coupled energy closure **BLOCKED**. Do not use .5*dᵀKd as arbitrary potential.

`diagnostics/closure/EnergyLoop.cpp`, `results/closure_20261115/energy_v3`:
the actual BeamFEM `addForce` is sampled at prescribed configurations, no dynamics,
mass damping, cable or contact. Distal position z and proximal local-frame rotation
θy form a closed rectangle; ∮(F_tip,z dz + τ_prox,y dθy) uses midpoint64/256
panels per side. Spatial y torque is power-conjugate to the imposed planar rotation.
The rest configuration is fixed. Derivative curl is independently finite-differenced.

| Translation amplitude mm | Rotation span rad | Closed work,256panels | Normalized circulation | Cross-derivative curl |
|---:|---:|---:|---:|---:|
|.001|.00002|4.36438456e-15|2.77963e-8|-2.09199e-7|
|.01|.0002|4.36438452e-11|2.77962e-6|-2.09110e-5|
|.1|.002|4.36437901e-7|.0002778851|-.00209109|
|1|.02|.004363827088|.02704147|-.20909573|
|5|.1|2.719040316|.40929343|-5.21944379|

Work units=model force·mm. First three are within the old planar-angle range;
last two are separate Beam-only mathematical diagnostics, NOT valid LayerNetwork
grasp performance. Coarse/fine circulation converges (relative difference≈1e-8),
so it is not removed by integration refinement. `energy_audit.json` contains exact
rows and curl. A distal-frame-fixed control gives roundoff circulation; that
restricted control alone did not test frame dependence. Initial incorrect relative
SDK path and inadequate controls are preserved in `energy`/`energy_v2`.

Nonzero converged circulation and cross-derivative mismatch obstruct a general
state potential for this actual implementation/rotation convention. This does not
prove every possible corotational beam model is nonconservative. A separately
implemented energy-derived beam would need new force/tangent/dynamic regression;
silently changing the validated original Beam to achieve energy PASS is prohibited.

The intended balance is Δ(K+U)=W_external+W_cable+W_parameter−D_friction−D_Rayleigh−D_numerical.
Contact elastic/slider dissipation are partial observable terms; fixed-grid
detachment estimate and actuator parameter work are not exact full-system closure.
FrameLayerNetwork own pressure dissipation is in layer0/1/2.csv because the original
recorder does not identify this distinct class. Missing terms are never set to zero.
No closed global energy certificate or grasp objective is issued.

Next: independent variational beam component, identical EA/EI/BC/load comparison,
then energy-derived actuator/contact bookkeeping. Old golden Beam remains untouched.

Actual live three-finger field isolation also finds Beam resultant moment
−2.2629438920710246e-5force·mm aboutY. Thus the global moment issue is not merely
a missing energy observer, nor resolved by excellent local free-object residuals.
`threefinger/field_balance/summary.json` preserves each field separately.
