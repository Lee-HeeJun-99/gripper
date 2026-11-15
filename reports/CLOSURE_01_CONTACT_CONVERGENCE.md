# Active-interval contact: measured convergence

Status: **PASS** for the stated two-finger sphere/+Fx diagnostic, not all grasp geometries.
Campaign `results/closure_20261115`, new source `models/closure/`, base commit20249c9 preserved.
All numbers below are actual SOFA results unless labelled independent quadrature.

## Cause and separate implementation

Uniform reference-length samples aliased the narrow active SDF interval. Increasing
sample count changed which points were active; material friction history attached
to moving quadrature locations additionally confounded integration and history.
The new component finds the sphere intersection analytically, partitions each
straight beam segment into its active interval, then uses Gauss-Legendre8/16/32.
Rounded cylinder/box use bounded convex line minimization and bisection. No smooth
derivative is claimed at SDF seams. This remains a linear-segment skin, NOT film surface contact.

Normal density is `kn * penetration`, same kn=.001 and skin=.1mm as baseline.
Reference-length integration weights are preserved. Boundary force is zero;
integrated continuum force differentiation has no additional boundary-force term.
Finite quadrature and stick/slip branches still require FD/error checks.
Material history is committed only at AnimateEnd on fixed .01mm reference knots,
interpolated from last geometry and projected in the old tangent frame. Moving
Gauss points do not own history. Detachment energy is a separately labelled grid
estimate, not proof of exact global energy closure. Original StickSlipContact unchanged.

## Independent numerical reference

`tools/closure_reference.py`, `results/closure_20261115/reference/summary.json`:
sphere R5mm, skin.1mm, segment at z5.099mm; active length .20198019704908254mm.
SciPy boundary-split QUADPACK is the independent reference. Max absolute errors
at Gauss8/16/32 are1.6918e-11/3.2214e-12/3.7808e-13, versus old uniform sampling
1.1154e-6/4.9035e-7/1.7785e-7. These are mathematical integrals, not SOFA trajectories.
18DOF moving-boundary force-Jacobian FD max error8.3731762842709223e-12.
Additional C++ objectivity/action-reaction/moment/kFactor/stiffness/re-entry tests
pass; max moment defect5.293955920339377e-22. Elastic penalty stick is not exact constraint stick.

## Actual SOFA spatial/time/history sweep

Same load1e-6,+X, dt.0005s,18s, hold6..14s, mass damping2, cable.001,
pressure.001,mu.3,100mm two guided fingers. New trial directories, no old raw overwritten.

| Nodes | Gauss8 displacement mm | Gauss16 | Gauss32 |
|---|---:|---:|---:|
|11|.0009316720335022|.0009316884034973|.0009316282332463|
|21|.0009275065160921|.0009288772831866|.0009283307556132|
|41|.0009246845803261|.0009265953472664|.0009260966163538|

All six quadrature comparisons <1%; mesh11→41=.5973045%,21→41=.2412426%.
dt half change .02602475% <.1%; history spacing half .02806955% <1%; repeat bit-identical.
The original1% diagnostic line is unchanged. This is a finite convergence trend,
not proof of exact continuum contact or all shapes/torques. See `gate.json` for11 checks.
Three-finger torque convergence is evaluated separately and is not covered by this PASS.

Reproduce in a NEW namespace:

```bash
REGRIP_CLOSURE_OUT=results/closure_repeat PYTHONPATH=tools \
 /home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/closure_campaign.py convergence --workers 2
REGRIP_CLOSURE_OUT=results/closure_repeat \
 /home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/closure_evaluate.py
```

Each raw directory contains scene/config/command/stdout/stderr/state/contact/patch/metrics,
Git dirty state, source/binary hashes and artifact hashes. The initial unguarded pilot
binary was separately reconstructed byte-identically in `build/closure_20261115/prototype`;
it is not used to qualify the main guarded-source sweep (`prototype_recovery/result.json`).
