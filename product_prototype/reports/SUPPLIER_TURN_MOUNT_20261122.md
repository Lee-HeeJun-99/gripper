# Supplier-sized turn mount continuation — 2026-11-22

Baseline6f4d423; no old results/SDK modified. ONE f0/c0 branch only.
873 reconstructs three finite forks,axles,nut proxies and a connected bolted
branch,retaining both original Palm feet/bores and independent Root connection.
Six loose shim parts are replaced by finite integral thrust lands. Full recipe
has287parts,not293. Ten changed STL solids are closed positive single bodies.
FAIL: second wheel intersects a cross-member4.101848614mm3. Runtime8.534s.

874 decomposes the actual failed union: component17 alone accounts for that
volume; it is the third fork's cross-member atz56.75mm.875 raises ONLY that
support route12mm,retaining its full connection. No positive volume overlap
between changed solids and retained assembly; a zero-volume Palm mating face
with328faces is preserved. Status stays REVIEW_REQUIRED,not assembly approval.
875 runtime8.662s; unmeasured threads/retention/material/strength remain open.

876 service checker FAILS on missing group metadata of non-pin wheel entries.
878 corrected checker selects pins before requiring group; missing/unknown PIN
group still rejects. New explicit --recipe input permits direct immutable
result-recipe verification. All24 exact stepped-pin10mm sweeps,12bore gauges,
18driver paths clear nominally in7.421s. Actual tool/thread/hand/preload NOT tested.

877: ONE .45mm design wire,translated first guide→Root→three turns→drum,
circumscribed finite probes including arc sagitta,all287solids retained.
No UNRESOLVED_OBSTACLE hits,24.533s. Intended wheel proximity hits are fully
recorded,not discarded as zero penetration. Not continuous-wire/contact-law PASS.
880: other5 ORIGINAL .5mm Root/lead paths vs10changed solids,706probes/path,
no hits,3.082s. Their R2 supplier bend failure remains;this is not all-wire
mutual clearance or endorsement of incompatible legacy paths.

879 actual CAD sections atworldy36 and287instance BOM generated and visually
inspected. Images explicitly not SOFA results. Partial sections cannot show
all support connections;single-body STL checks and full CSG are separate evidence.

Native dynamics NOT RUN: whole-wire constitutive/sliding contract and actual
mass/material/joints still unqualified; no reason to run old mismatched coupons.
No STEP/fabrication/50gfinal/time/mesh/100g/Lift PASS. Existing failures preserved.

Actual sources/results:
`product_prototype/cad/supplier_turn_mount.py`, `supplier_mount_diagnose.py`,
`supplier_wire_mount_screen.py`, `supplier_other_wire_screen.py`,
`supplier_mount_review.py`, updated `complete_drive_service.py`.
Raw `product_prototype/results/product_supplier_{mount873,mount_diag874,mount875,
service876,wire877,service878,review879,other_wire880}/` (individual actualfolders,
not a shell expansion command). Producer/input hashes and source commit recorded.
CAD children guarded4GiB/420s;actual peakRSS NOT MEASURED. No SOFA binary used.

Reproduction with NEW tags (do not repeat unchanged cases):
```
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/supplier_turn_mount.py --tag UNIQUE --turn3-rise 12
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/complete_drive_service.py --tag UNIQUE_SERVICE --recipe product_prototype/results/product_supplier_mount875/full_assembly_recipe.json
```
NEXT geometry-derived COM/inertia-per-unit-mass and explicit material/retention
interfaces for this changed hardware,then remaining channel redesign. Do not
copy all6 branches until Root seat/translated Skin interface and whole-path
compatibility are qualified. Actual measurements remainNULL.
