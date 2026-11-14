# Integrated research components, separate from certified models

This module does not modify `plugin/`, `models/finite_rotation/` or `models/multilayer/beam.py`.
Units: model F, mm, s; stiffness F/mm, E F/mm², pressure F/mm², energy F·mm,
mass F·s²/mm. None is calibrated PET/vacuum hardware data.

## LayerNetwork

0 = linear-in-planar-angle conservative springs. Adjacent-layer energy is the certified
`s=Delta u-h*(theta_l+theta_u)/2`, `E=.5*k*s²` generalized to multiple layers and point selections.
1 = independent prescribed-normal-pressure elastic-perfectly-plastic sliders:
`N_i=p*A_i`, `cap=mu*N_i`, `t=clip(k*(s-z_old),±cap)`, `z_new=s-t/k`.
Static and kinetic mu are assumed equal. Tributary areas partition the assumed width×length;
actual seal pressure, normal contact distribution, vacuum leakage and opening are not solved.
Force/Jacobian evaluations never mutate history. Plastic offsets and nonnegative dissipation
are committed on AnimateEnd only. Stored elastic energy is not a conservative potential for
the full friction evolution; the single-slider cycle work/dissipation balance is tested separately.

Modes 0/1 are restricted to planar rotations <0.005 rad. Normal confinement, when enabled,
is an additional linear bilateral centroid-gap penalty, not an actual contact-pressure solve.
It is only used in small-planar research scenes. 2 = existing objective finite-rotation elastic
connector kernel; it is not a finite-rotation friction model or a large-deformation film certificate.
Do not combine finite-rotation mode with the linear normal-confinement approximation.

## RoutedCable

Material guides `a_i=p_i+R_i*(0,0,offsetZ)` define exact polyline length
`ell=sum ||a_(i+1)-a_i||`. Prescribed tension uses potential `T*ell`;
length control uses `.5*kc*max(ell-ell_initial+shortening,0)^2`.
Forces/torques are energy gradients. The global tangent contains both length Hessians and
the rank-one stretching term, with the SO(3) spatial connection correction. Actual all-18-DOF
finite differences of the full routed component test both control modes.
Commands are explicit step schedules; contraction is not assumed to equal motor stroke perfectly.
The route/offset is a research assumption. There is no wire-guide friction, sheath compliance,
measured routing, hardware motor or real cartridge model.

## AnalyticContact

Sphere, infinite local-y cylinder and axis-aligned-in-object-frame box signed distance
give tension-free penalty energy `.5*kn*min(distance-pointRadius,0)^2`.
Finite 3D attachment/object rotation derivatives are differentiated independently of detection.
For box edges/corners and the center of sphere/cylinder the SDF is nonsmooth/singular;
smooth-branch finite differences do not certify those events. Samples are nodal collision points,
not a continuous swept film surface; spatial collision sampling convergence remains necessary.
There is no object tangential friction. Fixed objects benchmark detection/response only.
A free-object negative control is not a stable grasp. The grasp eligibility gate rejects it and
blocks full grasp-design optimization until enclosure/friction and a perturbation envelope exist.

## Recorder and evidence

The recorder saves full sampled rigid positions/velocities and scratch static residuals,
plus component energy/dissipation/cable/contact diagnostics. `stride` is recorded and trajectories
are sampled, not claimed to contain every integration step. BeamFEM's total energy API is absent;
component diagnostics are NOT a complete coupled-system energy audit.
Every trial has config, command, source/binary identities, exit/log checks and artifact hashes.
Only actual equilibrium results receive effective stiffness, and transient experiments do not
become optimization performance merely because the engine finished.
