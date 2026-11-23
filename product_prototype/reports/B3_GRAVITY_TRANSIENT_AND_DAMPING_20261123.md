# Gravity transient / Native damping contract1161–1165

Started at4c6bd43, clean branch. No old trials repeated unchanged.
1161 independent rest-linear forced gravity reference: actual M/K/G/root,
declared field Rayleigh coefficients, exact affine matrix exponential and
backward Euler,4GiB/120s guard,3.882s. First2.5ms frozen discrete vs continuous
Skin displacement41.8753% (42.980µm L2); Native base first step matches the
frozen discrete state5.03e-9 relative. Later discrepancy cannot be assumed
pure integration error; max Native-vs-frozen discrete7.526%. This was an
explicit physical velocity-damping assumption, not verified Native contract.

1162 actual Native no-Guide/no-Cable/no-contact coupon: same curved full
Skin/Rail mesh/body mass/root, method=small linear FEM, gravity9.81. Separate
model: no Guide mass or mapping.40steps/100ms,0.506s,no ERROR. Existing frozen
observer410 extracts initial K.1163 independent physical-damping recurrence
FAIL: maxq2.559%,v18.543%; firststep≈3.01e-9. Full failure retained.
Continuous comparison in1161/1163 is CONDITIONAL on that damping assumption,
not proof of true Native continuous response.

1164 removes ONLY matrix/FD observer, actualNative40steps/0.421s. Entire
q/v output matches1162 EXACTLY. Observer cache pollution not supported.
1165 tests four exact algebraic recurrence hypotheses, fixed coefficients,
no fitting/no state changes. A=M+dt(Cm+Ck)+dt²K in every hypothesis:

|RHS velocity coefficient|max q relative|max v relative|
|---|---|---|
|M (physical velocity damping)|0.0255913|0.185433|
|M+dt Cm|0.0197847|0.144576|
|M+dt Ck|0.00633774|0.0471852|
|M+dt(Cm+Ck)|5.633e-9|7.164e-7|

Thus the actual isolated coupon follows the A-only field-Rayleigh recurrence
to high accuracy, not the assumed velocity-damping law. This discriminates
an installed Native configuration contract; NOT a universal SOFA bug claim,
not a nonlinear B3 cure. No existing FAIL is relabeled. Full physical/time/
mesh/energy/material/joint qualification remains open.

Completed next actual contrast1166/1167: field coefficients0, same nominal
alpha1/beta1e-4 on Native EulerImplicitSolver. Actual Native0.472s/40outputs,
no ERROR. Physical velocity-damping recurrence now matches all outputs:
maxq9.747e-9,maxv7.393e-6 relative,0.1% algebraic Gate PASS ONLY. Rest K hash
identical to1162. Configuration/law distinction,not coefficient magnitude
tuning or retroactive repair of old B3. Continuous-time errors still large;
no time/mesh/grasp/energy qualification. Proceed to bounded full-joint zero
Cable contrast,explicitly accounting for new global Guide damping too.

Original next action (now completed): field coefficients0, same nominal alpha1/beta1e-4 on
Native EulerImplicitSolver instead. Check actual A and intended recurrence;
explicit configuration/law change, not retroactive reinterpretation of B3.
Do not tune coefficient magnitude or damp velocities in postprocessing.

Raw: results/b3_gravity_transient1161,b3_linear_gravity_coupon1162,
b3_linear_gravity_assess1163,b3_linear_gravity_unobserved1164,
b3_linear_damping_contract1165. Commands/source/binary identities in each
preflight/producer/process/input_hashes. Fresh-tag reproduction via respective
sofa/b3_*.py --tag NEW_CASE; no old paths overwritten. Native SDK unchanged.
