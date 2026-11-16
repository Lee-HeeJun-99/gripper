# Autonomous research status — active continuation 2026-11-16

## Latest 2026-11-17 checkpoint through372 (NOT project completion)

Local source/tool commits through3181ce8. Actual fixed-sphere356 completes
8s;366 completes16s/1600steps in268.204s. Final tip -0.00672mm,max speed
0.00854mm/s,T=0,contact multipliers0. This is frictionless FIXED-object
release/near-rest recovery,NOT free6DOF/3finger grasp or design superiority.
Actual states: designs/visualizations/film_native_20261117_sphere_recovery_actual372/.
Full-cycle buffer-clearance audit358 FAILS (-0.00013543mm at7.99s);the gap
to the radius8 zero-thickness sphere remains positive0.00986457mm. BothSide
contrast367 is REJECTED as a fix:all5 physical journals byte-identical in370.
Time348/351 still FAIL0.1%;full energy/friction/free grasp/Optuna BLOCKED.
Next REAL implementation is candidate-complete triangle contact with its own
row-observer interface;independent temporal work is a shared C2 tendon
profile. No candidate-complete or C2 implementation is claimed yet.
See FILM_TEMPORAL_COUPLING_20261117.md and LONG_RUN_RESEARCH_CHECKPOINT.md.
Historical activity notes below are not live process status.


## 2026-11-17 actual continuation through343 — project NOT complete

Local feature commit518208f adds current closest point/gradient/Hessian and
SQP line-search globalization,without changing accepted forces or tolerance.
Actual333 completes4s/400steps:70.0995s runtime;whole-triangle buffered gap
defect2.21e-11mm versus0.000531mm in307. Radial moment and force pullback
checks pass in limited scope. Discrete force-location covering arc73.208deg
is NOT contact area/pressure/holding performance. Fixed-object,frictionless,
single-finger only;NOT free6DOF or full-energy certification.
Failed320/322 and rejected remedies325/328/329 are preserved. Same-binary
short time comparison337 FAILS0.1%,including pre-contact motion/energy;
the contact event alone cannot explain all time error. Full-window344 and
subsequent development must be judged from their actual final result files.
Details/reproduction: FILM_TEMPORAL_COUPLING_20261117.md and
LONG_RUN_RESEARCH_CHECKPOINT.md. Grasp Optuna remains BLOCKED;no fabrication
or actuator performance is claimed. Historical notes below are not live status.


## 2026-11-17 continuation through319

Actual current-normal sphere307 completes4s; however exact triangle audit312
finds buffered gap -0.000531mm. A new closest-primitive AD contact model is
now implemented and actually SOFA-tested:316 completes20 steps/.1s;317
buffered gap -7.13e-14mm;318 radial moment defect3.18e-15;319 force pullback
defect7.47e-16. These are limited checks,NOT full convergence certification.
See FILM_TEMPORAL_COUPLING_20261117.md for definitions and prior failures.
Whole-cycle292 time convergence remains FAIL;full energy and grasp Optuna
remain BLOCKED. Actual free6DOF/3finger/multimaterial grasp is NOT RUN.
Next executed tasks are wide closest-contact320 and tangent-failure321;
their final result files,not this historical activity note,define status.


## 2026-11-17 latest actual checkpoint through305

Project NOT complete. Work continued beyond the old campaigns. Source feature
commits through29ef7e4 are local only; current-sphere geometry is an additional
experimental implementation, not a replacement certification.

Actual fixed-cylinder270 closes over4s;275 completes8s closing/hold/release.
282 completes16s including settling (1600steps,281.424s): final tip -0.007395mm,
maximum speed0.009374mm/s, zero prescribed tension and no positive contact
impulses. These are actual research-parameter results, NOT free-object grasp.
The first800 rows of282 match275 bitwise (state/contact/momentum/coupled CSV).
Sphere284 closes4s but supports locations over73.148deg versus Cylinder
123.752deg. Discrete force-bearing location spans are NOT contact area,
continuous wrapping angle, pressure or holding capacity.

Whole-cycle275/288 time comparison292 remains FAIL at0.1%: tip2.3268%,
normal force14.4819%,attachment energy1.1316%,kinetic energy8.3910%.
Inherited failures remain. Same-binary cache benchmark281 has3 alternating
pairs, all5 physical CSVs bitwise identical, median runtime ratio0.77813
(22.19% reduction);704 mechanical evaluations become402, with302 exact reuses.
This is scoped performance qualification, not physical convergence.

Measurement issue isolated: main journal.x is WORLD, not displacement.
Late world-minus-rest force reconstruction loses precision. Near-rest
prescribed probe293 gives relative impulse residual0.00419962 in294 world
reconstruction versus2.78543e-8 in295 direct local-displacement reconstruction.
296 recorder ON/OFF physics CSVs match bitwise.291's earlier attempt wrongly
interpreted main x as displacement and is INVALID postprocessing, not physics.
Old whole-cycle raw lacks exact local coordinates: do not retro-certify it.

New root cause298: frozen begin normals give accepted exact-sphere radial-law
moment deviation0.6430% in the wide Sphere test. New SphereStep uses actual
current radial gaps/normals and TRUE constraint geometric tangent. Independent
FD relative error2.21e-15;actual30120-step test and302/303/304/305 partial
equation checks pass their LIMITED scopes: accepted radial-law defect1.59e-15,
force-row reconstruction4.97e-17, impulse residual3.49e-6,derived BE identity
4.02e-10. This is a NEW fixed-support sphere model, not native-contact
equivalence, friction, CCD, contact-area convergence or free6DOF certification.
300 source-archive omission is preserved as prephysics FAIL;301 fixes it.

Current actual extension306: inspect summary/result before interpreting its
prefix. No tolerance relaxation, fake forces, SDK edits, hardware, remote push
or paid service.299 rejects unsupported moving colliders before accepted rows.
Three fingers/free6DOF/12-wrench/multimaterial, full energy, final structure
superiority and grasp Optuna remain BLOCKED/NOT RUN.

## 2026-11-17 actual continuation through264 — supersedes older status

Project NOT complete. Functional commits: b8b9cc3 (profiling/routing),
6172967 (cache recovery),9354793 (nonlinear contact),74175ca (BDF2 alternative),
ed40987 (mandatory accepted-stage owner). Sources/builds/raw remain separate.

Actual235/243 complete400/800-step fixed-cylinder closing;246 time FAIL:
force9.27393%,tip0.163093%,attachment0.169901%,kinetic4.73995%.
Independent240/241 confirm accepted impulse equations and the derived BE
identity, NOT whole energy or global force/moment certification. BDF2 actual
244/247/248 also FAIL250; do not adopt it as a qualified time fix.

Actual251 higher-tension one-factor capacity probe fails free Newton at2.95s.
Available2.94s state has73.122deg load-bearing location span, but partial-run
diagnostic258 and plot259 are EXPERIMENTAL/PARTIAL FAILED, not wrapping/grasp
approval.263 with single-Newton predictor gets past that stage to3.36s, then
FAILS the coupled Newton30-iteration budget. This is algorithmic failure,
NOT OS memory/runtime exhaustion. No tolerance/iteration inflation was used.
Short260 accepted impulse/energy checks and actual negative-owner guard264
pass their LIMITED scopes.265 tests previous accepted velocity initialization;
inspect summary/result before using its data. No automatic restart is assumed.

Read FILM_TEMPORAL_COUPLING_20261117.md and LONG_RUN_RESEARCH_CHECKPOINT.md.
Remaining: robust complete closing/hold/release, mesh/history/dt, current-normal
angular consistency, reactions, whole energy, self-contact, free6DOF/3finger/
multimaterial/12-wrench grasp. Final-design superiority and grasp Optuna remain
BLOCKED/NOT RUN. Research parameters are not measured PET/actuator properties.

## 2026-11-17 continuation through224 — supersedes historical checkpoints

Project NOT complete. Code checkpoint b8b9cc3 qualifies profiling/routing;
subsequent native coupling is experimental working-tree development.
Scoped PASS: passive journal identity; reusable-lift derivative/state identity
and4.562% median speed improvement; distributed-guide kernel/API; closed-cylinder
construction; actual20/40-step coupled Sphere BE equation solves. Accepted
nonlinear impulse residual .93498 reduces to <=3.56e-6 in the checked20-step
trajectory. This is NOT full force/moment, time or energy certification.

FAIL retained: inherited gates; native cycle180; object collision mesh201
(fine-pair force1.7359%, kinetic4.2255%); coupled time219. Failed210/211
energy line search is retained;213 uses residual merit, SAME tolerances.
Native LCP nonconvergence222/223 motivates direct active-set reference224.
225/226 are the next actual reproductions: use summary/process result, not
partial CSV, to determine completion.

EXPERIMENTAL: inward no-object bending with slower control and fixed-cylinder
load-bearing location span11.243deg. Sphere broad wrapping NOT approved.
BLOCKED/NOT RUN: whole energy/current-normal angular consistency, self-contact,
friction time/history, free6DOF/three-finger/multimaterial/12-wrench grasp,
final design and grasp Optuna. Properties/actuator/guide hardware remain assumptions.
See the two new20261117 reports.


## Final measured state of this response (through146; project incomplete)

Actual coupled film/rails/tendon and fixed-sphere surface contact implemented.
All launched processes complete. Partial coupon4-observable time PASS remains
strictly scoped. Coupled Trapezoidal AND BDF2 attachment-energy time FAIL;
full BDF2 coarse→fine .7455%, fine-pair .4853%. Pre-1s error also persists after
local refinement. Three BDF2 partial discrete-energy audits PASS but global
grasp energy BLOCKED. Sub-tolerance mapping suppression hypothesis rejected
by source/API unit144. Actual1s geometry arches away, not a qualified wrap.
Free6DOF/12-wrench/Sphere-Cylinder-Box grasp NOT RUN; grasp Optuna BLOCKED.
Response/context budget checkpoint, not OS timeout/final goal completion.
See newest NEXT and FILM_CONTACT_DYNAMICS_20261116.md; no background restart.

## Latest continuation: actual coupled actuation, full grasp still unfinished

Native follow-up110–118 is COMPLETE, not RUNNING: separate installed-ABI
plugins and no-contact control PASS; actual tendon-driven skin contacts fixed
R8 sphere atx95. Native100/200/400-step time FAIL (nonadjacent force25.423%,
tip2.044%). Fixed reaction unobservable after projection: BLOCKED, never zero.
All launched physics processes are complete; no background restart is claimed.

See FILM_CONTACT_DYNAMICS_20261116.md (newest evidence, supersedes historical
status below). Mapped-mass MBK cache defect corrected independently, no SDK
edits. Coupon Trapezoidal3280/6560/13120 windowed time Gate PASS (.1%, all pairs,
physical intervals and endpoints); bitwise repeat PASS. Old coarse/BDF2 FAIL
retained. Fine static21→81 space PASS, old11→41 space FAIL retained.
Actual Film+separate flexible Rails+routed eccentric Tendon implemented and
API/mapping/force/tangent validated. Low-load8s recovery observed; nominal
T=.001 runs to2s with profiled phase refinement without Newton failure.
Coupled low-load1600/3200/6400 time FAIL due attachment-energy .8232% nonadjacent
difference. This is not hidden by passing tip motion. Fixed-sphere Native
integration is experimental; patched SDK lacks collision binaries, so any
installed-SOFA experiment uses separate rebuilt plugins and explicit ABI audit.
No free6DOF grasp, wrapping certification or grasp Optuna. Global energy BLOCKED;
partial no-object discrete energy identity PASS only. Original friction-time
FAIL unchanged. Research NOT completed; no automatic continuation claimed.

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

## Newest completed experiment status

Hard-boundary campaign25 and mapped reference26 are complete, not RUNNING.
Hard mapped short FEM/API/mass consistency PASS; full transient convergence FAIL
despite zero Newton failures. Hard versus penalty waveform differences are far
smaller than time-refinement errors; root penalty is not supported as the main
remaining explanation. Phase27 localizes the largest discrepancy after contact.
No long physics process or automatic restart is claimed at this checkpoint.
Film+Rails/tendon, friction-time qualification, full energy,12-wrench grasp and
grasp Optuna remain unfinished. No OS/session hard-timeout was observed here;
individual runs stayed within480s. Further work is not declared completed.

## Latest verified development checkpoint — nonlinear defects corrected, final goal unfinished

Local feature commit bceda3a records Newton-stage tracing, exact cache keys,
trial-state tangent and independent BDF line-search correction. Subsequent
BDF2 and mapped-boundary work is identified by exclusive source snapshots.
PASS limited: tiny-coordinate API regression; distinct main/trial matrix test;
passive tracing purity; unloaded/no-contact SOFA; 11/21/41 final force balance;
short BDF2 versus independent FEM (relative differences below 2.89e-10).
FAIL: full transient tip/U/contact-area/normal-force convergence; nonadjacent
11→41 energy 1.1486% and area 1.3360%; original friction temporal failures.
Mapped hard-clamp testing is a separate boundary model, not a penalty-model
PASS substitution. Full film/rail/tendon grasp, energy and Optuna stay blocked.
See FILM_SHELL_PHYSICS.md and new raw campaigns; prior entries are historical.

## Latest film implementation checkpoint — final goal NOT complete

Source commits38f3966(film mechanics/contact) andb86e305(equal-volume/competition).
PASS limited:independent membrane/plate/cantilever patch,objectivity,force/Hessian,
actual SOFA API4modes;actual finite-width fixed-plane deformation/contact exists.
Equal-volume skin/rail concept439.33979mm³ and5daytechnical/application drafts
implemented. Baseline/grasp advantage,layer friction and hardware NOT certified.

FAIL:actualfilmEuler dynamic force residuals,BDFnonfinite,base-dtindependentNewton,
coarse→fine contact/energy. Rootfixture continuation achieves21nodestaticendpoint
residual6.35e-6 only. Actual first free M/C/K matrix matches5.58e-17;nonlinear
RHS/correction remains unverified. Independent200/400Newtoncompletes,NOTSOFA.
Temporal exactgreat-circle referencePASS butgeneralendpointtangent NOTimplemented;
originalSphereEvent0.146423%andCurved0.8519%FAILstay. Fullenergy/graspOptunaBLOCKED.
All children finished;no ongoing process or automaticrestart is claimed.

## Latest sphere-event result — further development, not completion

New SphereEventReturn + separate actual SOFA adapter handle fixed-sphere chord
Birth/Death and outside-to-outside transit. Unit FD/objectivity/discrete identity
and actual API PASS. Time FAIL remains:512internal subdivisions give adjacent
0.09758%/0.09756%PASS,but20→80is0.146423%FAIL. Solver-free reference gives
0.146397%,isolating temporal return/loss quadrature in this experiment.
No tolerance changes;oldCurved.8519%FAIL also remains. Manifest
DESIGN_TEMPORAL_EVIDENCE_20261116_v1.json verifies853artifacts,not physics.
Code commit1108fad. All launched physics children finished;no background job.

## Newest physics/design checkpoint

PASS(limited):Changing-normal active one-point path kernel+actual SOFA API and
20/40/80dynamic phase-loss time test(.00177531%max). This NEW fixed-supported
sphere benchmark is not the original curved/freeobject case;old.8519%FAIL stays.
General moving CurvedContact integration/Birth/Death/event-exact law/adaptive
spatial owner/global energy/longduration remain EXPERIMENTAL or BLOCKED.

IMPLEMENTED:baseline source extraction;two tapered-film concept meshes,
50mm body target,3zone circuits,OBJ/XML and SVG/PNG. Actual SOFA geometry
loading+4geometry regression tests PASS;Shell mechanics and grasp comparison
NOT RUN. Material5.74xbaseline is a design risk,not an improvement. Final design
NOT SELECTED;grasp Optuna BLOCKED. No real material measurements or hardware run.

## Newest actual moving3D owner/adapter checkpoint — NOT final completion

Latest completed regression:current03math6/6PASS;06repeat journals identical;
explicit solid-sphere inertia20/40/80contact processes complete,but temporal
phase loss.851917%FAIL. Initial defaultI/m=1was a numerical isolation condition,
not a certified solid sphere. Cases are separate and not pooled. All children
have completion records;no ongoing RUNNING/background restart is implied.

Subsequent work also implemented TemporalYield fixed-plane vector event+IFT
(256states),six-test mathematical regression,and a fresh clean06SDK/API/wrench
build. This is a prerequisite,NOT yet a new changing-normal temporal return law.
No whole3finger simulation/grasp optimum is claimed. No host resource exhaustion
has been evidenced by these bounded experiments;the larger objective remains
unfinished. Full-duration exact replay is algorithmically capped,not a reason
to remove that cap or declare the project complete.

IMPLEMENTED:independent exact-function GeneralVectorCurvedContact,with immutable
material geometry,original Birth/circular return,once-commit tokens and optional
SphereHistoryChart seed. This is128operator bounded replay,NOT a qualified
general adaptive STATE fitter. Adaptive integration is a separate implemented
feature;do not conflate it with adaptive history compression.

PASS in limited scope:2910material states versus explicit point prefix;normal
frame covariance2.1272e-16;actual matching-SDK API/FD;moving sphere global
internal wrench8.61292e-22 and force FD1.18994e-13. Actual free sphere/Hermite
20/40/80step dynamics completed. Adaptive.02/.01/.005mm integration contrasts
PASS1%including aligned phase plastic loss(max~9.41e-9relative). New model's
exact unchanged-configuration identity avoids repeated rounded yield projection;
no positive physical loss threshold or force/torque correction is applied.

FAIL:adaptive time comparison,maximum phase-loss difference.851919%>unchanged
.1%. Final accumulated loss alone.0642703%would pass but does NOT override
phase FAIL. Prescribed identical geometry(no Solver) reproduces.851935%,so
the main measured error is not eliminated by changing the SOFA Solver.
Independent variable-capacity scalar benchmark confirms endpoint-capacity loss
is first order(.10899/.054957/.027594%error at20/40/80),while event-integrated
capacity work matches analytical reference to6.46e-15relative. This scalar
formula is NOT installed as a general3D friction/force/Jacobian replacement.

BLOCKED/NOT RUN:qualified general adaptive history compression,full3finger
11/21/41mesh/history/time,global energy,12wrenches/shapes and grasp Optuna.
No existing full-gripper FAIL has been deleted or reclassified. Old vector and
curved indices still PASS integrity. Current summaries,not old RUNNING entries,
identify finished children. No automatic restart is installed.

## Newest prerequisite — general sphere chart PASS in mathematics ONLY

SphereHistoryChart now supplies nonparabolic normal-force capacity,spatially
varying normals and material first/second jets for prescribed previous Hermite
geometry.129states and event/invalid-input controls PASS in sphere_chart04.
An actual covariance FAIL was corrected by relative-control interpolation;
the1e-16criterion was not relaxed. No SOFA dynamics/Commit approval is claimed
for this chart. The adaptive general-history owner and curved forcefield
integration are still NOT RUN;full gripper/energy/graspOptuna remain unfinished.

All launched children have completion/exit records. This is a finite response
working-context checkpoint,not host exhaustion or project completion. Resume
the first task at the top of NEXT;no background restart exists.

## Authoritative latest checkpoint — vector patch qualification,not gripper completion

All physics/reference children of this vector cohort have actually finished.
No RUNNING process or automatic restart is implied by historical sections.
Same branch development/regrip-autonomous-research. Model/metrics details are
in reports/vector_history/QUALIFICATION_v1.json and immutable raw snapshots.

PASS in FIXED-NORMAL PATCH scope:normalized vector phase/history,strict five
prospective loss references(including1.056e-26Fmm),actual Matching SDK
Force/Jacobian/API/query purity;100/200/400step Newmark time tests;1e-9→1e-10
state-fit contrast;exact repeated journal;50step force reversal;771constant
frame covariance states. Base→quarter movement x.00032505%,y.00103590%,
plastic loss.01805761%PASS unchanged.1%line. Representation loss.00034348%
PASS unchanged1%line. Actual dynamic force residual<=7.08e-14relative.

Outward interval arithmetic is EXACT-RESULT equivalent to the rational
predicate in actual20/100/400/reversal journals(all common values identical).
400step runtime455.897s→6.7775s;100step115.056s→3.5717s. This is bounded
arithmetic acceleration,not changed friction or a whole-gripper speed claim.
Independent material-coordinate first/second derivatives and AD pullback now
PASS;they are not yet connected to the moving curved-contact SOFA component.

EXPERIMENTAL:source-matched fixed-patch discrete energy audit,with signed
linearization,cached-acceleration and representation inventories separate.
BLOCKED/NOT RUN:general moving3Dnormal/capacity/Birth/Death integration,
qualified three-finger Mesh/History/dt/global energy,12wrench shapes and grasp
Optuna. Original Beam/Curved/History/Birth sources and Golden unchanged.
The entire ReGrip objective is NOT marked complete. Remaining work is real
development,not merely documentation or another completed-Hermite rerun.

## Newest scope correction — research NOT complete

Actual fixed-patch projected-cubic100/200/400step runs and repeated200run are
complete. Base→quarter x/y.0049881%,loss.0155430%PASS.1%;this is NOT moving3D
grasp certification. Newmark cached acceleration was checked against actual
SDK cpp;matrix residual<=9.23e-14,discrete energy residual<=5.18e-24Fmm.
Full gripper energy/pressure work and100mm grasp Optuna remain BLOCKED.

Noncollinear projected-cubic100steps:TIMEOUT480s,60commits,not PASS. The
normalized gap/direction alternative passes independent phase/state and five
strict loss references;linear version has an actual8192cell API-budget FAIL.
Cubic version actual API PASS but first dynamics FAILS at step11. New bounded
shape-preserving-gap implementation is being evaluated;no completed dynamic
success should be inferred until its actual summary exists. Older statements
below that snapshots were never deployed are HISTORICAL,not current facts.

All three-finger Mesh/History/dt/full-cycle energy/12wrench/shape/graspOptuna
qualification remains unfinished. No original physical tolerance changed.

## Newest measured vector checkpoint — overall objective remains unfinished

PASS in scope:600circular-return states;normal transport/isometry;12step
noncollinear function history/dense plastic reference;function rigid covariance;
one-sided material derivatives;actual Matching SDK F/dF/matrix/Data/query/API;
actual fixed-patch100/200step dynamics and separate20step current-source smoke.
Directed Newmark fixed-patch dt/2movement.000833938%,loss.00259944%PASS.1%.
Euler fixed-patch time checks FAIL and remain preserved. dt/4 NOT RUN.

Adaptive snapshot EXPERIMENTAL/FAIL,NOT deployed in SOFA:coarse/fine sample
tests alone were insufficient. The independent withheld-state test exposed a
4.6%target overshoot;stricter internal estimation corrects the withheld error
without relaxing its budget. Strict loss integration still exhausts500000
TOTAL evaluations;latest diagnostic identifies unresolved upper-bound
accumulation,not a measured negative energy or physical engine crash.
50digit point comparison FAILS4of72branch/loss cases near yield;absolute loss
density error1.8261e-29F. No tiny-loss cutoff or fake PASS applied.

No running child/automatic restart should be inferred from historical text.
Current actual processes must be checked. All three-finger/full-shape/global
energy/grasp optimization gates remain BLOCKED/NOT RUN;this fixed-patch model
has no moving boundary,normal compliance,Birth/Death,rigid rotations or6DOF
object. It cannot certify the gripper. New source/binary snapshots are in
results/vector_history_*;old manifests/physical models remain unchanged.

## Newest actual continuation — vector reference,not SOFA approval

Same branch resumed fb6a698,old indices PASS4945/149and34/3. No prior physical
child remained. Independent circular vector-return600states and stateful
function-history tests actually PASS in validation01. Preserved new failures
include unresolved quadrature and a tiny loss17.17%error,corrected only after
analytic virgin yield-front splitting (tolerance tightening alone did not work).
This is fixed-normal/fixed-patch mathematical scope,NOT3D/SOFA/grasp PASS.
Current work is objective transport/general stateful front accuracy and bounded
cost,not a repeat of completed Hermite/mesh runs. All earlier physical FAILs,
global-energy BLOCKED and100mm grasp Optuna BLOCKED remain unchanged.

## Authoritative checkpoint — incomplete objective,not a completion declaration

All physical runs/replay described in the latest PROGRESS/NEXT are completed;
no pending physics child or automatic restart remains. Old "running" entries
below are retained chronology. Prior premature stopping was the agent's own
choice,not evidenced host exhaustion. Actual current trial/policy limits are
documented separately and must not be described as a server/session failure.

PASS in scope:actual Hermite SOFA integration/API/invariants,fine21→41spatial
contrast,original1000nm24s hold/recovery,immutable local-prefix motion/normal
force contrasts,point/recording query purity,source/raw integrity and exact
sealed4s replay. Base index4945artifacts/149blobs;replay34artifacts/3blobs.
FAIL:coarse11→21,small-phase time/history losses,including0vs4.365e-19Fmm
newly resolved prefix loss. Old v1ignored-XML profile PASSs are INVALIDATED.
BLOCKED:qualified total physical energy and100mm grasp Optuna. NOT RUN:new
12wrench/shape/full-recovery qualification of the refined model and3D SOFA
integration of the new stateful scalar history reference. Overall EXPERIMENTAL.

Last validated physics/reference source:a5703beff2839d0feea9f8174e862e645948871f.
Replay source:a543bc4c84896028e06e9896c1b4c05e1c14fcf4. Packaging commit is
`git log -1`;source indices deliberately avoid self-referencing SHA claims.
First unfinished development:objective vector yield-front/material-history
function,not another rewrite of ConservativeBeam or the completed Hermite map.

LATEST IMPLEMENTATION:independent PatchRefinedContact v2,actual registered
SOFA Data/API/FD PASS,empty-vector4s parent X/V/Rexact. V1local profiles are
INVALIDATED (Unused Attribute);their original raw remains. V2actual grids
528000/624000states confirmed;local4s profiles are running before bounded
prefix contrasts. Original1000nm full24s also running. See TOP of NEXT for
the current processes/paths rather than old "running" chronology below.
Global goal is NOT complete;physical thresholds/old failures remain intact.

NEWEST:actual Hermite implementation and11/21/41dynamics are completed.
New phase-grid21→41spacePASS;full-cycle time loss.0682459%PASS.1%,history
loss.06299997%PASS1%,repeatX/V/R0. Additional small-phase time/history FAILs
remain;full grasp/energy qualification and100mm graspOptuna remain BLOCKED.
Actual read-only24s point traces both PASS,showing narrowly localized yielding;
at7.2s only8/813coarse and12/1623fine active points carry plastic loss.
v15observer8s160.047s PASS,physicalX/V/R0. Latest live-work/restart details
are at TOP of NEXT;historical running statements below are retained chronology.

The prior stop was an agent-selected campaign checkpoint, NOT an observed
session timeout or exhausted system resource. It did not complete the user's
research objective. Development has resumed; the historical checkpoint below
is retained as history, not the current curved-contact status.

- Actual new `CurvedMaterialContact` SOFA integration: implemented, clean-built,
  dense-map/API/FD/objectivity/action-reaction tested; ConservativeBeam unchanged.
- Actual 11/21/41-node dynamics completed. Inherited all-node connectors/cable
  routing changed physical hardware with mesh; separate controls expose this.
- Fixed hardware plus derived uniform-density tributary masses: 11→21 motion
  1.597823% FAIL;21→41 .423918% PASS against unchanged1% criterion.
- Strict-FP native compilation of unchanged kernels: actual path equivalence
  PASS. One runtime pair at21nodes: history .0025→.00125 motion/loss PASS1%;
  repeat/recovery PASS. Half-dt motion PASS .1%,plastic loss .160535% FAIL .1%.
- Quarter-dt full18s: ACTUALLY COMPLETED1101.416s under the one recorded1320s
  exception(4GiB retained). FAIL:global moment relative residual .001031812
  exceeds .001. Half→quarter motion/loss differences pass,but the underlying
  physical failure forbids qualification. Base→quarter loss .196644% also FAILS.
- Checkpoint v2/v3: FAIL trajectory equivalence despite exactly restored force
  and Jacobian. Public first-step MBK/RHS/solution errors1.735e-18/0/1.098e-25
  support assembly roundoff amplification. Not used for physics qualification.
- Actual synchronized8s journal:48000stage rows,X/V/R exactly unchanged;
  kinetic algorithmic residual ≤1.4751e-20. NOT global stored-energy closure.
- New discrete radial-return energy identity:2000independent states PASS;
  actual16000step pre-Commit identity residual2.63344e-26,X/V/R exactly unchanged.
- Independent structural-only compensated summation contrast is now running:
  actual5000step scope test PASS(object,all rotations,roots,velocities exactly
  untouched). Actual18s hold at base/half/quarter dt PASS;global moment relative
  1.99483e-5/3.22488e-5/6.21926e-5 versus1e-3. Actual24s repeat/recovery PASS.
  Base-dt loss still FAILS time convergence;half→quarter motion/loss PASS.
  This is a21node half-dt candidate,not full-grasp certification.
- Its own same-half-dt11/21/41and fine-history revalidation is active.
- Energy observer has been moved AFTER live structural summation and BEFORE
  history Commit using public scene APIs. Actual1s/8s X/V/R differences0.
  Same-run Beam/normal/layer projections,algorithmic cable work and contact
  return accounting reduce8s derived residual to4.51719e-13;remaining after
  explicit potential remainders -6.22707e-14. Not yet global qualification.
  New Frame pressure-return audit passes actual1s;full24s journal is RUNNING.
- Full12wrench certification,global energy,100mm grasp Optuna remain BLOCKED.

Current raw: `results/autonomous_20261116_curve_a01`,
`results/autonomous_20261116_full_native_a01`,
`results/autonomous_20261116_checkpoint_a01` (plus explicit native/scalar controls).
Last committed source checkpoint: `0c6cb77`;additional energy/integrator work is active.

## Latest actual checkpoint (supersedes RUNNING lines above)

- Same-half-dt fine21→41mesh and fine history PASS1%;coarse11→21FAIL1%.
- Full24s synchronized journal completed;X/V/R unchanged,remaining signed
  residual-1.45037e-13;global energy still BLOCKED,not a success certificate.
- Whole contact-cycle loss time convergence FAIL even when hold loss passes.
- Integer-index clock implemented/tested. Actual base24/half24/quarter18
  completed;all original hold gates PASS,base/half recoveryPASS. Fixed clock
  does NOT resolve full-cycle loss(half→quarter.441979% FAIL.1%).
- Actual public solved-MBK probe4s PASS query purity,initial sampled damping
  minima positive.17.1srelease probe RUNNING;coupled negative-damping hypothesis
  not established. No physical damping modification.
- Event-aligned release-only time refinement is a NEW integration-grid
  experiment. Unit/clean buildPASS;4sactual prefix testRUNNING. No inherited
  full time certification. Native3D/12wrench/energy/grasp Optuna remain blocked.
- Actual raw:results/autonomous_20261116_fixed_clock_a01 and
  results/autonomous_20261116_event_clock_a01,in addition to prior campaigns.
- No automatic restart is installed or assumed. Check actual results before
  resuming;existing output names are deliberately refused.

## Latest measured results (supersedes earlier active-process statements)

- New nonuniform grid actual24s coarse/fine,41nodes,finer material sampling,
  repeat all completed and pass original physical hold/recovery. Full-cycle
  time loss.0682459% PASS.1%;fine space comparisons/repeat PASS.
- Additional phase-resolved time/history loss still FAILS;all flags and tiny
  absolute errors are retained. No global grasp/optimization approval.
- Initial variant comparator used different dt;old FAILs preserved. Actual
  SAME-grid .5s controls show exact X/V/R equality;v2physical reanalysis of
  existing full raw passes without rerunning or loosening limits.
- Actual new-grid coarse24s energy journal840.463s,X/V/Rexact,remaining
  -1.55243e-19 after separately derived signed terms. NOT full physical energy
  certification. Fine24s BLOCKED by1986.658s profile forecast versus1320s policy,
  attempts0;this is not a server-forced failure. Unknown pressure fields NULL.
- Research continues:read-only per-point24s SOFA traces and exact cable-query
  reuse. Frozen100state API plus1s actual path tests pass;8s test RUNNING.
- Mathematical slip-band reference shows why small force error need not imply
  small loss error;it is NOT a completed 3D adaptive history implementation.
- No object-pose correction was introduced;plasticity bins show a decaying
  transient rather than a proved permanent roundoff-creep floor.
- Final goal remains incomplete;12wrench certification and100mm grasp Optuna
  stay BLOCKED/NOT RUN rather than inferred from this single +Tz research case.

## Historical checkpoint 2026-11-15 (not current model certification)

Branch `development/regrip-autonomous-research`; baseline63970172ad196e0add3ad42a67ccaee4c7a8975e.
Raw campaign `results/autonomous_20261115_a01`,compiled physical component
`build/autonomous_20261115_a01/v3/libReGripMaterialPointContact.so`.
See FINAL_REPORT and manifest for final source checkpoint and exact hashes.
Validated source checkpoint:456d83f2f36fb0e64deabac91341c636681af36d.
New campaign integrity:PASS894SHA256artifacts. Raw1173017042bytes,external only.

| Scope | Result |
|---|---|
| Historical source/raw/binary integrity | PASS1845entries,old physics preserved |
| New immutable material-point component clean build/API/FD | PASS |
| Actual plastic Commit versus observed plastic | PASS,exact equality |
| Same-hold loss history convergence | PASS .129703/.279753/.049621% vs1% |
| History motion .01→.005→.0025 | FAIL4.61737/1.01697% |
| History motion .0025→.00125 | PASS .0300247% |
| Mesh11→21→41 motion | FAIL4.95984/2.80102% |
| Fine dt-half motion/loss | PASS .0977366/.0999735%,borderline.1% |
| Half→quarter-dt motion/loss | PASS .015950/.074528%,679.15s actual run |
| Base→quarter-dt motion/loss | FAIL .113702/.174427% vs.1%;time qualification incomplete |
| Hold force/moment relative residuals | PASS local1e-3 |
| Repeat | PASS,hold motion/loss exactly reproduced |
| 24s recovery | PASS base/fine-repeat;not fully tested by18s cases |
| Independent curved-contact pullback | PASS60states,NOT SOFA-integrated |
| Global energy closure | BLOCKED |
| New12wrench/full-shape certification | BLOCKED by convergence/energy |
| New100mm grasp Optuna | BLOCKED;0new trials,no fabricated Pareto |
| Native surface/new GUI | NOT RUN;prior independent research unchanged |
| Continuous-contact long-soak/no-leak certification | NOT RUN;bounded samples EXPERIMENTAL |

Largest remaining measured blocker is Beam/contact spatial convergence.
Plastic-state consistency improved;it does not repair spatial kinematics or
complete the synchronized global energy/work journal. No real material
measurements or actual gripper performance are certified. Research fingers
still have explicit planar guides and the~95.15mm base-radius assumption.
