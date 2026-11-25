# Stage1 retained tendon and prescribed motion — 2026-11-25

Start98d1dd6, bearing/positive torque component checkpoint19f69a0. No historical
RevA–H regeneration, Native experiment, SDK edit, push or history rewrite.
Toolchain remains cadquery-ocp7.9.3.1.1 / vtk9.6.2 in /tmp/regrip_stage1_ocp.

## Actually implemented

- PlanarY0 drum/idler path by rigid6mm module translation, real matching Palm
  holes; right bearing module+1.5mm, central shoulder length12.5mm.
- Tapered PET24→12mm and edge-following3mm rails, preserved thickness/material
  assumptions. Actual index pin through sheet, positive terminal endstop.
- DIN7991M3 flush terminal bolts outside laminate; split freely swivelling
  factory-nipple receiver and axle. No fictional friction clamp/knotted wire.
- CarlStahl NI000032 finished-end maximum envelope3.8x11mm; actual manufacturer
  wire range0.45..0.63mm includes0.50mm. Side-load both finished ends into split
  receiver/removable drum cup. Pullout/bend fatigue remains Stage2 NOT MEASURED.
- Real cassette dock with locating boss,2M2 screws, below-Palm support arms and
  matching Palm slots; future cartridge attachment, not implemented jamming.

Manufacturer source: https://www.carlstahl-technocables.com/de/de/produkte/konfektionierte-seile/aufgepresste-seilendverbindungen/
DIN7991 dimensions: https://tvsat.com.pl/PDF/B/bn_616_bossard.pdf
Factory terminal B/D drawing ambiguity is handled by conservative combined
11mm maximum envelope; no made-up exact stepped nipple dimensions.

## Actual failures and correction

Failed/intermediate local exports preserved, indexed with hashes/source snapshots
in validation/revJ_trials. Disconnected cap,33 then6 real bulk intersections,
bad STL topology and precision-only unsuccessful hypothesis are NOT erased.
The earliest float/Common import failure has no frozen source; explicitly noted.
Zero-wall countersink/edge tangencies needed physical edge material, not mesh
hole filling. revJ_margin has283 valid closed STL parts and0bulk collisions,
but60deg front-fork corner collision0.009486mm3 per pair. The actual intersection
was X40..40.385/Z-95..-94.750 in local part coordinates. A1mm corner relief
away from the axle land fixes that sampled interference.

revJ_forkclear:283actual parts,0bulk intersections. Independent
validation/revJ_motion2:283closed positive-volume meshes,31prescribed poses
0..60deg with actual articulated swivel/rigid tip, no collision against fixed
hardware or another Finger. Flexible span88mm, distal5mm rigid, Root endsz-7.
This is sampled geometry, NOT continuous CCD/FEM/Native physical performance.

validation/revJ_wire1 FAIL: rotating coupler hits protruding cap screws;
internal lead conflicts with one drum-cap screw; changing tangent crosses
Idler foot/Palm. Circumscribed-chord artefacts against own circular supports
are separated from actual interference and require independent analytic CAD
containment/tangency certificate, not a hidden collision suppression.

Current revK changes: recessed cap screws/thicker plate, real longitudinal
Palm/foot wire opening, three noncollinear cup screws outside lead channel.
First foot relief left a detached sliver (FAIL); opened relief to actual edge.
First6mm flush screws exceeded old thread-hole depth (FAIL6actual intersections);
extended actual housing holes, without moving bolts or ignoring intersections.
Current actual job revK_threadclear. Overall release remains FAIL/open.

## Reproduce new outputs only

```
PYTHONPATH=/tmp/regrip_stage1_ocp /home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/stage1_manufacturing/scripts/incremental_stage1.py --tag NEW_UNUSED_TAG --base revI_supplier --phase mechanisms
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/stage1_manufacturing/scripts/mechanism_motion.py --case revJ_forkclear --tag NEW_UNUSED_MOTION_TAG
```

Motion2 already complete; do not rerun unchanged evidence. Next: actual revK
whole-wire/rotor and tangency checks, service/tooling, cassette gauge, dimensioned
manufacturing drawings/BOM and fail-closed release checklist. Aggregate ASCII
STLs>50MB remain local, ignored; actual assembly STEP and individual STL retained.
