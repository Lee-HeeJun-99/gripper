# Rev S → T → U: actual own-material and maximum-wire corrections

2026-11-26. Stage1 manufacturing geometry only; no Native/hardware run.

Rev S matched previous fixed/interFinger motion checks but the independently
extended checker found **66 own flexible Skin/Rail–terminal-front intersections**
(`validation/revS_own_material1`). These old scoped passes are not silently
promoted to own-material clearance. Failure remains preserved.

Actual Rev T removes23.600000mm³ from each of three terminal fronts, at
X49..51/Y±7.3/Z-95..-83. Other289parts retain identical STEP hashes. The
actual original DIN7991 bearing cone endsX48.7, leaving0.3mm to this cut;
nearest bolt bore startsY7.8, leaving0.5mm lateral web. Actual distal5mm
clamp/index surfaces remain. These are geometric statements, NOT allowable
stress or clamp-force certification.

`revT_relief_contract1`: exact rigid-plane circular-arc upper intrusion
R-sqrt(R²-11²)=0.723059mm at60°, R=88/(π/3). Nominal1mm relief leaves
0.276941mm. The producer's earlier0.719mm metadata was an approximate
arc-length projection, not this rigorous rigid-plane bound; original metadata
is preserved, not retro-edited. Actual mesh test is authoritative for sampled
geometry: `revT_own_motion1` **PASS**,292closed positive meshes,31poses
0..60°,0hits, including own actual Skin/Rails and rigid hardware. Not CCD,
FEM deformation or driven force validation.

During manufacturing tolerance review, the independently tested0.52mm maximum
wire interfered with actual R0.28 groove at nominal centreR11.25: drum common
volume0.181514mm³ and Idler0.206751mm³ (`revT_maxwire_fail1`). Nominal0.50
wire was clear. Do not use nominal-only PASS to certify specified diameter
tolerance. Rev U physically enlarges only both U profiles per Finger to
R0.300+0.010/-0 at unchanged majorR11.28, outward-open. Actual groove root
is21.960+0/-0.020, NOT22mm. Minimum21.94 exceeds manufacturer42×0.52=21.84
recommendation by0.10mm. Recommendation is not fatigue or strength evidence.

Commands (from repository root; existing output names are immutable):

```
PYTHONPATH=/tmp/regrip_stage1_ocp /home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/stage1_manufacturing/scripts/terminal_relief_contract.py --case revT_inner_relief --base revS_documented_motor --tag NEW_TAG
PYTHONPATH=/tmp/regrip_stage1_ocp /home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/stage1_manufacturing/scripts/mechanism_motion.py --case revT_inner_relief --tag NEW_TAG
PYTHONPATH=/tmp/regrip_stage1_ocp /home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/stage1_manufacturing/scripts/groove_tolerance_contract.py --case revU_maxwire --tag NEW_TAG
```

Use420s/4GiB child bounds. Actual U maximum-wire BRep PASS and0.52D full
wire/rotor PASS. Length±0.25endpoints also PASS with Drum assembly phase
±1.2732395°, maximum length error2.84e-14mm. No wire stretching is used.
RevV_pocket_blend2 further implements actualR0.35 pocket end blends and a
stepped manufacturer end-envelope (head3.8x3/stem2.8x3). Both are source
bounds, not measured ends. First V trial failed duplicated shared-edge
enumeration, then a unique-edge map fixed the producer in a NEW output tag.

V actual CAD292single valid solids/0bulk overlaps;31pose conservative
retainer translation-box/own-material motion PASS;0.52D wire/rotor PASS;
40key approaches,21nut approaches,16countertool pairs,12rigid service paths
and reserved cassette/whole-wire sector PASS. All scopes are sampled nominal
or declared conservative geometric envelopes, NOT driven contact/FEM/CCD.
Actual split pocket cutter tested78positions with0retained-solid intersection;
max stepped-end common0. A source-listed [NS TOOL MRB230R0.35x4](https://us.ns-tool.com/en/products/detail/78)
provides4mm under-neck reach,0.66neck and0.5cutting-edge length. Reach is
NOT flute length. Taper/shank begin1.9mm outside the unassembled split half;
the tested0.35radius cylinder contains its0.33radius neck. This is geometry
and catalogue sourcing, not machining feeds/chatter/fixture certification.

Matched screw trimming uses ACTUAL measured grip+nut height+0.55; final
exposed tip0.50..0.65 and6g gauge. Analytic possible length6.61..7.09 fits
stockM2x8. Maximum additional positive tip0.07 and negative head0.02 fit
the tested conservative envelopes. The12row inspection template is BLANK,
every hardware entry NOT MEASURED. Do not blindly cut all screws7mm.

Final manufacturing package/checklist work continues; no Stage1 release
is granted by these component results. Latest save via actual git log.
