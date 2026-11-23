# Root disconnect and drum termination — 2026-11-23

## Continuation1041–1058

Independent c1 termination1041/1042 preserves c0 and uses its own saved lead,
opposite pad service direction and positive finite hardware.300-part candidate.
Nominal seven-part full-turn drum envelope1043 has no fixed-part hits;this is
not a real motor-axis,wire-winding or Native dynamics certificate.

Catalog retaining screw dimensions use Accu SSCF-M3-12-A2:
https://www.accu.co.uk/metric-cap-head-screws/3820-SSCF-M3-12-A2 .
M3x12,2.5mm socket,1.3mm drive depth define the nominal cavity;actual purchased
socket fit,thread mating,preload and availability remain unqualified/UNKNOWN.
1045/1055 retain own-drive floating mating artifacts as REVIEW;all six indexed
nominal shanks have no other-hardware hits.Three Root hoods are now independently
placed1051/1052 and axial nut obstruction checked1053/1054,not retention-force tests.

Actual13-part STL/section packs1044/1049 created;not STEP/full assembly approval.
1050 screens4290 finite probes on six current REST reference paths:zero unresolved
obstacles,77.29s.1056 checks the two changed Root clamps against those same paths,
with298 exact unchanged CSG identities;zero new hits,not dynamic/interval proof.
1057 instance BOM contains300 valid solids,actual assembly mass NULL.
1058 software regression PASS;physical tests remain zero.1047 provides eight
instrumented test plans and34 NULL fields,not fabricated measurements.

Current assembly:results/product_all_hood_drive1055/assembly_delta_recipe.json.
Latest BOM:results/product_current_BOM1057/. Old1036 service failure and185
unresolved continuous-cartridge prisms remain unchanged. Next priorities:
positive pad/nut retention and unloaded reversible service,remaining five distal
keepers and two drum modules,physical thread/preload/pullout tests,then actual
materials/joints and justified Native integration. No100g/Lift/STEP/product PASS.

Started clean at b1c01a6;1018–1029 reused,not rerun. New maintenance geometry,
NOT Native SOFA/holding/time/mesh/physical service qualification.

## Internal joins and actual retaining axes1030–1031

Same294part assembly1018. All three cartridge partitions keep their assumed
Skin–Rail bonds and explicit c0Eyelet–Support bondline together. Root Clamp
and its two clamp bolts/nuts also travel together. Thus the DECLARED cut-set
does not require breaking these internal adhesive joins or opening Skin clamp.
This is not proof of complete physical joint topology or adhesive strength.

Six actual two-cylinder retaining-bolt proxies independently checked:18mm
continuous shaft/head union sweeps and head-radius20mm axis approach cylinders.
All six approach axes clear. Sweep/mount boundary artifacts~9.2e−7..3.53e−6mm³
remain REVIEW. These nominal proxies have NO drive geometry,so no real hex bit,
thread/hand/tool fit approved. Do not drill/choose a driver from this screen.

1031 implements an acyclic dependency plan with unique/known prerequisite
validation. Unload,drum release,free fixed route,secure cartridge,retaining
bolts,withdrawal,bench service,reassembly remain physically BLOCKED/NOT RUN.
First missing mechanism at this baseline:reusable drum-side free-end termination.
No hardware IO or automatic physical stage completion from CAD evidence.

## Integral nut hood1032–1034

One f0Root Clamp modified with integral negative-longitudinal roof+connection,
same two3.4mm bolt passages. No added loose fasteners/nut deletion. Skin bearing
region and original clamp stack remain.294instances;one actual closed STL.
Extra volume/inertia/stiffness not adopted in Native. Roof targets0.05mm gap
above original nominal nut tops. Static three Skin/clamp-head mating artifacts
retained REVIEW;no other changed-vs-retained hit.
1033 rechecks retaining access against changed assembly;axes still clear,
boundary sweep artifacts remain.1034 translates two actual nuts:free at+0.025mm,
hood obstruction at+0.1mm (~0.857mm³ each);carrier obstructs−0.1mm. This is
sampled geometry,not six-DOF capture/roof strength/vibration/thread locking or
measured retention force. No actual material or preload assigned.

## New free-end clamp1035–1038

One c0 drum termination candidate reuses v52catalog M1.6cap screw/nut dimensions.
Floating pad,wire bore,and integral body on actual generic f0drum;three extra
instances=>297. Free0.45mm feed-end comparator,not the old0.5mmB3wire or a selected
supplier assembly. Screw head initially0.4mm off body so it acts as an adjuster;
cap-bearing torque is NOT a preload relation. Nominal unloaded pad/wire gaps
do not hold a wire. Actual friction/crush/slip/pullout/fatigue NULL.

1035 static solids clear.1036 nominal key/screw envelopes and short free-wire
capsules clear,but actual pad service fails against drum flange:0.1mmpositiveY
translation already0.0200mm³;static fit alone is not assemblability.
1037 v59 opens ONE narrow pad pocket through added body AND original flange
toward negativeY. Incoming c0lead pulls positiveY;positiveY stop retained.
1038 changed pad path10mmnegativeY:seven actual pad samples,key/screw envelopes
and three finite wire probes clear. Original1035/1036 failure preserved.
Endpoint exactly matched and hashed to890source lead before adding the short
free tail. No actual clamping/load path/screw thread or continuous service PASS.
Loose pad capture during unpowered service,captive nut insertion/locking,c1
termination,motor horn/D6shaft fit and rotating envelope still unqualified.

1040 rechecks8actual cartridge positions against changed297part hood/drum
assembly:clear samples only. Existing185continuous-sweep prism questions not
reclassified. Root/hardware/wire joints and complete physical sequence unqualified.

All bounded workers4GiB/420s,new unique paths. Plan1031 is a short software
utility,no physical process. ActualCAD STL/source/command/hash/runtime in each
new case. SOFA SDK/binary NOT USED. No old Raw/FAIL/Manifest change or push.

Reproduce ONLY with NEW tags:
```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/root_disconnect.py --tag UNIQUE_ROOT
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/root_nut_hood.py --tag UNIQUE_HOOD
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/drum_wire_clamp.py --tag UNIQUE_DRUM --config termination_drum_clamp_v59.json
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/drum_clamp_service.py --tag UNIQUE_PAD --case product_drum_pad_breakout1037
```
NEXT independently implement/check c1termination and joint tool/nut access,
then nominal rotating hardware envelope;never invent absent B3/CAD part motion
as Native dynamics. Actual force/pullout/material/drive fit requires specimen
and supplier-dimension qualification. STEP/Native100g/Lift/Recovery still open.
1039:197softwaretestsPASS,5.188sbody,not physical service/holding qualification.
