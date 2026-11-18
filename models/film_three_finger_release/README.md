# Bounded deformed release and separated FREE V3 continuation

This is a separate EXPERIMENTAL integration branch. Old Lobatto/contact owners,
their failed horizons, sources and binaries remain unchanged.

`ThreeFilmAccelerationReleaseODE` starts from an explicit EDGE V2 state:
20us of three-row acceleration complementarity (64 RK4 substeps), followed
by the remaining free implicit-midpoint interval. At each force query solve
`a=M^-1(F-Cv+J^T lambda)`, `w=Ja+v^T H_gap v`, `lambda>=0,w>=0,lambda*w=0`.
Enumerating eight subsets is intentionally bounded to these THREE independent
owned rows, not a general production contact solver. No component force
clipping, tensile force, velocity reset, position projection or compliance is
introduced. The small backward-error bound applies only to linear algebra
residuals, not the nonnegative-force condition. All RK-stage whole-triangle
gap checks and positive-force tangency guards retain1e-10 tolerances.

The100us/8 and100us/64 attempts1072/1074 fail RK trial tangency. They remain
FAIL. The20us/64 release interval is separately qualified in1075/1078; the
model does not convert the old full-step failure to PASS. No velocity jump
occurs at this release, so no impact impulse/loss or multistep restart is added.

Actual1079 matches independent1078 q/v EXACT, original1e-12 API gate.
Minimum whole-stage gap1.42109e-13mm; momentum3.55122e-19Ns; all applied
normal forces nonnegative; endpoint outgoing velocity>=.00631256mm/s.
The RK accumulated endpoint is passed verbatim to the fractional free
remainder; actual stage-clock join is EXACT.1076's older reconstructed
join differed9.02056e-17s and is not exact internal-clock qualification.

FREE V3 checkpoints retain complete mechanical/mass/root/clock identity and
released material-owner audit, with explicitly empty active contact set.
`ThreeFilmFreeODE` checks the entire existing quadratic midpoint dense
numerical surface path with `earliestSurfaceEvent`; it REJECTS any reimpact,
not integrates an unverified new impact. This is not a proof of an exact
continuous nonlinear trajectory. Actual1080/1081 reach27.6ms with strict
positive surface clearance; exact FREE resume comparison is a separate test.

Private legacy sampled-work history is NOT restored. Stage work uses its
own explicitly linked origin. Root reaction work remains unmeasured/null.
Friction, self-contact, physical thickness, full time/mesh convergence,
wrapping, holding, gravity lift and physical material calibration are NOT
qualified by this branch. Common prescribed tension is NOT a mechanical
equalizer. Sphere6DOF remains free; isotropic normal contact has zero angular
Jacobian by geometry, not an extra orientation constraint.

Reusable actual DLL:
`build/three_film_release_20261118_three_film_actual_clock_release1079/libReGripThreeFilmRelease.so`
SHA256 `22add00153af4573a0e852c954af0514f444ca4d23c03a1d9f5136ab05e9cc51`.
