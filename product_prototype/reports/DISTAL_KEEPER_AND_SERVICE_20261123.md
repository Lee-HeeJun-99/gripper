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
