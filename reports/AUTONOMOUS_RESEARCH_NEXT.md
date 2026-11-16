# Next research checkpoint

## Profiling continuation and rejected optimization

Actual profile28:150steps cost50.859s; force/damping39.406s, gradient/RHS9.862s,
linear solve1.399s, mapped mass product.00724s. Nested residual timing includes
force/mass: do not double-count it. Instrumentation preserved every CSV value.
A runtime gradient-only AD experiment preserved exact state/force/energy, but
cost94.966s (1.867x slower), shifting work into repeated Hessian evaluations.
It is rejected as an optimization; default AD and FilmShell were restored and
cleanly rebuilt/tested in final30. Failed code is retained in Git eebbb45,
campaign29/sources and the archived test under reports/film_newton_experiments/.
No original model/raw/Golden was removed. Full time/grasp Gate remains FAIL.
Next cost research should first count accepted/rejected force evaluations or
test element-local derivative dimensions/compile-time specialization, against
both mathematical equivalence and actual runtime; do not repeat runtime flags.
All launched runs are complete. There is no claimed background continuation.

## Completed25/26/27 — first next research task is now contact-phase diagnosis

Campaign25 finished; do NOT rerun it. Reference26 and phase27 are also complete.
The hard-root alternative did not fix time convergence. First next task:
profile mapped assembly/mass/Newton cost and isolate contact-phase dynamics
against a small event-aware/reference problem before attempting1600+ steps.
Use phase27/summary.json; preserve all old time/mesh failures. The command below
is retained for reproducibility only, never as blind repetition.
No background task or automatic restart remains running.

## Latest continuation checkpoint — do not restart completed campaigns

Completed source investigation: exact cache key, force-stage tangent,
line-search position scaling, owned BDF2 history and mapped MBK residuals.
Do not repeat the old matrix-getter failure or diagnose a blanket wrong H.
Do not use final-tip agreement as full time convergence.

1. Inspect results/autonomous_film_20261116_hard_transient25/summary.json and
   each process/result.json before any execution. If no summary exists, check
   the actual process first; partial trajectories are NOT convergence evidence.
   The hard boundary is distinct from original fixture100 and cannot erase its
   FAIL. Hard mapped short-reference26 and unmapped regression already PASS.
2. For the remaining transient error, distinguish stiff boundary, true contact
   event/fast modes, and time/measurement error. The coupon is frictionless:
   its temporal failure is not evidence against the friction-history model.
   Compare hard/penalty waveforms and event-aligned same-time samples, then
   design a minimal prescribed-contact or frozen-tangent experiment.
3. Only profile justified further refinement. The existing hard 200/400-step
   runs cost about71/137 seconds, so 800 is expected about275 seconds. A naive
   1600-step same implementation is predicted over480 seconds and must NOT
   be launched unchanged under the default limit. First profile mapped mass
   assembly/redundant work, or use a shorter hypothesis-separating interval.
4. Preserve 11→41 energy1.1486%/area1.3360% FAIL; hard-boundary mesh is a new
   qualification, not an original-model PASS. Verify mass and BC identity.
5. General changing-normal friction still requires work beyond the special
   great-circle reference. Then film/rail attachments, tendon, single-finger
   wrapping, free-object12-wrench tests and fair baseline comparison.
   Energy/grasp Optuna remain BLOCKED; do not run unqualified optimization.

Reproduction, using a NEW unique tag (commands never overwrite old raw):

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/film_nonlinear_assess.py results/autonomous_film_20261116_exact_time13
$PY tools/film_nonlinear_assess.py results/autonomous_film_20261116_bdf2_transient18
$PY tools/film_slope_run.py --tag RESUME_UNIQUE --steps 200 --duration 2 --time --newton-tolerance 1e-15
```

The last command is only appropriate after checking campaign25, not a request
to blindly replay it. Build/raw identities live in each campaign's
identity.json/compiled.json and source snapshots. No automatic restart or
post-session background continuation is implemented. Final goal is incomplete.
Historical tasks below are superseded by this checkpoint.

## First unfinished work after film mechanics — actual nonlinear RHS audit

DO NOT reimplement film_shell or rerun failedBDFblindly. ReadFILM_SHELL_PHYSICS.md.
Actual firstfreeM+dtC+dt²H agrees5.58e-17. Next compare SOFA nonlinear residual,
velocity/position update,rayleigh force andfixed-root projection against
ImplicitReference.cpp at firstnonzero-ramp step. Export currenttrial/oldstate/RHS
at Newton stage,not justendStep. Independent200/400stepsfinish;100failsNewton30.
An initial unsupported-directLinearSolvermatrixgetterwasnotused:SDK requires
BaseMatrixLinearSystem. Probe raw includes15rootSCALARDOFs;film_matrix_assess
correctly filters15. Do not call the unfiltered29%boundary difference a defect.

Then robust nonlinear integration and fullmesh/history/time/energy gates before
layer/rail coupling,tendon andfree6DOFfilmgrasp. DisplacementDOFspreservegeometry
x=rest+u;NativeCollisionrequirescorrectmapping/pullback,notusingu asgeometry.
New equal_volume_v2isCONCEPT,not8layerjamming. Pressure/friction data remainnull.
ActualActuator/team/rulesdataareexternalBLOCKED;do notinventthem.

Fresh regression commands(PYsameConda):
$PY tools/film_shell_run.py --tag UNIQUE --steps 30 --solver static --plane .1 --width 24 --thickness .06101941552425123 --load .000001 --nodes 21 --single --fixture 100 --ramp 10 --displacement
$PY tools/film_implicit_reference.py --tag UNIQUE
$PY tools/sphere_temporal_reference.py --tag UNIQUE
$PY -m unittest discover -s tests -p test_film_design.py -v

Temporal next:use exactchanging-normalgreat-circleplastic-workreference toderive
GENERAL evolving-normal vector law+off-planeendpointtangent. Scalar branch
exactnessisnotSOFAEnginePASS. No largerinternalgrid-only fix orOptunaGatebypass.
This unfinished working-context checkpoint is not host-resource exhaustion;
no background automatic continuation exists. Commands use fresh bounded paths.

## First unfinished task after sphere-event experiments

Do NOT repeat the20/40/80 sphere event campaigns:all finished. Read
TEMPORAL_SPHERE_EVENT_RESEARCH.md and raw event_guarded512. Internal refinement
32/128/512reduces errors first-order but nonadjacent20→80stillFAIL. This falsifies
any claim that adding exact Birth roots alone closes temporal loss convergence.
Next derive event-aligned varying-capacity vector plastic work with changing
normal/slip direction,including yield/re-stick. Reuse TemporalYield/MovingReturn
and existing scalar variable-capacity analytic reference;do NOT create another
scalar-only success or merely raise512cap. First independent prescribed path,
then new actual SOFA version matching Force/Tangent/Commit,then CurvedOwner.
Current fixed-sphere event law is independent;new original-geometry integration
and adaptive128operator replacement are still required.
Reproduce only for regression with fresh tags:
`$PY tools/sphere_event_prescribed.py --tag UNIQUE --substeps 512`
`$PY tools/sphere_event_run.py --tag UNIQUE --substeps 512`
Design next:qualify film bending,not more concept images. Currentmaterial5.74x
baseline requires equal-material comparison. See REGRIP_FINAL_DESIGN.md.
No host resource exhaustion observed. This is an unfinished working-context
checkpoint,not completed final research or an automatic restart promise.

## New first work — transfer tested active temporal path and qualify film mechanics

Do NOT reimplement MovingReturn.h or its actual MovingSphereBenchmark.
Canonical04bounded SDK/API/dynamics and independent moving-return_a02 tests
are completed. It supports already-active positive-capacity paths only:normal
chord,affine capacity/material displacement,substepped backward circular return.
Next NEW CurvedContact/Owner version must use EXACTLY this same state transition
in Force/Jacobian and Commit. Old Owner still calls old return;changing only
force is WRONG. Preserve Birth/Death and explicitly derive their temporal path,
capacity0,slip/re-stick and representation inventory. Scalar TemporalYield is
only a fixed-plane event prerequisite. Then repeat original short curved
space/history/time tests before full3finger. ExactOwner128cap is still not solved.

Design branch of work:Concept v2 meshes/loaders/drawings and geometric screen
exist in designs/. Do not repeat initial CAD generation or claim actual contact.
Next qualify a film Shell/membrane+bending ROM with transverse DOFs. Matching
SDK lacks SolidMechanics.Spring bending library;TriangleFEM alone is not a
bending shell. Build optional matching component independently or implement a
validated independent film kernel;do not mix installed SDK ABI. Run plate
patch/objectivity/bending-energy/mesh tests before comparative grasp.
First redesign equal-material candidate:currentfilm5.73588xbaseline and8.717μm
equal-volume thickness expose real tradeoffs. Pressure zones require sealed
pouches/ports/shared3circuits and layer sliding,not just a stiffness parameter.

Fresh reproducible commands:

```
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/moving_sphere_run.py --tag UNIQUE
$PY tools/design_regrip.py --tag UNIQUE
$PY tools/design_validate.py --version UNIQUE --tag UNIQUE
$PY tools/design_kinematics.py --version UNIQUE
$PY tools/design_render.py --version UNIQUE
$PY -m unittest discover -s tests -p test_design_regrip.py -v
```

Canonical physics raw:results/vector_history_moving_path_20261116_canonical04;
film loading:results/autonomous_design_20261116_v3. Old failure raw unchanged.
No background automatic restart or finished final system is implied.

## New first unfinished work — general temporal return/work and adaptive STATE fit

All launched tests currently have completion records. The final goal is NOT
complete,and no host exhaustion or automatic continuation is asserted. Next
work is actual temporal-law implementation,not another report-only campaign.
For a physicalR=1solid-sphere inertia control add `--solid-inertia` to the
short dynamic command;do not pool it with earlier default-inertia cases.
The first full-duration3finger run must await the finite-prefix replacement
and temporal/energy Gates;do not disguise the128operator limitation by truncating
the physical sequence or approving a short smoke as a full grasp.

Newest additional prerequisite already implemented:TemporalYield.h and
test_general_temporal_yield.cpp (256affine vector/fixed-plane roots+IFT).
Do not reimplement that root. Extend it only after deriving the changing-normal
path and coupled elastic/plastic evolution. An event fraction alone is not the
whole3D return map;all intermediate history derivatives must reach endpoint
force/Jacobian. Already-yielding/slip/re-stick and Birth/Death need explicit
branches. Scalar event-work is only a diagnostic analytical reference.

Latest self-contained math regression:
`$PY tools/curve_general_reference_suite.py --tag UNIQUE_MATH`.
Latest clean actual adapter build:build/vector_history_owner_20261116_verified06;
its identity/compiled.json and raw snapshots pin actual compiled source.
Use earlier05time/space cohort for comparisons;do not mix binaries/cohorts.

DO NOT repeat the already implemented Owner/Curved adapter. New files are in
models/general_vector_history. Owner is exact128operator replay;the adaptive
material quadrature is NOT an adaptive state compressor. Source/raw manifests
and bounded build/API tools now exist. Same branch;no new branch or push.

The real moving sphere/Hermite integration-spacing test now passes including
small-phase loss,while time FAIL remains. Prescribed no-Solver geometry matches
the SOFA time defect,isolating return/time/capacity work rather than SparseLU.
Next derive a GENERAL VECTOR event-aware temporal return and work rule with
changing normal/capacity. The new scalar capacity-work analytic benchmark is
only a reference;do NOT replace3D loss by its trapezoid formula without deriving
the actual3D state transition and mechanical tangent. Compare old/new laws in
independent prescribed geometry,then NEW component/build and actual short SOFA.
Do not fix the phase FAIL by using only cumulative loss or deleting tiny losses.

In parallel/after isolation,derive general adaptive state fitting around actual
SphereHistoryChart. Resolve active-boundary one-sided gap/direction limits,
yield-front state and prospective-loss error;unknown cap0normalized limits must
be rejected,not guessed. Exact replay owner is now a bounded independent
reference. A full48000step gripper cannot run under its128operator cap;do not
merely increase the cap and claim production readiness. Fit/representation U
must be inventoried separately from Coulomb heat. Test actual SOFA FD after
adaptive partition changes. Then original3finger11/21/41and dt/history gates.

Newest reproducible sources/commands:

```
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/curve_general_owner.py --tag UNIQUE_BUILD --adaptive
$PY tools/curve_general_dynamic.py --tag UNIQUE_RUN --build build/vector_history_owner_UNIQUE_BUILD --speed .2
$PY tools/curve_general_prescribed.py --tag UNIQUE_PRESCRIBED
$PY tools/curve_general_assess.py --tag UNIQUE_ASSESS --kind time 20261116_adaptive5_20 20261116_adaptive5_40 20261116_adaptive5_80
```

Completed binary:build/vector_history_owner_20261116_adaptive05/
libReGripGeneralVectorContact.so. Its compiled.json/source snapshot pins actual
source hashes independently of a later packaging commit. Raw references:
results/vector_history_compare_20261116_adaptive5_space/assessment.json and
...adaptive5_time/assessment.json;prescribed_20261116_time02/summary.json;
capacity_20261116_a01/test/stdout.log. Initial failures remain in time01,
adaptive01..04,material_rule_a01,rule_geometry_a01 and moving adaptive3_20.

## Updated FIRST unfinished task — general-history owner and curved SOFA adapter

SphereHistoryChart.h has now implemented the earlier plan's nonparabolic
capacity/normal/material-jet derivation for a sphere and immutable old Hermite
geometry. Its129state math/guard tests PASS;do NOT redo that derivation.
MaterialDerivative/materialLift and fast exact-equivalent vector integration
also exist. These are prerequisites,not an actual3finger SOFA implementation.

Next implement an INDEPENDENT general-history fitter/owner around this chart:
preserve old material coordinate and previous geometry;store gap/direction
independently of force quadrature;fit state plus prospective return/loss error;
handle active interval boundaries,Birth/Death and empty-history charts;then
connect its pure value/AD query and once-per-step Commit to a NEW CurvedContact
component. Test the old(s(q)) material chain terms,normal transport and actual
capacity derivatives. Reuse the correct original Hermite virtual-work map.
First prescribe a moving patch/reference,then actual SOFA API/short3finger
profile,then original Mesh/History/dt/energy gates. Do not treat this math
chart as completed SOFA integration or start grasp optimization prematurely.

Newest independent reproduction(fresh tag):
```
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/curve_general_reference.py --tag UNIQUE_SPHERE_CHART
$PY tools/curve_vector_evidence.py --version v1 --verify
```
Source/raw/binary identities live in results/vector_history_general_20261116_
sphere_chart01..04 and the new evidence index.01/02FAIL are preserved.
No process remains to wait for. There was no host resource/permission error;
this is a finite response working-context handoff,NOT final-goal completion.
No automatic restart is installed;resume actual code work explicitly here.

## FIRST UNFINISHED DEVELOPMENT — general moving curved-contact history adapter

The vector reference,actual normalized-patch SOFA implementation,100/200/400
time and history contrasts,reversal,arithmetic acceleration and first/second
material-coordinate pullback are now IMPLEMENTED and exercised. Do not repeat
the completed Hermite/11/21/41campaign or start the old vector-reference task.
All vector-cohort children finished;no autonomous restart is installed.

Continue SAME branch. First verify reports/vector_history/manifest_v1.json
when present,and read QUALIFICATION_v1.json. Source commits are in git log;
compiled.json/raw source snapshots identify actual binaries,including earlier
versions. The whole gripper remains unqualified and grasp Optuna BLOCKED.

Implement a NEW adapter for existing CurvedContact,NOT an overwrite:

1. Replace the fixed patch's c=C(1-x²) assumption with the actual previous
   curved geometry's mu*normalForce(s). Preserve the old MATERIAL coordinate
   when patch bounds move;normal-force quadrature points are not history IDs.
2. Store/transport the vector state in the documented object material frame.
   Old local point/normal can be reconstructed from immutable previous geometry;
   gap/direction must remain tangent to that normal. Constant-frame covariance
   alone does NOT validate a spatially/time-varying frame field.
3. Use MaterialDerivative/materialLift for old e(s(q)) chain terms when force
   abscissae move. Current derivative is for a parabolic fixed-capacity seed;
   general-capacity derivatives and contact Birth/Death boundaries still need
   derivation. Do not freeze old(s(q)) as an AD constant or assume a derivative
   exists at a material partition,contact event or shape seam.
4. Independently validate prescribed moving-patch force/moment/loss and AD
   against a dense/function reference BEFORE a short actual3finger profile.
   Then same-physics Mesh/History/dt/full-cycle energy qualification. Retain
   existing1%/0.1%/1e-3gates. No12wrench approval or graspOptuna until then.

Fresh-tag smoke/reproduction commands(current fast model,NOT the future3Dadapter):
```
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/curve_vector_evidence.py --version v1 --verify
$PY tools/curve_vector_reference.py --tag UNIQUE_SMALL --only outward
$PY tools/curve_vector_reference.py --tag UNIQUE_CHAIN --only pullback
$PY tools/curve_vector_reference.py --tag UNIQUE_TINY --only normalized --outward-normalized
$PY tools/curve_vector_sofa.py --tag UNIQUE_PATCH --steps 100 --dt .01 --solver newmark --directed --compression-every 1 --normalized --outward --initial-vy .001
```
No host OOM,disk exhaustion or permission failure is claimed. A future session
must resume actual adapter development rather than treating this checkpoint
as final-system completion. Preserve failures/old SDK/Golden/SQLite/no Push.

## Newest unfinished task — finish noncollinear function-history integration

Do NOT repeat completed Hermite/11/21/41campaign or fixed-patch100/200/400
collinear runs. Same branch development/regrip-autonomous-research.

First read actual results/vector_history_sdk_20261116_normalized_cubic_turn20_a02
summary/process logs. Its predecessor failed at step11 due to gap interpolation
near yield. The projected-cubic alternative timed out480s after60/100steps;
the exact range-cache20step profile still took72s. Do not blindly increase
time or drop small dissipation. NormalizedSnapshot preserves yielded phase
separately and now uses admissible Bezier controls,with a linear-gap fallback.
Independent strict five-probe references PASS,including tiny loss1.056e-26.

Continue with actual noncollinear dynamics,paired representation-energy
inventory and independent function/dense references. Profile20steps BEFORE
100steps. Retain1%representation,0.1%time,1e-3force/moment gates. Prove exact
query-cache/range-lookup equivalence;test pure queries and one Commit. Then
moving normals/material-coordinate Birth/Death and nonconstant capacity must
be implemented before this fixed-plane benchmark can replace any3Dcontact.
It is NOT a free-object grasp,even if all patch gates pass.

Reproduction(new UNIQUE tags only):
```
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/curve_vector_reference.py --tag NEW_NORMALIZED --only normalized
$PY tools/curve_vector_sofa.py --tag NEW_PATCH --steps 20 --dt .01 --solver newmark --directed --compression-every 1 --normalized --initial-vy .001
$PY tools/curve_vector_assess.py --tag NEW_AUDIT CASE_TAG_1 CASE_TAG_2
```
After new source commit,seal NEW vector evidence version;never rewrite old
indices. A campaign checkpoint is not final-goal completion. No automatic
restart is installed or promised.

## NEW authoritative checkpoint — vector reference/actual SDK isolation advanced

The old "implement independent vector reference" task HAS NOW BEEN IMPLEMENTED
and actually tested,including a separate fixed-normal Vec3SOFA ForceField.
Do NOT rerun the completed Hermite/11/21/41or the new fixed-patch campaigns.
The final100mm grasp objective is STILL INCOMPLETE. No automatic restart exists.

The NEXT unfinished task is CELL-WISE STICK/SLIP CERTIFICATION for the
piecewise-cubic projected VECTOR snapshot in `AdaptiveSnapshot.h`,not another
blind sample-count increase. Actual candidate trials exhausted a TOTAL500000
evaluation budget under three different bounded strategies(local bounds,
integral-relative reintegration and degree6/10front-guided partition).
The preserved last diagnostic reports quantity17(unresolved LOSS UPPER BOUND),
not measured friction loss,at x~.9636128864. Resolved D~4.7357794e-18Fmm;
accumulated unresolved bound1.5983134e-24 exceeds requested~4.74e-25.
72independent50decimal-digit samples show4branch discrepancies,but max
point LOSS-DENSITY discrepancy1.8261e-29F is not proof that floating precision
alone causes that global bound problem. Do not conflate density F with Fmm.

Candidate follow-up:exact/interval Bernstein signs of the local cubic/capacity
polynomials to certify whole sticking intervals BEFORE quadrature. For equal
capacity c,polynomial p and constant vector d:
- unprojected:yield k²|p+d|²-c² (degree6);
- projected:2*c*(p.d)/|p|+k|d|²,with squared polynomial
  4*c²*(p.d)²-k²|d|⁴|p|² (degree10);keep the unsquared sign condition.
Current floating derivative-isolation roots are NOT certified interval signs.
Consider exact-rational representations of finite binary interpolation data
or outward-rounded intervals. Whole-interval equality needs explicit sided
derivatives,not denominator epsilons. Any ideal-function certificate must also
separate implemented floating evaluation error;do not silently discard small D.

Only after those tests:qualify an adaptive state Commit with representation
energy tracked separately,then new curved/moving3Dcontact using preserved
Hermite pullback and Birth kernels. The adaptive snapshot has NOT been put
into the SOFA benchmark or three-finger scene because its strict gate FAILS.
Current clean SDK/API+20step smoke is for UNCOMPRESSED function history ONLY.

Actual fixed-patch results:Euler100→200 FAIL.1% (x.364449%,D1.140386%).
Distinct directed Newmark100→200 PASS.1% (x.000833938%,D.00259944%);
not a3finger/time/global-energy certificate.400step contrast NOT RUN:measured
200step119.875s plus observed growth makes a default480s launch unjustified
without a new profile/algorithm. Prefix memo preserves ALL CSV values exactly
but119.563s vs119.875s gives no demonstrated speedup. Do not present the
forecast as an actual timeout or host exhaustion. Old failures remain.

Safe fresh-output reproductions from the external-drive project root:

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/curve_vector_reference.py --tag NEW_field --only field
$PY tools/curve_vector_reference.py --tag NEW_snapshot --only snapshot
# The latter CURRENTLY FAILS;preserve it. Independent50digit diagnostic alsoFAILS:
$PY tools/curve_vector_reference.py --tag NEW_precision --only conditioning
$PY tools/curve_vector_sofa.py --tag NEW_smoke --steps 20 --solver newmark --directed
# Read-only old-data analysis into a NEW result directory:
$PY tools/curve_vector_assess.py --tag NEW_assessment \
  20261116_directed_newmark02 20261116_directed_newmark_half01
```

All outputs under results/vector_history_*,build/vector_history_sdk_* are
exclusive/external-drive local files. No source/binary/raw/golden/SQLite from
the earlier curved project was overwritten. Same branch,no remote push.
500000is an actual local algorithmic resource cap,NOT host RAM/timeout/session
exhaustion. Further mathematical development remains possible;this is not a
completion declaration or an assertion of automatic future execution.

## Authoritative unfinished checkpoint — all listed physics children completed

The earlier stop was agent-selected,not a recorded host/session exhaustion.
The requested Hermite SOFA implementation and11/21/41actual convergence runs
are complete. The FINAL PROJECT OBJECTIVE IS NOT COMPLETE. Do not use old
"running" entries below as current process state. No automatic restart exists.

Physics/reference source checkpoint:a5703beff2839d0feea9f8174e862e645948871f.
Replay tooling checkpoint:a543bc4c84896028e06e9896c1b4c05e1c14fcf4.
Base index V2 verified4945artifacts/149Git blobs,zero errors. Replay index
verified34artifacts/3blobs. Actual sealed4s replay199.861s gives X/V/Rexact0.
All source/raw/build/old failure data is preserved on the external drive.

### First genuinely unfinished development task

Implement an independent VECTOR material-history FUNCTION reference on a
fixed-normal,fixed contact patch,using `models/yield_front_history/ScalarField.h`
as a scalar regression/reference ONLY. It is NOT a3Dfriction implementation:
do not clip vector components independently or drop normal-transport terms.
Select a piecewise/adaptive state representation controlled by energy AND
plastic-loss error,not force error alone. Resolve circular Coulomb yield
fronts before quadrature and differentiate the consistent return. Compare
against an independent dense/reference integral,including tiny newly resolved
losses;keep1%FAILs instead of imposing an absolute loss cutoff.

Then add objective tangent-frame transport and moving birth/death separately.
Validate energy changes from representation/transfer explicitly,not as heat.
Only after kernel/derivative/energy tests,integrate a NEW SOFA component with
Hermite virtual-work pullback. Require actual XML Data registration/string
parsing/grid counts,query purity and once-only Commit before dynamics.
Do not rewrite ConservativeBeam or overwrite Curved/PatchRefined v1/v2.

### Actual current failures and constraints

- Same-half-dt11→21motion1.62423%FAIL;21→41.416289%PASS. New phase-grid fine
  spatial contrast also passes,but does not certify every coarse mesh.
- Aggregate full-cycle time loss.0682459%PASS.1%;small-phase time loss FAIL.
- Actual625/312.5nm8.2s prefixes completed478.444/781.959s. Peak movement/
  rotation/normal force and7–8.2s loss PASS1%;2–3s loss0vs4.365e-19Fmm
  gives100%relative FAIL. Keep the absolute value AND original FAIL.
- Original1000nm full24s827.740s hold/recoveryPASS,but1250→1000nm15–16s
  loss1.085017%FAIL1%. A factor1.25contrast is not a factor-two certificate.
- Default312.5nm4s ACTUALLY timed out480.011s. Original longer prefix remains
  BLOCKED. Different sparse-recording contrast was proven state/common-CSV
  exact before its measured900s prefix. It does not approve undersampled
  full-cycle contact gates. No identical failed run was blindly retried.
- Fine24s energy forecast1733.038s>1320s policy,attempts0,BLOCKED;NOT observed
  host exhaustion. Whole physical energy,new12wrench and graspOptuna remain
  BLOCKED/NOT RUN. Existing discrete residual identities are not certification.
- Scalar reference v4PASS,including a preserved pre-fix zero-capacity tangent
  FAIL4→correct0. Max10pieces/120steps,independent dense-slider convergence,
 3x3potential tangent FD and nonunique-event rejection. NO3D/SOFA integration.

### Exact integrity/replay commands,not automatic execution

```bash
cd /media/ubuntu/99419895-2058-45b4-b746-b36ea7112e4e/research/LHJ/ReGrip
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/curve_evidence.py --version v2 --verify
$PY tools/curve_evidence.py --version replay --verify
# Fresh output MUST be absent. Preserves sealed binaries,parameters,steps.
$PY tools/curve_replay.py \
  --case results/autonomous_20261116_phase_grid_a01/patch_refinement_v2/uniform_profile4 \
  --out results/autonomous_resume_replay_a02
```

For an actual saved11/21/41case,choose its sealed `grasp/*` directory and a
different fresh output;the replay launcher verifies role-specific binary
hashes,all original scene/control values and exact trajectory equality.
Existing output names are intentionally refused. A successful replay does
not change that case's FAIL/limited physical verdict.

All new research needs a unique build/campaign path,4GiB/default480s/max4long
children. Exceptions require measured cost and finite decisions. No physical
threshold changes,object correction,unapproved push or fake resumption.
After vector history qualification:recheck late pressure/release,mesh/time,
transaction-level fixed-state pressure/work accounting,then12wrench/shapes and
100mm grasp optimization. Keep95.15mm research radius distinct from50mm target.

## NEWEST — independent element-refined contact v2 is running

Do NOT accept v1local625/local312 runner PASSs as refinement:SOFA ignored
their unregistered edgeSpacing attribute. Original stdout/raw/assessments are
preserved;reports/curved_evidence/PATCH_V1_INVALIDATION.json overrides that
interpretation. V1direct-field API tests were insufficient for XML registration.

Independent v2 fixes Data construction. Actual SDKAPI now checks findData and
string parsing;FD6.75082e-10 PASS. Six reversible source transforms restore
the ENTIRE frozen parent source exactly. Actual v2uniform4s142.441s matches
parent X/V/R exactly and logs480000states/120elements. Runtime ldd resolves
all6SOFA libraries to Matching SDK. Actual local profiles now log528000/
624000states,so refinement is genuinely active. They are currently running,
along with original-component1000nm full24s. Inspect their actual summaries
before any command. No automatic restart is installed.

```bash
# Same PY/environment exports below;from external-drive ReGrip root.
# Only if own profile PASS and exact prefix path is ABSENT:
$PY tools/curve_patch_trial.py --spacing .000625 --prefix
$PY tools/curve_patch_trial.py --spacing .0003125 --prefix
# Separate new evidence filename;never overwrite preliminary judgments:
$PY tools/curve_patch_assess.py --version completed
```

Both profiles preserve4GiB/480s. Prefix8.2s requires an actual measured own
forecast <=900s,else BLOCKED with attempts0. Local resolution is immutable
on reference90--100mm,not moving-patch remapping or uniform full-interface
refinement. Early prefix success cannot certify late pressure/release,
full energy,mesh/dt or12wrench grasp. Inspect original1000nm full24metrics
for original hold/recovery and late-phase loss once complete.

v15actual NEW-grid fine8s489.679s PASS,X/V/R0,residual-3.06377e-19. Fine24
forecast1733.038s exceeds1320s policy,attempts0. This is a recorded POLICY
block,NOT observed environment/session exhaustion or research completion.

## Newest checkpoint — phase-resolved slip-front investigation

Prior Hermite implementation,11/21/41 runs,new-grid24s dynamics,repeat,
mesh41and material1250nm runs have COMPLETED. Historical "running" entries
below are not live process claims. The full objective is NOT complete.
Actual per-point24s traces PASS query purity (X/V/R differences0),
coarse551.234s/finer708.429s. `slip_front/localization_v1.json` shows at7.2s
8of813/12of1623active material points carry plastic loss. Narrow yield-band
sampling is supported as a hypothesis,not yet a proven replacement model.

Current work:public cable snapshot observer v15 actual8s160.047s PASS;
new-grid coarse4s133.897s PASS,fine4s and minimum-spacing1000nm4s underway.
Inspect actual summary/logs first. No automatic restart is installed.
625nm was ACTUALLY REJECTED by the preserved .001mm minimum guard;do not lower
the guard silently. A prior runner KeyError happened BEFORE physics and
is distinct from that actual initialization failure.

```bash
# Same PY and three external-drive environment exports as below.
# Only after own4s summary PASS,and if exact output path is absent:
$PY tools/curve_local_history.py
$PY tools/curve_phase_energy.py --version v15 --duration 8
$PY tools/curve_phase_energy.py --version v15 --duration 8 --fine
# 24s requires own8s forecast <=1320s;otherwise policy BLOCKED.
$PY tools/curve_phase_energy.py --version v15 --duration 24 --fine
```

Priority:compare actual7–8.2s loss at .0025/.00125/.001mm using identical
cold-start phase grids;do not use failed checkpoint trajectory equivalence.
Then test a yield-front-resolved material history representation. Scalar
parabolic-capacity exact reference shows low force error with large loss
error,but does NOT certify the real3D model. Keep phase FAILs/Optuna blocked.

## Latest active work — do not repeat completed Hermite or clock campaigns

The requested Hermite SOFA implementation and11/21/41runs are DONE,not pending.
Fine21→41passes1%,coarse11→21still fails,with observed motion order1.958.
Uniform-time full-cycle loss remains FAIL despite hold checks passing.
Release-only refinement also actually FAILS.1%(.1312976%);do not rerun it as
if merely unexecuted. No observed session/environment limit caused the earlier
stop,and this work is not declared a completed research objective.

CURRENT actual children:phase-grid fine24s,phase-grid41node/finer-history4s
profiles,and grouped/reused energy observer8s. Check their JSON/logs FIRST;
no automatic restart is installed or assumed. Default4GiB/480s/max4long;
900/1320exceptions have actual own profiles and finite decisions in raw.

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
export REGRIP_BEAM_PLUGIN=build/autonomous_20261116_full_native_a01/beam/libReGripConservativeBeam.so
export REGRIP_CURVE_BUILD=build/autonomous_20261116_curve_native_a01/v1
export REGRIP_CURVE_OUT=results/autonomous_20261116_phase_grid_a01
# Execute ONLY if its own profile JSON passed and this exact full path is absent:
$PY tools/curve_phase_grid.py full_coarse --nodes 41
$PY tools/curve_phase_grid.py full_coarse --history .00125
$PY tools/curve_phase_grid.py full_coarse --tag repeat1
```

Next:assess actual coarse/fine FULL cycle and phase loss with unchanged.1%,
new-grid space/history1%,original equilibrium/recovery criteria. Do not inherit
old uniform-grid certification. New material sampling jointly refines its
normal/tangent midpoint integrals AND stored material points;it is not an
independent legacy Gauss8/16/32knob. Independent normal reference remains separate.

Actual old-grid split journal v11completed24s,remaining9.824e-18 after separately
derived mapped friction work. Whole physical/time energy certification is NOT
inferred from this discrete bookkeeping identity. New v12grouping and v13pure
energy-query reuse must pass independent split/actual-state comparisons before
new-grid use. Frozen old v9/v10/v11/v12binaries/source snapshots remain;
current-source rebuild guards deliberately reject mixed versions.

Keep12wrench certification/new100mm grasp Optuna blocked until required new-grid
convergence/energy/repetition passes. No fabricated candidates or real PET claim.

## Active continuation 2026-11-16 — implementation is no longer pending

The tested Hermite map is now integrated in `models/curved_contact`,with actual
11/21/41-node SOFA runs and original spatial limits. Do NOT repeat the old
"implement Hermite" task below. Current priority is full time/loss qualification
of the fixed-hardware,tributary-mass21node candidate,then synchronized energy.
11→21 still FAILS;21→41PASSES. Do not relabel the coarse model as qualified.

Current commands (external-drive project root):

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
export REGRIP_BEAM_PLUGIN=build/autonomous_20261116_full_native_a01/beam/libReGripConservativeBeam.so
export REGRIP_CURVE_BUILD=build/autonomous_20261116_curve_native_a01/v1
export REGRIP_CURVE_OUT=results/autonomous_20261116_full_native_a01
$PY tools/curve_qualification.py
```

Completed,do not duplicate or overwrite:
`curve_quarter_exception.py`→grasp/quarterdt_exception (1101.416s,global moment
FAIL.001031812);`curve_return_journal.py`→return_journal_v4(PASSlocalidentity);
`curve_checkpoint_solver_probe.py`→checkpoint_a01/solver_probe_v4(EXPERIMENTAL).
Completed continuation:transaction_journal_8s_v6 and the independent
`curve_compensation_campaign.py` under results/autonomous_20261116_beam_compensation_a01.
Current bounded children:`curve_compensation_refine.py`(same-half-dt mesh/history)
and `curve_compensation_energy.py --steps 48000`(full24s synchronized journal,v9).
These are real active processes,NOT an automatic future-session restart.
Check actual process/results before any resumption;tools refuse existing names.
The original900s blocked decision and failed checkpoint equivalence remain.
Actual quarter assessment is separate:quarterdt_actual_assessment.json. Half
versus quarter motion/loss pass but physical moment failure remains. Original
canonical_completed's900sblocked decision is not overwritten.

Next meaningful alternatives if loss still fails: separate endpoint-return
integration error from transport/global virtual work using the new actual
pre-Commit audit;compare public assembled solver systems before blaming missing
physical history. No arbitrary damping or friction changes to force PASS.
Keep grasp optimization blocked pending required convergence/energy gates.

The new observed fine-dt moment floor selected a more immediate test:use the
preserved Compensated.h arithmetic ONLY on structural free X/Z translations,
never object/quaternion/root. New component rejects non-roundoff discrepancies
or >2ULP adjustments. Actual scope test and profile are prerequisites;higher
resolution full contrasts launch only after base hold and their own profiles.
Its base/half/quarter hold tests and24srecovery have now actually passed.
Half→quarter time motion/loss PASS;base time loss FAIL is preserved.
Do not reuse standard-Euler spatial/history qualification as certification of
this new integration-arithmetic contrast. Its same-half-dt mesh/history cases
are running. Use `curve_compensation_assess.py --checkpoint UNIQUE_NAME` after
actual completion;existing qualification_v1.json is an immutable partial view.

After the full24s journal finishes,inspect all phases and the independently
derived Frame-return projection. Its first1sactual API/query-purity test PASS.
Cap-dependent RETURN energy is not fixed-state stored energy:the independent
pressure test shows released energy must include plastic and projection terms.
Do not infer vacuum-source work from finite differences of a clipped trial
potential. Physical vacuum work remains outside this prescribed-cap model.

## Historical plan (retained; Hermite implementation tasks now performed)

Read FINAL_REPORT,STATUS,assessment.json and manifest first. Do not rerun the
immutable a01campaign in-place. Work inside external-drive ReGrip directory.

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
git status --short
git log -4 --oneline
$PY tools/research_evidence.py --verify
$PY tools/birth_verify.py --raw
$PY tools/research_assess.py
```

1. Prioritize remaining4.96%/2.80% Beam-mesh translation differences.
   Contact-history loss already passes1% in this new model;do not rewrite the
   ConservativeBeam or tune its parameters to mask spatial error.
   Adjacent dt comparisons pass,but base→quarter motion.113702% and loss
   .174427% fail.1%;do not classify base-dt time qualification as complete.
2. `models/contact_kinematics/HermiteMap.h` is a tested independent candidate.
   Implement a NEW component using virtual-work pullback,not just a point
   replacement. Validate curved-contact detection,reference integration,
   normal/tangent consistency,multiple active intervals and query/Commit.
   Straight-segment active bounds without a proven conservative envelope can
   silently omit curved contact. Director length/axial strain is an assumption.
3. Compare against dense AD2 before optimizing assembly. Sparse equivalence is
   tested,but no production speedup or curved-contact dynamics result exists.
4. Run prescribed geometry/reference before3finger dynamics. Then profile4s
   and use independent11/21/41mesh and fine-history tests with original1%line.
   Normal Gauss order differs from immutable midpoint tangent integration.
5. Finish transaction-level work/energy accounting:matched-state Beam/FrameLayer/
   cable/contact/parameter/external work and Rayleigh loss. Scalar identity is
   not a global energy model;detachment inventory is not automatically heat.
6. Only after space/history/time/energy qualification:12wrench trials,shapes,
   pressure-capacity contrasts and new100mm grasp Optuna Study. Maintain
   failure controls and50mm target versus95.15mm research-layout distinction.

New namespace/clean build example(existing names are refused):

```bash
export REGRIP_RESEARCH_OUT="$PWD/results/autonomous_next_a02"
export REGRIP_RESEARCH_BUILD="$PWD/build/autonomous_next_a02/v1"
$PY tools/research_build.py
$PY tools/autonomous_trial.py profile_next --history .0025 --profile
$PY tools/autonomous_trial.py reference_next --history .0025 --duration 24
```

These reproduce CURRENT linear-centerline material points,not future curved
contact. Sources are snapshotted before compilation and identities guarded.
Default4GiB/480s,max4long children.900s only after recorded profile decision.
No background automatic restart installed. Source checkpoint is in manifest;
final documentation commit is visible in Git log.
Last validated source checkpoint:456d83f2f36fb0e64deabac91341c636681af36d.
New raw/source/build verifier passes894entries. All physics children in this
campaign have completed;there is no pending quarter-step process to resume.
