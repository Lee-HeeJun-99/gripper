# Three-finger actual continuation — 2026-11-18

## FREE V3 exact resume1082 — actual SOFA

From1081 checkpoint173(27.3ms),a separate Free Owner reproduces two steps
through27.5ms. q/v error0,all force stages exact,actual field error0 with
only declared legacy sampled-work excluded;checkpoints174/175 byte-identical.
Minimum gap6.76473674e-6mm,momentum4.31892292e-19Ns. Original1e-12 gate.
1083 extends checkpoint176(27.6ms) by24steps to30ms;actual measured four-step
runtime22.7082s yields conservative forecast302.498s<480s. Check its result,
not this pre-execution forecast,before asserting completed Unload.

Exact replay with a fresh unique tag:
```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/film_three_film_free_resume.py --tag UNIQUE --parent 20261118_three_film_free_four1081 --checkpoint-step 173 --steps 2 --compare
```

## CURRENT — actual deformed release1079; separated continuation1081

**Actual SOFA1079** integrates the same27ms accepted state of failed1061
through a separately defined acceleration-complementarity release variant.
No stiffness/damping/mass/control change,no force clipping,no velocity reset
or geometric projection.256 actual RK stages all have nonnegative applied
normal forces and whole-stage clearance>=1.42108547e-13mm. Shared momentum
residual3.55121519e-19Ns. At27.1ms active set empty, outgoing normal velocity
>=.00631256147756mm/s. q/v match independent1078 EXACT under original1e-12
API; quaternion and mapped physical state checked exactly at commit.
RK accumulated clock joins free remainder EXACT. This is a LIMITED actual
deformed release,NOT completed Unload/recovery,holding/lift or full physics.

Actual1080 restores FREE V3 and takes one step.1081 continues four steps to
27.6ms. Each uses all960 triangles and existing quadratic midpoint dense
numerical-path CCD; new impact is explicitly rejected,not ignored.1081 minimum
force-stage gap1.99168699e-6mm,momentum4.32180607e-19Ns. No friction/grasp
certificate follows. Legacy work restarts at each process; root work NULL.

1072/1074 are preserved failures: full100us explicit acceleration queries
leave the tangent manifold;1074 first refusal at27.00078125ms has
gap-7.35412e-13mm,vn-1.10922e-9mm/s,lambda+9.72447e-8N. Gate not relaxed.
1075 instead localizes the new integration law to20us,64RK substeps and then
free midpoint;1073 independently tests all8 coupled active subsets,permutation,
zero-reaction and invalid-compliance guards.1077 local64/128 comparison gives
relative full-state q1.93028e-13%,v5.83336e-10%,but both share the same80us
free-remainder bias and there is no base-to-quarter/full-cycle test: NOT
full0.1% time convergence. Tiny gap/residual relative differences are not waived.

1076 old actual release matched its reference but its RK/free clock join
reconstructed from the macro start differs9.02056208e-17s; keep its result
but do NOT use it as exact accumulated internal-clock qualification.1078
independent and1079 actual pass the corrected accumulated endpoint forward.
RK quadrature weights and fractional remainder durations are their actual
floating values; do not force their sum to a nominal value or invent work.

Build:build/three_film_release_20261118_three_film_actual_clock_release1079/
DLL SHA25622add00153af4573a0e852c954af0514f444ca4d23c03a1d9f5136ab05e9cc51.
Raw:results/autonomous_film_20261118_three_film_actual_clock_release1079/,
...three_film_free_profile1080/,...three_film_free_four1081/.
Each contains archived runner/scene,source or parent identity,SDK,binary and
raw hashes,actual command and guarded process exit/runtime. All before/after
physical conditions remain research assumptions,gravity0 andfrictionOFF.

## Release diagnostics1062–1066 (not actual release)

1062 archived independent replay captures the previously rejected100us trial
from actual checkpoint170. Initial reaction+1.0641827e-7N becomes negative
at27.05ms (-4.8875909e-7N) for all three material edges. Nothing is committed.
1063/1065 reintegrated signed bilateral diagnostic locates a reaction root at
27.009042662754602ms, bracket9.31322568e-14s. Outgoing free midpoint remainder
has whole endpoint gap+2.87091638e-7mm and momentum residual3.53960e-19Ns.
1065 importantly measures pre-event collocation reaction minimum
-4.4303170e-16N: this signed diagnostic is NOT an admissible unilateral
trajectory and is NOT directly installed into SOFA. No tiny-force exemption
or clipping is permitted. Next experiment1067 seeks an admissible interval
split satisfying both nonnegative pre-stage reactions and separating free
acceleration, with explicitly refined root uncertainty. Its result must be
checked before actual owner integration; signed-reference PASS alone is not
physical release PASS.

1064 independent regression preserves fourth-order analytic Lobatto behavior
(errors6.33439e-9,3.96261e-10,2.47720e-11), maximum tangent FD1.63276e-16,
and verifies optional rejected-stage observer leaves accepted q/v EXACT while
still rejecting tensile contact and never mutating input state.

1066 read-only actual failed-horizon accepted-prefix geometry at27ms is checked
against the exact serialized q/v before rendering. Reconstruction7.05686e-15mm,
scale1. Skin width-mean tip z deformation-.289499920mm,root-tip tangent angle
1.75203891deg; rail tip angles6.87049/6.85541deg. Body centre z-63.47737494mm,
gravity0. Contact area/pressure/holding load NULL,wrapping NOT ESTABLISHED.
Actual image/OBJ:
`results/autonomous_film_20261118_three_film_unload_shape1066/`.

Functional commit:bea42b197f00e09cc745d8203191c7a9a93f0ef7 qualifies actual
Face->Edge and typed resume;1063–1066 diagnostic sources are archived per run.
No timeout/resource exhaustion caused1061;it stopped at a physical active-set
transition. Existing full time/energy/material/grasp gates remain unmet.

## CURRENT — typed Edge resume qualified; Unload stops at release

1059 actual Face->Edge event PASS;1060 four-step V2 resume EXACT including
byte-identical snapshots.1061 requested30ms FAILS after accepted27ms at
negative stage reaction (127.184s,not timeout).1062 independent signed
diagnostic reproduces +1.06418e-7N at27ms and -4.88759e-7N at27.05ms.
No negative reaction committed.1064 independent passive-observer regression
and query-purity PASS. Next is zero-reaction event and coupled release;
full time/energy/wrapping/lift remain UNQUALIFIED. Detailed1059–1061
evidence and reusable DLL are recorded below; earlier status is historical.


## Actual support migration implemented — through1048

1042 independent isolated new triangle117 birth PASS. Six old/new rows share
the same projected mass;plastic impulse retains new117 rows and releases old124
rows with outgoing normal velocity~+.0201492mm/s,old impulse0. Root time
23.495650505693598ms,bracket9.31322e-14s. Not a full globally earliest CCD.
1043 extracted reusable kernel exactly reproduces this reference;old3-row
J/H match exactly,new6-row directional gap FD7.32e-10mm,H directional relative
8.81327e-9;world momentum balances meet inherited1e-17Ns/1e-16Nmm s gates.

1044 **actual SOFA** ONE100us deformed contact-support transfer PASS:
q/v,event time,impulses,quaternion,actual field control all EXACT to independent
reference under original strict1e-12 API. Whole-stage minimum gap-3.57758e-12mm,
momentum residual3.63071e-19Ns,vn5.46925e-14mm/s. Global linear balance
1.91115e-21Ns,angular1.05097e-24Nmm s. New stage journal separates the two
Lobatto intervals and actual impulse event;weights total100us. Instantaneous
impulse is not a continuous force. Old rows genuinely separate;the object
remains in contact with new rows,so this is NOT object release or successful
Unload. Initial condition is an individually accepted23.4ms prefix of failed
1033,not a claim that1033's requested horizon completed. Parent failure stays.

1048 read-only actual segmented energy inventory consistency PASS:
Wt1.03791839116e-6Nmm,Wexternal1.18270777203e-7,Wdamping7.08645143619e-8,
normal constraint work-1.41849e-22,stable plastic loss4.811702162e-12,
signed residual-2.59885e-15Nmm. Kinetic subtraction differs from stable loss
by-1.84999e-20Nmm;NOT extra physical heat. Callback energy error6.78e-20Nmm,
stage-control error0N. Root work NULL;no whole-energy/time certification.
Actual graph:results/autonomous_film_20261118_three_film_actual_transfer_work1048/actual_transfer_inventory.png.

1045 actual generic-resume regression after embedded-module guard PASS,
q/v/time/used stages exact.1046 runner preflight indentation error:SOFA NOT RUN,
failure.json preserved;import/negative runners corrected and14 new/changed
Python tools py_compile PASS.1047 actual bridge from transferred checkpoint
does NOT finish requested4steps:one23.6ms step accepted,then endpoint drift
rejects. This exposes another contact transition;do not claim persistent
post-transfer/full Unload PASS. No repeated unmodified long run is justified.

Reuse actual transfer DLL:
build/three_film_transfer_20261118_three_film_actual_transfer1044/libReGripThreeFilmTransfer.so
(SHA256940b6cb43e89d00392fcabebb63373a226fab3ef187fdf9d6fc2fdef092741f7).
Reuse generic checkpoint DLL:
build/three_film_resume_20261118_three_film_bridge_regression1045/libReGripThreeFilmResume.so.
Next bottleneck:detect/resolve further inactive-surface births and releases,
not hardcode only124→117. Validate generalized owner independently before SOFA.
Full all-pair time1041 remains FAIL;wrapping/holding/lift remain unverified.

## Newest actual checkpoint through1041 — still INCOMPLETE

Actual1022 completes Hold to19.99999999999999ms in106.8482s;minimum
whole-stage gap-3.49942e-12mm,momentum5.24636e-19Ns,vn1.45484e-14mm/s.
1021 same-DLL opt-in owner profiling retains exact states/used rows versus
continuous1002. Inclusive2-step costs:coupled10.1652s,implicit7.7376s,
selected geometry3.4572s,material force/Hessian1.5498s. These are nested and
MUST NOT be summed. No speed improvement is claimed.

Actual1024 Unload200us FAILS after accepted23ms,before25ms completion:
whole-stage clearance gate. The failed process is NOT a completed trajectory.
Independent1026 cubic numerical-path chain rule on its accepted prefix:
endpoint reconstruction7.11e-15mm,chain-rule error8.09e-15mm;selected
features stay124/6 through that prefix.1028/1030 independent334-bit audit
over ALL960 triangles identifies the discrepancy as stage versus endpoint:
22.9ms midpoint gap-9.69884e-11mm,23ms endpoint+1.81888e-11mm.
AD distance value error<=1.42e-14mm. Thus this specific clearance failure is
real numerical Stage-position drift,not candidate omission or large geometry
roundoff. It is NOT solved by deleting midpoint clearance checks.

1027 actual regression after permitting explicit100/50us checkpoint grids:
q/v/time/stages EXACT versus1002,strict1e-12 unchanged.1029/1034 start from
EXACT SAME complete20ms checkpoint at100/50us and complete20→22ms:
minimum gaps-1.23279e-12/+2.30216e-12mm. No force/material/control changes.
Their clocks accumulate,endpoint discrepancy6.94e-17s is recorded.1041 listed
100→50us pair STILL FAILS:normal constraint-work residual99.99498% relative,
absolute1.67122e-19Nmm. Motion,separate stored/kinetic energies,force and stage
tendon work pass0.1% for this pair only;no base-to-quarter/full-cycle PASS.
Legacy sampled work is NOT continuous across restarts and not substituted.

Actual1033 extended100us Unload FAILS after accepted23.4ms with endpoint
drift. Independent1036 replay captures REJECTED,NOT COMMITTED trial:
mid23.45ms triangle124 gap-8.42e-8mm;end23.5ms selected triangle117 gap
+2.498e-7mm. Initial reaction remains positive~1.266e-5N. It is NOT release.
1036 raw accepted_initial force0 was an unmeasured diagnostic placeholder,
NOT physical zero reaction;use its rejected_initial computed reaction instead.
Future driver writes null for this unmeasured field.1037 frozen-triangle
contrast ran but its initial diagnostic harness did not record the completed
trial;FAIL preserved. Corrected1039 records same fixed124 branch but whole
surface gap-8.79934e-8mm:holding old ownership does NOT fix new contact.
Therefore a new surface/owned-row event must be resolved,not simply more
unchanged time refinement or a relaxed gap tolerance.1040 actual regression
after opt-in pre-rejection observer hook again q/v/time/used rows EXACT;
observer never permits a failed state to commit.

1025 actual10→20ms partial work inventory:Wt2.02742614486e-4Nmm,
Wexternal1.11798136627e-5,Wdamping5.78768015695e-6;
signed residual-1.03539e-12Nmm,NOT heat/full energy.1035/1038 reuse the
immutable read-only material observer with canonical GCC dependency closure;
new PersistentRows diagnostic hook is proven NOT included by that observer.
No included file or binary identity exemption.

1031 visualization failed because installed Matplotlib lacks Axes3D;failure
and OBJ preserved.1032 uses standard orthographic projection of SAME actual
3D coordinates,scale1,not a fabricated pose. Skin width-mean tip z at20ms
-0.167364mm,root-to-tip tangent bend1.18514deg;rails about5.80deg.
These discrete shape metrics do not establish contact coverage or wrapping.
PNG/OBJ:results/autonomous_film_20261118_three_film_hold_shape1032/.
Sphere centrez-63.46909358mm,gravity0,NOT lift. Area/pressure/holding load NULL.

Last feature commit before these diagnostics:be34e4639a770bfc03156333e1760f591cda0717.
New compiled resume DLL1027/1029/1034:
build/three_film_resume_20261118_three_film_resume_grid1027/libReGripThreeFilmResume.so.
Latest regression DLL1040:
build/three_film_resume_20261118_three_film_resume_hook_regression1040/libReGripThreeFilmResume.so.
Next:isolated triangle117 Contact Birth using original124 persistent branch,
shared multi-row impulse,then retained-row/release and whole-surface validation.
This is not a declaration of full production contact completeness or grasp.

Project INCOMPLETE. Measurements below are **actual SOFA** unless explicitly
identified as read-only mathematical postprocessing. No wrapping,lift,holding
load,frictional grasp or design superiority certificate is claimed.

## Persistent transfer implemented

Separate `models/film_three_finger_resume/ThreeFilmResume.cpp` reuses the existing
conservative mechanics and fixed compressive-row Lobatto step. Original owners'
REST checks remain defaults;new owner validates a complete checkpoint instead.
No fake counters,force/velocity projections or relaxed residuals. Public
`Context::setTime` synchronizes exact accumulated clock and dt on11 contexts.
BaseContext has no public setTime:1013 compile failure preserved;1014 uses
public Context API,SDK unchanged.

|Campaign|Actual operation|Result|
|---|---|---|
|1014|1002 step40→44,4 resumed steps|strict1e-12 PASS,q/v/time EXACT|
|1015|1014 serialized step42→44,2 steps|q/v/time and all used stage rows EXACT|
|1016|1014 step44→50,to10ms|q/v/time and all used stage rows EXACT|
|1017|step50→80,10→16ms Hold|COMPLETE,scoped EXPERIMENTAL|
|1018|five corrupt checkpoint actual runs|guards reject;original harness FAIL preserved|
|1019|read-only same1018 reassessment|PASS:zero accepted rows in empty buffered files|
|1020|read-only actual8→10ms energy/work|callback/control consistency PASS,not full energy|

1014 runtime22.4137s,whole-stage minimum gap-7.46070e-14mm,momentum
4.10910e-20Ns,normal velocity1.81327e-15mm/s. All field positions,control,
length,stored/kinetic energy agree exactly;only private legacy work is excluded
explicitly.1017 whole-stage gap-1.32516e-12mm,momentum2.24238e-19Ns,
normal velocity6.63840e-15mm/s. Gates remain -1e-10mm,1e-17Ns,1e-10mm/s.
The actual accumulated time at step80 is0.016000000000000014s,not replaced by
step*dt. Checkpoints save actual xyzw quaternion;historical1002 reconstruction
is allowed ONLY after zero angular velocity/increment checks for all prefix states.

## Energy origin and state ownership

Snapshot includes exact public nodal masses,rigid mass/inertia,root map,
positions/velocities,quaternion,time/dt,step index,active owners and source/binary
provenance. Contact multipliers are recomputed by the SAME stateless one-step
equations,not imported from Native IDs. The three fixed compressive rows are
not a production release active set. Invalid identity,quaternion,mass,mapping
or row ID is rejected before a physical state commit. Invalid init currently
aborts the process;no silent continuation or recovery is claimed.

Private legacy sampled-work history is NOT restored and NOT joined across
chunks.1020 uses full-AD read-only observer946 and actual accepted stage q/v:
8→10ms tendon work4.33297448587305e-5Nmm,external work2.14250610771e-6,
damping6.98284909313e-7,normal constraint work-8.32911e-25;
signed residual-7.00187e-13Nmm. Callback energy error6.09864e-20Nmm,
control mismatch0N. This is a numerical/partial inventory,NOT physical heat.
Root reaction work stays NULL. First200us inventory1011 and post inventory1007
remain separate origins;overlaps must not be counted twice.

## Scope and blockers

Same research geometry/material/control as1002:three100mm films,root radius50mm,
sphereR30mm plus.01mm midsurface buffer,film1g each,sphere100g,Tmax.0001N per
rail,ramp10ms,release20–30ms,Fz-.001N,gravity0. Six equal prescribed tensions
are NOT a physical equalizer. No actual PET/TPU or actuator measurements.
Initial impact fixture is not stationary-object closing. No full-thickness,
self-collision,general friction,full time/mesh/energy certificate.997 overall
time FAIL and999 deformed-release FAIL remain unchanged.16ms is not evidence
of wrapping/holding/lift. Contact area/pressure/holding load remain NOT MEASURED.

## Reproducibility

New source baseline94cdf31 plus per-campaign archived source hashes.
Build:`build/three_film_resume_20261118_three_film_resume1014/`.
DLL SHA256:`32360e2ffabb94749d5e0f6aa8e739d5128734b98f2fc0fbfa9aab04ccd77146`.
SDK `/home/ubuntu/SOFA/v26.06.00`,no mixed Sofa dependencies.
Raw `results/autonomous_film_20261118_three_film_resume1014/` and corresponding
1015/1016/hold1017 directories. Each stores exact scene,command,process result,
q/v,all stages,field geometry,checkpoint files and hashes. Unique names required.

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/film_three_film_resume.py --tag NEW_UNIQUE --step 40 --steps 4
$PY tools/film_three_film_resume_continue.py --tag NEW_CHAIN --parent 20261118_three_film_resume1014 --checkpoint-step 42 --steps 2 --compare1002
```

Next:complete bounded actual Hold/Unload;diagnose genuine lambda=0 release,
never commit tensile contact. Profile and quantify actual curvature before
longer physical time or any grasp claim. No automatic post-session execution.
## Latest verified continuation — 1059/1060; Unload1061 FAIL (2026-11-18)

Actual SOFA1059 implements bounded deformed Face->Edge transition at
23.67137720356692ms, preserving velocity without an impulse or projection.
Independent q/v/time match EXACT; whole-stage gap >= -7.21201e-13mm.
New material-edge owner stores ordered nodes [77,73], source triangle117,
birth time, exact normal/parameter and accumulated clock in REGRIP_EDGE_V2.
Actual1060 restores the V2 state in a separate Edge Owner: four subsequent
steps, all36 stage rows and ForceField observations match EXACT (legacy
sampled-work excluded with a declared new origin); four checkpoints are
byte-identical. Original strict1e-12 API gate retained.

1061 attempts 59 steps from24.1ms to30ms. FAIL after29 individually accepted
steps, latest checkpoint170 at~27ms: next bilateral stage reaction is negative.
Runtime127.184s, exit-6, NOT timeout/resource exhaustion. Unilateral guard
correctly refuses the trial; no negative reaction is committed. This is not
completed Unload, object release, wrapping, holding or lift. Existing1041
time FAIL and whole-energy/friction/self-collision/mesh BLOCKED remain.
Next: locate zero-reaction event using signed diagnostics only, remove
released material-edge rows, re-solve coupled dynamics and recheck ALL triangles.
Do not simply continue with negative force or reset velocity.

Reusable DLL:
`build/three_film_primitive_20261118_three_film_primitive_actual1059/libReGripThreeFilmPrimitive.so`
SHA256 `52d558a749f2a5288a51ab9b522b1cc128cd9b804eb1300ce62705d1310fc637`.
Raw: `results/autonomous_film_20261118_three_film_primitive_actual1059/`,
`...three_film_edge_resume1060/`, `...three_film_edge_unload1061/`.
Sources at0fa09fb plus archived feature-development source snapshots.
No completed grasp or automatic background restart is claimed.
