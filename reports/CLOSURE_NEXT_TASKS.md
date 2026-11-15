# Resume without redoing immutable history

Workspace is external disk:
`/media/ubuntu/99419895-2058-45b4-b746-b36ea7112e4e/research/LHJ/ReGrip`.
Branch `development/regrip-contact-closure-optimization`. Read AGENTS/CLOSURE_CURRENT_STATUS/
FINAL_REPORT/manifest first. Original30mm/old100mm/golden/build/raw/SQLite remain immutable.

## Read-only verification now

```bash
cd /media/ubuntu/99419895-2058-45b4-b746-b36ea7112e4e/research/LHJ/ReGrip
git status --short
git log -8 --oneline
/home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/closure_verify_evidence.py --raw
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool reports/closure_evidence/balance_audit.json
```

## P0: Beam physical validity, not solver tolerance

Live field isolation identifies BeamFEM net Y moment−2.26294389207e-5 at13.98s;
closed work remains nonzero under64→256 integration. Object/free DOF residuals
cannot detect this by themselves. Implement a NEW energy-derived/objective beam
component/model; preserve inherited golden Beam. Derive deformation measure,
force/torque and consistent tangent, test rigid transforms/net moment/closed work,
then same EA/EI/mass/BC/load linear-limit and SOFA dt/mesh regression. Do not simply
cancel residual torque or change acceptance criteria. Global energy and reaction
balance must pass before100mm objectives become eligible.

## P1: Spatial/history convergence and cost

Three-finger q8→32/n11 translation difference1.9645%,rotation1.1608%;q16→32
translation2.4498%. History half changes tiny parasitic translation4.1077%,rotation
.008545%; dt half translation.2016%,rotation.00455%. Keep BOTH metrics and existing
criteria; don't switch away from a failed observable. n41q16/q32 and single retry
timeout480s; retry ends≈23000/36000steps. Profile sparse assembly/allocation/history
before another same-resolution attempt. New version goes to separate build/namespace.

For mathematically equivalent implementation tests (NOT approval of current design):

```bash
cmake -S models/closure -B build/closure_followup/unit -DCMAKE_BUILD_TYPE=Release \
 -DCMAKE_PREFIX_PATH=/home/ubuntu/SOFA/v26.06.00
cmake --build build/closure_followup/unit -j2
build/closure_followup/unit/test_closure
cmake -S models/closure_frame -B build/closure_followup/frame -DCMAKE_BUILD_TYPE=Release \
 -DCMAKE_PREFIX_PATH="$PWD/.runtime/closure_sdk"
cmake --build build/closure_followup/frame -j2
build/closure_followup/frame/test_closure_frame
```

Exact current model reproducibility in a NEW raw namespace, frozen existing plugin:

```bash
REGRIP_CLOSURE_OUT=results/closure_followup_01 \
 /home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/closure_frame_campaign.py wrenches --workers 2
REGRIP_CLOSURE_OUT=results/closure_followup_01 \
 /home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/closure_frame_campaign.py convergence --workers 2
REGRIP_CLOSURE_OUT=results/closure_followup_01 \
 /home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/closure_frame_evaluate.py
```

This will reproduce current model limitations; do not repeat high-resolution
timeouts without a distinct cost hypothesis. Helpers currently select frozen
`build/closure_20261115/frame` and matched SDK explicitly; any future plugin path
change must update recorded identity and receive a new campaign, not overwrite it.

## P2: Native surface refinement

Positive buffer fixed zero-gap loss. Sphere gripper only two positive-normal contact
points in this test. Need independent triangle/dt refinement,full6force/6torque,
friction controls,cylinder/box,release,recontact. Box-plane calibration is not full
gripper validation. Keep impulse/dt conversion and scoped scalar solver.

Existing source/config dependency for native tool is immutable
`results/closure_20261115/trials/wrenches_Fxplus`; new output name below is unique:

```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/closure_native_gripper.py \
 --name native_surface_lat48_followup --lat 48 --buffer .0005
```

480s/4GiB cap unchanged; timeout is not a favorable objective. The native tool's
three hold subchecks remain EXPERIMENTAL; use full independent physical audit.

## P3–P5

After beam/global balance+spatial gates: actual all-shape/multiwrench convergence,
pressure ON/OFF load/torque limits (low-load gain was below mesh error), isolated
100mm Optuna3smoke then≥24 COMPLETE with candidate revalidation. Gate command:

```bash
PYTHONPATH=.python-deps/grasp:tools \
 /home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/closure_optimization_guard.py
```

This currently returns BLOCKED without a study/objective. Existing30mm study remains
separate. Match source/runtime hashes. Full3finger/native memory scope still needs
its own long-run qualification. Replay environment/GUI argv are saved in
`results/closure_20261115/threefinger/replay`; GUI is optional, never a physical gate.

All experiments: ≤4 long children total,each4GiB/480s,unique output,finite retry list.
Current bounded high-resolution retry exhausted; no jobs left running at handoff.
Reports/CSV/figures contain simulation or mathematical results only; physical PET,
vacuum distribution/friction/wire fabrication parameters still require measurement.
