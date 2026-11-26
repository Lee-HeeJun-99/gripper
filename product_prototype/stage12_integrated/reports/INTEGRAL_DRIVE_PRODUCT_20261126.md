# Rev AK2 — integrated motor support product candidate

Official RevAA304 remains unchanged. RevAK_integral2 is an **unadopted235-part
candidate**, not a manufacturing/strength release. Last preceding work save:
`d4e6521`; obtain actual current HEAD using `git log -1`.

## Actual product change

AJ250 used a separate grounded spindle, two bridge screws and two compression
spacers per Finger. AK machines the motor pilot register, finite floor and
grounded8mm bearing journal into one motor plate.15 separate parts removed.
Motor is relocated+5.5mm axially; Drum, Idler, Finger and installed winding
geometry remain fixed. The nominal5.3mm through bore clears the5mm shaft;
the8mm journal supports the actual688A4mm-wide bearing on ground, not input.
Finite9.6mm shoulder and retaining clip remain. A bearing seizure therefore
does not create the old AF input-hub/bearing/drum bypass in the declared graph.
Other fault paths and actual force cap remain unqualified.

Actual supplier shaft range and CAD bore now overlap9.7..11.2mm, versus AJ
4.2..6.2mm. Clamp axisY12.7 lies inside the minimum shaft extentY14.5; the
declared3.2mm clearance zone is covered by0.2mm. These are geometry contracts,
not evidence of clamp contact pressure, axial retention or transmitted torque.
Proposed22.010..22.030mm pilot well/depth2.68..2.72mm are manufacturing
requirements, not achieved process capability. Minimum pilot axial gap0.18mm.
Internal motor runout, journal coaxiality and loaded deflection remain needed.

## Actual failure and correction

AK1 nominal interference and mesh tests passed, but an independent foot-support
Boolean found4.8126945046mm2 missing under each motor plate. F0 missing bounds:
x88.8..91.70031,y-1.125615..2.2mm. This was a legacy pedestal aperture, not an
active relocated mounting bore. AK2 restores that region in the **new blank**
and recuts active bores. This is not a weld/plug repair. Old STEP and FAIL remain.
AK2 supported area519.4513322356mm2 equals actual complete foot area; relative
missing area below6.1e-14 for all three sectors, unchanged1e-8 criterion.

## Executed evidence

| Actual result | Location / scope |
|---|---|
| Nominal common-volume0 | cad/exports/revAK_integral2/summary.json |
| BRep/single-solid/positive/closed STL PASS | validation/stage1/AK_geometry2 |
| Full nominal feet and journal/shaft coverage PASS | validation/transmission/AK_support2 |
|48 co-rotation/slip sample poses,1272 commons,0 hits | validation/stage1/AK_drive_motion2 |
|5 finite-wire/hardware poses,613 commons,0 hits | validation/stage1/AK_wire_motion2 |
| Collet necessary demand/geometry only | validation/transmission/AK_collet_requirements1 |
| Ground-bearing graph screen only | validation/overload/AK_bypass1 |
|235 actual part IDs and STEP hashes | bom/revAK_identity1/CANDIDATE_BOM.csv |
|195 unchanged AJ part hashes, changed interfaces invalidated | models/geometry/AK_binding1 |
|311 files checked; wrong-hash/missing-result controls rejected | validation/provenance/AK_files1 |
| Existing Stage2 system gate:25 errors,22 criteria missing | validation/integrated/AK_readiness1 |

Assembly STEP and changed part STEP/STL actually exist in cad/exports/revAK_integral2.
No Native/Finger/grasp simulation or hardware test was run in this AK cycle.
No whole-Palm strength or complete Stage1 release is implied by these screens.
Old tab stress convergence8.833449% FAIL is preserved, not bypassed.

## Reproducibility

From repo root, OCP child prefix is:

```
ulimit -v 4194304
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=/tmp/regrip_stage1_ocp timeout 420 /home/ubuntu/miniconda3/envs/robot_ws/bin/python SCRIPT ARGUMENTS
```

Executed script/arguments under stage12_integrated/scripts:

```
integral_motor_support.py --tag revAK_integral2
candidate_geometry_audit.py --candidate revAK_integral2 --tag AK_geometry2
integral_support_contract.py --candidate revAK_integral2 --tag AK_support2
system_wire_motion.py --candidate revAK_integral2 --tag AK_wire_motion2
direct_drive_motion.py --candidate revAK_integral2 --tag AK_drive_motion2
collet_wrench_contract.py --candidate revAK_integral2 --tag AK_collet_requirements1
```

These tags already exist: do not rerun or overwrite. PureJSON BOM/binding,
topology, scope audit and readiness scripts were executed with system Python.
Producer snapshots and model/result SHA256 are retained in each result.
AK1 stays local with its original summaries/producer and STEP/STL; no deletion.

## Remaining system work

After product save f8c07c5 a further actual fixture cycle generated
hardware_test/fixtures/AK_collet_stand1:6 new finite parts plus actual AK hub
and bolt, nominal common-volume0. Independent inspection AK_collet_stand1
passed valid/closed/positive meshes and1% volume checks. Integral machined
D-shaft/flange reacts into a finite plate through two M4 envelopes, not an
assumed motor bearing. This replaces neither the complete force-cap calibration
rig nor actual clamp capacity testing. See AK_COLLET_REACTION.md for remaining
adapter/guard/material/measurement/authorized-load prerequisites. No safe test
load was invented and no device was operated. Commands actually executed:
`collet_reaction_fixture.py --tag AK_collet_stand1`, then
`fixture_geometry_audit.py --fixture AK_collet_stand1 --tag AK_collet_stand1`
under the same bounded OCP environment. Independent fixture raw/producer
hashes are stored. Service3 actually rechecked inactive/dead/MainPID0.

Maximum transient force cap still NOT QUALIFIED: actual friction/spring/rate,
load-side inertia and tendon stiffness bounds are missing. Shaft clamp requires
actual pressure/contact and combined torque+axial load analysis; bolt preload
must not be equated to shaft normal force. Whole-Palm mounting/contact, actual
Finger ports/root clamp, materials and full Stage1 manufacturing/tool access
must use AK, not old AA/AH results. The preliminary AF calibration stand does
not automatically fit AK. All22 Stage2 criteria remain unfulfilled.

External automatic budget remains6 used/0 remaining; no reset or launch.
This work used the current interactive session only. No background continuation
is promised. Hardware is unmeasured, powered operation/purchase unauthorized.
