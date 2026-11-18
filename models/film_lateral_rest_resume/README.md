# Stationary-origin typed continuation

Separate `LateralRestResumeODE`, not an incoming-sphere guard removal.
Reads REGRIP_LATERAL_REST_FREE_V1, exact public film/body mass, root map,
q/v/quaternion and accumulated time. Requires explicitly empty contact set,
STATIONARY_SEPARATED origin and current positive whole-surface clearance.
External force and gravity remain zero, original C2 input unchanged.

Existing free midpoint and dense numerical-path CCD are reused. First birth
rejects the uncommitted step: a separate impact/contact solve is required.
The explicit50ms horizon and at-most64-step inherited cap bound continuation;
longer runs are not silently permitted by resetting physical time or step IDs.
Legacy sampled tendon work is not reconstructed or cumulatively spliced.

1545 actual10..10.2ms and1546 through16.6ms strict q/v/clock/control
comparison PASS,error0.1548 suffix restart reproduces states/stages/full
checkpoint tokens exactly.1547 retains18 further accepted steps through
20.2ms,then rejects first birth:the full32-step horizon remains FAIL.
The separate `film_lateral_rest_contact` model qualifies this prefix and
actual first impact/remainder through20.4ms;this FREE owner never fakes it.
Further actual intervals must have their own completed summary/API evidence;
this limited result does not certify time/mesh/energy convergence or grasp.
Use `tools/film_lateral_rest_resume.py` with unique tags. `--reuse-build`
uses the frozen provider archive and checks ALL compiled sources/binaries/SDK.
Never pass incoming-object LATERAL_FREE_V1 checkpoints to this owner.
