# Remaining c1 lead continuation — 2026-11-23

Starting local07a424c, clean worktree. Previous958–970 not repeated.
Native B3 functional50g and failed time/mesh qualification remain unchanged.

971 implements the exact-parent-hashed delta resolver and coherent f1/c1
Turn completion: actual c1 donor fork identity, nine source wheel/pin/nut parts,
six loose shims replaced by actual integral lands. All changed-vs-retained/new
solid CSG checks clear,281candidate parts,10.490s. Source c1route887,NOT mirrored
c0route. 972 finite full Root/three-turn/drum lead705probes against281parts:
no unresolved obstacle,28.537s. Intended wheel proximities remain recorded;
not friction/fatigue/contact-law or moving-clearance approval.

`assembly_recipe_io.resolve_recipe` rejects external paths, cycles, parent SHA
mismatch, missing/duplicate removals and duplicate final part identities.
Delta recipes retain exact source/parent hashes instead of repeatedly writing
ever-larger assembly copies. They are not standalone CAD files. 973151software
tests PASS. No physical preload/joint/material or Native test performed.

Reproduction with NEW unique tags:

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY product_prototype/cad/remaining_lead_completion.py --tag UNIQUE --case product_remaining_clamped968 --finger 1 --cable 1 --delta
$PY product_prototype/cad/remaining_root_wire.py --tag UNIQUE --case product_remaining_c1lead971 --full-lead --delta
$PY product_prototype/cad/manufacturing_test_run.py --tag UNIQUE
```

Next: independently place f2/c1 complete Root clamp into the resolved971parent,
then source c1 Turn completion and finite wire screen. Service/moving clearance,
joint strength and actual bolt fit remain separate tasks. No full assembly,
new Native hardware adoption,100g,Lift,mesh/time or STEP qualification.

## Continued974–981 after9914651

974 f2/c1actual13partRoot/clamp placement: only Palm0volume seam retained
(328faces),no other intersections,10.001s. 975 separate actual c1Turn completion
against all retained parts: clear,283parts,11.477s. 976 actual c1fulllead705probes
against283parts: no unresolved obstacle,31.370s. Old functionalHoldingscope
unchanged;these are REST CAD tests,not new Native dynamics.

Service tool generalized to explicitfinger/parent-delta with exact composed
Root-frame equality. 977f1/978f2/979f0 each checked AGAINST THE SAME completed975
assembly,not earlier incomplete neighbours. Screw/tool/nut/pad continuous convex
envelopes and7sampled subassembly positions clear in all3 cases (10.289/11.219/
9.427s). Nut travel4.8mm is the old nominal design choice,NOT measured tolerance,
preload or physical friction lock. Tool is circumscribed shank only,not full
key/hand. Assembly removal remains sampled,not continuousCCD approval.

980 current283part instance BOM created from exact resolved CAD. Every part
evaluates to one closed positive solid;no mass inferred from geometricvolume.
Actual material/density/mass/vendor/process fields NULL. Missing joint/drive
manufacturing specs remain open. 981154softwaretests PASS8.809stestbody.

```bash
$PY product_prototype/cad/remaining_clamped_root.py --tag UNIQUE --finger 2 --case product_remaining_c1lead971 --delta
$PY product_prototype/cad/remaining_lead_completion.py --tag UNIQUE --case product_remaining_f2clamp974 --finger 2 --cable 1 --delta
$PY product_prototype/cad/remaining_root_wire.py --tag UNIQUE --case product_remaining_f2lead975 --full-lead --delta
$PY product_prototype/cad/pressure_nut_service.py --tag UNIQUE --case product_remaining_f2lead975 --finger 2 --delta --local-envelopes --nut-travel 4.8
$PY product_prototype/cad/resolved_assembly_bom.py --tag UNIQUE
```

Next982 checks all6REST lead paths against final283parts,including old f0paths
whose neighbouring hardware has changed. Cost estimate before launch:6x~31s
plus one mesh assembly,within420s guarded child/4GiB. This is NOT unchanged prior
experiment repetition. Other full-finger segments,wire-wire distance,moving
clearance,physical materials/joints,Native time/mesh and STEP remain open.

## Continued982–987: actual static path coverage

982 all6lead paths against SAME283part completed975candidate clear,4230finite
probes,130.190s (420s/4GiB guarded). Actualproximities retained perpath JSON.
985 separately checks station0..5guide-centre chains only,66probes total,9.077s,
no obstacle or Eyelet proximity intersections. Firststation is independently
matched to Root route origin with1e-10mm identity guard,not a physical tolerance.
CADring centroids define numerical straight chains;this is NOT real flexible
wire equilibrium/finiteborecontact/winding/anchor validation or prescribedSOFA.

98315lead-pair numerical distance references;986 adds the actual985guide chains
to form distalguide→Root→drum paths. Both minimum nominal+sagitta-expanded gap
2.0495544998508044mm. Closest segment indices/parameters/point witnesses saved.
Extendedprecision endpoint/interior minimization validated against analytic
crossing/parallel/skew/endpoint and rigidmotion references. NOT interval/exact
certified distance,manufacturingtolerance,movingCCD or a physicalwirecontact law.
Distal anchor/drum termination beyond endpoints and all deformed paths remain
unverified. These static passes do not qualify whole dynamic assembly.

987159softwaretests PASS5.333sbody/5.925sguard. No newNativeSOFA run: actual
joint/material/preload missing;no newconstrained-loop hypothesis introduced.
Old Native time/mesh FAIL,100g/Lift/STEP gaps retained. No purchases or push.

```bash
$PY product_prototype/cad/completed_lead_audit.py --tag UNIQUE
$PY product_prototype/cad/completed_lead_audit.py --tag UNIQUE --finger-chain-only
$PY product_prototype/cad/lead_pair_distance.py --tag UNIQUE --finger-chain-case product_finger_chains985
```

NEXT independent product work: explicit distal wire-anchor and drum termination/
motor-horn interface from actual chosen part drawing;continuous cartridge
service/whole-tool access and deformed hardware/wire clearance. Real clamp
preload/slip/indentation and materials require hardware,remain NOT MEASURED.
Do not rerun971–987 without a new changed-geometry/physical hypothesis.
