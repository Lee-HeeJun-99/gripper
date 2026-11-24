# Footprint-preserving proximal backing — 2026-11-24

Baseline: immutable `b3_railback_grasp1001298`, source starting HEAD b10394e.
Motivation: accepted-state diagnostic1360 placed most .6–1.2s projected tip
rotation loss in0–70mm; width-redistribution1362 rejected12 guide feet. Neither
result proves a unique failure cause. One new finite candidate adds0.125mm
behind BOTH2mm-wide rails on0–70mm, preserving all old nodes and108 guide feet.
No force, friction, material modulus, guide offset or terminal-position sweep.

## Geometry and assumptions

1364:120newnodes/168tets per finger,35mm³ added material,85.354939mg/finger.
E250MPa/nu.3 copied old assumptions; density2438.712547kg/m³ derives old1g
and actual core volume, NOT a measured selected material. Added volume/mass:
NOT equal-material efficiency. Perfect bond; outer root nodes0–5mm fixed to
represent the same clamped material interval. Actual clamp/preload/adhesion,
manufacturing and dynamic hardware clearance remain unqualified.

56 bonded interface triangles cancel exactly; remaining old exterior retained
in one actual exterior union, no guide collision removed. Initial sphere gap
4.53484mm, modeled-guide gap22.28194mm, wire AABB capsule bound14.40390mm.
1368 audit: inverse declared collision/observer edits give identical original
physical XML; added-to-added AABB bounds43.763/43.763/48.511mm. This is initial
geometry/XML scope, NOT full dynamic interference or hardware verification.

## Actual Native evidence

-1365: fixed-parent linear mapped coupon, independent CST+BE reference;
 q error8.67e-19m,v2.65e-15m/s. PASS_LINEAR_MAPPED_COUPON_ONLY.
-1366: .05s startup completed, but extra material retained default zero local
 Rayleigh damping. Preserved unchanged; NOT a matched-damping comparison.
 Producer then copies baseline mass1/s and stiffness.0001s into added material.
-1367: corrected .05s/20outputs,1.007s runtime; positive saved elements,bond0.
-1369: .6s/240outputs per body,31.937s runtime; original minimum volume ratio
 .985639, added.996443,bond0,noSOFAERROR. BOUNDED_EXECUTION_ONLY.
-1371: .6s object speed1.94987mm/s; compositeFz.702236N and Support.278784N
 versus weight.981N. Guide0. Max solver iterations1001. Linear momentum
 inventory residual4.34e-19Ns, not convergence/energy certification.

Composite collision surface includes Skin/Rail/reinforcement. Collision-pair
force alone does NOT isolate bare Skin. No contact area/pressure invented.
Holding1.6–2s NOT MEASURED by these startup/entry cases. Old time/mesh FAILs
remain FAIL, actual hardware/jamming NOT MEASURED. Added reinforcement is not
layer jamming or measured variable stiffness.

## Mid-response result and decision

1370:1.2s/480outputs,63.464s runtime;minimum original ratio.985613,
reinforcement.994567,bond0,noSOFAERROR.1372endpoint compositeFz.702336N,
Support.177712N,speed138.0218mm/s,maxsolveriterations1001.1373actual first
finger tip angle at1.2s51.188585° versus baseline52.083700°;proximal turn
−8.321728° versus−7.871305°. Thus this ONE candidate fails its intended
early proximal shape-retention improvement. Added material did not establish
a useful Native stiffness improvement under this coupled transient. This does
not prove every reinforcement impossible or identify a unique solver cause.
Do NOT proceed to expensive full2s Holding solely to count another trial.
FullHolding window remains NOT MEASURED,not retroactively FAIL. Next compare
allthree actual fingers and contact-force changes before anothermechanical
candidate;material provenance needed before claiming bareSkin contribution.

17 contact-layer software regression tests pass,including3new reinforcement
checks. Software checks are not time/mesh/physics certification.

## Follow-on actual provenance and all-finger comparison

After featured80265b,actually executed frozen1242 read-only observer1374 on
the1.2s candidate,63.210s runtime. All9physical journals exactly equal the
original480outputs.1377 uniquely joins74normalrows at previous1.195/1.1975s.
1378 maps9active rows:all actual Skin at100mm,none added reinforcement;
no unmatched activepoints. This is sampled normal-row provenance,not whole
tangential force partition/contact area/distributed wrapping.

1375 analysis incorrectly asserted allthree tipangles mustworsen,failedbefore
measurementserialization. Failure retained; source snapshot NOTCAPTURED before
patch. Corrected1376 writes actual data without assumed outcome:1.2s tipangle
changes candidate-minusbaseline −.895115,+.799535,−1.287919degrees. Hence
nonuniform coupled response,NOT universal stiffening or universal worsening.
Firstfinger observation remains valid;candidate is not selected as a consistent
shape-retention improvement. No extraNative Holding run performed.

Next READY:independent fixed-boundary small-load composite-bending comparison
of old and addedbacking,using exactsame baselinefootprint/root and material.
This isolates whether discrete coupledFEM/mapping actually gains intended
bendingstiffness BEFORE interpreting staticsectionI as dynamicimprovement.
No force/material/thickness sweep. Full100gHolding/Lift/time/meshremainblocked.

## Reproduction (never reuse an existing result tag)

Use `/home/ubuntu/miniconda3/envs/robot_ws/bin/python` and repo root:

```bash
python product_prototype/sofa/proximal_reinforcement_geometry.py --tag NEW_GEOMETRY
python product_prototype/sofa/contact_layer_coupon.py --reinforcement --tag NEW_COUPON
python product_prototype/sofa/b3_contact_layer_native.py --reinforcement --exterior-union --tag NEW_PILOT
python product_prototype/sofa/b3_contact_layer_native.py --reinforcement --exterior-union --duration 1.2 --pilot proximal_reinforcement_damped_pilot1367 --tag NEW_MID
python product_prototype/sofa/proximal_reinforcement_audit.py --tag NEW_AUDIT
python -m unittest discover -s product_prototype/sofa -p test_contact_layer.py
```

Actual commands, source/binary/scene/geometry hashes, child limits4GiB/30–420s
and process artifacts are in each case preflight/command/process files. Raw
detector.csv stays local and ignored. Source snapshots retain each producer.
Contact work/whole energy/root reaction are NOT MEASURED here.
