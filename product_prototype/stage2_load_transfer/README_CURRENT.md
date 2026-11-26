# Stage2 — actual Rev AA load transfer

Baseline HEAD `c0e5dfdc6fe3812b8bbd09ed3392e239a30aca2a`; CAD
`revAA_heel_relief2`, package `revAA_mbd1`, Stage1 `release_revAA2`.
Stage1 is unpowered engineering definition only. No Stage2 release exists.

Read-only CAD integration: `models/geometry/revAA_extract2/summary.json`.
304 actual STEP hashes checked against current BOM. Every solid valid;
adaptive BRep integrals reconstruct the actual assembly with unchanged
1e-8 volume/inertia and 1e-9 m centroid criteria. Initial non-adaptive
failure is preserved separately. These are geometric m³/m⁵ quantities,
NOT actual mass/inertia of motors, bearings, threads or stranded rope.

Queue: `STAGE2_TASKS.json`. No full grasp or Stage3 actuation authorized.
Physical first-article records remain blank. Do not edit Stage1 evidence.

Reproduce using `/home/ubuntu/miniconda3/envs/robot_ws/bin/python`,
`PYTHONPATH=/tmp/regrip_stage1_ocp`; extraction command is in its summary.
Choose a NEW output tag (existing result directories are immutable).
