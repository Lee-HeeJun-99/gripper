# Product-driven track reset — 2026-11-26

Starting HEAD: d01db2b6dd3f196ac142b6e6af2c7b226caf209c. RevAA remains
the official unpowered engineering-definition baseline. No integrated release.

## Executed drive design cycle

`direct_clutch_candidate.py --tag revAE_direct_clutch1` generated an actual
244-part STEP assembly and 51 changed part STEP/STL files. A friction drum
on a bearing around the motor-mounted input hub replaces the separate rigid
shaft/coupling/support train. This is a make-part candidate, NOT a rated clutch.

Actual nominal intersections reject this assembly. Root/motor placement,
old shaft washers, motor pilot, clamp screw, adjuster plug and nipple cap
conflict. `--tag revAE_direct_clutch2 --internal-clearance-fix` preserves the
first failure and removes obsolete shaft washers, trims the pilot-conflicting
collar and corrects the actual plug bore. The second assembly has 238 parts
but still FAILS interference. Its independent geometry audit passes valid
single solids, positive closed STL and assembly integral reconstruction;
that does NOT qualify interference, strength, retention or overload protection.

Manufacturing inputs: the actual 5mm STEP motor shaft is retained; bearing
boundary is NSK 688A 8×16×4mm (not the different 688ZZ 5mm width). The
[NSK specification](https://www.nsk.com/engineering/688a-esm-md.html)
defines an interface candidate, not the hub/shaft/clamp strength. Purchased
bearing CAD is an exterior envelope; no invented internal mass or drag.

The WM Berg [clutch catalog](https://www.wmberg.com/berg/media/products/pdfs/INCHSectionG.pdf)
does not turn a custom requested calibration into a delivered guaranteed cap.
Neither custom friction geometry nor a supplier's adjustable minimum torque
proves maximum transient tendon load. Spring, friction, bearing drag, motor
overhang and operating-speed/energy bounds remain required.

## Actual Finger boundary cycle

`actual_finger_boundary_map.py --tag actual_boundary_AD1` reads actual
RevAD STEP identities and measures distal fragment contacts. PET ends at
Z=-93.2mm; the nominal terminal stop is Z=-95mm. At -1.8mm local axial
advance the front first touches; at -2.0mm its common volume is 0.36mm³.
The nominal local fragment is clear. These are finite geometry probes, NOT
a deformed Finger simulation or a certified 1.8mm working-stroke allowance.

Model contract: independent PET/Rail axial fields; PET distal end free until
finite-stop/contact; Rail terminal finite pads; real root clamp contact.
The actual root datum Z=-7 and Rail terminal station Z=-95 give 88mm;
PET length is 86.2mm. These match the reference rod datums but do not
validate root preload, friction, material or large-deformation strength.

## Execution and scheduling

Six previously authorized external worker calls have been consumed. Service
`regrip-stage12-20261126-3.service` was inactive/dead, MainPID=0, with
RUN_BUDGET_EXHAUSTED. No new manager/service or budget renewal was launched.
Current work uses this interactive session only.

The pure task selector now balances A/B/C; after two consecutive same-track
cycles it selects an executable alternative if present. Controls reject
unmet prerequisites and do not fabricate tasks from an empty queue. No
manager security, Supervisor, STOP handling, budget or execution controls
were changed.

Resource bound for CAD: `ulimit -v 4194304`, `timeout 420`, one BLAS thread,
robot_ws Python with `PYTHONPATH=/tmp/regrip_stage1_ocp`. Per-result producer
snapshots and STEP hashes are stored in the unique directories. No SOFA run,
hardware operation, purchase, push or history rewrite occurred.
