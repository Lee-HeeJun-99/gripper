## Latest Skin-contact continuation — 2026-11-19

Source commits fbc9754,0ec92f0; details: product_prototype/reports/SKIN_CONTACT_CONTINUATION_20261119.md.
Trials147–175 use unique Raw paths; legacy and earlier FAILs unchanged.

-150/152: first finger impulse1.07s coincides with−.214888mm cable error.
 Assembled J matches previous geometry (~1.25e-16),not current geometry;
 reported linear error3.33e-9 does not certify geometric shortening.
-Backside guide149/151 (normal−3mm,unchanged hardware size) fails:no finger load,
 object follows support40mm. This routing is not selected.
-Outboard4 candidate155 initially meets functional holding and child-J row-load
 criteria, but these are NOT physical Skin holding. Geometry168 FAIL:
 Skin gap>=3.394mm despite active row influence;child/FEM coordinates match0.
 Detector173 confirms object–GUIDE pairs and NO object–Skin pairs through.4s.
 Child Jacobian influence is NOT direct contact provenance;169 is not grasp PASS.
-Read-only mapping logger171 and native detector174 give EXACT state equality
 (STRICT1e-12) over their respective2s/.4s scopes. Split-vs-unsplit172 FAIL:
 contact partition changes dynamics and is not a passive observer substitution.
-Base/Half/Quarter155/162/163 all completed2s;all-pair/all-common-time167 FAIL at
 unchanged.1% gate. No100g/Lift or final CAD selection is authorized by these results.
-Minimal Rigid3/DiagonalMass158 FAILs factory/state/topology initialization;
 not proof the entire SOFA capability is unsupported. Full bridge remains BLOCKED.
-CADv5 retained;STEP/assembly kernel/moving hardware/wire swept clearance,
 full energy/contact area/pressure remain NOT QUALIFIED/NOT MEASURED.

Next:bind actual Contact collision-model pair and response Constraint row identity,
 not mechanical-J influence. Use public detector provenance first,then eliminate
 Guide-first contact without disabling hardware collision. No custom solver rewrite.
Exact commands/Raw/Build identities are in the new detailed report.
All launched physics children completed;no automatic continuation is promised.


# Native Cable coupling and holding continuation

Start HEAD cfffbbf;branch development/regrip-autonomous-research unchanged.
Functional commits:3f600b7,af356fb,e29719f,956d6c3. New work stays in
product_prototype/. No legacy FEM/contact/Gauss solver redevelopment or SDK modification.
Results below are **product trials**,not identically numbered legacy campaigns.

## 1. Same-FEM cable isolation

All cases use E250MPa,nu.3,100mm finger,410mm³ core,1g/FEM finger,
same root clamp and C2 8mm command. All material inputs remain assumptions.
Surface guides are1mm inward from the edge,normal0.1mm;outboard guides14mm
beyond the edge,normal3mm. One physical cable is removed in single-cable cases;
its second logger link intentionally aliases the first constraint,not a second actuator.

|Trial|Physical configuration|Actual shortening at1s,mm|
|---|---|---|
|051|single,outboard|4.450715|
|052|single,surface|8.000000|
|053|paired,surface|8.000000/8.000000|
|054|paired,outboard|5.373844/5.807751|
|089|single,normal3 only,lateral inset1|8.000000|
|090|single,lateral14 only,normal0.1|2.624643|

Thus paired-cable interference is not the sole cause. The extra089/090 comparisons
separate the normal and lateral changes;the large lateral extrapolation is critical
in this tested geometry. This is not a claim that every exterior mapping always fails.

055/059/064 independently reconstruct the native mapped positions from rest tetrahedra:
max error8.88e-16m,weights−29..37,row L1 amplification73.
Native Cable Jacobian equals the exact **previous accepted-state** path gradient:
error0. Parent virtual-work pullback error7.11e-15;independent length-gradient FD
error1.28e-9. Mapping arithmetic itself is consistent in this test.

At constant command,the accepted FEM alternates between two states:
one-step motion norm4.1601mm,two-step motion norm<=1.04e-7mm after.8s.
The final-state path gradient differs from the assembled previous-state gradient
by up to.96646 per component,while the linear constraint residual is tiny.
Therefore small linear solver residual is not proof of nonlinear path satisfaction.
The read-only audit changed q/v/guide states by exactly0:STRICT1e-12 purity PASS.

056/057 halve/quarter dt for the same1s physical path:shortening improves to
4.757538/5.417416mm but still fails the8mm command. No tolerance was relaxed.
This motivated **removing unrealistic massless exterior affine-guide mechanics**,
not replacing SOFA's solver or pretending that dt refinement alone fixed it.

## 2. Native mechanism candidates and rejection

- Surface-only guides track well at Hold but bend outward in the tested configuration;
  fixed R20 gap stays>25mm. Accurate control is not useful wrapping.
- Bounded rail-back guides reverse the observed bending direction but have low
  eccentricity. Wires centred exactly on a rail surface are not fabrication-ready.
- 10° root tilt permits actual R30 contact with wire clearance about1.85mm.
  The15° trial071 was rejected for initial penetration before SOFA execution.
- 100g holding trials074/077/078 fail after support withdrawal. Changing root angle
  or stroke alone did not solve it. Their failures are preserved.
- Bilateral rigid guide attachment candidates082–091 were not qualified:
  factory/ordering failure082 was corrected separately;later runs completed but
  constraint residuals stayed large. NNCG/global assembly did not certify these joints.

## 3. Stock rigidification rather than exterior affine points

An installed SOFA rigidification example was inspected. The new optional model uses
RigidMapping + SubsetMultiMapping,not a custom force law/solver:

-12 rigid guide frames/finger,three disjoint noncollinear FEM attachment nodes/frame;
-216 flexible nodes plus36 rigidified nodes reconstruct the original252-node FEM;
-full Skin/Rail mass and FEM remain on the mapped full body;root fixture moves to
 the free subset with the same physical nodes;
-single native mixed-system EulerImplicitSolver/SparseLDL and native constraint solver;
-hardware mass10mg/frame and normalized isotropic inertia1e-6m² are **assumed**;
 core mass1g is retained;additional hardware mass.12g/finger is not hidden;
-guide collision proxy encloses an OD3mm,L2mm eyelet by radius sqrt(1.5²+1²)mm.
 Supports/arms/wire swept collision are not fully represented by these spheres.

093/096 noncontact trial:joint coordinate error1.39e-17m,quaternion normalization
error3.55e-15,Hold shortening error<=9.88e-10mm. About69mm tip motion is observed.
This is a different mechanical design with locally rigid attachments and additional
mass,not a matched-material superiority result over the original massless model.

094/095/099/100 fixed-sphere contact and full closing/release were actually executed.
Some conditions contact the **guide hardware before the Skin**. The new observer
separates surface rows,hardware-only rows,and support rows using actual native
Jacobians and multipliers. Projected fixed-body zero is not interpreted as zero reaction.

The global model initially used zero Rayleigh damping explicitly. The optional
component-film-damping variant restores the original input assumptions **on Film only**:
Mass rayleighMass=1/s,FEM rayleighStiffness=1e-4s;object/hardware stay undamped.
This is an explicit damping-model comparison,not measured PET loss or a numerical fix.

## 4. Predeclared holding functionality,not final grasp certification

Each withdrawal trial writes holding_protocol.json **before execution**:
gravity9.81m/s²,window1.6–2.0s,reference1s,downward slip<=2mm,speed<=5mm/s,
support surface gap>=5mm,support resultant<=1e-5N,and actual-row partition consistency.
The criterion limits downward slip,not upward settling;all translation drift is reported.

100g trials102/103/106/107 fail. Separate50g trials111/112 establish external-support-free
contact but fail the speed/slip criteria. Their failures remain unchanged.

115/117 (R30,50g,depth50mm,component Film damping) satisfies the declared **kinematic**
holding protocol for.4s:support force0,support gap44.12mm,max speed.0184mm/s.
The object rises about3.92mm after the reference pose;this is settling during closing,
**not a palm-driven Lift**. Mean object support.490499N is supplied entirely by
**Guide hardware**,not Skin. Thus this is only a conditional hardware-contact holding
observation,not proof of film wrapping,100g capacity,or ReGrip design superiority.

118/119 expose further limits:sampled finite-wire gap about+.2805mm,but contact-transition
cable error reaches.3463mm with positive tension and BlockGS reaches1000 iterations.
120/122 NNCG reduces reported linear error and iteration count,but not this nonlinear
path error. Do not turn a small linear residual into a whole-physics PASS.

121 uses a fixed101-knot piecewise-linear approximation of a quintic support withdrawal.
It is **not exactly C2** and is a changed physical input. Holding is again observed,
but the transient cable error remains about.2149mm. Lift is withheld pending qualification.

## 5. Native fixture clock correction

Old trials show exactly one-step fixture timing offset:LinearMovementProjectiveConstraint
evaluates begin-of-step context,whereas journals are labelled by accepted-end time.
The old.2mm end-clock discrepancy is preserved;the begin-clock error is0.

The optional end-clock-motion adapter stores the desired command in motion_commands.json
and serializes native keyTimes minus dt. It never overwrites accepted positions/velocities.
124/127 verify actual support against the declared end-clock path:component error0m.
The serialized native begin-clock prediction also agrees exactly. Different dt cases
must share the **declared** command hash,not raw shifted XML keyTimes.

129/130 are a bounded same-binary half/quarter dt study through2s,including the hold
window but excluding most release/recovery. Same physics is checked by canonical
scene fingerprints and declared command hashes. All common outputs/all three pairs,
absolute and relative errors,are assessed without an arbitrary small-value floor.
Assessment133 is FAIL at the unchanged0.1% gate. All common times/all three pairs
share binary,physical-scene fingerprint and declared motion hash. Near-zero velocity
relative error reaches199.75%,but substantive object-motion differences also reach
about1.44mm. Hold cable errors base/half/quarter are.21489/.09091/.05674mm.
Matched100g132 fails holding;50g hardware-only success must not be extrapolated.

Public BaseMass initial element matrices140 match the12 guide inputs exactly.
Opt-in query purity versus131 over4 steps gives state difference0 (STRICT1e-12).
Frozen native_rigid_guide_holding_v2 scene replay141 matches all1200 steps exactly:
q/v,guide/object quaternion and support. This is reproducibility,not time accuracy.
146 validates four expected input rejections without claiming any physics test.

Cross-guide bridge136–138 remains BLOCKED: the present native DiagonalMass scene
fails initialization. No SDK patch or fake isotropic substitute was used.
Functional source commit ff21719; experiment-local snapshots remain authoritative.

## 6. CAD and remaining limits

drawings/native_guides_v5 and meshes/native_rigid_guides_v5 use the exact device inputs
of111. The body fixture is R20/50g for that source configuration;115 uses R30/depth50,
with the same device geometry. This distinction is retained in the JSON configurations.
Guide support feet now follow the native three-node attachment pattern. Terminal
eyelets are placed at the actual last cable point,not an offset duplicate anchor.
BOM distinguishes30 intermediate eyelets and6 terminal anchors,plus36 support bodies.

Closed STL volumes remain210/100/100/410mm³. These are not complete hardware mass.
Static CAD input checks do not certify moving support/arm interference,guide strength,
wire bend radius,retention knot,adhesive,or fabrication tolerances. FreeCAD/OpenSCAD/
OCC/OCP/cadquery were unavailable when checked. STEP/kernel assembly is NOT GENERATED.

No complete energy/work certification is claimed. Sampled cable work is explicitly
not stage-consistent work. Root/support work,pressure/contact area remain unmeasured.
Self-collision,full thickness/moving hardware clearance,time/mesh/friction certification,
Skin-dominated holding,Lift,and final fabrication readiness remain unfinished.

## Reproduction

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY product_prototype/sofa/cable_matrix.py --tag UNIQUE_SINGLE_OUT --cables 1 --guide outboard
$PY product_prototype/sofa/cable_matrix.py --tag UNIQUE_PAIR_SURFACE --cables 2 --guide surface
$PY product_prototype/sofa/run_native.py --tag UNIQUE_HOLD --guide-location outboard --outboard 14 --stroke 8 --rigid-guides --mapped-guide-joints --global-native-ode --component-film-damping --fingers 3 --object free --radius 30 --object-depth 50 --object-mass .05 --gravity --floor --support-shape sphere --support-gap .4 --withdraw-support --smooth-support --end-clock-motion --intersection LocalMinDistance --constraint-journal
$PY product_prototype/sofa/holding_assess.py --case UNIQUE_HOLD --tag UNIQUE_HOLD_ASSESS
$PY product_prototype/sofa/guide_joint_audit.py --case UNIQUE_HOLD --tag UNIQUE_JOINT_ASSESS
```

Each new directory preserves command,source snapshot/hash,compiled binary identity,
installed SDK,geometry/materials,actual solver,Raw/impulses and process results.
4GiB/480s per child,at most4 long physical children. Peak RSS is not measured by
the historical launcher and is not fabricated;the4GiB address-space cap is not RSS usage.
