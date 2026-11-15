# Exact restart and next research tasks

Use the external disk. Existing campaign names are immutable. No remote push.

```bash
cd /media/ubuntu/99419895-2058-45b4-b746-b36ea7112e4e/research/LHJ/ReGrip
git status --short
git log -6 --oneline
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/beam_verify_evidence.py --raw
```

Read CURRENT_STATUS,FINAL_REPORT,BEAM06/09 before any grasp optimization.
Failed contact/history/dt and incomplete coupled energy are HARD prerequisites.
Do not run more12direction performance trials or grasp objectives to evade them.

## 1. Fresh mathematical build

```bash
cmake -S models/conservative_beam -B build/beam_resume_clean \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH="$PWD/.runtime/closure_sdk"
cmake --build build/beam_resume_clean -j2
ctest --test-dir build/beam_resume_clean --output-on-failure
```

Requires local commit4d19774 for the immutable dense reference; shallow archives
need that history. Do not overwrite frozen prototype/v2 binaries. For core source
changes create a NEW build+compiled manifest and rerun affected API/physics gates.
Native installed-SDK build is separate; do not load its collision libs into the
matched headless SDK or use symlink ABI substitutions.

## 2. Unique new experiment namespace

```bash
export REGRIP_BEAM_OUT="$PWD/results/beam_resume_conservative_01"
$PY tools/beam_trial.py tip --duration 12
$PY tools/beam_grasp_trial.py Tz_v2 --duration 24
$PY tools/beam_multilayer_followup.py
```

The runners refuse existing output names. Default compiled source/binary guard
targets frozenv2. The top-level source+binary snapshot records dirty state;
source equality is checked separately against compiled manifest. This example
reproduces diagnostics,NOT an instruction to call the grasp certified.

## 3. Contact and material-history convergence — highest remaining priority

Use the frozen existing trajectories/profile first. Isolate active-boundary
motion,history interpolation/return-map and grid-cell activation; define an
independent moving-contact reference. Implement a conservative material-history
transfer as a NEW component if needed,without editing the validated old model.
Test no-contact,stick,slip,release,recontact,objectivity,nonnegative dissipation,
force/Jacobian and pure-query vs committed-history behavior BEFORE SOFA.
Then homogeneousv2/new-build q8/16/32,history.01/.005,n11/21/41,halfdt and repeat.
Limits remain1%space/history,.1%dt,1e-6repeat,1e-3static/global residual.
Do not simply repeat failed480s cases. Profile first;734.78s fine case was ONE
explicit900s exception backed by a678.49s prediction,not a new global timeout.

## 4. Native reaction audit

The original projected-only parent-J audit omitted guide DOFs. Preserve itsFAIL.
Physical contact reactions require child surface `Jᵀλ`,mapped using actual world
contact point arms before projective removal. Zero-pad sparse unused trailing
child columns,not nonexistent forces. Free mapped components must agree with
the parent's projected impulse. Native physical reruns/balance files are the
authoritative corrected-observer evidence,not a torque added to the engine.

```bash
$PY tools/beam_native.py --lat 12 --name native_research_next
$PY tools/beam_native_balance.py --name native_research_next
```

Always inspect ERROR logs and stage completion. Native output uses installed SDK
with its OWN rebuilt beam/frame libraries;not patched-SDK memory certification.

## 5. Complete coupled energy journal

Record actual Ubeam,Ulayer,Ucontact,Utangent,K,external and cable command work,
pressure-parameter work,friction/release loss and actual Rayleigh work at every
stage. Use BEAM09 derived single-beam baseline; don't define unclosed residual
as convenient dissipation or put missing terms0. Gate hold/release energy and dt.

## 6. Only after gates pass

Revalidate sphere±forces/±torques,release/recovery,μ0/lowμ/wireOFF/overload and
misplacement controls;then cylinder/box with correct inertia. Recompute measured
patch rank+cone+capped LP separately from actual dynamic qualification. Compare
pressureOFF/low/medium/high at matched load limits. Research95.15mm root radius
does not meet50mm body target; actual wire path/film properties remain unknown.
Only then create NEW100mm grasp SQLite study;do not reuse old30mm or linearFEM DB.

Independent structure study may continue separately,but candidate mesh slip
qualification currently FAIL. Inspect slip at unconnected new nodes and refine
the FE objective mesh BEFORE selecting a new candidate. Do not redefine maximum
interface slip to connector-only slip for success. Existing24COMPLETE values are
linearFEM,not24SOFAgrasp successes.

## 7. Bounded memory and visualization

Further240000continuous-step/persistent-contact/hours tests require a new finite
resource plan. Existing120000two-cycle plateau is postrelease and not those tests.
Keep bounded children/max4 and4GiB/480s defaults. Old runs must not be overwritten.
Optional actual-state replay: use recorded replay/environment.json and
gui_command.json from this campaign;GUI was not launched. No synthetic animation.

All resumption must keep the latest failed checks visible. Real PET/vacuum/μ,
tendon routing,pressure/contact-area and hardware measurements are still needed
before interpreting numerical designs as actual gripper performance.
