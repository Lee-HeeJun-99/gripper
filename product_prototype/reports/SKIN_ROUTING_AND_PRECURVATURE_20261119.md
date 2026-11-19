# Native distributed routing and manufactured precurvature — 2026-11-19

Start:da71cdc. Functional commits:8f1cbc7,1de4288. No SDK or legacy solver
changes,no remote push. This is product trial259 onward,not the legacy campaign
number sequence. Every physical trial has immutable launch_command.json,scene.scn,
geometry_generator.py,source/,config.json,SDK/runner/binary hashes and guarded logs.
Research material/friction/hardware assumptions are NOT measured PET/TPU properties.

## Physics and design hypotheses

Earlier247/256 use depth75mm:late Skin normals push the object down. More normal
force cannot make those measured friction cones support upward load. This work
changes deformation/moment distribution,not a repeated constant-offset/stroke sweep.
The matched single-finger and new free-body comparisons use depth65mm;therefore
their difference from247 is NOT attributable solely to routing.

Common:100mm material length,W24→12mm,root radius50mm,root angle14deg,3x120deg,
Skin.1mm,rails.5mm,E250MPa,nu.3,mu.3,core1g/finger,12 bracket frames10mg each,
wire radius.25mm,guide OD3mm/length2mm,conservative native guide sphere radius
sqrt(1.5²+1²)=1.802776mm. Two independent4mm CableConstraint commands,NOT an
equalizer. Stock EulerImplicitSolver/SparseLDL/BlockGaussSeidelConstraintSolver,
MinProximityIntersection(useSphereTriangle),Rigid3 sphere collision,stock mapping.
All native tests reuse unchanged Controller binary33baec3658a718b7bff6f472f6701f6f75c02a70507bbe5a4ea4260fa478e1c2.

Candidate A:normal offset3→9mm along distal60→100mm via cubic smoothstep.
At each station the same route is used by native CableConstraint and CAD sources.
Unit-tension guide moments differ from constant routing by up to5.859833mm*N/N;
independent rotational virtual-work finite differences agree within1.34e-8mm.
This is a moment-distribution change,not a force-field implementation.

Candidate B:manufactured stress-free circular distal reference,20deg over60→100mm.
Geometry-only259 first rejects30deg starting50mm (initial Skin gap−2.200mm);
30deg starting60mm also fails declared.2mm buffer before physics. The20deg/60mm
reference has1.275807mm initial Skin gap and positive element determinants.
For arc coordinate s,start a,k=theta/(L-a),phi=k(s-a):
X=a+sin(phi)/k−z*sin(phi),Z=(1−cos(phi))/k+z*cos(phi).
Width is unchanged. Root straight section and material-node identities are retained.
Native FEM initializes these coordinates as its rest shape;no q prescription is
applied during dynamics.269 zero input four steps leaves q/v exactly at rest0.
This is NOT evidence that a flat PET sheet naturally acquires this shape;manufacturing,
residual stress and bond assumptions require physical validation.

Candidate C combines A/B only AFTER261/262 independent runs. Its separate sector
variant uses distal8mm (not9) to satisfy finite guide/object initial clearance.
It is NOT a pure one-factor superiority test against A/B.

Native flat reference and mass1g are unchanged in A. B/C tetra volume410.098113mm³
versus410mm³ flat (+.02393%);nominal section/arc length stay the same. This discrete
curved reference is NOT an exactly equal-volume comparison. Constant prescribed
mass also implies a slightly different effective density. No stiffness/friction
was increased to manufacture a successful outcome.

## Completed single-finger fixed-R30 comparison

All800steps,dt.0025s,2s,zero gravity,closing0–.5/hold.5–1/release1–1.5/recovery1.5–2.
Fixed sphere reactions use unprojected mapped collision-state J^Tlambda,not the
projected fixed body's zero reaction. Row-source partition checks agree0. Fixed
reaction is NOT free-body momentum or holding certification.

|Trial|Mechanism|Runtime s|Hold Skin Fz N|Hold cable max error mm|Disposition|
|---|---|---:|---:|---:|---|
|263|constant baseline|16.570|.086128|1.896932|direct Skin,but nonlinear cable FAIL|
|261|A distal|18.674|.092713|2.81e-7|Skin only;121/121 hold frames upward cone|
|262|B precurve|31.118|.196204|1.065602|better direction,but cable FAIL|
|268|C original hybrid|32.390|.154486|1.85e-7|Skin only in single finger;assembly fails below|
|285|A2 sector route|18.350|.127085|4.37e-8|Skin only,121/121 upward frames|
|286|B2 sector precurve|30.155|.207494|1.665979|cable FAIL;not selected|
|292|C2 sector hybrid|12.777|0 in hold|.618763|Guide Fz.285482N;reject Skin grasp candidate|

Actual coupled surface gap,tetra determinant ratios,tip chord angle,wire/guide gaps,
force partition,return error and per-station unit-tension moments are preserved in
264/265/266/271/289/290/296. No inverted element samples in those runs. Full
self-intersection,root reaction,pressure,contact area and whole energy remainNULL.
Minimum dynamic finite-wire/guide-to-object gaps for A2 single:3.949/2.396mm.
Tip recovery is a fixed-object/zero-gravity result,not a free grasp recovery claim.

## Assembly failure discovered and corrected — do not promote267

Original A/B/C outward lateral24mm paths cross neighbouring guide collision proxies
when assembled at120deg. Actual-scene audit287 finds initial proxy gaps−3.359378mm
for267/283 and−2.663441mm for275. Thus267's experimental support-free holding
observation (Skin.4905N,Guide0,slip.5323mm) is retained but cannot qualify an
initially overlapping product. Whole-surface penetration during267 reaches−2.112686mm.
283 finished1600steps in423.024s but is likewise unqualified.275 reached the480s
policy timeout before2s;its partial CSV is NOT completion or holding evidence.
No old result/Raw was overwritten. The new guard293 rejects this overlap BEFORE
launching SOFA;the initial geometry check now includes neighbouring guide spheres.
294 was an analysis import error,corrected in295/297/311,not a physics failure.

A2/B2 route each physical guide within its120deg sector,using unchanged finite
hardware radius and positive margin m=.5mm. For radial position r and width w:
outboard(s)=min(24,sqrt(3)*r−2*(guide_radius+m)−w/2).
It is a distributed3D route/physical support-arm change,not collision deactivation
or a uniform offset sweep. Initial inter-finger proxy gap becomes1mm. It changes
normal and lateral moment distribution,so A1→A2 is not a pure one-variable contrast.
C with9mm distal offset cannot meet both this sector and initial object clearance;
8mm gives1.529mm guide/object initial gap,then actual292 becomes Guide-supported.
That is a measured rejection,not justification to shrink/delete hardware collision.

## A2 actual free-R30/50g gravity test291

Completed800steps/2s in278.824s,zero native ERROR/missing intersectors. Initial Skin
gap2.689863mm,guide proxy inter-finger gap1mm. Identical physical support withdrawal
protocol1–1.5s,support40mm downward;closing0–.5,hold through2,release starts2.
Full3-finger release/recovery was NOT run by stopping at2s.

301 actual Contact pair→response→constraint row partition error2.17e-19Ns.
302 meets the predeclared experimental functional hold protocol1.6–2s:

- downward slip.053164mm≤2mm;maximum speed.00045845mm/s≤5mm/s;
- minimum support gap40.146836mm≥5mm;support reaction0N;
- Skin Fz.4904999994N,minimum Skin weight fraction.9999999988;
- Guide/Rail/object support0;Skin resultant moment is separately inventoried314;
- native gravity9.81m/s²/object.05kg actually integrated,not prescribed object pose.

303 active Skin normal_z stays.484456..484479;upward Coulomb coefficient
.746901..746919 throughout the hold window,not one favourable frame.
312 body/collision q/v/time differences0 over800states at STRICT1e-12.
313 linear/angular momentum residual2.17e-19Ns/4.24e-22Nms inventory only.
314 measures Skin normal Fz.329559N plus tangential Fz.160941N;maximum hold
resultant contact moment3.82e-12Nm. Scalar cone excess2.71e-20Ns is recorded,
not silently clamped or a maximum-load/6DOF wrench-closure certification.

IMPORTANT:This is functional Skin-load holding evidence,NOT whole-product PASS.
304 strict gap/active-response consistency FAIL:maximum active nearest gap
.200000665mm vs declared.2mm. Global minimum actual Skin gap.197219mm is positive,
but that does not waive the failed buffer/proximity condition.305 sampled guide
proxy inter-finger gap.199463mm is positive but guide/guide proximity interactions
and missing full support-arm/wire/palm/self-collision prevent Gate2 certification.
Cable transient shortening error reaches~.0384mm despite tiny settled error.
309 proximity geometry does NOT show broad pressure-bearing wrapping. Do not
equate one closest triangle or row count with contact area or wrapping coverage.

## Numerical evidence and bounded next work

261/270/272 are SAME binary,geometry,input/initial state with800/1600/3200steps.
Full2s common-time/all-pair assessment276 FAIL at unchanged.1% gate,no floors.
Worst relative short-length error200% includes roundoff-scale values,but meaningful
motion differences also exist (maximum aggregate nodal-motion difference.942133mm).
Pre-hold.6–.9 comparisons also FAIL;do not dismiss this as only zero recovery values.
Native residual261 reaches2.66e-6 and245 iteration-limited frames. Stock NNCG284
uses unchanged physics and no custom solver:max residual3.12e-8,no iteration-limited
frames,17.169s vs18.674s. This is NOT a nonlinear/time/whole-contact certification.
300 analysis regression recreates historical243 errors.csv byte-for-byte:
SHA2566f774bbf3597942a45c4515d73f3778ccd54e5e90f8c467050c16b8fa5cdf491.

A2 full2s half/quarter forecasts557.65/1115.30s exceed480s and are NOT RUN.
Short.6s half306/quarter307 forecasts167.29/334.59s fit policy and are separate
contact-entry convergence experiments,NOT hold-window refinement. Actual final
assessment and matched constant-route free-body308 are appended in checkpoint.
Never treat an in-progress or timed-out process as a completed horizon.
Policy timeout is not operating-system memory exhaustion;peak RSS NOT MEASURED.

## CAD and reproducibility

v7 references preserve the rejected assembled paths. v8 contains sector-routed
Skin/rails,guide-envelope reference assembly,STL,SVG,BOM and exact shared config
bytes of285/286/292. Candidate cores are watertight. Old flat FreeCAD/SCAD exporters
now reject curved/profiled configurations rather than silently emitting mismatched
flat solids. FreeCAD/OCC/CadQuery are unavailable in the Python environment;
STEP/kernel assembly NOT GENERATED. Support solids,hardware stiffness,wire bend
radius,fasteners,motor,manufactured rest curvature/tolerances remainunverified.
No PHYSICAL FABRICATION READY designation.

Actual accepted-state comparison figures:results/mechanism_figures299/ and
results/sector_three_actual305/. Each has source/binary/config/dt metadata;no
displacement amplification,concept pose or fabricated pressure distribution.

Exact executed commands are in each results/<case>/launch_command.json and
process/command.json;do not reuse output tags. Reusable build:
product_prototype/cad/build_response_public_187/libReGripProductSequence.so.

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY product_prototype/sofa/mechanism_tests.py --tag NEXT_UNIQUE_MATH
$PY product_prototype/sofa/response_load_assess.py --case distal_sector_three291 --tag NEXT_UNIQUE_LOAD
$PY product_prototype/sofa/response_wrench_assess.py --case distal_sector_three291 --tag NEXT_UNIQUE_WRENCH
```

No100g,Lift,12-Wrench,Optuna or final design selection until required physical
and wrapping gates pass. Mechanical equalizer and measured material validation
remain separate unfinished work. This checkpoint is not project completion.
