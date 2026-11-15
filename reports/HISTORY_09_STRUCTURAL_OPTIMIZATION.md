# HISTORY 09 — full-interface slip objective diagnosis

**PASS independent numerical diagnosis; historical SOFA candidate remains FAIL**.
No old Study was changed and no new structure candidate is approved.

`tools/history_independent.py structural` independently assembles the SAME linear
midpoint rod EA/GA/EI and10 physical connectors10..100mm,k84.1732992010.
Entire interface maximum slip (mm):

|Nodes|Maximum|
|---|---:|
|11|1.208947984669e-7|
|21|3.552695441413e-7|
|41|3.552695441356e-7|
|81|3.552695439867e-7|
|161|3.552695441247e-7|

For this linear element, displacement and rotation interpolate affinely, hence
interface slip is piecewise affine and its continuous maximum occurs at an
element endpoint. Every interface endpoint is counted, not only connectors.
The11node mesh has no between-connector endpoints; it misses the physical
inter-connector maximum. 21nodes reveals it; subsequent meshes agree closely.

This explains why the former SOFA21node result3.5545e-7 differs from the coarse
Optuna objective1.20895e-7. It is NOT an actual new SOFA/FEM equality theorem
for finite rotations. Existing24COMPLETE/3PRUNED independent structural trials
and failed candidate are preserved. A future mesh-qualified structure Study must
use entire-interface maxima and independently rerun actual SOFA candidates.
