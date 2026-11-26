# Rev AA — Stage1 unpowered first-article design release

2026-11-26. Actual case `revAA_heel_relief2`; release audit
`validation/release_revAA1/summary.json`. Stage1 engineering definition only.
**No production, powered operation, actual load or hardware qualification.**
The historical Hrelease FAIL and every later failed trial remain unchanged.

## Actual implemented and checked

-304native single valid BRep solids;304closed positive STL meshes; nominal
 all-pair solid common0; assembly STEP actually written/reread.
-Locating-left/captured-floating-right625-Z P6 bearings, outer caps/inner
 abutments,8mm shaft shoulders, washers/fine nuts; actual bilateral stop
 checks. Current SKF local-envelope/gauge/coax requirements replace mean-only
 fit claims. Endplay is deliberate, not fictional preload-free zero play.
-Positive transverse pin and retained plugs carry drum torque; actual split
 coupling has5.05input/4.45output bores, real screws and4.4plain shaft grip.
 Actual extra4.42GO nut-passage bound and6g/6H drawing requirements. Pin,
 thread strength, jaw elastic closure and clamp force remain NOT MEASURED.
-Two factory NI000032 ends per finished Tendon, positive split/blind receiver
 and drum cap.0.48..0.52wire; outlet-length190.809325±0.25 at0.1N design
 reference. Internal receiver4mm is included in that length, not omitted.
-Metal sleeve/shoulder/washer preload path bypasses rotating POM/receiver.
 Nominal gaps0.03; matched acceptance0.025..0.035 and midplane±0.005. Finish
 sleeve5..10µm below actual unstrained fork opening; re-match shims. No
 measured free-spin/preload/thermal or fork elastic closure certification.
-42nominal thread-envelope paths/fullnut overlap;32source-aware stock length
 checks. Worst motor engagement2.66..3.34, bottom margin1.16. Nominal major
 thread cylinders are NOT tap-drill instructions or helical contact models.
-40actual tool/active-fastener staged swing/extraction jobs. MFbolts must be
 preinserted; tighten/remove MF nuts from below with fixed key. Motor/plate
 assembled on finite bench support. Terminal clamps before pivot/Tendon.
 Real AF4shaft counterhold, fine-nut swing and coupling/motor-module paths.
-31prescribed0..60° whole laminate/rigid/wire poses, max-stock and receiver
 fastener exterior witnesses; maxD0.52/length±0.25 wire checks clear. No
 dynamic sliding, cable law, actual recovery or continuousCCD claim.
-New combined bearing/journal/endplay counterexample failed Rev Y: actual
 maxcommon15.011668mm³. Rev Zbroad U cuts only6pulley bodies;298parts remain
 identical. Full-torus common0 for declared0.045radial/0.155axial offsets;
 analytic radial/axial margins0.015/0.035. Minimum root21.85 vs42d21.84 gives
0.01recommendation margin, NOT a measured life/strength/fatigue guarantee.
-Z60° rigid neighbor gap0.079809 failed the explicit0.4pair uncertainty
 budget. Closest-point-driven AAheel pockets raise three actual gaps to
0.515955. All other recorded rigid interFinger pairs retain>=0.4 by strict
 removal-only BRep proof; not all operating angle errors/elastic deformation.
 Actual1mm heel cutter40positions common0. Conditional selected bore webs
2.325/1.225 and half remaining thickness2.39; not exhaustive minwall/strength.
-12current rigid service paths clear; receiver/sleeve/inner shims extracted
 asGROUP through open fork.3mm sleeve cannot pass through2.2mm fork eyes.
 Flexible wire manual peeling/unwinding is documented, not rigidified as a
 false installed-wire extraction simulation. Jamming dock/gauge and wire
 sector separation13.920484 preserved. Real vacuum chamber is not installed.

## Actual manufacturing definition

`cad/assembly/revAA_mbd1/ASSEMBLY.step`,608self-contained part STEP/STL files,
304BOM rows,41dimensioned supporting views,691actual face records. Authority:
current datum/fit sheet and part BOM overrides, then native STEP/face catalogue,
then supporting SVG. These are model-based instructions, not an assertion
that review projections alone provide every hidden dimension or GD&T.
Actual assembly/exploded overview is illustrative; service evidence separate.
General and critical tolerances are requirements for incoming/machined parts,
NOT measured process capability. Billet CNC/turn/grind/ream, source-listed
R0.35receiver tool and dimensioned custom broad-groove tool are specified.

## Mandatory subsequent holds (outside this Stage1 design release)

Actual blank inspection schema:
`validation/revAA_first_article_template2/INSPECTION_RECORDS.csv`,51entries.
Executed checker result FIRST_ARTICLE_NOT_MEASURED (all51missing), not a
fabricated zero/PASS. Canonical case/limits/full IDs and operator/specimen/
gauge/calibration/time are required; software negative controls reject empty
or incomplete inputs.13software tests passed; none is a physical measurement.

Qualified shop must accept actual micro-machining, grinding, thin rim/burr
control, profiles/gauges and fixtures BEFORE fabrication authorization. Inspect
actual parts/matched fasteners/shims, then perform unpowered/free-spin and
guarded Stage2load tests. Do not energize or suspend an object on this release.
Actual material lot allowables, clamp friction, swage pullout, fatigue,
retention torque/cure, driver/thermal behavior, loaded cable seating radius,
actuation, full as-built tolerance closure and100g grasp are NOT MEASURED.
No old B3 functional result is transferred to this different CAD assembly.

## Reproduction

Use fresh output tags only, inspect old outputs instead of overwriting:

```sh
PYTHONPATH=/tmp/regrip_stage1_ocp /home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/stage1_manufacturing/scripts/release_gate_current.py --case revAA_heel_relief2 --package revAA_mbd1 --review revAA_review1 --tag NEW_UNIQUE_AUDIT_TAG
PYTHONPATH=product_prototype/stage1_manufacturing/scripts /home/ubuntu/miniconda3/envs/robot_ws/bin/python -m unittest test_release_evidence test_current_release
```

CAD child limit4GiB/420s maintained. No SOFA, SDK modification, purchase,
hardware actuation, remote push, history rewrite or historical raw deletion.
