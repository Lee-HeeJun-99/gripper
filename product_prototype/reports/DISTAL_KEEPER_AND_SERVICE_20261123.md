# Distal keeper and service continuation — 2026-11-23

Starting HEAD debe10b; clean tree. Reused988–1004 without rerunning them.
No new SOFA trial: Native time/mesh,100g/Lift,material/joint and STEP Gates stay open.

## 1005: actual one-station keeper

Actual f0/c0/s5 frame, not the Root1.2mm-bore frame. Parent1000 retained;
replaced only one Support and added cover,two screws,two nuts:294 instances.
Six actual saved watertight single-body STLs, not STEP or fabricated parts.
Split cylindrical housing includes axial shoulders and finite wire passage.
No Guide/terminal/collision hardware removed. Only one channel implemented;
do not propagate to remaining five without independent checks.

[Accu SSCF-M1.6-6-A2](https://www.accu.co.uk/metric-cap-head-screws/3783-SSCF-M1-6-6-A2)
provides nominal M1.6x6,pitch0.35,headD3,height1.6,AF1.5. Normalized supplier
limits and the separate Aspen nut source are in config/distal_keeper_v52.json.
Stock,actual thread fit,length tolerance,preload,material and joint strength
remain UNKNOWN/NULL. Smooth thread envelopes are not actual helical engagement.

1005 world CSG REVIEW: split plane2.1208e-5mm³; head bearing artifacts
8.5408e-7/1.9123e-6mm³. No tolerance applied and original hits preserved.
1006 same-shape local diagnostic: split has no intersection; head bearing
faces have zero volume. This supports coordinate/mating-plane sensitivity,
not certified nonintersection or clearance and does not replace1005.

## 1006: real service failure

Two nominal all-roll1.5AF key-shank envelopes clear retained assembly.
Not whole bent key/hand clearance. With screws/nuts removed, sampled normal-Z
cover withdrawal collides with f1/c1 distal terminal at0.5,1,2mm:
0.046118/0.399153/0.971548mm³. Endpoints clear; service direction rejected.
Axial terminal tests show obstruction after0.3mm(maxL5) or2.3mm(minL3).
Not six-DOF slack retention, strength or pullout qualification.

1007:174 software tests PASS;7.931s guarded runtime. Not product Gates.

Reproduce with NEW tags:
```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/distal_keeper.py --tag UNIQUE_KEEPER
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/distal_keeper_service.py --tag UNIQUE_SERVICE --case product_distal_keeper1005
```
Raw:results/product_distal_keeper1005,product_distal_service1006,
product_keeper_regression1007. Each includes command/source hashes and bounded
process evidence;CAD-only,SDK/binary identity NOT APPLICABLE. No measured capacity.
NEXT independently test diagonal cover withdrawal,then nut/screw service and
actual review drawings. Unchanged full B3/dt/alarm sweeps are not justified.

## Continued after feature05c984d: service and assembly evidence

1008 diagonalY/Z=1 fails own Eyelet/terminal obstruction.1009 slope0.25
avoids that sampled own obstruction but still hits neighbor terminal up to
0.040646mm³. These are not repaired paths; stop slope-only exploration.
Next cover design needs a different split/removal architecture or a separately
verified cartridge-out service order. Do not remove neighboring hardware from
the operating model to claim clearance.

1010 creates six actual STL copies,part CSV,and two saved-STL section drawings
in meshes/distal_keeper_v52 and drawings/distal_keeper_v52. PNG visually
inspected. This is one keeper,not full CAD Assembly/STEP or released drawing.
1012:176 software regressions PASS,7.904s guarded,not physical product Gates.

1011 tests nominal screw withdrawal and side-entry nut convex envelopes.
Screw start-bearing numerical faces remain REVIEW. Both nut envelopes hit
Support (~0.410mm³): original entry starts at nut centre and does not provide
full-width clearance to the rear half during lateral extraction. A convex
envelope hit alone is unresolved,not an actual collision proof; explicit
slot modification is a conservative design response,not evidence deletion.

1013 v53 changes only nut entry start to centreY−1.65mm. It still has the same
three static mating-plane artifacts; no other static assembly hit. Opening
the slot sacrifices hex antirotation capture: manual retention/wrench/locking
must be designed and tested. Do not call it a captive or qualified nut.
All previous parts/configs/failures remain unchanged. New1014 fastener study
uses the v53 configuration named and hashed in1013 rather than hardcodedv52.

1014 does NOT solve nut service: first nut hull hits retained s4 Support
0.877533mm³;second still hits s5 Support0.409824mm³. A slot in the local wing
does not clear the complete retained support architecture. No further blind
slot enlargement; preserve both designs as REVIEW. Refine actual nut motion
against those specific supports before designing a different access direction.
1011 generic scope text has append-only SCOPE_NOTE clarifying no cover tests
were run under --fasteners-only. New outputs have explicit mode/scope.
Regression runner now hashes every CAD Python module and snapshots all test
modules,not only the unchanged top-level unittest importer.

1016 refines hull warnings with14actual nut-solid positions. Both initial
positions clear. Nut0 hits s4Support atY+3/+4mm (0.044527/0.858277mm³);
nut1 hits s5Support atY+2/+3/+4mm (0.034200/0.185851/0.331460mm³).
Thus the candidate service failure is real at sampled positions,not merely a
filled nut-bore hull artifact. Stop this slot-only family; no arbitrary wall
deletion. Next distinct design hypothesis must change access/split architecture
or independently verify complete cartridge removal/bench assembly sequence.
1017:178 software tests PASS,5.320s unittest body. Every CAD module hash and
all test-source snapshots recorded. Not time/mesh/physical capacity PASS.

Exact read-only resume:
```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/product_distal_nut_actual1016/summary.json
```
New-hypothesis reproduction using a NEW tag:
```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/distal_keeper_service.py --tag UNIQUE_ACTUAL_NUT --case product_distal_slot1013 --fasteners-only --nut-samples
```
All CAD trials guarded4GiB/420s;longest new worker10.94s. Pack1010 was a short
0.505s local STL/plot utility,not a physics process. No active research child.
Actual pullout/thread/preload/material data need specimens;CAD kernel/STEP
unavailable. No background continuation or completed product claim.
