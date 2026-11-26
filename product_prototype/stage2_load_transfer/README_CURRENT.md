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
Actual independent gate: `validation/integrated/release_audit2/summary.json`
=> STAGE2_NOT_QUALIFIED. Selected17bounded-study evidence hashes PASS in
`validation/integrated/evidence_audit3`; this is NOT system approval.

Major new findings: layer-end loads39.14N PET /19.57N per rail despite0.818N
Tendon in the reduced closing model; rigid coupling alignment is load-critical;
motor0.45Nm holding reference could imply40.3N ideal cable tension in a jam.
An independent qualified maximum-load mechanism is missing. No new powered
or100g trial should proceed. Stage1 RevAA unchanged; new six-part sliding-PET
RevAB geometry and real304part STEP are CANDIDATE ONLY, not adopted/released.

Resume selection:
`python product_prototype/stage2_load_transfer/scripts/stage2_status.py --next`
Next READY: drive_force_cap; finite-rotation separate-layer candidate; coupling preload.
There is no session-external runner. All launched analysis children completed.
Physical first-article records remain blank. Do not edit Stage1 evidence.

Reproduce using `/home/ubuntu/miniconda3/envs/robot_ws/bin/python`,
`PYTHONPATH=/tmp/regrip_stage1_ocp`; extraction command is in its summary.
Choose a NEW output tag (existing result directories are immutable).
