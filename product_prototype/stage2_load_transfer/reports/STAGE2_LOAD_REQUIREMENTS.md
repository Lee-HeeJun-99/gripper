# Frozen scope and conditional load requirements

Before analysis, `models/analytical/criteria.json` fixes geometric, equilibrium,
energy and convergence thresholds. Physical preliminary strength factor 2
requires evidence-backed allowables; it is NOT a waiver of fatigue or local FE.

`scripts/load_requirements.py --tag envelope1` executed 42 geometric conditions
(three wire diameters, two actual groove-floor limits, seven bend poses) and
18 ideal contact wrench cases. Gravity load is 0.981 N. Equal contacts at
120 degrees are a scenario, not an assumed measured force distribution.
Full force/moment equilibrium is enforced by nonnegative friction-cone edge
weights. One point contact cannot balance the six-component sphere wrench in
these locations, even when a scalar vertical-force calculation appears adequate.

For three equatorial contacts, assumed mu=0.2/0.4/0.6 requires normal force
1.635/0.8175/0.545 N per finger. At latitude +30 degrees (above equator),
mu=0.2 and 0.4 are infeasible; mu=0.6 requires 16.6707 N/finger. Below-equator
contacts differ. These are NOT verified Rev AA contacts or measured friction.
No certified tendon tension can yet be derived from contact force alone.

Actual flat-groove seating scenario: centre radius 11.165..11.190 mm using
released root D21.850..21.860 and wire D0.480..0.520. This is not the former
11.25-mm prescribed cable centre radius, nor a prediction including strand
flattening. Prescribed 60-degree takeup becomes 16.90674..16.91530 mm.
Cable-length derivative and analytic virtual-work moment arm agree within
3.02e-8 relative (criterion 1e-6). This verifies work-conjugate geometry,
NOT that the Finger assumes the prescribed constant-curvature shape.

Further loads: solve actual nonlinear Finger / contact geometry; then obtain
normal closing, holding, asymmetric and start/stop demands. Until then load
capacities must be reported as functions of tension and speed, not certified
at an arbitrarily chosen 1.5 N. No full grasp executed.
