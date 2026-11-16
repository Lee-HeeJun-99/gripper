# Current-sphere fixed-support contact prototype

## Closest-primitive and nonlinear globalization extensions

`closestSpherePrimitive=1` instead constrains the current closest point on
each native-selected point/segment/triangle. The primitive's material vertex
indices stay fixed during a step;its closest-point barycentric coordinates do
NOT. `ClosestPrimitive.h` differentiates the piecewise smooth gap including
that movement. Zero-weight native support vertices are retained. Degenerate
features and sphere-center normals are rejected explicitly. Feature-switch
tests are distinct from smooth-branch FD tests. This does NOT certify that
Native's candidate feature set covers the whole surface or swept trajectory.

With `sqpMerit=1`,a separate numerical globalization uses

    merit(y) = Phi(y) + rho sum_k max(-g_k(y),0)
    rho = 2 max(lambda_current,lambda_QP) / h.

Since dg/dy=h*C^T,the physical impulse multiplier lambda corresponds to
the incremental-potential multiplier lambda/h. Directional derivatives use
the appropriate one-sided inequality branch. Armijo merit acceptance is
supplemented by the inherited residual test near energy cancellation. rho
is NOT a penalty contact stiffness:it appears ONLY in line-search selection.
No accepted force,Hessian,gap or residual gate is modified. The final30-step
Newton,16-trial line search,1e-10 gap and original residual gates remain.

Failure320/322 at3.25s is independently reconstructed from exact rejected
local coordinates,masses,trial multipliers and supports. Geometry/tangent
FD matches;ordinary residual/feasible-potential globalization stalls. Releasing
QP-inactive multipliers alone328 also FAILS and is NOT the selected remedy.
Exact L1 merit332 solves the same mathematical step in15 iterations;
actual short334 completes20 steps. Wider qualification is separate. The
unexposed `releaseActiveSet` kernel switch is retained only for the rejected
independent comparison,not enabled in the SOFA adapter.

Actual316/317 short contact reduces the whole-triangle buffered-gap defect
from7.80e-5mm (301/309) to7.13e-14mm. This is not finite-thickness clearance,
pressure,contact-area,time-convergence or grasp certification. Diagnostic
logger323 has all5 physical journals bitwise identical to316 (327).

`diagnostics/film_sphere_contact/Replay.cpp` and `film_sphere_replay.py`
recompile immutable archived headers for rejected-step analysis. Solver
variants explicitly snapshot the new SphereStep header. Rejected states are
never treated as accepted dynamics. A separately observed fast no-contact
failure321 has a nonpositive MECHANICAL tangent;FD324 matches and an exact
indefinite free-Newton alternative325 fails its residual line search. Do not
attribute that separate failure to sphere contact geometry.

This is an **independent contact discretization**, selected by
FilmNativeCoupledCorrection.currentSphereNormal=1. The inherited frozen-native
model is retained as the default and all its raw results/binaries are immutable.

For a normalized material support w extracted from one scalar native row,

    p(q) = sum_i w_i (Xrest_i + u_i)
    g(q) = |p(q)-c| - R - contactDistance
    n(q) = (p(q)-c)/|p(q)-c|

w is fixed during ONE step, not an assertion that the closest-point barycentric
coordinates remain fixed in the continuous surface problem. Unlike the old
linear plane, g and n are evaluated at the CURRENT Newton trial.

For independent root velocity y, q=q0+h B y and P=dp/dq B. The stationarity
equation is Phi_y - C lambda=0 with C=P^T n. The TRUE mechanical tangent is

    K_L = Phi_yy - h sum_k lambda_k P_k^T
          [(I - n_k n_k^T)/|p_k-c|] P_k.

It is tested independently by finite differences, including the contact
geometric term. A nonpositive tangent is rejected, not replaced by artificial
stiffness. A future failure emits a replay block with exact local coordinates,
masses, support rows and rejected trial; this is not physical accepted state.
Normal singularity at the sphere center is explicitly rejected without epsilons.

The final nodal impulse is sum_k w_ki lambda_k n_k. It is published separately
from the native predictor Jacobian. NativeObserver MUST read nodalImpulses and
rowNormals, not multiply the new lambda by the old begin-normal Jacobian.
Row CSV explicitly distinguishes force-point geometry and Jacobian stage.
For an exact frictionless sphere, its accepted normal-force moment about c
vanishes. Actual short301 and wide307 runs verify this LIMITED geometric law.

## Status and limitations

Additional bounded uniform BDF2 comparison345/346/347 uses the existing
two-step history transformation,beta=2/3,q*= (4qn-qold)/3,v* likewise.
The kernel h is beta*dt and its multiplier is beta times dt*endpoint force.
Independent physical BDF residual9.58e-17 and kinematic residual5.55e-17 pass;
actual20/40/80-step runs and impulse/radial-law checks pass in scope. BUT
time comparison351 FAILS0.1%,especially contact-force/attachment-energy.
This mode is NOT selected as a qualified replacement for BE. The default
remains BE. Endpoint force sums are not exact continuous impact integrals.
BE-only energy analysis explicitly rejects the BDF2 mode.

* Mathematical geometry/objectivity and true tangent FD: PASS (test executable).
* Actual SOFA20-step301: finite/equation/radial-law checks PASS in scope.
* Actual4s400-step307: completes; independent diagnostics are separately stored.
* Fast1s306: FAIL at0.94s, nonpositive tangent. Do not treat all inputs as stable.
* Whole-surface nonpenetration is NOT enforced by these fixed supports. Exact
  triangle-distance audit312 finds a buffered midsurface gap of-0.000531mm,
  while the gap to the declared R8 sphere remains positive. This is NOT finite-
  thickness clearance or contact-area/pressure certification.
* Only fixed spheres, scalar frictionless rows and the declared film/root
  topology are supported. Moving colliders/additional body masses are rejected.
* No CCD, friction history, full energy, self-contact, free6DOF,12-wrench grasp,
  shape-general qualification or optimization approval is provided.

The native W/dFree/lambda remain predictor diagnostics. This prototype changes
the accepted contact geometry and tangent; it is NOT a claim that the installed
SOFA native contact solver has been replaced or certified. Scene/binary/source
identities and the actual interpreter/solver commands live in each campaign.
