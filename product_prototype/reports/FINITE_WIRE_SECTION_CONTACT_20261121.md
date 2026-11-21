# Finite wire-section / Native groove contact continuation

Baseline `cebebc3`; installed SOFA26.06 SDK unchanged. This is a new minimal
contact model, **not a continuous wire, circular wrap solver, equalizer or B3**.

## Implemented and actually executed

`sofa/root_wire_contact.py` reuses the actual Root wheel/land geometry and frozen
332/512 passive observers. Wheel DOFs are ideally fixed. One free Rigid3 sphere
of radius0.25mm represents only a wire cross-section, with ASSUMED mass10mg,
constant inward10uN and tangential initial speed+/-2mm/s. Gravity0,mu0,
dt250us,60steps/15ms. All wheel/land collision models remain enabled. No prescribed
bead trajectory, position correction, custom force law or new solver.

* 845 positive direction:60finite states,8.87s; tangent travel+30.000036um.
* 846 negative direction:60finite states,8.77s; tangent travel-29.999964um.
* Both:46steps with nonzero contact impulse; maximum linear momentum residual
  3.31e-24Ns. Response rows contributing to the free sphere come exclusively from
  actual wheel TriangleCollisionModel / wire-section SphereCollisionModel pairs.
  Sum of those rows equals body impulse exactly in the saved journals.

These are completed Native runs and response-provenance checks, not time/mesh,
energy, physical friction, wire stiffness, sliding wrap or Holding qualification.

## Analysis failure and correction

Original845/846 summary gaps and847 closest-point/gap analysis used unconditioned
SI coordinates with `trimesh.proximity.closest_point_naive`. That routine selected
triangle vertices instead of nearby face interiors on this small geometry.
The apparent positive-gap contact discrepancy was an **analysis error**, not a
demonstrated Native contact defect. All original files remain unchanged, with
append-only `GEOMETRY_ANALYSIS_CORRECTION.json` annotations.

848 intermediate conditioned analysis and849 final initial/accepted-state analysis
use `metric_mesh_query.closest_si`: scale geometry AND points by1000, query in mm,
return in m. No physical geometry, SOFA state or contact acceptance tolerance is
changed. An independent dimensionless face/edge triangle minimization cross-checks
each selected closest point; maximum difference2.34e-19m.849 records actual
trimesh version/source hashes. Corrected initial gap7.107980um; accepted minimum
signed sphere/triangle gap is approximately-3.79e-19m (retained as negative, not
rounded into a clearance PASS). Exact per-case numbers in849.

850 adds the unit-conditioned query, degenerate rejection and provenance regressions
to the bounded design test runner. These tests are software checks, not productGates.

## Reproduction

Use `/home/ubuntu/miniconda3/envs/robot_ws/bin/python` from repository root:

```
python product_prototype/sofa/root_wire_contact.py --tag UNIQUE_POS
python product_prototype/sofa/root_wire_contact.py --tag UNIQUE_NEG --tangent-speed=-0.002
python product_prototype/sofa/root_wire_contact_assess.py --tag UNIQUE_ANALYSIS --cases UNIQUE_POS UNIQUE_NEG
python product_prototype/cad/manufacturing_test_run.py --tag UNIQUE_TEST
```

Do not repeat845/846 unchanged as new research. Each raw directory preserves the
executed scene, producer snapshot, actual command, binary/source hashes and logs.
Child guard420s/4GiB leaves margin below480s. No long child remains after completion.
Next independent task: verify detector observation time vs previous/accepted state
and discrete impulse/work accounting from these saved rows, without rerunningSOFA.
Then assess the minimum missing wire connectivity/tangency contract. No 3-Finger
integration until that model and the existing physical Gates are qualified.

## Follow-on chronology / work cycle851–853

Feature253f9c1 preserved all preceding data.851/852 read existing rows only;
no repeated physical execution. For each direction,519 detected sphere centres
match the previous accepted centre exactly; maximum difference from current
accepted centre1.007782um. Thus an AnimateEnd journal time is not the geometry's
evaluation time. No continuous birth time is established by the3.75ms first
nonzero-impulse record.

Stable kinetic increments use `m*(v_new-v_old) dot (v_new+v_old)/2`, not subtraction
of two large energies. Midpoint impulse identity residual<=6.47e-27J; BE position
update residual<=3.86e-19m. BE geometric-work identity residual<=3.86e-24J.
Contact midpoint impulse-work approximately-7.108e-11J and BE inertial defect
approximately-3.687e-11J are **not separately measured physical heat/plastic loss**.
Root reaction work, true impact loss and complete-wire elastic energy remainNULL.

At the first accepted contact, normal velocity remains-2.18193mm/s; next step is
approximately0. The first velocity agrees with the position-level relation
`v_normal=-previous_gap_to_accepted_plane/dt` within1e-12m/s, while accepted
geometric gap is approximately0. Consequently an explicitly imposed instantaneous
perfectly-inelastic `v_plus=0` reference is **NOT QUALIFIED** here. This is not a
new Native solver defect claim or an SDK correction; its position-level contract
differs from that reference law. No velocity postprocessing, blind dt sweep or
new custom solver was introduced. Existing contact/time Gate failures stay open.

853 plots actual accepted states, exact plane sections of the saved wheel triangles,
normal velocities and step impulses (not force peaks). Image visually inspected:
`results/product_root_wire_plot853/actual_wire_section.png`. Proxy geometry and
scope are marked, no amplified displacement. Matplotlib's unavailable optional
Axes3D warning does not affect this2D figure; no3D rendering is claimed.

Repro read-only continuation:

```
python product_prototype/sofa/root_wire_work_audit.py --tag UNIQUE_WORK --cases product_root_wire_section845 product_root_wire_section846
python product_prototype/sofa/root_wire_contact_plot.py --tag UNIQUE_PLOT
```

NEXT: circular arc/continuous wire connectivity remainsBLOCKED on a matched
Native model contract; these spherical-proxy tests do not supply it. Physical
friction/bend/retention/load-deflection remainNOT MEASURED. Continue independent
wire/axle assembly inspection and supplier-data/bench-data ingestion when such
data exist. Do not repeat constrained-loop/Alarm/dt sweeps without a new hypothesis.
