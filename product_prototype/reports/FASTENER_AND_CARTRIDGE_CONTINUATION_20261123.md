# Fastener / cartridge continuation — 2026-11-23

Start: clean `development/regrip-autonomous-research`, local/remote
`b25699ea37c5305cd9c978843da3b2fa017654ce`,0behind/0ahead after fetch.
No history rewrite,remote push,SDK edits,Raw deletion or detector.csv addition.
Existing B3 functional outcomes and all time/mesh/energy failures remain unchanged.

## Cycle A — catalog fastener and conditional tolerance contract939

Candidate dimensions,NOT purchases or specimen measurements:

- [Accu SSF-M1.6-3-A2](https://www.accu.co.uk/flat-point-set-screws/4488-SSF-M1-6-3-A2):
  M1.6×0.35,3mm,A2,0.7mmhex socket,flatpoint diameter0.55–0.80mm.
- [Böllhoff ISO4026 dimensional sheet](https://eshop.boellhoff.de/out/media/pdf/ISO_4026_Edelstahl_A2___en.pdf):
  crosschecks pitch/socket/point and3mm nominal length interval2.8–3.2mm.
  This interval is NOT an Accu lot certificate. Set screws are compressive
  adjusters,not tensile retention screws. No standards-edition qualification.
- [Aspen ME177-016035](https://www.aspenfasteners.com/content/2D_PDF/product89/ME177-016035.PDF):
  brass M1.6×0.35RH nut,AF3.02–3.20,height1.05–1.30mm.
  [Westfield same-size dimensional table](https://www.westfieldfasteners.co.uk/Standards/Nut_Hex_M.html)
  supplies a minimum corner span3.41mm crosscheck,not an Aspen lot certificate.

Normalized facts/URLs/date are in `config/pressure_shoe_fastener_v47.json`.
No full restricted PDF is republished. Stock/price/Korean supply,actual thread
classes,proof load,material properties,locking,friction/preload remain NULL.

DESIGN TARGETS,not demonstrated process capability:hex pocketAF3.30±.03mm,
height1.40±.03;shoe.30±.01mm,XY1.6×1.2±.02;axis placement±.05mm.
939interval arithmetic gives total AFclearance.07–.31mm,heightclearance.07–.38mm,
conditional largest-tip edge margin.04mm. The existing nominal.07mmfree-stack
closure equals.2turn/72° at.35mmpitch;this is **NOT a tightening/preload command**.
Actual contact reference,root-constrained compliance and indentation must be
measured. There is no torque-to-force value or demonstrated safety factor.

## Cycle B — actual finite cage and preserved failure940/941

Only ONE secondRoot changes. Replace D1headed proxy with a nominal major-
diameter M1.6headless adjuster envelope,flatpoint/hexsocket and captive nut.
Three saved new STLs are closed/positive/single-body;full assembly289parts.
Skin/Rail/.30mmshoe/wire/otherRoots unchanged. Nut cage side entry,top/bottom
walls and flats are finite solids. Local floor/roof design dimensions.43/.55mm
are NOT global minimum wall or load capacity.

940FAIL:old lowerlip retained D1.1passage,actual adjuster intersection.1241548mm³.
941physically machines D1.7through the whole lip+cage,not a collision exclusion:
no static solid intersections,5.809s. Old lip edge ligament nominal.15mm is
**not strength-qualified**. New cavity AF3.3,height1.4;nut z1.3..2.6mm.

Purchased thread designations are specified,but assembly meshes deliberately
use envelope cylinder/clear bore,NOT fabricated helical flanks or certified
6g/6H fit. Manufacturer thread tolerances/gauging are still required. Cosmetic
helices would not establish fit or proof load. No new force/mass/Native joint
is adopted;A2/brass are catalog candidates,not measured SOFA material inputs.

## Cycle C — service geometry,not visual assembly approval

- 942software FAIL:world-coordinate nut-sweep Qhull produces23faces,notwatertight;
  Manifold rejects it. POSTMORTEM retained. Root-local declared geometry gives
  a valid20face sweep. No faces deleted,epsilon or artificial thickness added.
- 946valid Root-local sweep finds **actual RootClamp overlap1.61735mm³** at6mm
  nut withdrawal. Screw/tool/pad envelopes and sampled assembly positions clear.
- 947interval-report serialization fails on numpybool;logs preserved. 949casts
  result scalars to Python types without changing the geometry arithmetic.
- 949actual nut/RootClamp bounds plus declared cage mouth give nominal fully-
  removed nut travel window4.4475208..5.1524792mm. Midpoint4.8mm has.352479mm
  endpoint AABB margins;NOT actual tolerance/continuous clearance certification.
- 948tests4.8mm:continuous conservative screw/alllength/tool/nut/pad envelopes
  clear,then7part diagonal assembly removal clear at7sampledpositions.5.183s.
  Nut at3° has clearance,5°/10°/30°hits cage,60°symmetry fits. This is a geometric
  rotation barrier with backlash,NOT selflocking/zero-rotation/proof torque.

Service sequence:unload actuator and unthreadwire;unscrewadjuster;retain and
slide nut4.8mmRootward;slide shoe4mminboard;then remove7partkeeper/Support
subassembly diagonally(outboard+longitudinal). Real hands/thread turns,tool
handle,retention during inversion and damaged/worn parts are unqualified.

943actual.45mm secondchannel envelope vs289solids:obstacleclear18.770s;
wheelproximities recorded,not contact-law PASS. 944actualv47reviewpack includes
10STLs,289partrecipe/BOM,parameters,sections and DESIGN explodedrecipe.
945actual Rootstation12mmsection visually inspected. FreeCAD/OCP/OCC/cadquery
imports and FreeCADCmd/freecadcmd unavailable in checked environment;noSTEP.
135softwaretestsPASS950(1.965stestbody/2.511sguard),NOT productqualification.

## Next cycle / qualification boundary

Continue with a separately identified remainingRoot placement/interface screen,
not blindly cloning6units into an approved assembly. Each actual pair and wire
route must be checked. Physical clamp/preload/slip/filmindentation/threadfit/
fatigue require actual parts and instruments;measurements remain NOTMEASURED.
No new50g/100g/Lift/time/mesh/variable-stiffness/fabrication PASS. No unchanged
Native895/dt/alarm repeat. Manufacturing design can progress independently.

Read-only resume:
```
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/product_captive_service948/summary.json
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/product_nut_window949/summary.json
```
Reproduce only with a NEW hypothesis/tag:
```
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/pressure_captive_nut.py --tag UNIQUE --through-passage
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/pressure_nut_service.py --tag UNIQUE_SERVICE --case product_captive_nut941 --local-envelopes --nut-travel 4.8
```
All actual scripts/input hashes/process commands/runtime/results are retained.
CAD pack `meshes/` and `drawings/b3_captive_nut_v47/`;no fabrication order.
