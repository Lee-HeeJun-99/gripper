# Current selection — 2026-11-26

Retain supported direct winch as minimum engineering architecture; actual
Rev AA has304parts and bounded design-release evidence. Current documents:
`STAGE1_CURRENT_PRODUCT_SPEC.md`, `STAGE1_CURRENT_MANUFACTURING_DATUMS.md`,
`STAGE1_CURRENT_ASSEMBLY_GUIDE.md`, `STAGE1_CURRENT_VALIDATION_REPORT.md`.
Selected sourced motor17HS15-1504S1/A0648 supersedes earlier incomplete pilot
projection source. Not production/powered/hardware approval. Historical
comparisons and failures below remain unchanged.

# Stage 1 — design selection, 2026-11-25

Baseline Git c4dd6b3; existing 300-part CAD and all Native evidence retained.
This is a NEW fabrication candidate, not a replacement of historical B3.

|Mechanism|Evidence|Stage 1 decision|
|---|---|---|
|B3 fixed eyelets|50g functional Holding/Lift; internal bracing in earlier100g|Keep research reference; not release as production|
|Registered parallel-axis lever|1892 closes Finger;1904/1925 no observed internal bracing, speed FAIL|Useful force-path evidence; ideal pivots/return bonds not manufacturing parts|
|Bellcrank|joint-chain Native failure|Do not add unqualified linkage chain|
|Compliant transmission|small-load only; finite-speed blocked|Do not infer nominal-load capacity|
|Moving guide|finite-speed/retention/wire problems|Avoid extra joints for minimum prototype|
|Supported direct winch|two real bearings, replaceable shaft, machined drum, direct tendon|SELECT as Stage1 engineering candidate; no inherited grasp PASS|

RevA implements 46 actual OCC solids with individual STEP/STL and an assembly
STEP. STEP was reread and aggregate volume checked. Motor and bearing solids
are dimensioned INTERFACE ENVELOPES, not vendor internals. Sheet Finger is a
flat stress-free PET/rail concept, NOT the manufactured precurved B3 reference.
Single tendon per Finger is the initial minimum layout; second drum channel
reserves an independent future opening/return tendon, not an implemented return.

Actual revA verification FAIL:21 positive bulk intersections. Palm intersects
motor/plate/sheets; drum flanges intersect pedestal ends. These are not waived
as assembly mates. Next revision must physically change the support/slot layout.

Manufacturer inputs accessed2026-11-25:
- SOYO SY42STH38-1684A dimensional drawing: https://www.pololu.com/file/0J714/SY42STH38-1684A.pdf
  42.3 maximum square body,38±1 body length,31±0.2 hole pitch,4xM3 depth4.5,
  pilot22 +0/-0.05,shaft5 +0/-0.012,length24±1. Motor external shape is simplified.
- SKF625 dimensional reference: https://cdn.skfmediahub.skf.com/api/public/094ea584acc90401/pdf_preview_medium/094ea584acc90401_pdf_preview_medium.pdf
  boundary5x16x5 only. No bearing load-life or fit qualification inferred.

Motor is an interface candidate, NOT a torque/thermal/continuous-speed selection.
No procurement, physical test, Native run, price/stock or competition-rule
compliance is asserted. Exact competition rules have not been supplied.
