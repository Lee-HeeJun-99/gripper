# Independent multilayer static research model

Every layer has axial u, transverse w and Euler–Bernoulli phi=dw/dx; roots are clamped.
EA and EI are independent explicit inputs. The optional Timoshenko element uses
`psi=12EI/(kappa*G*A*dx²)` and reproduces the analytical transverse-shear compliance.
The inherited circular-equivalent A is not an 8×0.4 mm rectangular film section.

Adjacent-layer energy is `0.5*k*(u_upper-u_lower+h*(phi_l+phi_u)/2)^2` at selected nodes.
All-interface slip and selected-connector slip are reported separately. Point-spring k has units F/mm;
increasing connector count at fixed point k changes the design, not just the mesh.
Same-design mesh tests preserve physical connector positions and count.

The ideal wire model is a prescribed eccentric terminal moment T*e. It has no cable routing,
friction, follower forces, anchor or sheath mechanics. Tip contact is a planar unilateral penalty:
`reaction=kc*max(0,-gap-w_tip)`; no attractive force. It is not multi-body SOFA contact or a stable grasp.

The separate friction solver prescribes compression rather than solving a seal/normal contact:
`N_i=p*A_i`, `capacity_i=mu*N_i`, `traction_i=clip(k*(s_i-z_old), ±capacity_i)`,
`z_new=s_i-traction_i/k`, `D_i=capacity_i*abs(z_new-z_old)>=0`.
Tributary interface widths/areas are research assumptions, not measured vacuum load distribution.
Constant-pressure load cycles test yielding, hysteresis and dissipation. The single-slider closed
cycle work balance is independently tested. Full coupled pressure-work thermodynamics, opening,
pressure transients and real PET friction calibration are NOT implemented/certified.

JSON checkpoints bind design/pressure/mu/width and the state payload hash. A continued cycle is
tested against uninterrupted integration, including corrupt/mismatched checkpoint rejection.
This is static FEM state restart, NOT a SOFA checkpoint or Optuna SQLite resume test.

The ±20% sensitivity band is a declared numerical assumption, not measured uncertainty.
Small planar rotation <0.005 rad remains an eligibility gate; results beyond it are not valid performance.
Parameter combinations can be explored, but only tested configurations are claimed to pass.
