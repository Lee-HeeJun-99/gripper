# First-step gravity RHS1159–1160

Actually continued after1158 diagnostic: reused guarded frozen StepProbe1142,
sampled first step1159,5Native outputs/12.5ms,0.237s,no ERROR. Actual q/v/Guide
prefix differences exactly0 against1129. No state restoration or modification.

1160 independently constructs generalized gravity force G-transpose mf*g,
including attachment lever-arm moments, plus Guide COM masses*g. Native
initial elastic force queried read-only is0; all initial velocities0, hence
no initial gyroscopic term. Eliminates the actual projected root DOFs and
solves sampled Native A v_free = dt f_gravity. Relative errors:
Guide translation9.79e-10,rotation1.91e-9,free translation1.12e-9;
free RHS relative residual6.53e-9. Existing0.1% algebraic check PASS ONLY.
No evidence of missing first-step gravity or incorrect lever-arm moments.

This is not continuous-time accuracy, deformed force assembly, energy balance,
material qualification or Holding certification. Prior time/mesh FAIL preserved.
Early zero-input differences are compatible with unresolved startup dynamics;
do not claim a unique cause or repair. No full100g trial justified by this check.

Next: independent frozen linear gravity transient reference using actual rest
M/K/root and zero-input1127/1157, distinguish expected stiff-mode integration
error from nonlinear/mapping effects. Existing1137 spectrum alone is not this
forced transient. Do not change gravity/control or silently pre-equilibrate.

Read-only restart:
`python -m json.tool product_prototype/results/b3_gravity_rhs1160/summary.json`
Fresh-tag reproduction:
`python product_prototype/sofa/b3_gravity_rhs.py --tag NEW_GRAVITY_AUDIT`
Actual Native command, source/binary/SDK identity:1159/preflight.json.
