# HISTORY 05 — energy inventory, not artificial closure

Status: **BLOCKED full coupled closure; PASS partial recorded inventory**.

`tools/history_energy.py` evaluates the unchanged Beam strain energy on2401
actual saved SOFA states, plus the exact configured isotropic diagonal-mass
kinetic energy. `energy_partial/journal.csv` joins contact stored tangent energy,
plastic/detachment dissipation, layer dissipation and pressure by time label.
At24s, Beam energy4.31441548227e-20 and kinetic energy1.13726290154e-20
(model F·mm units). These are computed from simulation, not measurements.

Important synchronization limit: state is after AnimateEnd, while the existing
contact recorder reports pre-commit trial energy with that event's label.
The new tool explicitly records this limit. Merely matching timestamps does
NOT establish a force-stage-synchronized journal. Layer stored energy,normal
contact energy,actuator work,pressure work,Rayleigh stiffness loss and total
closure are `null`, NOT zero. Missing values prohibit full closure.

Independent flat-slider identity at fixed cap:
`F_end*du = delta U + C*|du_plastic| + kt*|delta e|^2/2`.
The last term follows algebraically from backward-Euler spring work, not from
fitting an unexplained system residual. Actual test W=.0009,U=.0000405,
Dplastic=.000819,D_BE=.0000405,residual-6.78e-20. This is a local prescribed
slider identity, NOT a derived whole nonlinear SOFA integrator energy theorem.

Next required change: journal force-stage poses,controller values,mass/stiffness
damping work and pre/post-return inventories at EACH engine step. Pressure
switches and contact birth/death need explicit event budgets. Parameter work
must not be reconstructed as whatever global residual closes the balance.
