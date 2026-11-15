# Exact restart — contact history

Do not rerun into existing output directories. Read FINAL_REPORT,HISTORY01/04/05
and `history_evidence/convergence.json`. Inspect Git status before changes.

```bash
cd /media/ubuntu/99419895-2058-45b4-b746-b36ea7112e4e/research/LHJ/ReGrip
git status --short
git log -5 --oneline
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/history_verify.py --raw
```

## Priority1: birth/transfer consistency,NOT another blind search

Production v3 drops partial slip during a newly activated material point's
crossing step. `models/contact_birth/BirthIncrement.h` independently computes a
crossing-aware increment and implicit-root Jacobian; grafting only its value
into the field would omit root derivatives. Integrate it as a NEW field/version,
derive complete force/Jacobian and value-only commit together,then test pure
queries,birth,detach/recontact,normal rotation and energy inventory.
Also test history-cell boundary degeneracy `u==l` when an active boundary exactly
coincides with a grid node; current general interpolation needs an explicit
boundary-limit treatment before claiming robust arbitrary geometry.

Preserve existing v1/v2/v3 binaries/manifests and c4c069e source snapshot.
New model build and campaign example (choose UNIQUE names):

```bash
export REGRIP_HISTORY_OUT="$PWD/results/history_resume_01"
export REGRIP_HISTORY_BUILD="$PWD/build/history_resume_01/v4"
$PY tools/history_build.py
$PY tools/history_trial.py profile --profile
$PY tools/history_trial.py base --duration 24
$PY tools/history_trial.py half_h --history .005 --duration 18
$PY tools/history_trial.py quarter_h --history .0025 --duration 18
$PY tools/history_trial.py half_dt --dt .00025 --duration 18
```

The example is a development diagnostic,NOT approval to optimize. Existing
history_assess comparison names expect the original campaign; extend a NEW
assessment rather than pooling different compiled models. Each launch has
strict compiled source/binary/dependency checks. Refuse incompatible SQLite reuse.

## Priority2: history/space/time and energy

Repeat prescribed contact references and assembled FD after any field change.
Run normal q,tangent cell order,material grid,nodes anddt independently.
Keep1% space/history,.1%time,1e-6repeat and1e-3relative equilibrium limits.
Use absolute errors in ADDITION to unchanged relative criteria.

`energy_partial/journal.csv` is postprocessed sampled inventory,not whole-engine
closure. Implement a synchronized per-step in-engine journal with pre/post
commit inventories and controller work. Do not fill unknown terms with zeros or
define numerical dissipation as the unexplained residual.

## Priority3: gated downstream work

Only after convergence+neededenergy+balance pass:12forces/torques,controls,
Sphere→Cylinder→Box,pressure capacity comparisons,new100mm grasp Study.
Optuna already imports; do not reinstall. Existing structure Study is not a
SOFA grasp Study. Entire-interface slip must include between-connector maxima;
independent21..161node reference explains the previous coarse candidate failure.

Native surface contact remains a separate constitutive/contact model. Physical
reaction is child-surface Jᵀλ/dt; do not replace missing guide reactions with
an external-force cancellation. Measure sustained-contact memory,FD/PSS and
unload/reload separately from minimal/released-scene evidence.

Default480s/4GiB,max4 physics children. Profile before exceptional limits.
Campaign contains one900s41node and one900squarterdt exception,not general
unlimited permission. All raw/build/env stay on the external drive.
41nodes completed775.519s;quarterdt timed out900.005s near138000/144000steps.
Do NOT rerun the same timeout blindly. Profile the expensive phases and correct
birth/history first;only then justify a new bounded trial or improved solver.
For optional replay use `tools/history_replay.py` in a NEW output campaign after
selecting a real trial,or existing `replay/gui_command.json`+environment.json.
