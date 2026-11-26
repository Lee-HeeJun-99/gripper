# Bounded B cycle — actual AK root axial retention (2026-11-26)

Starting HEAD 588a9812cb029e075515187a4895c1142314564f. Supervisor local save
PENDING; no worker Git add/commit or new commit SHA claimed.

One actual product mechanism analysis: AK_root_retention1 uses the actual
RevAK235 candidate's hash-checked PET, two Rails, root front/back and four
root fasteners. Each Z=-7..10mm root-material fragment was translated
independently at 0, +/-0.01, +/-0.1 and +/-0.5mm: 21 states,126 exact
BRep pair checks. No positive overlap with listed root solids. This is a
local axial retention investigation, not a full-Finger deformation solve.

Independent AK_root_retention_verify1 encloses the entire continuous
+/-0.5mm axial translation of each fragment in a conservative solid AABB.
All18 swept-envelope/root-solid overlaps are zero. Transverse0.1mm negative
controls are rejected: PET40.800mm3, each Rail5.814mm3 overlap. Thus these
root interfaces provide no demonstrated geometric axial retention over this
local interval. Fixed PET/Rail root DOFs require actual clamp preload/friction
or another proven physical restraint. No force/friction capacity is inferred.
No continuous whole-Finger escape, free cut surface or strength is claimed.

Both actual analysis children exited0 under4GiB/420s, threads1; no SOFA run.
Execution logs and limits retained; elapsed duration was not instrumented.
No new solver failure occurred; all historical failures remain untouched.
Read-only inherited release audit remains INTEGRATED_NOT_QUALIFIED with24
errors including22 unqualified Stage2 criteria. The AK local geometry result
is deliberately not inserted as system evidence. Same-revision release absent.

B task remains READY with revised prerequisite investigation and priority2;
next scheduler choice AI_whole_palm_support(C). Investigate real base mounting
and sliver/thin-plate discretization before any more Palm FEM; no blind mesh
refinement of prior FAIL. Next B must quantify actual clamp/bolt normal-force
and friction basis, or create a separate finite positive-retention candidate;
do not repeat these probes or apply an unsupported fixed-root boundary.
A collet/overload and Idler proof remain independently executable priorities.

No RUNNING queue record or owned live analysis child remains. Existing CAD,
BOM, source models, FAILs and unrelated untracked work preserved. No Stage3,
SDK, criteria, manager/security changes, hardware or external launch.
Exact save manifest: runtime/authorized_20261126_4/save_request2.json.

Evidence:
- validation/finger/AK_root_retention1/summary.json
- validation/finger/AK_root_retention1/execution.json
- validation/finger/AK_root_retention1/release_summary.json
- validation/finger/AK_root_retention_verify1/summary.json

Reproduction uses scripts/ak_root_retention_probe.py and
scripts/verify_ak_root_retention.py with the commands in execution metadata.
Their output tags are immutable; choose new tags before a future rerun.
CAD common threshold1e-8mm3 is the predeclared numerical overlap check,
not a physical clearance or inherited release tolerance change.
