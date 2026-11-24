# Consistent end-face traction — 1280–1283

Uniform triangular-face traction uses each face area/3 per vertex. The
50µN/layer total force and root moment2µNm are preserved. Affine virtual
work test passes for multiple section meshes. Unlike equal-node loading,
this distribution is mesh-independent in its continuum definition.
The original four equal point forces are NOT identical: coarse maximum
nodal difference4.16667µN. All historical runs retain original loads.

Actual Native pilot1281:50 steps,0.406s; forecast500steps4.058s.
1282:500steps100ms,2.474s actual, no ERROR/unused attribute, two500-row
state journals, minimum saved volume ratio0.9999999733. Installed same
binary SHA and plugin guard are recorded in preflight. Small FEM method
retained from1261; explicit correction link replaces ignored solverName.
This link change and load change are disclosed, not called pure mesh change.
Collision models retained, detector.csv preserved locally and excludedGit.

1283 endpoint independent CST difference6.05864e-17m; native tip
-1.18967920836e-7m. Last50 maximum node speed1.1591e-14m/s. Reference
reaction+50µN is computed, Native root reaction/energy remain NULL.
PASS_SCOPED_SMALL_STRAIN_REFERENCE only; no new mesh/time/contact/jamming
or grasp qualification. Prior B3 successes/failures and oversized Git blob
blocker unchanged. No SDK edit, push, Raw deletion or history rewrite.

Reproduce with Python `/home/ubuntu/miniconda3/envs/robot_ws/bin/python`:

```
product_prototype/sofa/layer_face_load.py --tag NEW_FACE_TAG
product_prototype/sofa/layer_traction_native.py --tag NEW_PILOT_TAG
product_prototype/sofa/layer_traction_native.py --tag NEW_NATIVE_TAG --steps 500 --pilot NEW_PILOT_TAG
```

Each command requires unique output. Assessment1283 producer explicitly
references1282; input hashes and immutable producer accompany actual result.
Do not reuse assessment unchanged for another source. Source commit and
scene/binary hashes are in each Native preflight; exact run command and
runtime are in process/command.json and process/process.json.
