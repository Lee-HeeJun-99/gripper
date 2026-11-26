# Protection window — not yet qualified

Actual new control: `validation/overload/jam_energy2/summary.json`.
The original NameError is preserved under jam_energy1, not relabelled PASS.

A published minimum torque must not be interpreted as a maximum. The
[HPMC-2.5 drawing](https://www.magtrol.com/wp-content/uploads/hpmc-25.pdf)
labels2.5oz-in **minimum**. The [manufacturer data sheet](https://www.magtrol.com/wp-content/uploads/hpm-hpmc.pdf)
describes a permanent-magnet air-gap transmission, not an uncontrolled clamp
slip. This is a distinct candidate mechanism, not an adopted or rated force cap.
Its dimensions/shaft interface differ from current stepped coupling. A web STEP
link returned a brake-named HPM file, not confirmed HPMC clutch geometry; do
not silently substitute it. No manufacturer model is claimed imported.

For a blocked distal end, linear cable stiffness k, load-side inertia J,
constant driving force F=tau/r and initial tension T0, conservation of energy
to first turning point gives:

`Tpeak = F + sqrt((T0-F)^2 + k J omega^2)`.

This includes positive drive work during arrest. Merely adding initial kinetic
energy to spring energy while dropping ongoing input work underestimates peak.
Independent solve_ivp integration and halved maximum steps agree with the
analytic result within6e-12 relative for the declared scenarios. Energy residual
<6e-14J. These are model verification results, not real tension measurements.

At reference torque0.01765388Nm/minimum radius11.165mm, F=1.58118N. Assumed
k=10000N/m,300rpm, provisional five-part J=3.10399e-6kgm2 and initial
T0=0.968626N give7.14987N, not1.58118N. Even zero initial speed gives2.19373N
under a sudden unbalanced constant input. These are counterexample scenarios,
not operating envelopes or a bound on omitted inertia. Added limiter inertia,
actual EA, contact waves, thermal/rate dependence, torque maximum and maximum
speed remain necessary before assigning a protected structural load.

Existing 40.3N reference remains preserved; no low-load envelope replaces it.
Next: actual limiter interfaces, rated torque extrema, independent speed/energy
budget and guarded calibration fixture. No hardware/purchase authorization.
