# Supplier-sized turn mount continuation — 2026-11-22

LATEST:twoRoot/sixturn ONE-sector review candidate has282parts at
results/product_supplier_second_root886/full_assembly_recipe.json. Both design
Root-through-drum wire envelopes887/890 have0unresolved obstacles against this
same parent (890runtime19.429s);wheel proximities all retained. NOTfullfinger,
mutualwire,movingclearance,Native or fabrication qualification. Final89191
software regressions PASS(1.911stestbody,2.474sguardedruntime).

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

Continuation881 completed geometry-only inventory of10changed saved STLs:
independent signed-tetrahedron vs trimesh inertia relative discrepancy atmost
7.88824e-11. Homogeneous density assumption explicitly separated;actual material,
mass/inertia remainNULL. See SUPPLIER_TURN_INTERFACE_20261122.md. Regression now
89software tests PASS,not new physical qualification. NEXT: second-channel finite
route/support architecture and a checked joint/material specification;do not
silently mirror the ONE branch or promote legacy wires to supplier-qualified.

Second-channel continuation882–884 (sourcee11fc36 plus recordedproducerhash):
882 explicitly decomposes and retains ALL existing second Root mount components,
rebuilding only its three-turn branch with real forks/axles/lands. First changed
channel remains in the actual parent;all new solids vs retained assembly checked.
Only a zero-volume Palm mating face438faces remains;no positive-volume hits.
Ten new saved closed single-body solids,full281parts,7.423s. This is not a blind
sector mirror;second Root deliberately remains legacy and bend-INCOMPATIBLE.
883 rechecks all24pin/12bore/18driver paths against this281part assembly:clear,
5.758s.884 checks SECOND LEAD ONLY,pull→3turns→drum finite .45mm envelope;
unresolved hits0,15.488s. Root arc deliberately excluded and declared,not
silently relabeled whole-path clearance. Intended contacts retained.

Evidencev47 independently verified11969previous immutable files,0mismatches;
13cases including failures,12172filehashes. Not13physicalPASS. NEXT second
Root redesign at its own actual guide/seat/interface,then both channels and
remaining sectors;actual joint/material/wirelaw still blocked. No newSOFA.

Continuation886–888 completes that NEXT geometry task independently:second
Root re-centred at(51.659633736,-36,-5.124234313)mm,new finite U-groove wheel,
fork,boss,OUTWARD(-Y)headed pin;firstguide/support translated2mm along incoming
branch and a real finite seat/bondline added. All6saved STLs closed singlebody;
full282parts,6.412s. Tiny positive support/bond CSG overlap1.11733027e-6mm3 and
zero-volume mating faces remain recorded:REVIEW_REQUIRED,not passed assembly.
Actualadhesive,bondstrength,retention and translated Skin attachmentNULL/unqualified.
887 second firstguide→Root→three turns→drum .45mm envelope vs282actual solids:
unresolved obstacles0,20.134s,intended wheel proximities retained.888 all24pin/
12bore/18driver nominal clear,5.861s. Neither means wire dynamics/CCD qualification.
890 rechecks FIRST wire against changed282part parent to avoid assuming no new
cross-channel obstacle;see actual summary for outcome. Other4Roots/12turns and
fullfinger wire path/mutualwire/movingclearance remain unqualified.

FreeCADCmd/freecadcmd and PythonFreeCAD/OCP/OCC rechecked2026-11-22:absent.
STEP NOT GENERATED. Evidencev48 verifies12172priorimmutablehashes0mismatch.
Reproduce secondRoot only with NEW tag:
```
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/supplier_second_root.py --tag UNIQUE_SECOND_ROOT
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/supplier_wire_mount_screen.py --tag UNIQUE_SECOND_WIRE --cable 1 --complete-root
```
Remaining priorities:qualify both translated guide/Skin attachments and finite
seat/retention/material,then remaining sectors/allwire/moving assembly checks.
Do not promote nominal clearances into strength or repeat old Nativecoupons;
wholewire law and physical data remain blockers to matched NEWNative adoption.

Immediate next design hypothesis:mechanically retained finite Eyelet seat
instead of unselected adhesive-only interface,keeping actual guide/wire sizes
and translated Skin attachment explicit. Do not erase/round interface CSG hits.
Actual retention/material/bond/force-deflection data remainNULL. Exact read-only
resume command:
```
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/product_supplier_second_root886/summary.json
```
New experiments require changed hypotheses and unique output,not unchanged886
repeats. All launched children exited;no automatic background research promised.
Final evidencev49 verifies12306previousimmutablehashes,0mismatches;12447files.
