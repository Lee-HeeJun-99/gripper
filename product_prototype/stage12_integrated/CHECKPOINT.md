# Latest product-system state — RevAJ250-part candidate (2026-11-26)

Actual HEAD is `git log -1`; preceding work save e195f9a. Official RevAA304
remains unchanged; latest unadopted candidate is CURRENT_CANDIDATE.json.
RevAJ full assembly STEP, changed STL and250-part identity BOM actually exist.
This is NOT an adopted manufacturing or integrated digital release.

Actual changes since that save: ground-supported spindle removes the declared
AF bearing bypass; shared pilot register avoids bolt-float centering; finite
compression spacers/complete seating; lighter local Palm tabs; M3 Idler axle
with2.38neck,0.1fillets and integral metal shoulder,3 loose washers removed.
Final geometry/BRep/STL/integrals, actual metal stack,48 sampled drive poses
and5 nominal finite-wire/rigid-hardware poses pass within their limited scope.
The entire motor-foot supported area is unchanged by Palm material removal.

Palm volume reduction36.433%;0.311908kg reduction only at illustrative2700kg/m³.
Actual tab1N FEM h3/2/1.5 passes equilibrium/energy/element checks; response
refinement0.128372% passes1%, unsmoothed stress8.833449% FAIL. No trimmed peaks,
strength or whole-Palm PASS. Follow actual support geometry, not blind refinement.
Root and PET boundary maps are geometry/conditional force contracts, not actual
assembled Finger load results. No new rod/BVP or Native grasp rerun occurred.

Latest candidate audit: validation/integrated/AJ_readiness2, NOT QUALIFIED;
22 Stage2 system criteria and same-revision full Stage1 release remain missing.
Protected maximum, collet/motor axial capacity, actual material and full loaded
Finger/Palm models remain unresolved. No Stage3/purchase/hardware/push.

Automatic6-call budget unchanged/exhausted; service3 rechecked inactive/dead,
MainPID0. No external worker or Native/FEM child left active after these tests.
READY tasks remain and are not a completion claim. See next selection CLI and
AUTONOMOUS_RESUME.md; do not reset old runtime or regenerate completed cases.

# Actual complete-system drive layout and fault correction (2026-11-26)

Previous local save ea2cce6; latest actual HEAD from `git log -1`.
RevAF_layout6 generated238-part full assembly;82 changed solids, full candidate
identity BOM, nominal intersections0, independent BRep/STL/integrals PASS,
48 sampled drive full-turn/slip poses PASS. No full Finger/wire-motion release.

AF force-cap topology FAIL: actual bearing creates a parallel input/output
torque route. Actual conditional inertia/window analysis saved; no force cap
certified. A keyed ten-part manual calibration stand was generated, interference
fixed, independent mesh audit PASS; strength/sensor/hardware NOT qualified.

Current actual next implementation: ground_supported_clutch.py, RevAG candidate.
Ground1 clamp-head collision preserved; ground2 nominal clear but input-collet
STL not closed. Ground3 removes the unnecessary coplanar spotface and is under
actual generation/revalidation. These failures are not hidden or relabelled.
Official AA and22 Stage2 gates unchanged, automatic budget0/no new launches.

# Product-priority reset and actual CAD cycles (2026-11-26)

Started from d01db2b. Current actual commit: use `git log -1`; this entry is
saved with the cycle, not a claim of a future commit. RevAA official baseline
unchanged; INTEGRATED_NOT_QUALIFIED, all22 Stage2 system gates unqualified.

Actual new evidence: revAE_direct_clutch1/2 assemblies FAIL interference;
direct_clutch_geometry2 passes geometric integrals/BRep/STL ONLY.
actual_boundary_AD1 establishes finite nominal PET end travel/stop from STEP;
no new general rod solve or Native trial. See PRODUCT_TRACK_RESET_20261126.md.

Track selector now balances A/B/C; existing external6-call budget exhausted,
service inactive, zero new launches. Current interactive work continues on
candidate_system_integration; RevAF wire/whole-assembly generation is being
debugged in unique directories, no release or successful whole assembly claimed.

# Bounded cycle — BVP-seeded axial initialization (2026-11-26)

Started from0e109553941e8784ce298969865fce42ac8c40d5. Supervisor local save
PENDING; no git add/commit attempted or new commit claimed. One actual
initialization diagnostic: axial_seed1 solves the SAME counterfactual finite
extensible rods with independent continuous BVP initial states, rather than
zero states. No equation, material, geometry or tolerance change; no retry sweep.
Four BVP references and12 midpoint root solves (16/32/64) complete successfully.
All12 independently pass full strain/rotation complex-step stationarity, axial
constraint, coordinates and stored-energy reconstruction. All12 deliberately
perturbed terminal rotations are rejected. Finest tip/reaction relative errors
max4.605e-6/2.202e-5 satisfy original0.001 criteria. Producer/input hashes verified;
run/verify exit0 logs retained. Original axial_boundary1 FAIL and7 independently
failed equilibria are unchanged. Initialization sensitivity is supported; branch
uniqueness, minimum stability and actual guide boundary conditions are NOT proved.

Read-only axial_seed_release1 remains INTEGRATED_NOT_QUALIFIED(exit2),24 errors
including22 unqualified Stage2 criteria. No actual contact/BRep/strength/friction/
global assembly energy certificate, no CAD/BOM adoption; RevAA unchanged.
Next READY flexible_rail_contact: identify actual axial guide freedom/load ports
before selecting constraints, then coupled finite separate-body contact.
Alignment and fixture mechanisms remain independently READY. No RUNNING queue
tasks or live analysis children at handoff; children bounded4GiB/420s, STOP absent.
No SDK, criteria, manager controls or Stage3 changes. Existing artifacts and
unrelated untracked CAD/BOM preserved. Save awaits supervisor validation.

# Bounded cycle — axial boundary contrast (2026-11-26)

Started from0570ac49c556763500a7329366eb6b6c210e345a. Supervisor local save
PENDING; no git add/commit attempted or new commit claimed. One actual
finite-rod boundary analysis: axial_boundary1, not a repetition of free-tip tests.
Root fixed, zero terminal moment, dead transverse load, unknown axial reaction
with x_tip=L; this is an explicit counterfactual, NOT identified assembly guide.
Conditional typical materials/projected sections and RevAA adoption unchanged.

Four continuous BVP solutions converge at1/20mN for separate Rail/PET.
Their tip deflections decrease54.94/92.36% (Rail),74.78/95.70% (PET) versus
free-tip references. This quantifies boundary sensitivity, not actual contact.
12 midpoint solves at16/32/64: overall FAIL(exit2); only5/12 independently
satisfy equilibrium and axial constraint. Failed states and solver messages
are retained; no retry sweep. Independent complex-step strain/rotation energy
derivatives and coordinate/energy reconstruction reproduce12/12 saved states;
reproduction PASS is NOT equilibrium PASS. First verifier TypeError(exit1)
retained separately; corrected verifier exit0 with5/12 equilibrium acceptance.
Input hashes verified. No physical energy/contact/strength certificate.

axial_boundary_release1 remains INTEGRATED_NOT_QUALIFIED(exit2). Existing
release gates unchanged; no candidate CAD/BOM adoption, Stage3 or SDK changes.
Next: identify actual guide axial conditions and diagnose constrained-rod branch/
initialization using independent BVP evidence before coupled finite contact.
Alignment and fixture remain READY. All analysis children completed within
4GiB/420s. No RUNNING queue tasks. Historical failures/unrelated untracked
CAD/BOM preserved. Exact save request is pending supervisor validation/save.

# Bounded cycle — finite extensible free-tip reference (2026-11-26)

Started from a46536d2ec628e76c1da4d859aee83787d0bf1c1. Supervisor local save
PENDING; no git add/commit or commit SHA claimed. One actual design/analysis
cycle: scripts/extensible_rod_reference.py and validation/finger/extensible_reference1.
Rail and PET are separate finite planar extensible rods, root x/y/rotation fixed,
free axial tip, prescribed spatial dead transverse force, zero terminal moment.
These are explicit reference boundary conditions, NOT the actual assembly guide.
Independent axial strain is eliminated by exact stationarity e=(F dot t)/EA;
rotation remains nonlinear. Conditional typical material/projected section basis
and candidate RevAD lengths are unchanged. No CAD/BOM adoption or material fit.

Six body/load cases (0.1uN,1mN,20mN) and16/32/64 midpoint meshes give18 actual
solutions. Independent continuous BVP comparison passes predeclared0.1% finest
tip/rotation reference limits: largest finest tip difference0.006104%.
Small-load linear limit, finite virtual work and rotated-load objectivity pass.
Independent saved-state complex-step energy derivatives, axial equilibrium,
kinematic compatibility, stored energy reconstruction and input hashes pass
all18 states; deliberately perturbed terminal rotation is rejected.
All discrete optimizers report success and residuals are finite; original
individual child exit codes were not separately captured (outer log-reading
shell exit0 is NOT used as acceptance). Full logs/metadata retained.
PET20mN finite tip differs8.76519% from linear, Rail0.456074%; this provides an
actual finite-rotation reference rather than reinterpreting old linear states.

Read-only extensible_release1 remains INTEGRATED_NOT_QUALIFIED (24 audit errors,
including22 unqualified Stage2 criteria). Reference PASS is not contact, actual
BRep, strength, friction, dynamic/global assembly energy or system release PASS.
All prior failures and pre-existing untracked CAD/BOM remain unchanged.
READY flexible_rail_contact now requires coupled separate finite bodies, actual
guide axial boundary conditions, and actual geometry contact re-evaluation.
Alignment and fixture tracks remain independent READY work. No Stage3, SDK,
criteria, manager or save-control changes. No RUNNING queue records or live
analysis children at handoff.4GiB/420s bounds and STOP were respected.

# Latest bounded cycle — axial kinematic budget (2026-11-26)

Started at1c1d135761401fa430182dcbe5250b694d364482; supervisor local save PENDING.
No git add/commit attempted. One actual saved-state analysis cycle, not new
linear equilibrium trials: finite_kinematic_budget1 evaluates12 body states
from the existing16/32 distributed Rail/PET solutions. Producer/input hashes
were recorded before analysis.16point element quadrature, independent adaptive
quadrature, exact constant-slope control, and separate CubicHermiteSpline
shortening verifier all pass; input hashes and producer copy match.

Projected-to-finite coordinate reuse FAIL: Rail inextensible-lift x shortening
at32 is0.405602um(-1mN),0.466152um(+1mN), exceeding existing1nm contact budget.
Corresponding y changes1.450/1.781nm also exceed1nm. This is a coordinate
reuse rejection, NOT an independently solved finite-contact penetration.
Keeping material x fixed instead introduces engineering axial energy: Rail
3.09274/3.51997 times linear bending energy; PET0.976024/0.440899.
These alternatives quantify missing kinematics, not actual assembly energy
or a selection of axial boundary conditions. Conditional typical materials
and projected sections unchanged. No deformed actual-BRep certificate.

Read-only kinematic_release1 audit remains INTEGRATED_NOT_QUALIFIED.
All old failures remain immutable, including distributed8element Green FAIL.
RevAA remains adopted; no CAD/BOM, criteria, SDK or manager controls changed.
Next READY flexible_rail_contact: explicit separate axial/rotation DOFs,
variational/virtual-work and small-load checks, then actual finite geometry
contact. Alignment and fixture mechanisms remain READY independently.
No RUNNING queue records or live analysis children at handoff. No Stage3.
Results are pending supervisor validation/local save; no new commit claimed.

# Automation recovery after distributed-contact cycle — 2026-11-26

Actual distributed-contact results saved in1afffcb, original FAILs preserved.
Supervisor's first manifest rejection was scope-only: AGENTS common root
handoff paths omitted. Added only those two explicit paths, not arbitrary
root files; string result paths must resolve to already hash-verified records.
manager_flow2 tests this exact production manifest shape through two real
isolated supervisor commits and continuations. Child permissions unchanged.
Remaining original4x1800s service3 launch uses runtime/authorized_20261126_3;
consult live status before overlapping work. No integrated release PASS.

# Bounded cycle — distributed elastic Rail/PET (2026-11-26)

Started from19e9ea67e34edc8bbaf43bd6738b58508043fbc6. Supervisor local save PENDING;
worker did not stage/commit or change manager controls. RevAA remains adopted.
New actual output: validation/finger/flexible_distributed2/summary.json.
Nine RevAD-length small-load separate-DOF linear cases use the existing beam/QP
kernel with distributed unilateral interface, continuous cubic extrema and moving
tip-tangent terminal walls. Overall FAIL(exit2):8element +/-1mN PET Green tip
errors0.272/0.180nm exceed declared0.1nm. All16/32cases pass; finest motion
relative error max3.483e-7. All9force/moment/gap/complementarity/static-energy
checks pass. This is conditional typical-material projected geometry only.
Independent saved-state verifier passes, input hashes checked, release audit
remains INTEGRATED_NOT_QUALIFIED with22unqualified Stage2 criteria.

New mechanism evidence: terminal-only -1mN interface gap -0.200001mm;
distributed contact changes Rail tip from -0.279148 to -0.243442mm. Small
+10uN open-contact case matches independent terminal Green reference.
This excludes terminal-only reference as a distributed-surface certificate.
First attempt serialization failure(exit1) preserved in flexible_distributed1
with original producer/input hashes/log; first state was not serialized.
No old failures, CAD/BOM, criteria or SDK changed. No full finite deformed BRep,
finite rotation, friction, strength or global dynamic energy PASS.
Next READY: independently validated finite-rotation actual Rail/PET geometry;
preserve coarse Green failures and quantify discretization separately. Do not
repeat this9case linear experiment as new progress. No RUNNING queue records
or live analysis children at handoff. Save manifest contains cycle files only.

LATEST:9case flexible terminal reference saved in f5225df. Actual two-cycle
manager/save controls pass in isolated Git repositories; child sandbox remains
unchanged. Remaining5x1800s service relaunch is regrip-stage12-20261126-2;
check its live status before overlapping work. Explicit file/hash manifest,
staged guard and parent local save resolve the observed read-only-Git blocker.
No full system release is implied. Next distributed contact remains READY.

RECOVERY2026-11-26: saved9cases and every input hash independently inspected;
recovery_audit1 passes111 result/failure records. Historical Git-write failure
below is preserved. Explicit cycle files are now being saved by the authorized
supervisor, not by widening/bypassing the child sandbox. Manager save protocol
and isolated two-cycle Git controls implemented before relaunch. Remaining
original budget5x1800s, no6run budget reset. Live status will be in
runtime/authorized_20261126_2/status.json under service regrip-stage12-20261126-2.

HISTORICAL SAVE BLOCKER for this cycle: git add and git commit both failed because
.git/index.lock cannot be created: Read-only file system. HEAD remains999fb6a.
The filesystem permission profile makes.git read-only; no bypass or manager
control change attempted. Research outputs and queue/checkpoint changes remain
in working tree. commit_guard.py executed PASS on EMPTY staging only and is
NOT evidence that these changes were staged/guarded/committed. A writable-Git
manager/session must stage only this cycle's explicit paths, run guard and
commit before starting the next research cycle. Unrelated untracked CAD kept.

# Latest bounded cycle — flexible terminal reference (2026-11-26)

Completed one new independent elastic-Rail/PET reference mechanism in
scripts/flexible_rail_reference.py, actual output validation/finger/flexible_reference2.
Green-function compliance includes Rail tip rotation in the finite-clearance
terminal guide; separate PET and Rail deflections are solved, not equal curvature.
RevAD PET free length86.2mm, Rail88mm; existing projected sections and conditional
193GPa/Mylar typical moduli only. Nine actual8/16/32-element cases at -1mN,
+10uN,+1mN pass predeclared reference, force/moment, gap, complementarity and
static energy checks. Worst relative Green/FEM comparison9.722e-7.
Terminal reactions at32: -1mN back52.931uN, +1mN front115.044uN;
+10uN stays open. Omitting clearance contact work causes3.94/4.60% static
energy identity errors. This is not a global trajectory energy certificate.
Import failure(exit1, missing osqp path) and serialization failure(exit1 after
solves) are preserved separately; successful retry used existing dependency
path, no install. No old failure or artifact overwritten.

IMPORTANT: terminal-only model can cross actual Rail surface. No distributed
interface or actual deformed BRep qualification, friction, finite rotation,
strength or system PASS. Adopted RevAA unchanged; RevAD remains candidate.
Read-only integrated release audit remains INTEGRATED_NOT_QUALIFIED.
Next READY flexible_rail_contact: separate-DOF distributed unilateral contact,
continuous gap and independent small-load checks, then actual geometry; do not
rerun this terminal reference as new research. All analysis children finished;
no RUNNING queue records. This worker did not modify/launch any manager controls.

# Integrated checkpoint — 2026-11-26

AUTOMATION AUTHORIZATION: user approved actual session_manager execution.
Activation configured for6x1800s, transient user systemd service
regrip-stage12-20261126-1, no auto-restart/budget renewal. Existing paragraphs
stating 'manager not activated' below are historical; actual service/live
status must be checked in runtime/authorized_20261126_1/status.json and systemd.
Control tests and launch preparation are committed BEFORE starting the worker
so that a clean tracked tree is handed over. Worker owns research edits after
launch; do not concurrently modify shared research files in another session.
STOP file and systemctl stop remain authoritative. See reports/SESSION_MANAGER.md.

LATEST completed follow-up, after3ef32a7 (supersedes READY/RUNNING and64
inspection-only statements below): actual owner64_working1 exit0, optimizer
300iteration-limit FAIL retained. Static constraint generation used220of3752
rows, then checked ALL original rows. working_controls1 executes the actual
archived branch on an independent QP and rejects disabled violation insertion.
No physical contacts removed or state corrected.

Stored final64 state independently passes owner64_working_force1:
1.345481e-9N force-equivalent residual and9.72769e-9 complementarity;
owner64_working_geometry1 actual annular-sector/front/back intersection PASS.
owner_states2 independently certifies16/32/64 states with exact source identity,
retaining original optimizer FAILs. It does NOT change their execution results.
Finest32/64 migration0.0209323% passes1% locally;16/64 is3.99215%, FAIL.
No full mesh, flexible Rail/friction, material strength or system approval.

Next READY: flexible_rail_contact; actual independent elastic-Rail/PET reference
model required before finite loading. Do not continue mesh-only optimization
of the same rigid fixture without a new hypothesis. Alignment and incomplete
hardware-fixture preparation remain independent READY tracks.
All known analysis children have completed. External manager is not activated.
Actual final local save via git log; release3 remains NOT QUALIFIED.

Current continuation (supersedes mid-session RUNNING statements below):
last committed implementation save is413eb44; final save is identified
by `git log -1`, not a self-referential hash. Adopted RevAA unchanged. AC/AD
remain unadopted candidates. release3 is INTEGRATED_NOT_QUALIFIED, all22 Stage2
system criteria still unqualified. No Stage3, Native or physical measurements.

Material-owned static constraints plus independently tested analytic point
Jacobians: owner_analytic_reaction2 certifies unchanged16/32 saved states at
1.301e-9/6.326e-9N force-equivalent residual, exact actual-channel geometry
owner_analytic_geometry1 passes. This is rigid prescribed Rail, frictionless,
inextensible PET only;16-to32 axial migration differs about4%, not1% PASS.

owner64_1 has no final summary and its exec process is no longer available;
exact termination cause/exit code was not captured, so NOT labelled timeout.
Latest local initial guess n64_00000590.json is retained with SHA through
owner64_inspection1. Full saved state/material coordinates are also in that
tracked inspection result. It is NOT a completed solve. Independent exact
actual geometry owner64_geometry1 PASS, but owner64_reaction1 FAIL:
1.001656e-6N vs1e-8N; complementarity2.16556e-7 vs1e-7. No mesh PASS.
owner_rank1 actual diagnostic: active rows/rank16:27/7,32:112/10,64:196/15;
large row dependence supports a numerical working-set investigation but is
not a proven sole cause. No inequalities or physical state were removed.

Actual next cycle completed after413eb44: owner64_cone1 REJECTS signed QR
reduction (15rows, maximum nonnegative reconstruction residual0.0816634).
owner64_cone2 adds only existing physical rows,170total, to recover the local
cone within7.41822e-9 against1e-8 numerical criterion. This is NOT nonlinear
feasible-set equivalence or permission to drop collisions. No new equilibrium
has been solved; contact_constraint_conditioning remains READY for a verified
working-set method with ALL original nonlinear checks retained.

Fixture v1 pin path FAIL preserved. V2 actual Z-pin and stock socket plugs,
90deg shaft assembly setup, pass finite pin/tool/RH-thread extraction samples
off-bench and11 sampled retained-support poses. No strength or hardware PASS.
Source closure, gate negative controls, empty-input rejection and offline
manager controls strengthened. Manager remains NOT activated.
No analysis child remains running after explicit polling of known sessions.
READY work remains; no claim that independent digital work is exhausted.

Next: diagnose cone-preserving contact working-set formulation using owner_rank1
and the stored64 guess, then independent force/geometry/migration certification.
Actual coupling selection, guaranteed overload cap, coupled flexible-Rail and
friction, full AD Stage1 revalidation, and system strength remain unfinished.

Cycle3-7 mid-session: actual RevAD funnel3fronts +304part STEP; adaptive
integral/face-model/BOM/local continuous-aperture audits pass bounded scopes.
Actual exact circular-arc PET envelopes clear AD at stored32segment states;
ruled-loft earlier FAIL preserved. Force and migration still FAIL, including
analytic-gradient AD6 and independent normal-cone recovery. owner_contract1
proves a numerical minimum-Jacobian can leave the physical normal cone and
SLSQP can report success at a wrong equilibrium. Does NOT by itself establish
the actual PET failure's only cause. Material-owned exchange is now actually
running material_owner2 under420s/4GiB; do not duplicate its output directory.

Actual HPMC clearance-gauge CAD and screening do not qualify a force cap.
Ideal Oldham reference,4part counterbalanced torque fixture,11sampled support
poses and strict blank recording/software controls executed. No hardware data.
Evidence audit2 passes44result/failure hashes with archival source resolution.
AA/oldStage2 directories remain unchanged. Manager is prepared/offline-tested,
not activated. This is a mid-session local commit, not an execution stop.

Cycle2: finite_pet1 inter-node gap FAIL preserved; exact circular-arc feature
constraints in finite_pet2 pass the bounded endpoint model. No end stop control
reveals1.40643mm migration. Actual RevAC three shortened PETs +304part STEP/BOM
created; initial integral FAIL independently corrected on same CAD by adaptive
audit revAC_geometry1. However actual deformed front/skin BRep common FAIL
channel_geometry1. Diagnostic1 separates new lip13.816 and old body3.921mm3
at60deg. Do NOT adopt AC merely from reduced endpoint PASS.

Next actual hypothesis: finite entry funnel allowing curved approach, and
contact against finite terminal surfaces instead of endpoint inequalities.
Session-manager preparation is dry-run only; no external worker activated.

Started from4e7130d; use git log for actual latest save. Adopted RevAA only;
RevAB candidate remains separate. Registry1 reconciled304 actual STEP hashes
and prior geometric integrals, with physical mass/inertia explicitly unassigned.

Jam-energy2 verifies a new transient overload counterexample, not a cap.
Integrated gate release1 correctly rejects missing system evidence and22
unqualified Stage2 requirements. Controls1 actually rejected12 corrupt inputs;
material-only changes invalidate part applicability even when STEP is identical.
No old geometry/Raw/criteria modified. No Native/power/purchase/push.

Next actual work: limiter candidate geometric compatibility and finite-rotation
separate PET coupon. These remain executable; this is a mid-session save.
