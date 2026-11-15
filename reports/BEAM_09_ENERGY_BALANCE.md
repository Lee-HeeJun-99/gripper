# BEAM09 — energy audit

Status: **PASS new-beam potential/virtual work and bounded single-beam dynamic
ledger; BLOCKED complete coupled grasp energy closure.**

All terms use F·mm and the actual spatial torque convention. A conservative
discrete beam potential now exists and its derivative/closed-loop work are
independently checked (BEAM02). The inherited `.5*dᵀKd` expression is not reused
as a finite-rotation energy. Rest/deformed beam energy is never assumed zero.

`diagnostics/conservative_beam/DynamicEnergy.cpp` queries actual SOFA mass,
kinetic energy,beam potential and tangent on each step. Constant tip force,
isotropic mass,α2/β.1,3s,dt.001/.0005/.00025:
normalized unclosed residual −4.98837e-12,−5.23120e-13,+2.80783e-14.
At dt.001:Wexternal3.13888518168e-8,U1.58028072190e-8,K5.78698842109e-14,
Dmass9.52642640336e-9,Dstiffness5.99967261609e-9 F·mm.

The backward-Euler linear energy identity is derived, not fitted:
`Dmass=α*h*v1ᵀMv1`, `Dstiffness=−β*h*v1ᵀJ0v1`,
`Dimplicit_linear=.5*ΔvᵀMΔv−.5*h²*v1ᵀJ0v1`.
External work=hF·v1. Any nonlinear leftover remains a separately reported
`unclosed_residual`; it is NOT defined to be a convenient numerical dissipation.
The observed tiny residual is specific to these very small beam loads, not a
large-motion proof for every inertia or integrator.

For the full grasp, cable command work, changing pressure/normal preload work,
stored elastic tangential state, release loss, layer friction and Rayleigh work
need a synchronized stagewise ledger. Existing contact cumulative dissipation
passes its nonnegative/monotone subcheck, but this does not close all those terms.
These missing integrals are not substituted with0. Full beam+cable+layer+
parameter+contact dynamic ledger and complete hold/release energy closure remain
BLOCKED/not qualified, and continue to block grasp-objective optimization.
