# Separate-layer unilateral contact — small-load evidence only

Actual RevAB dimensions: rails88mm, PET87.4mm, last4.4mm in a finite front/rear
guide channel with0.10/0.20mm nominal gaps. PET and rails have SEPARATE beam
degrees of freedom; no common curvature or distal axial bond is imposed.
Friction is0 as a declared limit, not a measured property. Applied transverse
test-fixture force±0.001N; this is Stage2 structural Coupon, not Stage3 closure.

Initial `sliding_contact1` FAIL: OSQP reported solved, but16/32element opening
responses violated independent equilibrium; apparent32element mesh error39.6%.
`sliding_contact2` preserves a failed active-set recovery: geometrically near
zero gap is not evidence of a supporting equality; redundant unloaded constraints
made the8element closing force certificate fail. No thresholds were changed.

Corrected3/4uses supporting duals to identify the active subspace, then solves
the SAME static convex energy and checks all inequalities/nonpositive duals,
stationarity and complementarity. This is NOT Native q/v postprocessing or a
new ODE solver. Actual8/16/32element controls pass1% refinement and1e-8N force
criteria. Exact cubic-gap extrema are checked, not only nodes/sampled contact.

At32elements:

- Closing: rail tip−0.24344059mm, PET tip−0.24093181mm; channel lip inactive.
- Opening with channel: rail+0.26111482mm, PET+0.15844316mm; actual normal
  multiplier sum0.000113758N from front-lip constraints.
- Opening with channel REMOVED in the local control: PET tip0, rails+0.29424525mm.

Independent `contact_independent1` rebuilds stiffness with DIFFERENT exact
quadrature and uses Bernstein polynomial convex-hull gap bounds. Stored actual
primal/dual states pass force, moment and complementarity; minimum certified
gap lower bound−6.06e-11m versus−1e-9m criterion. Corrupted Skin displacement,
zero contact reactions and moving Root controls are actually rejected.

These results support the intended transverse capture mechanism ONLY for this
small-deflection frictionless projected Coupon. They do not establish finite
rotation, axial sliding friction, shell wrinkling, clamp strength, actual material
properties, full assembly motion or100g grasp. RevAB is still unadopted.
