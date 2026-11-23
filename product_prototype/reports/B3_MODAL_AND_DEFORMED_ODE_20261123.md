# Reference cross-check and deformed ODE diagnostic1173–1175

Continued after actual full-joint time FAIL1170.1173 independently compares
proportional-damping modal closed form with affine matrix exponential using
coupon1166 K/M/f. No clipped modes, no fitted frequencies. K antisymmetry
5.82e-17; eigenvalue ratio2.915e9. Relative agreement9.70e-10 at2.5ms,
7.52e-7 at100ms. This validates the limited linear continuous reference,
not actual nonlinear dominant modes, mesh or B3 time convergence.
Lowest frozen frequency about28.55Hz; coarse2.5ms omega*dt≈0.448,
so large backward-Euler startup damping is plausible even for that mode.
Do not claim all actual response is this mode or prescribe blind dt reduction.

Actually extended read-only StepProbe input allowlist, no C++/SDK rebuild.
1174 actual ODE gravity candidate sampled50ms,previous47.5ms;24outputs,
0.436s; all q/v/Guide prefix differences EXACT0.1175 same-state matrix:
A=(1+dt alpha)Mtotal+(dt²+dt beta)G-transpose K G matches2.03e-16relative.
Free-motion RHS Mtotal*v_previous+dt*(mapped Native elastic+gravity) gives
velocity4.34e-9relative,RHS6.27e-10. Both Cable impulses0 as declared.
Optional mapped centripetal-term hypothesis also lies below0.1% at this small
response (velocity2.38e-7); hence this sample cannot uniquely certify or
reject convective inertia. No missing term was patched or force fitted.

Global ODE damping contract is thus verified at one small-deformation free
step ONLY. Force-controlled large-deformation B3 still NOT QUALIFIED.
All previous time/mesh/100g/energy failures retained. No new Holding/Lift claim.

Next bounded task: declare separate ODE-damped single-finger C2 force candidate,
retain existing input magnitude and geometry; sample a still-valid deformed
state, verify actual free-motion versus Cable correction and element quality.
Must record global Guide damping change,not call it identical old B3. If
quality fails,stop; do not launch100g or arbitrary force/dt/solver sweeps.
Native constrained higher-order alternatives previously failed; no custom ODE.

Read-only resume:
`python -m json.tool product_prototype/results/b3_ode_deformed_rhs1175/summary.json`
Reproduction uses fresh tags with b3_step_probe.py --sample .05
--reference b3_ode_gravity_base1168 and b3_ode_deformed_rhs.py.
Reusable compiled StepProbe1142 hashes verified,4GiB/120s; no SDK modifications.
