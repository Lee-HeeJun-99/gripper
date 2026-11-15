# Conservative beam — current status,2026-11-15

Branch: `development/regrip-conservative-beam-grasp`.
Baseline: `b468346f3277369d92f25cd2f5d5044c29124737`.
Overall100mm grasp physical qualification: **FAIL/incomplete**.
100mm grasp optimization: **BLOCKED**,not bypassed.

The main inherited-beam problem is independently reproduced and resolved in a
SEPARATE objective energy-derived SO(3) beam. Actual new3finger+Tz global moment
residual3.07426228029e-6 passes1e-3,with24srelease/recovery. This is a local
subgate,not a new twelve-wrench or surface-contact certificate.

PASS: clean build,new61+40kernel states,100state exact implementation equivalence,
SOFA APIs,78Python tests,prior3+5C++executables,2fresh600metric regressions,
singlebeam10cases,2/4layer equilibrium,8layer compensated halfdt/mesh/extended,
small-load beam dynamic ledger,matched120000step/2reload memory,replay.

FAIL: standard8layer uncorrected-precision equilibrium;3finger contact quadrature,
history anddt diagnostics;independent structural candidate mesh slip qualification.
Initial observer init/compile/NumPy serialization/sparse-child padding failures
are retained as development failures rather than silently suppressed.

EXPERIMENTAL: guided3finger+Tz,static wrench LP,native surface contact.
BLOCKED: complete coupled energy ledger,new12dynamic wrench qualification,
100mm grasp-objective optimization. NOT RUN: real material/hardware measurements,
all new-cylinder/box controls,hours/240000consecutive-step soak,GUI.

Separate real Optuna:24COMPLETE/3PRUNED independent100mm SMALL-PLANAR LINEAR FEM
STRUCTURAL trials. They are not SOFA grasp trials. Candidate actual ratio
1.68405837281,mesh-slip validation FAIL,not approved optimum.

All raw/build/runtime remain under the external-disk project. Do not delete or
overwrite old experiments. Exact restart commands and blockers: NEXT_TASKS.
Per-topic BEAM01..14,small JSON/CSV/figure and full evidence manifest accompany
the final report. No push,force push,history rewrite or main/oldbranch overwrite.
