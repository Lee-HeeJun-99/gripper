# Nonlinear native-contact coupling diagnosis

This is a continuation checkpoint, not whole-system certification. Units are
the existing research F/mm/s system, not measured material data.

## Actual SOFA finding

Campaign204 records begin/free/accepted velocities and the actual nodal
`J^T lambda` impulse, without changing the journal (bitwise equal to200).
Independent existing-kernel force reconstruction205/206 uses the accepted
and free coordinates, the actual XML nodal masses and root-map pullback.
Constrained root DOFs are excluded, not mistaken for free residuals.

For backward Euler, the measured free-DOF impulse residual is

`R = Jroot^T [M(v1-v0) + h*2*M*v1 - h*F(q1,T1) - Jcontact^T lambda]`.

The normalization is the sum of the four pulled-back term norms. This is a
diagnostic normalization, NOT a global force/moment certification.

* Free solve maximum relative residual: 3.55817e-6.
* Native accepted-state maximum: .934980488, absolute 2.94288e-6 F s.
* Substituting the free-state tangent prediction for the accepted force
  recovers the small residual. Thus the large difference is specifically the
  nonlinear force remainder after linear compliance correction.
* `delta q = h delta v` agrees within8.23e-14 mm; the contact-plane equation
  agrees within1.78e-15 mm. The impulse units and state-update factors are
  consistent in this test.
* Reconstructed kinetic energy differs by at most1.69407e-21 F mm.

This identifies a genuine splitting/linearization limitation in the tested
native dynamics, not a claim that every contact/time failure has this cause.
The no-contact midspan arch is separately reproduced by linear dynamics.

## Independent and actual coupled experiments

`CoupledPlaneStep.h` minimizes the BE incremental potential

`Phi(v) = .5*(v-v0)^T M (v-v0) + .5*h*c*v^T M v + U(q0+h*v,T1)`

subject to the same frozen native single contact plane. `U` includes the
prescribed-tension generator for the stage equation; that generator is NOT
stored cable energy. No extra force or shifted contact target is introduced.
AD supplies the existing mechanical gradient and Hessian; mass and root-map
pullbacks are explicit. The Schur denominator must be positive; there is no
small-denominator replacement or Hessian regularization.

Independent207: two actual native states converge in2/3 iterations, with
absolute impulse residual1.08608e-14 /3.10675e-16 and sub-femtometre plane
defects. These are independent computations, not actual corrected trajectories.

Actual208: a separate opt-in `FilmSphereCoupledCorrection` performs this solve
at AnimateEnd before state recorders. It reads public component Data, mass
and Jacobians, publishes the solved main q/v, propagates mappings and records
both native and coupled impulses. The original BE solver/SDK remain unchanged.
The20-step/.1s actual trajectory completes. Independent209 checks the actual
published trajectory: maximum relative impulse residual3.55817e-6, including
pre-contact steps. Before contact the CSV is bitwise equal to204.

Actual210/211: extending to.2s exposed a line-search failure at.11s. Trace211
shows an energy-Armijo trial rejected despite reducing KKT residual from
7.54944e-13 to3.23094e-18; the potential evaluation changes by about2.4e-18
around a magnitude2.00051e-5. Those failed runs/logs are preserved.

The new version uses a residual-merit line search with the SAME Newton and
contact tolerances. Actual213 completes40 steps/.2s; typical active steps
require3 iterations and impulse residuals around1e-17. This is an execution
and equation-consistency result, not time convergence.

## Explicit scope and unresolved requirements

The new model supports one active, frictionless, fixed-sphere plane, with the
native begin-stage normal/material weights frozen during the step. Multiple
active rows, unloading and newly violated inactive planes are rejected before
publishing a new state. It is not a general active-set/contact-law completion.
Free object motion, current-geometry central-force/angular consistency,
objectivity of the coupled fixture, whole energy, mesh/time convergence,
friction/history and long duration remain unqualified. Coupled215/216 are
separate time-refinement experiments; inspect their final summaries, not this
checkpoint, for their actual status.

No fixed reaction is manufactured from a zero projected sphere Jacobian.
The optional one-shot state dump184 found the film contact-mapper state but
does not supply an independently measured fixed-sphere reaction.

## Reproduction

From repository root, use a NEW tag (all runners refuse existing outputs):

```
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/film_native_momentum.py --tag UNIQUE_AUDIT --case 20261117_momentum_probe204
$PY tools/film_coupled_reference.py --tag UNIQUE_REFERENCE --case 20261117_momentum_probe204
$PY tools/film_rail_native_run.py --tag UNIQUE_COUPLED --installed-sdk --reuse-installed 20261116_installed_control110 --assembly-case 20261117_coupled_sofa208 --coupled-correction --free-motion --sphere --sphere-x 95 --steps 40 --duration .2 --tension .001 --guide-offset 2 --contact-rows --momentum-journal
```

New builds and sources are archived per campaign. The coupled kernel is hidden
within its DSO to avoid helper-symbol interposition on archived assembly DSOs.
