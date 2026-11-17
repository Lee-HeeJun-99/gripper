# Experimental impact references — not a qualified grasp solver

This directory is independent of the preserved BE/BDF2 accepted owners.
No old contact force, tolerance, raw result or SDK is replaced.

`ProjectedImpact.h` implements an instantaneous frictionless Newton law:

```
Mr = B^T M B
Mr (y+ - y-) = Jr^T p
p >= 0, Jr y+ - target >= 0, p_i (Jr y+ - target)_i = 0
target_i = -e min((Jr y-)_i, 0)
```

The default film event assumption is perfectly inelastic (`e=0`), not a fitted
correction to old SOFA velocities. Mass units are F s²/mm; velocity mm/s;
impulse F s; energy F mm. Numerical velocity and impulse tolerances have
different units from the existing positional gap tolerance. No diagonal
regularization or componentwise velocity clipping is used. The exhaustive
active-subset implementation is a small reference (at most 16 rows), not a
production whole-surface solver. Redundant rows can have nonunique impulses;
the deterministic sparse representative does not establish impulse uniqueness.
Coupled restitution producing energy is explicitly rejected.

`FilmProjection.h` constructs the SAME projected mass/J as the film's root
mapping, including quarter-weight slaves. `FilmEventImpulse.h` consumes q/v
at an externally resolved event, checks geometry/root compatibility and returns
post-impact velocity, reduced impulse, physical nodal impulse and kinetic loss.
It cannot discover a birth time or certify a contact active set by itself.

`AffineBirth.h` and `PrimitiveBirth.h` explicitly define affine relative/nodal
paths, including between-frame hits with separated endpoints. They are not
continuous solutions of the film ODE. Degenerate/grazing/unresolved events
reject without denominator epsilons. The affine conservative advance has a
finite reference budget, not a general deforming-surface CCD certificate.

`BracketedFilmBirth.h` instead evaluates actual implicit-Euler subintegrations
from q0/v0 for each candidate time, with the existing film mechanics. It resolves
ONE externally isolated entering bracket for constant tension. It does not
prove that this is the globally earliest event. A missing bracket/initial
contact/grazing rejects. For G(y,t)=0, its temporal sensitivity is

```
G_y = Mr (1+c t) + t² KU
G_t = c Mr y + grad(U) + t KU y
y_t = -G_y^-1 G_t
g_t = Jr (y+t y_t)
dt/dy0 = -t Jr G_y^-1 Mr / g_t
```

`FilmRestartHistory.h` retains the pre-impact audit inventory but removes old
states from the usable BDF stencil. A post-impact fractional remainder takes
one step; a changed step size also takes one step; BDF2 eligibility returns
only after two smooth states of a common step size. No-contact references use
the unchanged original BDF2 arithmetic. This helper alone is not a SOFA solver.

`IsolatedFilmImpactStep.h` combines bracket resolution, plastic impulse and
a BE remainder. Its scope is a SINGLE material-point event followed by a
contact-free remainder. A penetrating remainder explicitly fails; persistent
contact is not fixed by an arbitrary second velocity correction.

Actual SOFA components:

- `BallisticPlaneImpact`: exact force-free point flight/event/remainder only;
  rejects ODE solvers, mappings and projective constraints.
- `FilmSuppliedEventImpulse`: one supplied t=0 mapped-film impulse API test;
  not an autonomous birth detector or multistep restart validation.
- `FilmIsolatedEventStep`: one initial timestep or opt-in profiled 1 ms sequence
  (up to 160 steps), one isolated point event, zero tension, c=2 mass damping;
  not full triangle/contact-cycle BDF2. Startup/restart can independently use
  implicit midpoint: solve the same mechanical kernel for half a step then
  q1=2q_mid-q0, v1=2v_mid-v0. This preserves its midpoint force and velocity
  equations; it is a method contrast, not increased damping.

Actual 464/466 same-binary comparison reduces base-to-quarter attachment
error from 4.38155% (BE restart) to 0.901492% (midpoint), but BOTH FAIL 0.1%.
Actual 468 finer40/80/160 has adjacent PASSs but nonadjacent attachment
0.111655% FAIL. Do not erase the base-to-quarter failure. Actual 470 checks
all accepted FE triangle gaps and actual FF/owner q/energy journal agreement,
not swept trajectories. Independent469 checks the full single-event impulse
velocity tangent through the root IFT (FD absolute error 1.66e-9).

Run from the project root, with NEW output tags:

```
/home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/film_projected_impact_reference.py --tag NEW_REFERENCE
/home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/film_impact_sofa.py --tag NEW_API
```

Do not substitute these limited PASSs for the failed 434/437 first-contact
time gates, general friction, whole physical energy, free-object grasp or
Optuna qualification. The existing fixed-body guards remain in place.
