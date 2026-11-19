# Finite Guide/Support Native validation — 2026-11-19

Start HEAD:c686881eb8b37e31d06b59808ff86fac62b6d5a5,clean worktree.
Feature commits:fcf0282,ea5794a,9e09cc4,ad88042.
Evidence:evidence_product_finite_v23/manifest.json,linked to v22 and all earlier
immutable evidence. Prior immutable2695files verified,0mismatches;new3356files.
Old Raw,verdicts,SDK and original B3 geometry/checkpoints remain unchanged.

## 1. Priority and physical scope

Continued directly from the unfinished finite hardware/contact-point task.
Reused Native bodies extracted from375 at2.3875s,installed26.06.00,existing
physical journal332 and read-only row observer512. No FEM/contact/ODE solver
was written or replaced. No full Holding campaign was repeated.

Finite eyelet dimensions:OD3mm,ID1.2mm,length2mm,wire diameter0.5mm.
Radii come from the shared B3 configuration;length2mm is the explicit inherited
`generate.py guide()` design value,not a measured stock dimension.
Eyelet axis follows manufactured finger tangent:an explicit new orientation
assumption that enclosing spheres could not validate. Hole geometry is retained.

Native reduced scenes contain two FREE Rigid3 bodies,no film,cable,gravity or
object. Total inherited mass10mg/body and isotropic inertia1e-11kg m2 are NOT
newly calibrated eyelet/support properties. Compound cases keep BOTH eyelet
and support collisions enabled and identify their actual source separately.
Neither these runs nor static CAD geometry are Skin Holding or B3 model approval.

## 2. Actual Native trials and failed direction532–543

24physics children executed using existing4GiB/480s guard,max3concurrently.
532 original Native MinProximityIntersection with finite16-sector surfaces:

- alarm1mm completes4steps in28.424s,but reaches1001iterations with substantial
  residual(e.g0.0127846). Exit0 is NOT solver/clearance certification.
- alarm5mm aborts with `std::bad_alloc`,exit−6 after1.415s. This is an actual
  allocation failure under the4GiB child limit,not a policy-only forecast or
  evidence of host-wide OS exhaustion. Stack includes ConstraintProblem dense
  matrix resizing. Partial journals and failure are preserved.
- The dense contact direction is stopped;no further global alarm/iteration sweep.

Installed `LocalMinDistance` documents native geometric filtering.533 changes
ONLY the intersection component,not the hardware,ODE,friction,mass or tolerance.
All Triangle/Line/Point models stay enabled.16-sector alarm1 drops to at most3rows;
alarm5 to18rows. Children complete~0.206/0.274s. This is a CHANGE of detection
policy and resulting dynamics,NOT an identical-results performance optimization.
Fewer rows/shorter runtime do not prove candidate completeness.

536/542 refine finite contact tessellation32/64;540/541 refine dt at fixed32.
Analytic annulus volume11.87522023mm3;16/32/64 volumes11.57234699/
11.79906268/11.85615329mm3(relative errors2.55046/0.641315/0.160561%).
All meshes closed,winding-consistent with positive triangle areas. This analytic
geometric check is not the B3 FEM mesh Gate.

539 independent edge/triangle crossing tests find68/96strict crossings at the
first two32-sector alarm1 accepted frames. Alarm5 has no crossing detected in
4saved states;containment/swept motion is NOT certified. Analytical separated
and crossing triangles validate the classifier;near-parallel/boundary uncertainty
is explicit rather than cleared with a physical tolerance.

543 ALL-common-output,ALL-pair0.1%time Gate FAIL:alarm5 worst64.6243734%
angular velocity,alarm1 worst96.6319740%.545 contact-mesh1%Gate also FAIL:
alarm5 worst28.1021432% angular impulse. No error floor/interpolation/Gate change.
Alarm1 mesh outputs happen to match because entry remains missed;this is not a
useful contact-accuracy PASS. Aggregate solver errors up to~1e-9 are recorded;
no new residual certification is inferred from completion or iteration counts.

## 3. Native provenance,compound supports and an independent-audit correction

537 removes provenance observers from536 for a strict comparison:actual parent
q/v/impulse error0.550 adds proposed convex support hulls as separate native
collision children,not hidden geometry. Actual support-related rows arise.
552 adds NativePointJournal to read REAL mapped eyelet/support q/v.
555 adds a separate read-only `NativeFeatureRows` observer:actual Detector IDs,
element indices,line endpoint vertex IDs,normal,value,raw deltaT and points.
No constraint/state/force is altered. Checked RTTI public-vector access is used;
unsupported output types reject,not reinterpret memory.

Initial analysis534–551 showed apparent surface-point differences up to~0.097mm;
compound loaded points appeared~0.026mm off a reconstructed surface. These
diagnostic outputs are preserved. They were NOT grounds to change SOFA physics.
553 directly confirmed parent/child mapped API consistency,not a stale-mapping
defect.555 showed the actual Detector points lie on their actual finite edges
to6.72e-18m. Thus the discrepancy required investigating the independent checker.

Installed trimesh4.12.2 `triangles.closest_point` uses fixed `tol.zero=1e-13`
in mixed dot-product classifications. At very small SI triangles this selects
wrong regions.556 wraps the UNCHANGED library by translating each triangle to
its first vertex and nondimensionalizing by its actual maximum edge length,
then returns SI coordinates. No denominator/error floor or tolerance modification.
Degenerate triangles explicitly reject. Analytical vertex/edge/face projections
at m/mm/um scales and translated origins pass. Original direct-library errors
reach7.07e-7m in those references;conditioned errors≤3.47e-18m.
This is an analysis-only correction,NOT a force/contact/integration modification.

557/558 reanalyse the SAME untouched Native Raw with conditioned geometry:

|Measurement|Actual limited-scope result|
|---|---:|
|Mapped-journal/feature observer q/v/impulse difference|0|
|Parent→actual child position max error|1.38778e-17m|
|Parent→actual child velocity max error|6.66134e-16m/s|
|Active J point→ACTUAL previous mapped mesh|4.17981e-18m|
|Compound J point→previous reconstructed part surface|≤1.55401e-17m|
|J point→same response Detector point|≤1.56126e-17m|
|M delta-v→mapped impulse|≤4.78111e-22Ns/Nms|
|Angular ledger closure|≤1.95215e-22Nms|

Actual response provenance distinguishes6active eyelet/2active support body-point
records in550. These are NOT unique physical contact count,area or pressure.
Points match PREVIOUS geometry;free-predictor/accepted geometry distances are
reported separately,not selected to hide discretization. Exact ledger closure
does NOT certify zero internal angular couple or full energy conservation.
Original apparent geometry discrepancies were independent-analysis failures,
not proof of off-surface Native forces. No old verdict/scope/Raw was rewritten.

561/562 extend the NEW compound model's time comparison,not a full B3 run.
5630.1%Gate remains FAIL:alarm5 worst64.6243621%,alarm1 worst96.6319740%.
Neither finite surfaces nor correct provenance solved Native contact-entry time
consistency. Candidate NOT adopted into the complete three-finger model.

## 4. CAD and independent moving-hardware screening

`product_prototype/meshes/finite_eyelet_support_v11/`
`product_prototype/drawings/finite_eyelet_support_v11/`

Created36finite eyelet STL,36proposed support STL,one local eyelet STL,
parametric generator,SCAD part assembly,section SVG,BOM,geometry/config/checks.
Support hull is the earlier3-foot-to-guide CAD proposal,now using the actual
precurve/sector-limited guide route. All36hulls are closed. Intended support/eyelet
bond overlap still requires join/Boolean/material/strength verification.
This is a PARTS candidate,not complete Palm/Motor/Fastener STEP assembly.
Wire/bore radial geometric clearance0.35mm does not certify wire routing/bend radius.

Shared config is byte-identical to375/485. Two actually simulated eyelet centre
and orientation bases match the CAD exactly(error0). New support density/mass,
physical joint,stock guide and fabrication tolerances remain NOT MEASURED.

546/559 replay proposed supports on1200OLD Native485 saved body transforms.
This is NOT a Native simulation of the added hardware. Minimum support–R30 sphere
margin+0.647704578mm;hold minimum+0.800765357mm. Conditioned analysis559 confirms
546 values. A changed hardware model can change dynamics,so this is conditional
screening only,not new dynamic Holding/clearance evidence.

547 fixed-sector sufficient certificate FAILS(min−0.741014mm;hold−0.587807mm).
A sector violation is not a solid intersection.548 therefore implements independent
convex-support SAT with separated/overlapping-box reference tests:
518400pair-frame broad-phase checks,1597narrow checks,no overlap/uncertainty.
Minimum reported separating-axis gap among narrow pairs7.73708mm;it is not a
global Euclidean gap or penetration-depth measurement.
549 support vs oriented BOX enclosing each eyelet(including samefinger/different
guide,excluding own intended bond):1512000broad checks,7704narrow checks;
no overlap/uncertainty;worst narrow separating-axis gap1.55927mm.
Positive envelope separation is sufficient for those saved poses;not swept CCD,
new dynamics,wire/Skin/Palm/within-bond certification. No collision was disabled.

Actual Native mapped compound geometry plot560:
`product_prototype/results/b3_finite_actual_plot560/actual_finite_hardware.png`.
It uses Native child q,not prescribed deformation,frozen-motion prediction,
displacement magnification or relocated objects. Labelled NOT B3/grasp evidence.

## 5. Hardware mass/frame audit564

Partwise normalized volume moments of the same geometry are computed WITHOUT
inventing density. Eyelet COM is18.2533–25.1024mm from its Native mass origin;
support COM is7.6081–10.9368mm away. Actual public Native matrices have research
mass10mg at the frame origin and normalized isotropic rotational inertia1e-6m2.
The current lump is not a calibrated representation of manufactured hardware.
No union COM/inertia is fabricated:part overlap and material density ratio are
unknown;naively summing overlapped solids would double-count material.
Actual density,part mass and physical mass qualification stay NULL/BLOCKED.
Changing COM/inertia will be a NEW physical-model candidate,not a numerical fix.

## 6. Remaining Gates and next priority

- Functional50g Skin Holding/release485/489–491 preserved,not repeated or expanded.
- Finite reduced Native contact/provenance and strict mapped API are verified
  only in their stated scope. Contact entry,time,contact-mesh and wholeenergy
  qualification are NOT achieved. No100g/Lift/optimization approval.
- Next:use564 geometric COM/tensors to define explicit hardware mass/frame
  assumptions,then validate a Native COM-frame/shared-Jacobian mini reference.
  Keep density/mass choices labelled research assumptions until measured/selected.
  Do not silently change inherited lumped mass or reuse old checkpoints.
- Separately isolate Native event/step timing on the verified finite geometry.
  Do not repeat velocity-first/alarm/dt/mesh sweeps or post-set v=0 without a
  new physical/mechanical hypothesis. No custom solver redevelopment.
- Physical mass/material/joins and STEP completion are genuinely blocked by
  absent specifications/kernel,not by an invented OS failure. FreeCADCmd,
  freecadcmd,openscad PATH probes and Python FreeCAD/OCC/OCP/cadquery probes
  were unavailable;known FreeCAD library paths absent. STEP NOT GENERATED.
- Full guide+support3-finger/contact/interference proof still needs NEW Native
  dynamics once reduced Gates justify it. Conditional replay cannot replace it.

## 7. Reproduction/builds/checkpoint

Physical332 and read-only512 frozen hashes remain unchanged.
New build:`product_prototype/cad/build_feature_rows554/libReGripFeatureRows.so`.
SHA256:f2a8ca3a35608b5b62719cbbf6a09dea5f38fa6670fa7b73d603d06ffe597b59.
Compiled source frozen at`product_prototype/results/b3_finite_features555/Observer.cpp`.
SHA256:eb0149022d83fe5b6636a080dfcadaf40204722fdbdb24da8b0990ad6139869b.
Guard:`observer_identity.compiled_feature_rows()`;ldd resolves installed SDK only.
No SDK headers/binaries modified;no remote push. Actual child commands,scenes,
process logs/results,mass and Native journals are preserved per Raw directory.
Source snapshots and library source hash are in v23. Peak RSS is NOT MEASURED;
the existing Native child4GiB limit was enforced. No active physics child remains.

Immediate resume(read-only,no completed physics repetition):

```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_finite_hardware_mass564/summary.json
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/b3_compound_time563/summary.json
```

For justified regression ONLY,use fresh tags(not existing result directories):

```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/finite_guide_coupon.py --tag finite_compound_REPLACE_UNIQUE --intersection local --segments 32 --support --mapped-journal
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/finite_mapped_consistency.py --tag finite_map_REPLACE_UNIQUE
```

The second default command reanalyses552/550,not a newly named physics case;
pass --case/--reference explicitly when comparing NEW runs.
No automatic background continuation after session end is promised.
