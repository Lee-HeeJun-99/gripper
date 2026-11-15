# Optimization eligibility

Status: Optuna environment **PASS**;100mm grasp objectives **BLOCKED**.

Existing isolated `.python-deps/grasp` Optuna4.6.0 reused, no reinstallation or system
Python change. Historical30mm study (`results/grasp_20261115/optuna_v2`) contains
24 COMPLETE/3 PRUNED actual trials plus separate failure/pruning/resume/seed smoke.
That study and its source/binary hashes are preserved. They are **previous measured
results**, not newly run100mm trials or evidence of grasp closure. dt is not sampled.

`tools/closure_optimization_guard.py` reimports actual Optuna and verifies current
contact/wrench/convergence/energy evidence. `optimization_guard.json` records hashes,
blocking reasons, new100mm trials0,no SQLite study,no objective values. No deterministic
search result is relabelled Optuna. No failing candidate receives a penalty masquerading
as good performance. New three-finger finite-resolution12-direction holding does not
bypass unresolved spatial/history/dt convergence or the required global energy gate.

New100mm Pareto set **NOT RUN**, global optimum **NOT CLAIMED**. Old30mm stiffness/slip
Pareto is not combined with100mm pressure/material/torque/force objectives. Physical
material/pressure/friction remain assumed research inputs; no fabrication optimum.

Resume only after energy and improved-geometry convergence qualify:

```bash
PYTHONPATH=.python-deps/grasp:tools \
 /home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/closure_optimization_guard.py
```

Guard remains fail-closed. A future100mm study must use its own SQLite identity,
source/binary/model hashes,3smoke then≥24 COMPLETE physical trials, failed/pruned
separation and independent dt/mesh/contact/history/12wrench/release validation.
