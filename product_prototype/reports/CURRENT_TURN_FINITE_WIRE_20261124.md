# Actual guide-turn finite wire coupon — 2026-11-24

## Continuation1642–1655: vertex clearance is not surface clearance

Local commits07627fe and454346a preserve preceding cycles. No SDK changes,
no physical/tolerance/force adjustment and no new fullgrasp claim.

| Candidate | Actual Native run | Independent result |
| --- | --- | --- |
| Sector partition1642 | 1200outputs,68.349s | 10negative vertex states, worst6.478343um; FAIL |
| Rounded+partition1648 | 200outputs,16.541s | Correct rounded-solid audit1649:0insidevertices; not facet PASS |
| Rounded+partition1650 | 1200outputs,67.637s | 1652:0insidevertices;1651/1653 actual facet penetration proves FAIL |

1643 fresh172step prefix at first new crossing17.2ms,14.132s; observer q/v/
surface/impulse purity0.1644 independently replays every actual model-pair
dedup at17.2ms, all retained counts match; per-row linear impulse from detected
point separation timeslambda agrees with NativeJtranspose<=1.69407e-21Ns,
row/aggregate impulse error4.23516e-22Ns/Nms. Actualvertex360 near x10.992mm
has prior+2.034567um gap,accepted-.280271um. Sector15 triangle detected,
nextsector16 triangle absent at previous state; remaining edge feature event
is distinct from original4.4ms dropped-detected-facet case.
1647 actual164row reconstruction dFree error2.08709e-18m, NCP9.44346e-8m,
accepted mapping/linearized difference55.271nm. Linear residual is nonzero
here,not the sole demonstrated defect.1645 analysis assertion is preserved:
multiple same-name contact objects expose IDENTICAL shared wire J/state rows.
New analysis deduplicates only exactly identical same-state records; different
state/J/q/freeq at same key still fails closed. No Native rerun for that fix.

1648 producer initially applied the *straight* annulus distance to the new
rounded entrance. Its gap/negative-count fields are UNQUALIFIED_ANALYSIS,
not actual rounded-solid FAIL. Do not reuse those fields. Immutable summary/
Raw preserved. Independent1649 matches all Native geometry EXACTLY and checks
actual polygon-frustum membership. Producer now leaves rounded gap fieldsNULL
pending independent audit;1650 does not emit the wrong straight-hole metric.

Whole-facet test1651 clips every saved wire triangle against the288convex
polygon-frustum ring wedges. Two independent software tests validate cell
union vs analytic membership AND mesh ray containment, and known triangle
crossing. Actual first200states:76states have strict interior facet witnesses,
first12.5ms; tested16119broadphase triangle/cell candidates. FLOATING POINT
geometry audit,not sweptCCD or a new physics law. Independent1653 checks48
sample witness points against the actual FULL1650 Native wire facets:
all48 insideGuide by separate ray containment/nearestGuide triangles, lie on
wire facets within1.58383e-19m and within their barycentric bounds. Sample
interior depths.026283–.465772um; NOT maximum penetration of the full trial.
Thus no-vertex-intersection1652 is valid only in its explicitly limited scope;
it does NOT qualify finite wire/guide contact or allow fullgrasp integration.

Next physically motivated contrast: original500um wire collision facets span
the200um entry fillet. Refine only mapped tube axial geometry8..12mm to25um,
derived from sqrt(8R*(contactbuffer/4))=28.284um (heuristic geometry target,
not a proven bound on actual deformed wire). Same11mechanicalBeamDOFs,E,rho,
mass,16around,BC,dt,ALL Guide surfaces/features retained. New193stations,
3088mapped vertices,6144facets; minimum reference triangle area positive.
1654 fails Native initialization SIGSEGV,0outputs: generated exactmapping
index10 refers to nonexistent beam10 when installed useCurvAbs0 takesfloor.
Prior successful Scene serializes endpoint9.999999999999998.1655 reuses that
EXACT existing endpoint index; no SDK patch, endpoint physical/tolerance fix,
state correction or new solver. Failure1654 logs preserved.
Actual wire_local_mesh_pilot1655 RUNNING; inspect summary before any rerun.
If valid, independently check rounded vertices AND complete savedfacets before
longer run. Stop resolution family if no new valid hypothesis; no blind scan.

```bash
$PY product_prototype/sofa/wire_contact_phase_probe.py --tag UNIQUE --source-case partitioned_wire_full1642 --build-case identified_contact_build1625 --children --target-time 0.0172
$PY product_prototype/sofa/wire_pair_response_contract.py --tag UNIQUE --case partitioned_wire_full1642 --time 0.0172
$PY product_prototype/sofa/partitioned_eyelet_wire.py --tag UNIQUE --rounded --steps 200
$PY product_prototype/sofa/rounded_bore_assess.py --tag UNIQUE --case rounded_partitioned_full1650
$PY product_prototype/sofa/rounded_wire_surface_contract.py --tag UNIQUE --case rounded_partitioned_pilot1648
$PY product_prototype/sofa/wire_facet_witness_reference.py --tag UNIQUE
$PY product_prototype/sofa/wire_local_collision_mesh.py --tag UNIQUE
```

## Continuation1618–1639: measured constraint coverage, not a physical fix

Read-only observer now samples an explicit window and actual child positions,
free positions and J. Frozen1211 binary is unchanged. Separate build snapshots
1618/1622/1625 contain exact compiled source/binary hashes. Prefix Native runs
1619/1623/1626 match original q/v/surface/aggregate impulse **exactly0**.
Current source renames unused legacy `constraintId` output; frozen1625 header
still calls this `first_row`, but it is NOT the actual global row start.

At45.2ms: actual157normal rows, Min zero friction has ONE row per contact.
Native max diagonal-scaled natural complementarity residual3.020633e-7m.
Independent frozen-W/dFree SLSQP reference1621/1628 improves this to9.60095e-11m,
but **both FAIL1e-12**; optimizer.success is not a KKT or physical PASS.
No multipliers or state are installed back into Native.

Source ownership MUST match constraint context AND actual mechanical-state
context prefixes to original collision models. Path alone is ambiguous because
multiple responses have identical paths and shared ancestor J. Analysis1624's
9.5mm mismatch is UNQUALIFIED_ANALYSIS, not physical penetration;1627 fails
when unused legacy constraintId is mistaken for row start. Both artifacts stay
immutable. Correct1629 uses actual state prefixes (its frozen summary's
`ANDfirstrow` scope wording is stale, NOT its actual algorithm).
Actual reconstructed free gap vs Native dFree error1.85670e-18m; accepted-child
vs linearized gap difference.322747um. This does not explain away the4.60um
signed-solid penetration.

1630 finds penetrating vertex328 actually detected.1635 cross-checks row34:
child position equals physical wire surface exactly; J equals previous point
separation within9.15934e-16; actual bore face plane error0. Native J points
**into solid** (dot solid-outward normal=-1) after prior crossing. Accepted
frozen halfspace gap+2.602854um while signed-solid gap=-4.602854um, lambda0.
Across actual detector point pairs,991inside samples point inward;28234outside
samples point outward. Other-time native J/multipliers are NOT inferred.

Point computeNormals=1 contrast1631:1200outputs/8.937s, q/v/surface/impulse
hashes identical to Local1614, same.434165mm penetration1632. Not a fix.
Separate inner-entry R.2mm fillet1633 retains ALL collision features and outer
OD3/coreID1.2/L2; entryID1.6, straight bore1.6mm, endwall.7mm. Four-segment
quarter fillets,32azimuth,768triangles, chorderror3.843um explicitly recorded.
Actual Native1200outputs/107.987s; exact polygon-frustum solid audit1634 finds
**4.518705um penetration**,687negative outputs,1001iterations. FAIL; stop
fillet-size scan. Three independent ray-membership/volume/topology tests pass
only their software scope. STL not STEP/fabrication-ready.

### First crossing1636–1639 (new actual Native44step prefix)

First negative state4.4ms, not worst45.2ms: actual44steps/1.431s, observer purity0.
139normal rows, reconstructed dFree error6.50521e-19m. Native natural NCP residual
**0**, minimum frozen accepted halfspace positive.359395nm; yet actual vertex328
penetrates.683042um. Thus initial crossing is NOT explained by iteration-limit
failure alone.1638 matches both actual TrianglePoint detector outputs to previous
wire vertex; only ONE becomes a triangle response row.

Installed BaseUnilateralContactResponse.inl has hardcoded minDist2=1e-8f, i.e.
100um combined point-separation threshold in metre scene.1639 independently
replays original ordered outputs:24detector outputs→21retained,actual21rows;
retained actual mapping error5.89806e-17m. Critical detector pair17/facet16 is
discarded for pair4/facet15 (combined squared distance1.57433e-13m²). Retained
pair4 is actualrow25. Finger/wire motion crosses the unrepresented adjacent
facet although retained LCP solves. This identifies an actual source/geometry
coverage failure, NOT proof of every residual or whole-grasp failure.

Next: SAME physical coupon in consistent mm/kg/s units, first no-contact
mass/elastic/fixture API equivalence, then contact ONLY if that contract passes.
This changes physical scale of hardcoded Native numerical epsilons, not actual
material/geometry/load/dt. It is NOT a pure dedup-only edit or certified fix.
No SDK edits, custom solver, tolerance relaxation or further wholegrasp rerun.

```bash
$PY product_prototype/sofa/wire_contact_phase_probe.py --tag UNIQUE --build-case identified_contact_build1625 --children --target-time 0.0044
$PY product_prototype/sofa/wire_mapped_gap_contract.py --tag UNIQUE --case first_crossing_phase1636
$PY product_prototype/sofa/wire_response_dedup_contract.py --tag UNIQUE
$PY product_prototype/sofa/rounded_bore_assess.py --tag UNIQUE --case rounded_bore_wire1633
$PY -m unittest discover -s product_prototype/sofa -p 'test_*wire_geometry.py'
$PY -m unittest discover -s product_prototype/sofa -p test_rounded_bore.py
```

All original Raw/FAIL preserved; detector journals stay local and excluded from
Git. New component diagnostics do not qualify unbraced100gHolding/Lift,
time/mesh convergence, real wire properties or300partCAD performance.

## Units1640 FAIL and actual collision partition1641–1642

Checkpoint07627fe saves1618–1639. Next task ACTUALLY executed,not just planned.
Consistent mm/kg/s1640: radius/positions/translations×1000,E/1000,rho/1e9,
normal tolerance1e-12m→1e-9mm (samephysicalgate),rotations/quaternions/time
unchanged. AdaptiveBeamMapping useCurvAbs0 firstcoordinate is dimensionless
beam-index+barycentric,onlylocal y/z scale. Two regression tests check geometry
union and physical mass/EI conversion,not Nativephysicalqualification.
Actual no-contact1200outputs/6.693s: normalized q1.82051e-13/surfaceq2.79637e-15,
but rigidv3.220997e-9rad/s (1.5ms,node8,angularz),surfacev1.39543e-11m/s.
**FAIL strict1e-12 API**, not rounded toPASS. No mm-unit contact run allowed.
Raw1640 numbers are **mm/kg/s despite inherited SI-looking logger headers**;
only independent analysis converts them. No original Raw rewritten.

Independent implementation1641 keeps exact original256orientedEyelettriangles
and all original Line/Point features, partitions ONLY TriangleCollisionModels
into32azimuthsector contexts. No new seamLine/Point models;no actualsurface
removed, enlarged or hidden. Static fixture coordinates duplicated identically
as explicit collision representation,not additional physical guideparts/mass.
44step Native1.774s: minimum sampled gap+2um,0negative outputs;firstcrossing
removed in this prefix only. Still1001iterations: not numericalPASS.
Bounded full1200step trial1642 RUNNING;inspect actualsummary/process first.
Then independent actualcontact source/impulse andsolidgap audit required.

```bash
$PY product_prototype/sofa/wire_units_contract.py --tag UNIQUE_CONTROL
$PY product_prototype/sofa/partitioned_eyelet_wire.py --tag UNIQUE_PREFIX
$PY product_prototype/sofa/partitioned_eyelet_wire.py --tag UNIQUE_FULL --steps 1200
$PY -m unittest discover -s product_prototype/sofa -p test_wire_contact_representation.py
```

StartingHEAD98ac710, clean tree; old Raw and verdicts preserved. Goal is to
resolve the current finite-wire route incompatibility, not add unrelated CAD.

## Hypothesis and implementation1613–1614

1612 actual guide3 turn43.725595deg exceeds the37.169996deg straight-leg
feasibility limit for wireR.25/boreR.6/L2mm. A flexible wire might bend inside
the bore, so this is not proof the real structure is impossible.

New native BeamAdapter coupon starts with a **straight stress-free20mm wire**.
Only two endpoint rigid fixtures move (inward0.719218mm, upward3.723853mm,
rotations±21.862798deg). All interior beam DOFs remain elastic and free.
Ramp80ms, observe120ms, dt.1ms; initial finite bore clearance is positive.
The target endpoint turn comes from actual current geometry; this is a fixture
bending experiment, **not** measured1.5N cable actuation or fullgrasp.

Eyelet is actual closed32-sided OD3/ID1.2/L2mm annular solid. Finite wire
surface is16-sided, stock AdaptiveBeamMapping. All triangle/line/point models
enabled. E2GPa/rho1000 and zero friction remain inherited research assumptions,
not actual wire properties. Supports, root hardware and three fingers are not
part of this isolated coupon. No-guide trial is an explicitly isolated elastic
control, never a collision-disabled grasp PASS.

1613 failed producer serialization before any Native execution (no Raw).
Corrected array serializer, new independenttag1614; failure preserved.

## Actual results

1614 Native no-guide control completed1200outputs in6.344s; with guide completed
1200outputs in8.900s. Both finite. Endpoint position error1.735e-18m and
orientation-matrix error4.441e-16: fixtureAPI valid. Interior actual displacement
up to2.927mm, not a prescribed beam shape. Segment chord strain proxies are
.001528/.002484; these are **not** Native material strains or wire strength.

1615 independent signed distance to the actual polygonal annular solid:

- Guide case maximum sampled penetration **.434165mm**, firstnegative4.8ms;
  489negative outputs,484 with zero contact impulse: **FAIL**.
- Actual nonzero contact rows:19EyeletTriangle/WirePoint and6Line/Line;
  maximum resultant.068213N, maximum solveriterations113.
- Response/aggregate impulse partition error1.059e-22Ns/Nms. This does not
  validate contact geometry or physical accuracy.
- No-guide control crosses the same *virtual* reference solid, as expected;
  it is not missing-contact evidence because no guide exists in that control.

The analysis uses exact extrusion of the actual32-sided annular cross-section,
not an ideal circular bore. Negative saved surface vertices prove intersection;
positive vertices cannot certify whole facets or swept CCD.

## Actual next experiment1616

Fresh Native trial changes **only LocalMinDistance→MinProximityIntersection**;
all geometry, BC, material, dt, alarm/contact distances, friction and solver
tolerances identical. This tests contact feature filtering/coupling, not a
blind solver tolerance or force scan. Runtime limit120s/4GiB. Inspect actual
summary first, then apply independent gap/provenance assessment before any
qualification or further trial. No new fullgrasp is justified by completion.

Reproduction (Python environment,repo root;unique tags only):

```bash
$PY product_prototype/sofa/current_turn_wire_coupon.py --tag UNIQUE_COUPON
$PY product_prototype/sofa/current_turn_wire_assess.py --tag UNIQUE_ANALYSIS
$PY product_prototype/sofa/wire_contact_policy_contrast.py --tag UNIQUE_MIN
$PY -m unittest discover -s product_prototype/sofa -p test_current_wire_geometry.py
```

Child commands, SDK and actual plugin/runSofa hashes are in per-trial preflight.
No new ODE/FEM/contact law/SDK implemented. All old physical/time/mesh failures
remain; no100gLift/fabrication/product PASS from this coupon.

## Min policy1616–1617 and independent distance regression

1616 actual1200outputs/77.096s.1617 same exactsolid analysis: worstpenetration
4.602854um at45.2ms,685negative outputs (all havecontactreaction), peakresultant
3.373578N and1001iterations. Source partition2.168e-19Ns/Nms. Muchlessgross
escape thanLocal, but **still FAIL**, no micron error floor or relaxed gate.
Contact detection therefore matters; this does not yet isolate remaining error.

New distance regression initially failed when the *independent* trimesh
triangle reference was evaluated in metres: it gave213.8767um instead of200um
for a simple known point. Evaluating identical triangles in millimetres and
converting the distance back matches the analytic polygon extrusion<=1e-12m.
Actual production polygon SDF was unchanged. Three tests now pass, including
an explicit regression exposing the installed reference scale limitation.
Previous unscaled triangle-reference reports are not silently rewritten.

Next actual task is read-only constraint phase diagnosis at45.2ms. Extend the
existing1211 observer's sampling window, not reimplement its measurements;
preserve original binary. Collect W,dFree,f/current/freeq and test actual
q/v/impulse/surface purity before interpreting any contact residual. No new
fullgrasp or blind dt/solver iteration scan is justified.
