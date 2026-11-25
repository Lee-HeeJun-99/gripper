# Stage1 mechanical continuation — 2026-11-26

Continues799d378 after19f69a0/start98d1dd6. Original RevA–H, all Raw, old
verdicts and physics queue preserved. No Native experiment, SDK edit or push.

## Executed CAD and corrections

RevK: actual changing-wire interference required physical Palm/Idler-foot
relief, recessed left-cap heads and moving one cup screw out of the wire path.
RevK_threadclear:280parts,0bulk collisions,31sampled motion/rotor-wire PASS.
RevL_bore:289parts with actual hex sockets/flats and future cassette blank
adapter,0bulk collisions. Full3Finger wire check expanded beyond own module;
one analysis attempt failed on MF0 filename replacement; fixed prefix-only
mapping, original log kept. revL_fullwire3 actually PASS for that scope.
RevL_keys1 failed real L-key access; changed actual staged assembly order and
tested six permissible hex clockings. revL_keys2:38actual engaged finite keys
plus handles/6approach poses PASS. revL_paths1:12sampled extraction operations
PASS, explicit removed-part cutsets, no phantom operating-part removal.

RevM corrected the manufacturer stepped-terminal diagram: D isTOTAL length,
B is stem length, not B+D. Max terminal envelope now3.8x6mm,6.2mm sockets,
stem outlet seated at shoulder (old drum0.5mm datum gap removed). Historical
11mm conservative envelopes/old analyses retained, not rewritten.

RevN actual alternatives address manufacturer bend recommendation rather
than dimension scanning:22mm groove roots,0.28mm U profile, directly tangent
factory end, no tight3D Bezier transfer. SKF P6 sealed-ring local OD variation
is9um, so mean-only16H6 was inadequate to guarantee a floating outer ring.
New explicit housing limits16.010..16.021, nominal16.016; original stops kept.
Local-diameter clearance references: inner0.0005..0.0205mm with5f6;
outer0.0055..0.0325mm. These are NOT complete form-envelope or creep approvals;
incoming envelope/gauge inspection remains explicitly required and unmeasured.

Initial new tangent angle exposed60deg swivel head/nut contact. Real0.6mm
head recess, captive hex nut pocket and trimmed7mm M2 screws reduce projection.
First counterbore made a zero-wall tangent at body edge (STL FAIL); actual
open-sided machined spotfaces eliminate that edge, no mesh filling.
Root docking pad narrowed to leave a real spanner lane. Side-entry spanners
still conflict around some Palm nuts; actual finite deep nutdriver geometry
provides axial access at the declared early Root assembly stage.

RevN_motor_gap:289parts,0bulk intersections. Manufacturer motor shaft24+-1
otherwise consumes the nominal1mm gap. Actual motor/mount/fasteners shifted
back1mm; a NEW Palm blank replaces superseded current motor-hole datums.
This is NOT a shifted-hole rework instruction for a physical old Palm.

## Actual independent outcomes

- revN_motion_full4:289closed meshes,31prescribed0..60deg poses clear,
  including actual clipped Root17mm and distal5mm laminate meshes,88mm
  conservative flexible envelope, all fixed hardware and interFinger pairs.
- revN_allkeys3:40finite keys/handles and6approach samples, staged PASS.
- revN_nutdrivers5:21nut positions PASS by finite spanner/nutdriver paths or
  independently verified captive pocket. Earlier access failures preserved.
- revN_contract3:actual U-floor containment0mm3 excess, nominal wire torus
  intersections0mm3;4actual30deg nut rotation stops; actual seat radii8.008.
- revN_wire1:takeup16.935839mm, rotor86.25352deg, wrap258.34636deg;0wire/rotor
  hits in the then-tested scope. Latest complete laminate/capsule proof pending.

These are manufacturing/kinematic design checks only, not FEM, driven motion,
wire friction, preload, fatigue, load or hardware PASS. Discrete samples are
NOT continuous CCD. All latest gates must refer to the same final revision.

## Current actual work

revP_machinable replaces the sharp-ended blind cylindrical terminal pocket
with a rounded-rectangle6.2x6.2/R1 pocket accessible from+Y using a2mm endmill.
Its cap fasteners are relocated outside this machining volume. Actual CAD
job and subsequent final validation continue; no Stage1 release declaration.
Manufacturer packet already generated33three-view review drawings and289BOM
rows for revM. Latest larger-groove drawings/process callouts still to update.

## Primary sources (consulted26Nov)

- [Factory terminal dimensions/finished-only delivery](https://www.carlstahl-technocables.com/de/de/produkte/konfektionierte-seile/aufgepresste-seilendverbindungen/).
- [Manufacturer stepped-terminal diagram](https://www.carlstahl-technocables.com/fileadmin/Resources/Public/Images/konfektionierteSeile/stufennippel_aufgepresst.jpg).
- [Pulley recommendation](https://www.carlstahl-technocables.com/gb/en/products/pulleys/):22mm>=42x0.52mm; design recommendation, NOT tested fatigue life.
- [SKF P6 table3 p39](https://cdn.skfmediahub.skf.com/api/public/0901d1968094ddb3/pdf_preview_medium/0901d1968094ddb3_pdf_preview_medium.pdf).
- [Motor manufacturer drawing](https://www.pololu.com/file/0J714/SY42STH38-1684A.pdf).
- [Guhring cut-tap data](https://guhring.com/Catalogs/CatalogPDF/ea5d1884-7c23-4a3d-9904-dbf4ceacbead):M2/M3 nominal pilot drills1.6/2.5, inspect actual6H; STEP major envelopes are NOT drill diameters.

No price, stock, physical cure, wire fatigue or strength is invented. Motor
pilot projection is not dimensioned in the consulted sheet; specify incoming
clearance inspection rather than reporting an unverified catalogue height.
