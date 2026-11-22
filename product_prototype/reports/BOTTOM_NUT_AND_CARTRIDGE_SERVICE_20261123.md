# Bottom nut and cartridge service continuation — 2026-11-23

Started clean at f74631e. Existing1005–1017 were inspected,not rerun. This is
manufacturing/service CAD research,not a new Native SOFA/holding qualification.

## Distinct architecture: bottom-loaded hex pocket

1018 config/distal_keeper_v54.json reuses the catalog dimensions fromv52.
No new motor/material/fastener selection. Side slot is disabled; hex recess
extends through the underside to−5.5mm while retaining upper bearing roof
at−2.55mm. Outer body,bolt locations,wire passage and supplier inputs unchanged.
One f0/c0/s5 station only;294candidateinstances. Six saved closed single-body
STLs. Static REVIEW retains same3mating artifacts as1005;not exact clearance.
No actual hardware removed from the operating assembly.

1019: two continuous convex nut envelopes along local[0,0,−4]mm are clear,
as are14actual nut positions. Both1.5AF key-shank envelopes clear. Screw
withdrawal envelopes still contain original start-bearing artifacts;entire
service/strength/thread fit NOT approved. An open-bottom nut is NOT captive
when the screw is absent;temporary bench retention/assembly fixture required.
No arbitrary friction/preload/torque assigned.

## Separate unloaded cartridge service diagnostic

1020 explicit cut-set:51moving parts,241fixed parts,2retaining bolts assumed
removed. Actual guide hardware,neighbor fingers,Root bridges/turns,motor and
Palm remain present. Moving group follows actual carrier longitudinal axis,
not an invented object displacement. Eight positions0/0.1/0.5/1/2/5/10/20mm
have no CSG hit. Wire disconnection,Root pressure clamp/bond separation and
actual screw access NOT validated,so physical service remains UNQUALIFIED.

1022 conservative continuous hulls flag two clamp bolts versus f0_mount,
~0.086097mm³ each. Concave hull hit is unresolved,not an actual collision.
1024 refines only these pairs using existing per-triangle sweep tool:
no initial or swept positive-volume hit,839CSG tests;185numerical nonvolume
prisms remain unresolved(90/95). No exact/no-touch/whole-path clearance PASS.
Do not begin another large proof project solely to relabel this service screen.

1023 asks whether cover service geometry improves AFTER the declared20mm
cartridge translation. Six nonzero cover positions0.1/0.5/1/2/4/8mm clear;
zero position retains1.78e−5mm³split-plane artifact. This contrasts with the
in-place neighbor collision1006;does not approve cartridge disconnection,
continuous cover extraction or an operating gripper model with hardware omitted.

## Actual drawings and nut-bearing reference

1021 meshes/distal_keeper_bottom_v54 contains six byte-identical STL copies
and part CSV. drawings/distal_keeper_bottom_v54 contains saved-STL sections
Y0/Y3.5mm(PNG visually inspected). NOT full Assembly STEP/released drawing.
Pack exporter now labels/hashes the actual source case and configuration.

1026 actual Support/hex-pocket samples,2nuts × AF3.02/3.2 ×6angles:
AF3.2 is free at0/3degrees,obstructed at5degrees and above;AF3.02 is free
through10degrees,obstructed at15/30degrees. These are geometric sampled stops,
not exact backlash,thread locking,proof torque or preload capacity.
Nominal unloaded nut-to-roof gap0.05mm;closed underhead-to-roof grip3.75mm;
max nominal nut height1.3mm gives nominal tip projection0.95mm. The raw field
`nominal_full_engagement_length_mm` means assumed axial nut height ONLY,
NOT measured complete thread engagement. Chamfer/runout/length tolerance unknown.

## Remaining Gates and next distinct work

Native time/contact/mesh FAILs,100g/Lift,actual joints/materials and STEP remain
open. No new SOFA model adopted. Motor1004 remains BLOCKED on dimensioned horn
interface;official XL330 eManual download links still resolve to a landing page
in browser extraction,not a newly validated drawing. No guessed hole pattern.

NEXT: explicit Root clamp/bond disconnect sequence and finite temporary nut
retention/bench fixture. Physical joint pullout/preload needs specimens. Do not
rerun failed side-slot/cover-slope/dt/alarm studies without a new hypothesis.

Reproduce only with NEW tags:
```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/distal_keeper.py --tag UNIQUE_BOTTOM --config distal_keeper_v54.json
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/distal_keeper_service.py --tag UNIQUE_BOTTOM_SERVICE --case product_distal_bottom1018 --fasteners-only --nut-samples
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/distal_cartridge_service.py --tag UNIQUE_CARTRIDGE --continuous-envelope
```
Each bounded child uses4GiB/420s and preserves command/source hashes/runtime.
CAD Python process:SOFA SDK/binary NOT USED. All physical measurements NULL.
No remote Push,SDK edit,old Raw overwrite or after-session automatic execution.
1027:185softwaretestsPASS,7.158s unittestbody;not physical productqualification.
The [official XL330 reference](https://emanual.robotis.com/docs/en/dxl/x/xl330-m288/)
links PDF/STP downloads;the accessed download landing pages were not dimension
sheets,so no new motor interface geometry was asserted.

## Continued after feature482568f: finite temporary assembly tool

1028 config/distal_nut_loader_v55.json and actual two positional STL copies
of ONE hollow loader. Design OD2.9/ID1.9mm tip,16mmshaft,D6×6mmgrip.
Material,tolerance,hand force and strength NULL;not an operating product part.
Eight nut+tool positions per bolt from−4mm to+0.05mm. All16tool positions
clear retained hardware;all14nut positions up to zero are clear. At+0.05mm
nominal roof closure,small nut/roof CSG bearing artifacts remain REVIEW
(4.40e−6/2.80e−6mm³). No contact faces discarded or force imposed.
Nominal final screw clears hollow tool in both positions;not the complete
screw insertion or purchased tool/hand clearance qualification.

Simultaneous two-tool grips overlap24.354751mm³. Therefore retain predefined
ONE_LOADER_AT_A_TIME procedure:temporarily press/thread one nut,withdraw tool,
then service the second. Actual thread engagement/preload and temporary retention
must be physically verified;no claim the proposed sequence already works.
This implements the previously missing finite retention-tool candidate rather
than pretending the open-bottom nut is captive. Raw/STLs under
results/product_distal_nut_loader1028;not a new STEP assembly.

Next Root clamp/bond disconnect remains unqualified;do not present the
cartridge-out workaround as an approved physical sequence. No new Native trial.
Reproduce a new geometry study:
```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/distal_nut_loader.py --tag UNIQUE_NUT_LOADER
```
1029:188softwaretestsPASS,5.284sbody. Actual STL/SVG exporter whitespace is
preserved as generated;it is not a CAD validity or physics test. Source-only
diff whitespace check clean. Old manifests/Raw/FAILs unchanged;no newSOFArun.
