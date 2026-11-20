# Wire/Eyelet manufacturing continuation728–738

Scope: executable Manifold mesh CSG and static reference geometry, NOT actual
SOFA driven results or product qualification. Previous Native time/mesh FAILs,
functional B3 Holding and SDK are unchanged. All dimensions below are mm.

## Implemented and measured

- 728 V20 changes ONLY finite Eyelet axis to adjacent cable-branch bisector.
  OD3 / ID1.2 / length2 and wire diameter0.5 retained. CAD160parts generated,
  bounded worker4.822s. Actual731 geometric audit:6/36 bore conditions FAIL;
  12positive finite-segment/Eyelet intersections, max0.000447742mm³.
- 729 V21 changes ONLY bore radius0.6→0.7 relative to V20; OD3 unchanged,
  nominal radial wall0.8. CAD worker4.828s.731:0/36 necessary-condition FAIL,
  0positive wire intersections with own Eyelet/Support.
- 736 extends to ALL160parts/proxies and all36 full adjacent wire segments:
  no nonempty Manifold intersections. This does not include motor lead-in,
  rounded wire bends, tolerances, contact deformation or moving CCD.
- 732:V21 cartridge withdrawal5/10/15/20mm ×3fingers:12samples no positive
  intersections. NOT continuous swept service verification.
- 733:assembly/exploded PNG, sectionSVG, DXF, per-instance BOM regenerated.
  6/24 driver approach paths remain blocked while assembled; detach cartridge
  before clamp bench service. Human/tool-envelope access remains unverified.
- 734:canonical mount-module ASCII STL export:160actual saved-file reloads
  closed,positive,onebody.3original binarySTL mount failures retained.
  Tessellation/serialization changes, NOT digital geometry identity/BRep PASS.
  Legacy scope-file source label was hardcodedV19; separate correction records
  actualV21source. Producer now emits explicit SOURCE_SCOPE for future exports.
- Full assembly still has24UNRESOLVED tiny positive fastener seam intersections
  plus36intended Eyelet/Support bond overlaps. NO assembly clearance PASS.
- 735/738:design regressions only.730audit failed JSON serialization of
  numpy.bool_;original producer and FAILURE.json retained;731fixed native bool.

## Component selection boundary

737 converts existing707conditional drive/candidate snapshot to explicit approval
blockers; no manufacturer data refreshed or new procurement choice made.
At assumed1.5N/wire, two wires/channel,R8,efficiency0.5–0.8,SF2, conditional
torque remains0.060–0.096Nm. Stall/no-load ratings are NOT continuous duty.
Continuous loaded torque/speed, measured stroke, thermal duty, horn interface,
wire minimum bend radius, termination pullout and bond fatigue remainNULL.
No motor/material approved, purchased or measured. Rail grade/join unknown.

## Remaining and next executable work

742–743 continuation (after9d0829b):implemented frozen-motion bore replay over
actual historical485Rigid3 frames. Correctly includes CAD-to-body centre offset
and relative axis rotation,not body origin asEyelet centre. Same baselineconfig
SHA verified;historicalfloor-only motion independently inspected.36sites have
0failed savedframes/holdframes;maxrequiredradius0.66934932158mm vs0.7mm bore.
No candidate dynamics inferred. Future producer explicitly rejects moving
fixture commands without an actual pullpoint path.743adds this regression.
Evidencev37covers728–741;later archive captures742–743 separately.

Further cycle739–741 after first feature commit32a4825:
Circular fillet radius2mm (DESIGN ASSUMPTION,not supplier minimum) implemented.
Analytic90deg reference tangencies and constant radius tested; overlapping
fillets explicitly rejected.739 conservative box tube envelope returned12hits
at distalEyelet s4.740 tighter CIRCUMSCRIBED64gon cylinders + circumscribed
icospheres, inflated by analytic arc-to-chord sagitta bound, returned0hits
for6wires against160parts. This identifies coarse envelope false positives,
NOT permission to shrink wire radius or approve actual wire fatigue/friction.
74129design tests PASS. Actual path coordinates and producers retained in
results/product_wire_round739 and product_wire_round740. No Native run.

1. The finite rounded reference path is now implemented and screened at a
   proposed2mm radius. Obtain supplier minimum radius and fatigue coupon data;
   do not treat this successful geometric screen as material suitability.
2. Straight-branch bore necessary conditions on actual B3 saved transforms are
   now screened in742. NEXT:round the DEFORMED wire path and test actual finite
   support/other hardware at worst saved frames;include object and motor lead-in.
   Do not transfer old collision/mass qualification to the new shape.
3. Complete motor lead-in routing and supplier horn/shaft interface only with
   actual manufacturer drawings. Three paired drums != six prescribed forces.
4. STEP remainsBLOCKED:FreeCAD/OCC unavailable. No fabrication-ready claim.
   Continuous service/actuation clearance, strength, joining and tolerances open.

Reproduce NEW unique outputs (never overwrite existing campaign):

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY product_prototype/cad/manufacturing_run.py --tag UNIQUE_CAD --name UNIQUE_DESIGN --config product_prototype/config/manufacturing_b3_v21_bore.json
ulimit -v 4194304
timeout 480 $PY product_prototype/cad/wire_solid_audit.py --tag UNIQUE_WIRE --candidates UNIQUE_DESIGN --full-assembly
$PY product_prototype/cad/manufacturing_test_run.py --tag UNIQUE_REGRESSION
```

Source/config hashes and worker commands:results/product_wire_axis728,
product_wire_bore729,product_wire_solid731,product_wire_full736.
Artifacts:drawings/b3_manufacturing_bore_v21 and
meshes/b3_manufacturing_bore_v21_stl_ascii. Actual SOFA NOT RUN in these CAD
cycles; no unnecessary old loop/holding repeats. No session-exit background work.
