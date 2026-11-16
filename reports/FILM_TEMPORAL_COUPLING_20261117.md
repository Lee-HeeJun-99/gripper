# Film contact continuation: actual equations versus convergence

## Latest actual continuation — candidate closure/C2 (2026-11-17)

Project NOT complete. New implementation and measured results are in
[FILM_CANDIDATE_CLOSURE_20261117.md](FILM_CANDIDATE_CLOSURE_20261117.md).
Actual411 completes16s/1600steps in263.082s with whole-triangle buffer
gap >=-9.467e-11mm (unchanged1e-10 gate).392/411 use6 genuinely added-row
records;owned Jacobian/impulse/barycentric audits pass limited checks.
C2 tail-cancellation failure393 is preserved;fixed405 completes8s and
all800 ForceField/owner applied tensions match exactly. Full C2 dt/2
comparison427 still FAILS0.1% (force5.698%,tip3.753%,attachment .6038%).
Pre-contact ONLY C2 BDF2 .1s160/320/640 passes .1% in435;no contact
occurs there.434/437 complete1s/800/1600steps.438 passes ALL pre-entry
metrics but entry force64.35%/impulse11.01% FAIL.441 actual accepted
normal velocity flips -1.34057/+0.296019mm/s despite good endpoint gaps;
442 independently demonstrates the position-level BDF2 impact issue.
No whole-cycle BDF2 PASS.443 rejects unexecuted3200steps/687s by POLICY,
not OS exhaustion. All launched physics children have exited.
Selected NEW-binary regression433 PASS12 scoped groups,not45 global gates.
Short same-binary cost431 gains3.721% median over3 alternating pairs;
all5 physical CSVs match. No compounded/global speedup is claimed.
Whole energy,friction,self-contact,3finger/free6DOF/12wrench/multimaterial,
final-design superiority and graspOptuna remain BLOCKED/NOT RUN.
Actual saved-state figures: designs/visualizations/film_native_20261117_closure_recovery_actual423/.
No SDK edits,remote push,hardware,paid service or automatic restart.
Older RUNNING/final-checkpoint notes below are historical,not live status.



## Latest actual release/settling and rejected hypothesis through372

Source/tool commits through3181ce8 (518208f,dfb7b03,481fe14 are preserved).
356 completes800 steps/8s in141.901s and366 completes1600 steps/16s in
268.204s at unchanged dt=.01,using the SAME binaries. The latter has a
passive exact displacement journal,not a rounded world-minus-rest restore.
Final tip -0.00671990mm,max speed0.00854086mm/s,T=0,zero native rows and
zero coupled multipliers. Stored shell8.5350e-12,attachment1.4008e-13,
kinetic9.0937e-12 Fmm. This supports a LIMITED fixed-sphere frictionless
closing/hold/release/near-rest recovery mechanism,NOT free-object grasp.
Independent exact-local impulse audit371 maximum relative residual1.40255e-4
in scope. Actual renderer372 uses accepted states at6/8/16s,scale1.

Full-cycle audit358 exposes a NEW limitation that a4s audit did not show:
minimum declared-buffer gap=-0.0001354306mm at7.99s,triangle117(vertices
78,73,77). The gap to radius8 sphere is still positive0.00986457mm. Therefore
selected native-feature closest constraints do NOT guarantee whole-surface
buffer clearance. This is not a claim that the radius8 sphere interpenetrated
the zero-thickness midsurface,or a finite-thickness/pressure measurement.
361 row force error6.83e-16 and362 radial moment2.65e-15 still pass;these
equation identities plainly do not establish candidate completeness.
Derived signed BE identity360 residual2.32e-6 is not full physical energy.

368 investigates sidedness:the offending sphere center is on the triangle's
back side at begin/free/accepted stages(signed distances -8.01011,-8.00443,
-8.00986mm). Installed public SDK headers declare bothSide=false by default;
XML omits it. This suggested a detector-culling hypothesis,not a proven cause.
367 sets bothSide=1 on all three FILM collision models ONLY,with identical
geometry,controls,binaries,dt and duration. It completes,with local journal.
369 finds the SAME buffer-gap error;370 finds all5 physical journals byte-
IDENTICAL to356. Thus this setting is REJECTED as a remedy in the actual
MinProximity pipeline. Do not cite the back-side observation as causality.

Next implementation:an explicit whole-triangle candidate-completeness loop
after the nonlinear accepted solve,adding missed exact primitive constraints
and re-solving with unchanged residual/gap gates. This requires its OWN row
Jacobian/impulse observer interface;new rows must not be passed off as native
predictor rows. Bound closure sweeps/row count and preserve failures. No
current candidate-complete or swept-CCD implementation is claimed.
The adapter currently reads the native predictor constraint set once,then
changes the accepted nonlinear endpoint without re-running surface discovery.
Completeness at that changed endpoint is the adapter's responsibility;these
results are NOT proof of a defect in the installed SOFA collision engine.
Independent next temporal study is a C2 tendon profile shared by the field
and nonlinear owner,not arbitrarily changed damping/physical attachmentK.
All original time FAILs and grasp/energy/optimization BLOCKED states remain.

## Further actual time/observable tests through365

Default remains BE. Actual4s800-step344 completes142.950s;comparison348
still FAILS0.1%:normal force5.03197%,tip0.443226%,shell energy1.82763%,
attachment8.72091%,K26.0258%. This is the SAME closest/SQP model and same
binaries as333;only dt/output locations change. It is not compared as time
convergence against the inherited frozen-row or fixed-material-support models.

Current-sphere BDF2 is separately enabled only for bounded short tests. Actual
345/346/347 execute20/40/80 steps over.1s;351 FAILS. Base-to-quarter:
pre-contact tip0.843985%(BE5.69427%),attachment5.07215%;all-window normal
force46.6924%,tip0.657014%,attachment5.00895%. A finer adjacent onset-tip
comparison alone0.091579% is NOT the whole time result. Endpoint force
rectangle sums are not exact continuous-impact impulses.349 accepted BDF
impulse residual7.37e-6,350 radial-law checks pass in LIMITED scope.
352 minimum buffered gap=-7.66e-14mm. BE-only energy analysis rejects BDF2.

To avoid blaming all pre-contact error on ultrahigh attachment modes,354
uses FULL current stored/generator Hessian(including tendon geometry),actual
diagonal masses and the mapped root. At the common physical time.08s,the
largest total error projections have omega117.214,162.020,99.037,143.080rad/s.
This is an instantaneous error decomposition,not proof of a modal dynamics
model or a complete cause. No contact tangent is included before positive
contact force. No negative eigenvalues in this particular snapshot.

365 additionally projects the ATTACHMENT observable,not only total quadratic
error. Actual attachment difference2.88068104e-9 Fmm =linear2.70776623e-9
+quadratic1.72919850e-10 +Taylor remainder-5.03e-15. Mixed quadratic modes
contribute2.94765472e-11 and are explicitly retained. Largest signed linear
contributions include117.214(-2.5021e-9),162.020(+2.0234e-9),222.547
(+9.0631e-10),99.037(+6.0417e-10)rad/s. Cancellation is real;the sum of
absolute contributions is NOT actual lost energy. None of these small values
waives a relative-error FAIL. This supports investigating structural phase/
control excitation as well as attachment dynamics,not blindly loweringK.

353 is a preserved POSTPROCESSOR preflight failure,string comparison of
tensions8.0000000000000007e-5 vs8.0000000000000047e-5 at equivalent times.
354/365 use identical XML controls and explicitly bounded ULP handling;
no physical tolerance was changed. Their original summaries contain source/
binary hashes but did not record source HEAD;do not retrofit that field as
launch evidence. Future tool version records it.355 selected regression
passes;ambient pytest/anyio autoload conflict was resolved by disabling
unrelated plugin autoload,not changing project packages or physical tests.

## Full closest-sphere/SQP result through343

Feature commit518208f preserves the current-sphere/closest-primitive model,
new diagnostics and same-binary refinement runner. Raw333 records its original
source HEAD29ef7e4 plus actual compiled-source hashes;the feature commit does
not retroactively replace that launch identity.

320 and instrumented322 both FAIL at3.25s (last accepted3.24s) within30 Newton
iterations,not OS exhaustion or the480s limit. Exact archived-source replay326
has a positive mechanical and Lagrangian tangent. Directional study330 shows
linear stationarity defect3.10e-16 and tangent FD8.58e-11,but Newton velocity
increment norm39.27 and large nonlinear residual remainder. This falsifies
the claim that a missing Hessian or negative contact tangent is the cause.

The obsolete positive multiplier on a separating row is real,but releasing
QP-inactive multipliers alone328 still FAILS. It is not the selected remedy.
Unmodified replay329 reproduces the original failure. Exact L1 inequality
merit332 solves the SAME rejected step in15 iterations:residual3.24e-12,
gap1.78e-14mm. rho=2*max(lambda)/h is a SOLVER merit coefficient,NOT physical
contact compliance. It never enters accepted forces or the final tolerances.

Actual SOFA333 then completes400 steps/4s in70.0995s. Entire-triangle distance
audit338 minimum buffered gap=-2.2114e-11mm (versus -0.000530968mm in307).
The gap to the declared radius8 sphere is still positive0.009999999978mm.
Radial-law339 defect2.13e-15;row-pullback340 defect5.74e-16;minimum covering
arc of load-bearing row locations73.208deg. This arc is NOT contact area,
continuous enveloping angle,pressure or holding capacity.
Independent accepted-impulse residual341 is2.86e-5 relative;derived signed BE
identity342 residual8.11e-7. These are scoped equation/derived-identity checks,
NOT measured fixed reactions,whole energy or free-object grasp. Actual plot343
uses unmodified accepted positions,scale1. Partial-failed plot331 remains
explicitly labelled failed/partial.

Same-binary short20/40/80 trials334/335/336 all execute,but comparison337
FAILS the existing0.1% gate. Base-to-quarter all-interval tip4.4654%,normal
force32.5801%,attachment energy2.2567%;pre-contact tip5.6943% and attachment
energy2.2287% already fail before contact force appears. Contact entry
0.095/0.0975/0.0975s does not explain all trajectory error. A contact-only
event fix therefore cannot certify time convergence. Same-binary full-window
refinement344 is a separate bounded experiment,not assumed successful here.

Independent fast no-contact failure321 has mechanical LDLT minD=-3.206e-7,
zero contact rows;replay324 directional FD2.50e-10 agrees. An unmodified-
tangent indefinite free Newton alternative325 also fails its residual search.
This is a separate nonconvex fast-drive regime,not fixed by sphere normals.

No scope expansion to friction,self-collision,free6DOF,3finger,multimaterial,
12-wrench,full pressure work or grasp Optuna is authorized by these results.

## Closest-primitive continuation through319 (actual results,2026-11-17)

The whole-surface gap oracle found a separate spatial contact error: the
current radial-normal model still held native barycentric material supports
fixed within each step. In307 its minimum buffered triangle gap was
-0.000530968mm, despite passing its selected-support equations. This is not
a new claim of penetration into the declared radius8 sphere: the midsurface
gap to that sphere was still positive0.009469mm.

New opt-in `closestSpherePrimitive` follows the current closest point on each
native-selected point/edge/triangle. AD includes changing barycentrics in
gap/gradient/Hessian. Zero-weight native support vertices are retained.
Final forces use the gradient of the SAME gap and the observer records its
actual force location. This is a different, explicitly versioned contact
discretization; frozen-row and fixed-material-support modes remain available.

Independent branch tests,gradient/Hessian FD,three-node coupled tangent FD,
nonlinear solve and sphere-moment identity pass. Degenerate primitives and
undefined sphere normals are rejected,not regularized. Feature switches are
explicit nonsmooth branches,not smooth-derivative claims.

Actual316 completes20 steps/.1s in3.410s with the same fast sphere95/e2 input
as301. Audit317 finds minimum buffered gap -7.13e-14mm, versus -7.80e-5mm
in301/309. Radial-law318 maximum relative defect3.18e-15; independent row
force assembly319 relative defect7.47e-16. These are LIMITED contact geometry
and equation checks,not time/mesh/full energy or free-object certification.
Wide400-step/4s trial320 and failure-localization321 are separate experiments;
only their eventual final summaries may determine completion.

Whole-cycle time FAIL292 and all inherited failures remain unchanged.
No friction,CCD,full-surface candidate completeness,self-collision,6DOF grasp
or grasp Optuna approval follows from these local checks.

## Latest continuation through314

Full fixed-cylinder275 completes8s over800steps (184.667s). After prescribed
tension release,282 continues to16s over1600steps with the exact accepted-
evaluation cache (281.424s,480s hard limit). Final tip=-0.007395mm, maximum
speed0.009374mm/s, prescribed tension0, no positive contact multipliers.
The first800 rows of282 are bitwise equal to275 for state/contact/momentum/
coupled journals. This demonstrates a LIMITED frictionless fixed-object
closing/hold/release/recovery mechanism, not free-object grasp certification.

Benchmark281 uses the SAME binaries, three alternating pairs of100-step
actual SOFA runs. All five physical CSVs match bitwise, including the finite
reference276. Mechanical evaluations704->402, accepted reuses302; runtime
ratios0.7561/0.7781/0.7997. Median reduction22.19%. This scope is distinct
from the earlier4.562% workspace benchmark; percentages are not added.

Whole-cycle275/288 comparison292 still FAILS0.1%: full-interval tip2.3268%,
normal force14.4819%,attachment energy1.1316%,kinetic energy8.3910%.
Scalar impulse0.0470% passes that one metric, NOT the full system. Release
and ramp/hold intervals remain separately reported. No absolute-error waiver.

Late-force postprocessing has an independent precision limit: main journal.x
is WORLD geometry (rest+u). Subtracting rest loses displacement precision.
Prescribed near-rest SOFA probe293 uses NEW passive displacement.csv. Same
actual trajectory294 world-reconstructed relative residual0.00419962 versus
295 direct-local residual2.78543e-8.296 ON/OFF physical CSVs match bitwise.
291 incorrectly treated world x as u and is INVALID postprocessing. No old
full trajectory is retroactively certified: exact local u was not recorded.
This issue does NOT explain or erase the real motion/energy time failures.

Independent exact-sphere-law audit298 identifies another limitation: old
wide-Sphere284 accepted radial-force moment defect0.6430%, versus begin
defect2.43e-15. This diagnoses mixed-time contact geometry, not a measurement
of fixture reactions. The new current-gap/current-normal SphereStep includes
the TRUE contact geometric tangent (FD2.21e-15) and separate final nodal
impulses. Actual301/302 short accepted radial defect1.59e-15. Wide307/310
completes4s and reduces accepted radial defect to4.04e-15. Fast306 fails at
0.94s with nonpositive tangent: it is not declared generally stable.

New sphere material supports remain fixed per step. Exact closest-point-on-
triangle audits308/312 show buffered midsurface gaps-0.000419mm (old wide)
and-0.000531mm (new wide), despite positive gaps to the declared R8 sphere.
Thus radial-law consistency is improved, but full-surface gap/area/pressure
certification is still unavailable. No finite-thickness or self-contact claim.
Next contact work must address support/closest-point evolution, not just
increase Newton counts or copy the scoped radial PASS to whole-system Gates.

Actual negative guard299 rejects a moving-collider configuration with zero
accepted rows. Fixed-body prototypes cannot be converted to valid free6DOF
grasp by simply removing a constraint or adding object mass.

Source archive300 fails before physics because a new header copy was omitted;
301 includes it and passes the prebuild source check. Earlier snapshots are
post-build snapshots;275 onward adds explicit prebuild hashes and an entry-
script snapshot. Byte integrity is not full physical certification.

All values below are actual SOFA output or explicitly independent mathematical
reconstruction, using assumed research F/mm/s parameters. No real material or
actuator measurements, hardware runs, SDK changes or remote pushes were made.

## Accepted nonlinear equations

The original Native compliance correction solves a tangent system, not the
accepted nonlinear film equation. Audit205/206 measured relative impulse
residual0.93498 although the free solve and tangent prediction were consistent.
Independent207 and actual208–229 isolate and solve this nonlinear remainder.
Separately222/223 show the native LCP itself can stop with gap3.66e-6mm;
the public Wlambda relation and mapped displacement agree. These are two
different causes, not an observer-coordinate or impulse-unit explanation.

CoupledContactStep uses the existing AD film/rail/tendon energies, projected
root DOFs and actual XML masses. It enforces nonnegative scalar multipliers
and frozen native contact-plane inequalities by a direct active set and
nonlinear residual line search. No artificial force, denominator epsilon,
stiffness alteration or tolerance relaxation was introduced. Singular/infeasible
sets and nonpositive mechanical Hessians explicitly fail. Constraints with
friction blocks, external force fields and free objects are unsupported.

The final multiplier has a separate owner, coupled.constraintImpulses; the
native solver retains its raw predictor W/dFree/lambda. NativeObserver reads
the explicit final owner. Attempt227 to repurpose mapped native lambda was
rejected and its failure retained. This avoids treating an obsolete linear
constraint system as the final nonlinear system.

Actual235:400steps/4s fixed64-facet Cylinder,103.835s. Audit240 accepted
relative impulse residual <=1.75953e-5. Independent241 reconstructs stored
energy within8.61e-18 F mm and a derived BE discrete identity within7.15e-10
relative. These are local equation checks, NOT full physical energy closure,
measured fixed reactions, global moment closure or convergence certification.

The BE identity derives kinetic increment, mass damping, held-tension work,
constraint-impulse work and signed elastic/tendon endpoint discretization
terms separately. The latter are not physical heat or residuals renamed
numerical dissipation. Vacuum work and real actuator efficiency remain null.

## Time convergence: FAIL retained

235 versus243:400/800steps, same4s closing window, same geometry/material/
boundary/tension;243 executed188.296s. Profile235 with safety2 projected
415.34s and retained the480s hard limit. Corrected interval assessment246:

| Observable | Maximum relative difference |
|---|---:|
| Normal force |9.27393%|
| Accumulated scalar impulse |0.129156%|
| Skin tip z |0.163093%|
| Shell energy |0.107148%|
| Attachment energy |0.169901%|
| Kinetic energy |4.73995%|
| Tendon work |0.0907510%|

Gate remains0.1%. A single sample at t=4s is NOT a hold interval: corrected
assessor246 excludes this old245 reporting artifact. No complete release or
recovery is demonstrated in these4s windows.

## Independent alternative: uniform BDF2

CoupledBDFHistory recasts uniform BDF2 into the SAME implicit mechanical
kernel: q*=(4qn-q[n-1])/3, v*=(4vn-v[n-1])/3, h*=2h/3. The kernel multiplier
is2/3 of the physical-step impulse. BE startup is explicit. Variable-step
history is rejected. Unit tests include no-contact motion, contact, duplicate
and nearly duplicate unilateral rows and unloading.

Actual244/247/248 execute40/80/160steps over0.2s. XML explicitly requests
integrationOrder=2 on the accepted owner, while the Native predictor remains
BE. Independent249 measures accepted position identity defect1.45e-13mm and
relative momentum residual4.88e-6; fine252 <=7.38e-6. This does NOT imply
time convergence:250 FAIL, base-to-quarter tip2.0327%, normal force28.5331%,
attachment energy5.2793%. BDF2 is not adopted as a qualified fix.

Onset255 reconstructs a single active normal Jacobian from actual nodal
impulses. Incoming normal speed is finite, about-4.6 to-4.9mm/s. The BDF2
half-step first accepted normal speed is+1.664mm/s while other resolutions
remain negative. The frozen-plane chord fractions also differ. These data
support a contact-event/rebound investigation, not a claim that impulse
metrics cure the FAIL: scalar impulse and pre-contact dynamics also fail.
The diagonal mass stopping impulse is only a comparison scale, not an elastic
reference solution or exact continuous collision detection.

## Cache exception defect

230 reproduced reuse of a partial cache after a rejected degenerate geometry.
Both FilmShell and FilmRailTendon now invalidate BEFORE filling a new cache.
232 matching-SDK API tests and233 installed-SDK API/actual tests pass. The
tests require bitwise force/energy/Hessian recovery after an exception, and
cover Shell displacement/absolute and compact/noncompact regimes. This is
an independent correctness fix, not a fitted physical parameter change.

## Actuation and partial wrapping

Low-tension235 loads locations spanning11.243deg along a fixed Cylinder;
force-row reconstruction239 agrees to2.34e-16 relative. This is not a
pressure/area or unique-contact-point measurement.

Increasing ONLY maximum prescribed tension to0.001 per rail in251 yields
load-bearing locations spanning73.122deg in the AVAILABLE states. But free
Native BE Newton fails at2.95s (30 iterations), last accepted state2.94s;
251 is FAIL, not a completed4s trial. Plot259 is prominently marked PARTIAL
FAILED run, no displacement magnification. Postprocessing258 marks the
partial trajectory EXPERIMENTAL; old256 row algebra PASS is not an execution
or grasp PASS. No successful hold, release, recovery or free-object grasp
can be inferred. Core material volume is unchanged, guide hardware excluded.

## Mandatory accepted-stage ownership

The free-stage failure251 motivates an explicit single-Newton collision
predictor, NOT acceptance of a failed nonlinear step. The independent core
option nativeCoupledPredictor requires a FilmNativeCoupledCorrection named
coupled with completeFreeStage=1. That owner MUST solve every step, including
no-contact steps, before recorders. Default free-stage solver is unchanged.

Actual260 short contact executes; independent261 accepted impulse residual
<=3.56e-6 although the deliberately unconverged predictor residual is0.9422.
262 BE discrete identity relative residual <=5.87e-11. Short accepted state
difference from original233 is4.77e-11mm, NOT bitwise equivalence or a runtime
optimization approval. Actual negative guard264 disables completeFreeStage
and rejects before any accepted CSV row (exit-6, expected runtime error).
Compile failure257 is preserved;260 uses the public BaseContext get<T> API.

Full capacity experiment263 fails the coupled Newton30-iteration budget at
3.37s, last accepted state3.36s, runtime165.221s. It passes the former
free-motion failure location, but is NOT a completed closing cycle. The
last Newton residual at iteration29 is5.03e-7, so this is not an OS timeout,
out-of-memory event or merely a convergence-status reporting artifact.
265 isolates previous-accepted-velocity Newton initialization; default Native
initialization, tolerances and all failed traces remain preserved.

## Remaining dependencies

Time/space/history, current-normal angular consistency, actual pressure work,
full energy, reactions, self-contact and free6DOF remain unqualified. Three-
finger/multimaterial/12-wrench grasp, final-design superiority and grasp
Optuna remain BLOCKED/NOT RUN. Original changing-normal friction failures
are separate and unchanged. The existing45 gates are not new certification.
