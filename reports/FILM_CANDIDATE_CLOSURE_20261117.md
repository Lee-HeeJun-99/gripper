# Candidate-complete endpoint contact and C2 continuation

## Latest measured impact continuation 445–474 (2026-11-17)

Project NOT complete. Independent projected impulse,event root/IFT,root-map
mass,pre/post velocity and multistep restart now exist in models/film_impact.
Actual SOFA supplied-film and isolated-birth/remainder prototypes execute;
this is NOT the whole-triangle C2 event owner required by434/437.
See REGRIP_IMPACT_SOLVER_RESEARCH.md for equations,scope,failures and raw paths.
Actual same-binary464/466 midpoint startup reduces20→80 attachment time
error4.38155%→0.901492%,but remains FAIL0.1%. Finer47140/80/160 has
adjacent PASSs but40→160 attachment0.11165505% FAIL. Do NOT certify time
from the adjacent comparisons or replace the original C2-time FAILs.
Independent469 root+impulse velocity tangent FD error1.66e-9. Actual470/472
accepted whole-triangle clearance and actual FF/owner state-energy agreement
pass LIMITED audits,not swept CCD or full physical energy. Actual474 rejects
additional mass/moving colliders;12 physical journals match468/471 bitwise.
Selected regression473 passes12 groups,not global45 gates. First feature
commit1b2b18c;subsequent guard/evidence commit is recorded by Git.
All launched children through474 have exited;no OS exhaustion/480s timeout.
Whole energy,friction,self-contact,free6DOF/3finger/12wrench/multimaterial,
design superiority and graspOptuna remain BLOCKED/NOT RUN. No SDK edits,
remote push,hardware or automatic/background resumption.


## Scope and source identity

Continuation of `development/regrip-autonomous-research`, initially clean
`38897c18b9e6803b8cb3841416f7597941fe685b`. This is NOT project completion.
Feature commits: `2cb65dc` (closure/owned rows), `89351bb` (shared C2),
`4d93046` (one residual reference per physical step), `c4bba01` (bounded
C2 tails), `f229f05` (bounded experiments/performance qualification).
Each trial records its ACTUAL launch HEAD, including dirty-source snapshots,
prebuild source guard, binary hashes, command and SDK identity. A later commit
matching those bytes is not retroactively called its launch commit.

Initial historical checks PASS: 6738 inherited artifacts, 3233 older artifacts,
8889 v3-ledger bytes. Existing ledgers/raw/SDKs/Golden/SQLite were not replaced.
Later current-source changes are expected; v3 is not a current-source certificate.

All numerical values below are **actual SOFA execution** unless explicitly
marked independent mathematical validation. Materials/mass/tension/buffer
remain **research assumptions**, not measured PET or actuator capabilities.

## Actual implementation

`models/film_sphere_contact/CandidateClosure.h` implements:

1. Copy predictor supports into a separate row namespace.
2. Solve the unchanged nonlinear mechanics with current closest primitives.
3. Search EVERY valid triangle at the accepted trial geometry.
4. Add missed violated triangles, with independently differentiated rows.
5. Re-solve from the SAME previous q/v, mass, dt and applied tension.
6. Commit only after complete endpoint clearance and mechanical gates pass.

For the fixed sphere, `g=|closest(triangle,c)-c|-(R+buffer)`.
Impulse pullback is `I=J^T lambda`, with `J=dg/dx`; the Newton tangent includes
the existing true geometric constraint Hessian and mapped root chain rule.
Limits remain 256 rows, 8 closure sweeps, 30 Newton iterations, 16 line trials,
gap 1e-10mm and the original max(1e-15,1e-7*initial residual) stopping rule.
Degenerate triangles/undefined normals/rank failure explicitly reject; there
is no artificial stiffness, extra physical force or denominator epsilon.

Native predictor J/W/dFree/lambda are not modified. `ownedJacobian`,
`constraintImpulses`, `nodalImpulses`, `rowNormals` and `rowPoints` belong to
the accepted owner. Observer row reconstruction reads the OWNED Jacobian.
The independent row journal stores time, own row, added triangle ID, closest
feature, gap, impulse, normal, force point, support and full J. Row lifetime
is one accepted step, identity `(time,owner_row)`, NOT a persistent friction
history ID or a reused Native row ID. Audit436 additionally exports raw
barycentric weights and activation in `decoded_rows.csv`.

An opt-in outward-rounded AABB bound skips exact AD only when it PROVES
positive clearance. Near/violated triangles still use the same exact AD.
Its logged minimum can be a certified LOWER bound, not the exact minimum;
independent NumPy whole-triangle audits always compute actual closest distances.
Default remains disabled. This is endpoint completeness, NOT swept CCD,
self-collision, finite-thickness shell contact, contact pressure or free bodies.

## Failed experiment and actual correction

381 fails at6.86s after finding a missed triangle (gap -9.84645e-5mm).
The re-solve incorrectly reset its relative-residual reference to an already
equilibrated warm start (1.74681e-12), effectively demanding the 1e-15 floor.
It stalled at roundoff ~2.77e-15 despite satisfying the contact gap.
Independent replay387 reproduces it; tangent FD defect ~1.20e-10 at epsilon .001.
Replay390 preserves the ORIGINAL physical-step reference 1.95837e-4 and
solves in2 iterations: residual3.73889e-13, gap1.30740e-12mm.
The fix preserves ONE original reference across discovery sweeps; it does
not relax the original physical-step tolerance. Failed381 is preserved.

## Completed sphere contact/regression

| Actual case | Window | Result and independent whole-surface check |
|---|---:|---|
|376|4s/400|complete; minimum buffer gap -2.21141e-11mm|
|392|8s/800|complete; 6 added-row records; gap -9.46694e-11mm|
|404|8s/800|broadphase; all5 physical CSVs BITWISE identical to392 (410)|
|411|16s/1600|complete in263.082s; gap -9.46694e-11mm (420)|
|405|C2 8s/800|complete; gap -9.63303e-11mm; 5 added-row records|
|418|C2 8s/1600|complete in267.468s; gap -9.97782e-11mm|

These satisfy the declared 1e-10mm ENDPOINT buffer gate in these tested
windows. Old358's -0.0001354306mm buffer FAIL is preserved. That old result
did not prove radius8 midsurface penetration; its actual radius8 gap was
positive .00986457mm. The declared .01mm buffer is NOT certification of the
.05mm film's finite-thickness envelope.

411 final: tip -0.006720768mm, maximum speed .008541947mm/s, prescribed T=0,
shell8.53714e-12, attachment1.40118e-13, K9.09598e-12 Fmm. This is limited
fixed-object frictionless release/near-rest recovery, NOT free-object grasp.
421/436:2598 row records, closest-point error1.44e-14mm, barycentric error
5.76e-14mm, radial moment defect8.02e-15, nodal impulse difference0.
422 independent exact-local impulse residual maximum1.40249e-4 (limited
1e-3 equation gate); fixed/root reaction measurement remains unavailable.
408 derived signed BE identity residual2.31971e-6; stored energy reconstruction
error4.72e-17 Fmm. It is NOT full physical energy closure or friction heat.

Actual saved-state plots/OBJ (scale1,side projection,not concept deformation):

- `designs/visualizations/film_native_20261117_closure_recovery_actual423/`
- `designs/visualizations/film_native_20261117_c2_actual419/`

## Shared C2 input and its failure regression

`ControlProfile.h` is used by BOTH FilmRailTendon and the accepted contact
owner at the actual step time. Closing/hold/release use quintic smoothstep,
with zero first/second derivatives at knots. Legacy linear value evaluation
order remains unchanged and independently tested bitwise. C2 is a DIFFERENT
physical input, not a numerical repair that erases old linear-input FAILs.

393 fails at the final step: at t=7.999999999999874, naive polynomial evaluation
gives S=1.0000000000000009 and tension -8.88178e-19. The assembly correctly
rejects it. Symmetry S(1-x)=1-S(x) now evaluates the SMALL tail directly,
without clipping tension. Kernel400 tests8192 near-knot ULP probes, analytic
derivatives and legacy value bits. Actual405 completes; audit413 confirms
exact ForceField/owner tension equality on ALL800 steps and nonnegative input.
Final input2.5077e-42 is the finite-time value just before8s, not rounded to0.
Old393 remains a FAILED799-step run, not an approved prefix.

## Time convergence: failures remain

388 retains original 4s linear-input FAIL: force5.03197%, tip .443226%,
attachment8.72091%, K26.0258% (same-binary376/382).

C2 full8s405/418 FAIL0.1% in427:

| Quantity | Absolute maximum difference | Relative difference |
|---|---:|---:|
|Normal force|5.60333e-5 F|5.69842%|
|Tip z|.6570003mm|3.75252%|
|Shell energy|9.23977e-5 Fmm|.431046%|
|Attachment energy|3.00908e-6 Fmm|.603828%|
|Kinetic energy|3.80690e-5 Fmm|7.26348%|
|Tendon work|9.46447e-5 Fmm|.425745%|

Scalar impulse .0650995% passes only the all-window comparison; phase FAILs
remain. Hold K relative difference79.9533% is retained despite tiny absolute
energy. Do NOT cancel phase differences into cumulative totals for PASS.

Separate C2 BDF2 prescribed-input/pre-contact studies reuse the existing
accepted BDF2 law; Native predictor remains BE.20/40/80 still FAIL (424).
80/160/320 has an all-window tip PASS .093165%, but pre-contact phase
.122117% FAIL (430), so its total status stays FAIL.
160/320/640 over .1s passes all pair/phase motion, energy and work metrics
(435), maximum .0310978%, absolute tip difference1.10637e-7mm in the worst
phase. This is ONLY pre-contact structural time qualification at base
dt=.000625, not the original base dt, contact-time or whole-cycle approval:
there are NO positive contact impulses in these .1s tests. The inherited
phase label `onset` in their JSON is a nominal time window, not actual birth.

434 extends the SAME .00125s BDF2 model from initial rest to1s/800 steps,
actually reaching positive contact. It completes in117.104s. This is a cold
start, NOT a restored prefix.437 completes1600steps/dt .000625 in229.031s.
438 independently separates actual entry windows and remains FAIL:

- Before first recorded contact, ALL motion/energy/work differences pass:
  tip .000233791%, attachment .000211251%, K .000343662%.
- Entry-window force64.3535%, scalar impulse11.0093%, attachment .422104% FAIL.
- After entry-window force32.0441%, attachment1.76115% FAIL.
- Whole1s tip .00600398% passes, but force64.3535%, scalar impulse4.42458%,
  shell .178143%, attachment1.76115%, K .184841%, work .114964% FAIL.

441 projects actual first-contact velocities with the CURRENT owned AD row:
coarse/fine first positive times both .9775s (within floating arithmetic),
incoming normal speeds -2.98640/-2.99615mm/s, accepted normal speeds
**-1.34057/+0.296019mm/s**. Both endpoint gaps satisfy the1e-10mm gate.
BDF2 gap-history rates -1.33900/+0.298094 agree closely with that signature.
Thus equal recorded entry time and good endpoint gaps do NOT imply a
consistent impact velocity; this is not solely sampling-time alignment or
pre-contact structural drift. It does not prove all other temporal causes absent.

Independent mathematical counterexample442: fixed plane, incoming v=-1,
g_n=alpha*h, g_(n-1)=(alpha+1)*h, enforced g_(n+1)=0. The BDF2 position
identity gives v_(n+1)=(1-3*alpha)/2, which can be inward or rebound despite
zero accepted gap. Position complementarity alone does not prescribe an
instantaneous impact law. A perfectly inelastic v+=0 reference is explicitly
a NEW modeling assumption, not an already integrated SOFA fix. Next priority
is event-aware impact/velocity treatment and consistent multistep restart,
not more C2 tuning or arbitrary damping. Preserve the default BE model.

443 actually checks the default next-refinement guard:3200steps and a measured
1.5-safety forecast687.093s exceed1600/480 policy; physics attempts0. This is
an experiment-policy BLOCK, NOT observed OS memory exhaustion or a statement
that independent research is impossible. No unprofiled exception was launched.

## Performance and selected regression

431:3 alternating same-binary20-step pairs, all5 physical CSVs bitwise equal.
Broadphase/base runtime ratios .985692/.962786/.956619; median .962786
(3.72136% short-case saving). This is NOT a universal speedup and is not
added to prior cache gains. Full8s392/404 also matches all5 CSVs exactly;
their157.196/145.955s timings are NOT an isolated paired performance estimate.
433 selected NEW-binary regression PASS12 groups: actual API, factor, plane/
multirow/sphere/BDF/closure/C2 kernels, Python geometry and inherited bytes.
This does not re-run or combine all45 old physical gates.

Metadata caveats preserved:402's old wrapper incorrectly labels its unchanged
dt as refinement factor2; actual XML/command and physical byte equality403
show it is a same-step optimization contrast. Later wrappers fix the label.
407 analysis preflight failed because the wrapper command lacked `--steps`;
408 uses actual SOFA `-n` rather than inventing default20. Failed analysis
and failed physical runs are distinct.398/399 rejected partial393 before
creating any approved result. No missing values are replaced by zero.

## Remaining gates and executable continuation

FAIL: full time convergence; inherited mesh/history/friction failures.
BLOCKED: whole physical energy, measured fixed/root reactions, finite contact
area/pressure qualification, final design superiority and grasp Optuna.
NOT RUN: self-collision, film3finger/free6DOF/12wrench/multimaterial grasp.
The current owner explicitly rejects dynamic colliders/additional masses;
do not remove those guards or call three independent coupons a3finger grasp.
50mm palm target is not the old95.15mm baseline; no actuator/PET measurements
or contest team/rule specifications were invented.

Reproduction from repository root; choose NEW output tags:

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/film_owned_rows_assess.py --tag UNIQUE_ROWS --case 20261117_closure_recovery411
$PY tools/film_sphere_surface_gap.py --tag UNIQUE_GAPS --case 20261117_closure_recovery411
$PY tools/film_control_assess.py --tag UNIQUE_CONTROL --case 20261117_c2_bounded_cycle405
$PY tools/film_continuation_regression.py --tag UNIQUE_REGRESSION --case 20261117_c2_bounded_short401
# Only after inspecting437's COMPLETE summary/result:
$PY tools/film_native_cycle_assess.py --tag UNIQUE_ENTRY --contact-phases --cases 20261117_c2_bdf_onset434 20261117_c2_bdf_onset_half437
$PY tools/film_contact_velocity.py --tag UNIQUE_VELOCITY --cases 20261117_c2_bdf_onset434 20261117_c2_bdf_onset_half437
```

Reusable installed-ABI binaries are archived in build/film_native_*395 and
*401, assemblies *293 and *401, with exact loaded paths/hashes in each scene
and identity. Installed and Matching SDK libraries were not mixed or changed.
All physical children retain4GiB/480s and ≤4 long physics jobs. No hardware, paid
service, remote push, automatic restart or post-session execution is implied.
