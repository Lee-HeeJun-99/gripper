# Rail separation certificates and finite pressure shoe — 2026-11-23

Baseline clean HEAD `f822d0d`, branch `development/regrip-autonomous-research`.
Existing physical/model Gates and immutable Raw preserved. No new Native
physics or custom Solver. Actual joint/preload/material data remain unavailable.

## Cycle A: resolve the specific 41 numerical prisms, not by epsilon

917 CSG could not build volumes for41 nearly planar Support translation prisms.
New `cad/swept_separation_certificate.py` searches arbitrary separating axes
in float, then accepts ONLY a strict positive projection interval gap recomputed
with exact rational arithmetic. Original finite float vertex/axis/translation
values are interpreted as exact binary rational numbers. Endpoint is exact
`vertex + translation`, not the rounded float endpoint used in broad screening.
Each triangle sweep is the convex hull of its two endpoint triangles, including
rank-deficient/planar cases. A separating axis proves disjointness without
requiring a positive-volume mesh. Failure to find one means UNRESOLVED, not
collision. No thickness, tolerance floor, face deletion or state correction.

924:all **20336=41×(332Skin+164Rail)** triangle pairs strictly separated;
runtime11.311s. All actual axes and exact numerator/denominator gaps saved in
`results/product_rail_certificate924/certificates.json` with SHA256.
925 independent code replays the endpoint construction/dot products and checks
complete expected Cartesian coverage, no duplicates and exact positive gap
agreement:20336verified,5.243s. Minimum raw projection gap is deliberately NOT
reported as a Euclidean clearance:axes have arbitrary scaling.

The source917 result remains UNRESOLVED as originally produced. These new
certificates close ONLY its41 numerical-prism surface-separation questions.
They do not retrospectively upgrade all CSG/tangency/containment/physical-joint,
full moving gripper, tolerance or product Gates.

Regression covers planar separation, middle-only contact, strict tangency,
exact sub-ULP endpoint construction, axis-gap reference, rigid rotation and
invalid inputs. Independent replay rejects missing/duplicate/corrupt proofs.
927 guarded software regressions PASS. New source hashes/commands/process
logs accompany each case. Guard4GiB/420s; no SDK edits or external writes.

## Cycle B: separate pressure-shoe candidate

926 changes design pad thickness from0.03 to0.30mm, while keeping footprint
1.92mm² and Skin/Rail/Root/wire geometry unchanged. The upper lip and screw
lower endpoint rise by the necessary0.27mm to preserve nominal unloaded gaps.
This is an explicit coupled mounting adjustment, not an identical-geometry
physics comparison. 0.30mm is a research design dimension, NOT a purchased
material/process capability or proof of strength. No preload/friction invented.
Actual full288part static CSG has no intersections;3saved new STL solids are
closed single bodies. Actual pad volume0.576mm³. Runtime7.277s.

928:8.029s, finite screw sweep/assumed driver and sampled diagonal service clear.
929:25.835s, actual0.45mm second-channel finite wire envelope has no unresolved
obstacle hits against all288actual parts;intended wheel proximities retained.
Not allchannel/deformed/movingwire qualification. 930reviewpack includes9actual
STLs,288part recipe/BOM,parameters and DESIGN exploded recipe in
`meshes/` and `drawings/b3_pressure_shoe_v46/`. No STEP or fabrication release.
931actual x12mm section comparison visually inspected:pad thickening and raised
lip/screw endpoint are visible;Skin/Rail remain unchanged. NOT SOFA states.
932actual newcandidate section returns pad0.300000000000004mm and idealfree
stack closure0.069999998807899mm;actualpreload/stiffnessNULL.

933candidate-specific continuous sweep (5.706s) has840CSG comparisons,no initial
or prism hits,36nonvolumeprisms. 934newproofs use the NEW triangle indices:
17856=36×496pairs strictly separated,7.621s. 935independent replay verifies all
17856pairs,4.551s. Old triangle indices/proofs were NOT copied to the newshape.
Other CSG/numerical/tangency and containment limitations remain explicit.
936124softwaretestsPASS (2.706stestbody/3.415sguard),not physicalqualification.

## Cycle C: saved-source reproducibility

The certificate audit now validates each case's saved `producer.py`,rather than
requiring today's mutable generator to equal its earlier hash. Geometry/prior
data hashes and exact proof replay remain mandatory. 937replays924aftergenerator
evolution:20336verified,5.078s,oldRawunchanged. No physics rerun or retroactive
scope change. 938final software regression adds saved-producer identity check.

## Remaining qualification / decision

No new3Fingerphysics is adopted:actual pad/material/thread/preload/slip/film
indentation/fatigue evidence is required before a matched Native joint model.
0.30mmshoe is a finite CAD candidate,NOT manufacturingapproved. Screw is still
an unthreaded geometry proxy with no selected pitch/material/torque relation.
Static/service geometry clear does not demonstrate actual clamping/loadtransfer.
OnlyONE Root attachment changed;remaining4Roots/12turns and allsector/moving
wire/object clearance are not qualified. No legacyB3checkpoint reuse.
The specific 41/36 prism questions now have independently replayed proofs;
do not continue retrying their former CSG failure. Next actionable work is
finite thread/retention and pad-tolerance specification plus actual material/
preload/slip/indentation protocol. Real measurements remain BLOCKED here.

## Reproduction / exact continuation

Read current evidence first; do not repeat unchanged successful coupons:
```
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/product_rail_certificate_audit925/summary.json
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/product_rail_pressure_shoe926/summary.json
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/product_shoe_certificate_audit935/summary.json
```
For a NEW hypothesis/geometry and NEW tags:
```
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/rail_edge_clamp.py --tag UNIQUE --local-csg --pad-fit --open-foot --pad-thickness .3
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/rail_clamp_service.py --tag UNIQUE_SERVICE --case product_rail_pressure_shoe926 --longitudinal-ratio 1
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/clamp_stack_contract.py --tag UNIQUE_STACK --case product_rail_pressure_shoe926
```
No50g/100g/Lift/time/mesh/Native/product/fabrication PASS added. Physical data
remain NOT MEASURED;no paid services,SDK modifications or remote push.
