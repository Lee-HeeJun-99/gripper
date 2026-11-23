# Full-joint scope and reference energy1168–1172

Continued after coupon1166/1167 rather than stopping at its PASS.
1168/1169 actual Native full-joint zero-Cable/no-object gravity trials:
same Rail-back rest FEM/Guide mapping/mass/root,100ms,40/80 outputs,
runtime0.568/0.906s. Field coefficients0; ODE alpha1/beta1e-4. Global alpha
also damps Guide mass,so this is explicitly a NEW damping law/configuration,
not physically identical B3 or latest fabrication CAD. No SDK/solver changes.

1170 actual40 common outputs,clock mismatch≤1.39e-17s:
Skin30.4992%,Rail30.4983%,velocity174.325%,curvature30.1161% relative errors.
Existing0.1% Gate FAIL. Min volume ratios0.9999689/0.9999644,small strains,
no inverted saved elements. No relative floors/interpolation. No full100g,
Holding or Lift. Correct linear damping semantics do NOT cure time resolution.
Do not promote this candidate or change old verdicts.

1171 independent energy accounting uses actual Native linear-coupon q/v and
initial Native K,NOT Native potential-energy API or measured heat. For backward
Euler, deltaE=dt f*v_new - dt v_new*C*v_new - .5 deltaV*M*deltaV
- .5 deltaX*K*deltaX. For field A-only contract replace velocity damping work
by dt v_new*C*deltaV,which is signed algorithmic work,NOT viscous dissipation.
At100ms ODE reference numerical loss6.754e-8J,viscous work3.748e-9J;
maximum selected-contract residual relative6.869e-9. Field selected-contract
residual≤4.785e-9. No whole-gripper energy PASS: API/global energy NULL.

1172 figures use actual accepted Native states and explicitly labeled linear
reference ledgers,not prescribed shapes or concept rendering.

Next independent audit: cross-check continuous reference with proportional
modal closed-form solution and conditioning,then determine relevant forced
response modes before any integration-setting experiment. No arbitrary dt,
alarm,force,stiffness sweep. Actual nonlinear deformed damping/RHS must still
be verified before adopting ODE damping in force-controlled B3/100g trials.

Reproduction (fresh tags only):
```bash
python product_prototype/sofa/b3_ode_gravity_candidate.py --tag NEW_BASE
python product_prototype/sofa/b3_ode_gravity_candidate.py --tag NEW_HALF --half
python product_prototype/sofa/b3_rail_back_assess.py --tag NEW_PAIR --base NEW_BASE --half NEW_HALF --short none
python product_prototype/sofa/b3_linear_energy_contract.py --tag NEW_ENERGY
python product_prototype/sofa/b3_gravity_validation_plot.py --tag NEW_FIGURES
```
All Native preflights contain source/binary/SDK/command;4GiB/60s limits.
Related scalar reference workers4GiB/120s. Existing Raw unchanged.
