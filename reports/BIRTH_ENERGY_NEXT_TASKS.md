# Birth-aware contact — restart safely

Workspace remains on the external disk. Original results and failed attempts are
immutable. Current implementation is canonical v8_clean;do not overwrite any existing build or
campaign name. Read CURRENT_STATUS,FINAL_REPORT and BIRTH04/06 before optimization.

```bash
cd /media/ubuntu/99419895-2058-45b4-b746-b36ea7112e4e/research/LHJ/ReGrip
git status --short
git log -8 --oneline
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/birth_assess.py
```

Current binary `build/birth_20261115/v8_clean/libReGripBirthContact.so`;identity/compiled
source hashes in its build_manifest.json and final evidence manifest. Results:
`results/birth_20261115/canonical_v8`,including actual grasp/events/journal/replay.
Earlier v7,math_events,structure_refined,multilayer,golden and sanitizer remain
under `results/birth_20261115`. Inspect final manifest and Git
HEAD for last code/report commit;do not assume every prototype matches HEAD.

## Priority1 — remaining history/time errors

Birth-aware value/Jacobian/commit works,but canonical .01→.005 motion still
FAILS1%;.005→.0025 motion passes yet same-stage friction loss differs~26.3%.
Do not call motion convergence full history/energy convergence. The entire
latest comparison table, including completed fine cases, is in convergence.json.
The .0025→.00125 motion change is~.0325%,but friction loss still changes~8.72%.
Mesh11→21 and21→41 motion differences are~4.518% and3.043%,both FAIL1%.
Actual canonical grid counts are uniform1000/500/250 per edge,so a remaining
extra-cell count defect is not established as the cause of these mesh errors.
Investigate representation of a narrow patch with no
interior material-grid sample,zero-boundary anchors,and interpolation/return-map
noncommutation. Birth correction alone does not solve these spatial errors.
Keep full relative limits;absolute nanometre-scale shifts are an additional
diagnostic,not permission to turn FAIL into PASS.

The current SOFA Euler step evaluates forces before the state update;new contact
may first commit at AnimateEnd. IFT-correct endpoint history is NOT automatic
ODE event splitting. Canonical motion dt-half/quarter diagnostics pass0.1%,but
this does not certify history loss or complete dynamic energy accuracy.
Resolved through-events are rejected and need actual time subdivision.
Do not loosen the grazing denominator or replace it by an epsilon.

New source changes require a NEW build and homogeneous rerun:

```bash
export REGRIP_BIRTH_OUT="$PWD/results/birth_resume_01"
export REGRIP_BIRTH_BUILD="$PWD/build/birth_resume_01/v9"
$PY tools/birth_build.py
$PY tools/birth_trial.py profile --profile
$PY tools/birth_trial.py base --duration 24
$PY tools/birth_trial.py history_half --history .005 --duration 18
$PY tools/birth_trial.py history_quarter --history .0025 --duration 18
$PY tools/birth_trial.py dt_half --dt .00025 --duration 18
$PY tools/birth_assess.py
```

Never re-run a900s timeout unchanged. Profile expensive stages;preserve failed
raw. Default480s/4GiB/max4 long physics children. Existing quarterdt exception
is a single documented attempt,not a general elevated limit.
Both v7 and canonical quarterdt completed144000steps in their separately
profiled bounded attempts;do not pool their results. All physics children have
terminated. No pending background simulation must be recovered.

## Priority2 — truly global energy

Journal begin/force/pre/post-contact commit is implemented,but pressure work,
Rayleigh stiffness damping and global closure are null. Other FrameLayer end
commits may precede contact's pre-commit observation. A global transaction-level
journal must observe ALL owners before/after their commits and compute actual
external/actuator/parameter work;do not fit unexplained residual as dissipation.
Ideal wire T*L is a virtual actuator potential,NOT stored cable spring energy.
Contact reset loss is distinct from Coulomb friction heat.
Controlled actual plane dt1→1/128 event journals separately expose integrator
event-lag energy defects;see controlled_event_energy.json. Do not interpret the
accidental dt.25 near-zero residual as an exact energy certificate.

## Source checkpoint and reproducibility

Last code/report-parent commit is recorded in FINAL_REPORT;final documentation
commit is `git log -1`. Frozen binary SHA256:
`27b21bb08d0db153c21465b3e3d92e19c62c09b73dc0385fea975f6a895cd0d2`.
Source map/generated hash are in build/birth_20261115/v8_clean/build_manifest.json.
The failed early prototypes lack some historical header snapshots;do not claim
every failed prototype is reconstructible from current HEAD. Current v8_clean
and successful v7 core checkpoints are versioned.

For Python regression use the existing isolated launcher,not direct discovery:

```bash
mkdir -p results/birth_recheck_01
REGRIP_CLOSURE_OUT=results/birth_recheck_01 $PY tools/closure_validation_suite.py unit --suffix _isolated
```

Use a fresh recheck name next time. The plotting import failure after completed
physics was corrected by analysis-only restart;see analysis_restart.json and
analysis_final. Do not rerun completed physics merely to regenerate figures.

## Gated downstream

Only after history/space/time/necessaryenergy/balance pass:12dynamic wrenches,
controls,Sphere/Cylinder/Box release,re-jamming capacity,and new grasp Study.
Rank6/cone LP does not replace dynamic force closure. Current fingers are guided
planar and body placement~95.15mm,not the50mm design target.

The new24trial structural Study is INDEPENDENT LINEAR FEM,not SOFA grasp trials.
Candidate3 qualifies only its tested structure scope;candidate23 remains FAIL.
Keep physical connector locations fixed and evaluate ALL interface nodes on
refined meshes,not just connectors. Old Studies and their failures remain intact.
