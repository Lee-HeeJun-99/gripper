# Actual guide-turn finite wire coupon — 2026-11-24

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
