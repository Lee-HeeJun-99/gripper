# Supplier-sized whole-path continuation — 2026-11-22

Source baseline362b324. No SDK/old Raw edits, no new SOFA dynamics and no
product qualification. This is two consecutive CAD investigation cycles.
Software regression:82 tests PASS in2.764s;not physical qualification.

869 metadata lookup failed (V43 parts recipe has no baseline_config); failure
preserved.870 explicitly hashes the V21 design metadata alongside current V43
parts. All6 leads have positive analytic tangent budgets at pitchR5.85mm;
minimum straight remainder8.30mm. Coverage:5 remaining legacy Roots and18
turn wheels have groove-rootD3.5mm versus11.25mm guidance for the candidate
.45mm6x19 wire. This does not select a wire or certify fatigue.

871 builds and rereads3 closed positive single-body STL wheels for ONE f0/c0
lead, with tangency-based centres. All290 other parts retained. Runtime7.247s.
FAIL: turn2/turn3 flange overlap0.214085930mm3; old pins and integral bridge
also interfere. Positive tangent budget is demonstrably insufficient.

872 changes ONE variable: outer routing x70→74mm (not guide offset/stroke).
Actual finite-wheel CSG shows wheel/wheel overlap removed, but existing pins
and bridge still intersect: bridge overlaps17.664344,20.889849,26.838031mm3.
Runtime7.417s. Overall FAIL_FINITE_TURN_RETROFIT retained. Zero-volume CSG
face contacts are retained, not rounded away. Only three wheels changed;
forks/axles/mounts were NOT deleted to clear the screen.

Next: reconstruct one connected finite turn support/axle stack at the872
centres, preserving Palm connection and outward service. Check all retained
neighbors, full wire envelope and channel-to-channel clearance before copying
six leads. Do not adopt x74 as whole-path optimum or reuse B3 checkpoint.
Changed Root seat/bond/translated Skin interface, drum wrap and moving guides
remain unqualified. Material, retention and fatigue data NULL. No STEP.
Native whole-wire law remains BLOCKED; no new constrained-loop coupon is
justified by these incompatible CAD states. B3 time/contact/mesh/100g/Lift
and fabrication Gates remain open.

Reproduction (NEW tags, never overwrite):
```
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/supplier_path_audit.py --tag UNIQUE_PATH
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/supplier_turn_screen.py --tag UNIQUE_TURN --outer-x 74
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/test_manufacturing.py
```
Actual results: product_prototype/results/product_supplier_path869,
product_supplier_path870, product_supplier_turn871, product_supplier_turn872.
Producer snapshots,input hashes,source commit,launch commands and guarded child
process logs accompany actual CAD. Binary/SDK identity: NOT APPLICABLE (no new
SOFA run). Memory limit4GiB/child,420s guarded timeout; peakRSS NOT MEASURED.
