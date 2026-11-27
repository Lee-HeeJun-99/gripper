# P1 gravity-loaded product continuation — 2026-11-27

Selected task: `goal_primary_gravity_loaded_chain`. Starting actual HEAD:
`ee1619871d20dd9199b234dedf755df334f1828d`.

The ONE primary product remains **primaryP1_fixture15**, 78 actual parts:
Motor → stock hub/four M3 → Drum → factory cable → swivel/Terminal → Rail/PET
Finger → Root/RF → OPEN_FRAME → shared M5 → Ground/key → four separate axial
fixture bolts → Base. Failed AO, adopted AA, original 3-Finger, cartridge and
jamming extension are preserved. No design part, assembly or BOM bytes changed.
This cycle validates that product, rather than creating another architecture.

Actual new CAD is the loaded curved cable: two STEP/STL solid pairs under
`validation/integrated/primaryP1_gravity_cat_loaded1` and
`primaryP1_gravity_cat_demand_loaded1`. They use the solved drum payout,
catenary, independent swivel rotation and actual terminal pose. Each is a
single valid, constant-volume solid, with no stored-pose cable/rotor collision.
Independent STEP reimport checks all 78 original part identities. The new wire
volume errors are 1.68/1.69e-9 relative. Prior actual assembly/tool screens stay
applicable to unchanged design bytes; these two loaded poses are not CCD or
full same-revision 3-Finger Stage1 qualification.

## New physical mechanism and evidence

Actual Rail/PET CAD was sliced in rest material coordinates at 32/64/128
intervals. Exact clipped volumes and first moments reconstruct original CAD;
relative volume errors at 32 are at most 4.06e-13. Root material stays fixed,
77 mm Rail and 86.2 mm PET remain separately extensible, and the distal cuff,
terminal, swivel, rotor and cable use their own physical kinematics. Total
conditional mass remains 0.989895091786 kg. Densities, nominal manufacturer
motor/hub masses and COM proxies remain conditional, not source minima.

An initial direction-constrained swivel model hid a gravity moment of
-0.000166828660 Nm. Its mathematical results and independent tests are
preserved, but it is not a freely rotating swivel certificate. Adding an
independent swivel DOF balances that moment. A second limitation was the
straight free cable's nonzero distributed transverse weight. The final model
uses an inextensible massive string, drum tangency, variable free length,
wrapped/tail weight and actual rotor gravity. Independent closed-form string
integrals/adaptive centroid quadrature verify endpoints, tension, tangents,
material length and drum torque. No transverse force was filled by an
invented support. Cable bending, elasticity, wrap friction and source minima
are still unqualified.

Independent sinc kinematics/complex derivatives verify gravity forces and
virtual work. Saved rod/contact states also pass physical corner normal-cone,
free material-station, gap and actual PET/terminal/Rail BRep checks. Perturbed
normal, corner, swivel and cable-force states are rejected. Zero gravity
recovers the old actual P1 solution: state error 8.92e-14 and normal error
3.33e-15 N. This is an actual product reduction, not a separate ideal coupon.

At the **same motor-equivalent command 1.013271783025 N**, the finest normal
force is 0.322157029913 N, rather than the old gravity-free 0.408610416667 N.
Pure matched-command 8/16/32 comparisons are distinct from old unequal-command
tables. Base-to-finest normal/angle/energy/nominal Rail/PET stress differences
are 0.104756%, 0.259307%, 0.988367%, 0.907553%, 0.949866%: within the unchanged
1% criterion for this branch only. Mass64→128 normal difference is 1.84e-7
relative; string Gauss8→16 is negligible. These do not erase historical mesh
FAILs or establish dt/global-energy/strength convergence.

For the unchanged conditional target `100g*9.80665/(3*assumed_mu.8)`, a new
normal-target solve requires motor-equivalent **1.185442703380 N**, torque
**0.013336230413 Nm**, an increase of **16.9916%**. This assumes equal sharing,
a prescribed 20 mm spatial stop and typical moduli. It is not an actual
100g payload, free grasp, friction measurement, protected peak or capacity.

At this target, paired physical XYZ wrenches, in N and Nm, are:

| Port/reference m | Force XYZ | Couple XYZ |
| --- | --- | --- |
| Root `(0.0504,0,-0.007)` | `(0.234685173,0,0.892077401)` | `(-0.000005597,-0.000771609,0)` |
| Motor `(0,0,0.020)` | `(0.173925244,0,-1.493241940)` | `(0.001773277,0.013336000,0)` |

The full required Base external wrench is
`[-0.408610417,0,9.707554702,-0.076586225,-0.219987695,0]`.
Swivel torque residual is 1.49e-13 Nm; motor torque action-reaction error is
2.87e-15 Nm. String sag from its straight chord is 2.03948 micrometres.
These are conditional demands, not source-qualified load capacities.

The finite-radius swept wire's actual COM differs from the centreline-string
COM by up to 0.2175 micrometres. The independently derived tube first-moment
correction matches STEP reimport within 2.11e-11 m. This distinction is
explicit: the string has not been certified as exact 3D cable mass mechanics.

The new deformed Finger/swivel/rotor/string mass ledger and full external
wrench were transported through the existing finite Ground/Base unilateral
key/seat and four minor-core tension-only connector model at h=5 mm. Independent
direct tetra forces, energy, bolt law, contact and corrupt-field tests pass.
Bolt forces are 4.486864/4.901734/4.390683/4.561211 N; conditional peak Ground/
Base stresses are 0.320612/0.519141 MPa. This is ONE new-load case, no mesh PASS.
The upstream Frame and interfaces remain rigid in this transport; it is not
full coupled Frame/Root/Motor/Ground equilibrium or physical bench anchorage.

## Preserved failures and remaining release

Initial OCP and gmsh import failures used incomplete existing dependency
paths; corrected launches used existing local packages with no installation.
A numpy boolean serialization error and a verifier Path typo are archived.
The first normal-target solve incorrectly serialized its seed motor command.
The independent motor action-reaction check rejected it by 0.001936922854 Nm.
That original result is explicitly invalid for torque/load use. Corrected
`primaryP1_gravity_cat_demand32_2` and `...demand_ports2` are authoritative.
No old evidence was edited or deleted. This cycle had no timeout.

All **22 system gates remain UNQUALIFIED** in
`models/primary_system_gate_state8.json`. Newly qualified whole-system gates:
none. Existing Frame 52.7693%, Rail 1.30247%, Ground/Base stress/motion/energy
mesh FAILs, contact-gap 420 s timeout, friction/source-minimum/motor-current/
protector/full3-Finger/global-energy blockers are retained. Read-only actual
release remains INTEGRATED_NOT_QUALIFIED. SOFA runs: 0. Hardware NOT MEASURED;
Stage3 remains unauthorized.

Concrete next task: **goal_primary_gravity_port_interfaces**. Continue this
same P1 using the new full paired wrenches and selfweight. Map actual Root/
Frame and motor-case/Frame seats, lateral gaps, bearing and slip. Implement
positive cartridge/key or lateral motor bearing only where the actual load
path needs it; recheck changed finite CAD, assembly/tools and loaded cable.
Then resolve finite compliant Frame→Ground/key/Base with justified thread/
engagement/preload and an explicit physical Base anchor. Do not substitute
arbitrary resultant traction for connector capacity, clamp shared M5 DOFs,
tie nominal major cylinders or repeat blanket mesh trials.

Main result: `validation/integrated/primary_cycle7/summary.json`.
Final audit/count/save boundary: `validation/integrated/primaryP1_cycle7_closeout/summary.json`.
Save is PENDING Supervisor exact-byte verification, not a claimed commit.
