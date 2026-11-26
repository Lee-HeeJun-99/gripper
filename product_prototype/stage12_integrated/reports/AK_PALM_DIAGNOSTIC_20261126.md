# Actual AK Palm support and bending representation diagnosis

Starting HEAD: `6df5025ac5efcbf8a4920c9ee76a431445a0afdb`. One bounded C-track
analysis cycle, 2026-11-26. Supervisor local save is PENDING; no worker staging,
commit or new save SHA. Canonical result:
`validation/transmission/AK_palm_diagnostic_cycle1/summary.json`.

## Actual geometry

The RevAK235-part candidate and all235 STEP inputs were hash checked. The
previous hypothetical support occupies the Palm underside at Z=-12mm,
r20..30mm. Its actual material footprint is1532.560390612784mm2, not the
uncut1570.796326794897mm2 annulus. An initial full-annulus assumption failed
with exit1; AK_palm_mount1 retains its producer, inputs and FAIL summary,
and cycle mount.log retains the assertion. The corrected AK_palm_mount2
uses the actual cut footprint. This correction does not change physical
or CAD numerical tolerances or revise the previous FEM's support nodes.

Exact BRep distance queries to all234other modeled constituents find no
contact with this underside region. Minimum distance1.578931365318119mm,
F2_IDLER_BASE_NUT. Independently re-read bounding boxes conservatively exclude
all234from even the full annulus, with minimum lower bound0.6433565293705783mm.
Independent planar-face area integration gives1532.560390613760mm2, agreeing
with the material-slice volume/thickness area within1e-5mm2. The central
through-bore radius is20mm. A bore and available annular material do not
supply an actual clamp, preload, friction or six-DOF support. An external
base fixture may be designed separately; its existence is not established.

## Actual saved meshes and solutions

No mesh was regenerated or filtered. Inputs are the immutable full-Palm
h8_3/h6_1/h4_1 fields and their saved equilibrium summaries. The entire
actual solved strain energy was reconstructed independently. All original
quality, convergence, support and stress failures remain unchanged.

| h (mm) | Elements | Quality<.01 | Poor volume fraction | Poor solved-energy fraction |
|---:|---:|---:|---:|---:|
|8|57306|26|3.383e-9|5.161e-9|
|6|68367|26|3.315e-9|4.007e-9|
|4|117281|24|2.791e-9|6.290e-9|

The20worst elements per mesh have minimum altitudes about.00625..00816mm.
Their centroids are at least61.429mm radially from the artificial r30support
partition and30.887mm from the r4load partition. Thus these worst slivers
are not located at those partition circles. This does not identify every
CAD feature's cause or excuse any failed element. Negligible solved energy
in those poor elements does not bound their effect on conditioning or error.

A unit-curvature kinematic probe samples an exact quadratic displacement on
actual mesh vertices. For bending along coordinate a, perpendicular in-plane
coordinate b, and z measured from the actual midplane Z=-9.5mm:

    u_a=-a*z, u_b=nu*b*z, u_z=(a*a+nu*(z*z-b*b))/2

Curvature is1/m; E=70GPa and nu=.33 remain the prior assumed material, not a
certified grade. Exact strains are eps_aa=-z, eps_bb=eps_zz=nu*z and zero shear;
energy density is E*z*z/2. Its volume integral on each actual straight-sided
tetrahedron is exact using the barycentric quadratic moment. This is a
representation probe, not an equilibrium solution, measured product motion,
actual applied force, or new physical performance result.

| h (mm) | P1/continuum energy X | P1/continuum energy Y | P1 shear energy fraction X/Y |
|---:|---:|---:|---:|
|8|4.352432|4.347478|.269876/.270856|
|6|3.865342|3.995284|.231062/.255742|
|4|2.979603|2.968592|.174955/.172493|

All six exceed the predeclared diagnostic1% representation screen. The
197..335% excess and parasitic shear demonstrate a substantial representation
issue away from just the tiny failed elements. They do not establish a unique
cause or rigorous bound on the previous force-driven compliance error.

The independent verifier uses barycentric shape gradients and degree2
four-point tetrahedral quadrature, agreeing with the producer's P1/continuum
energies within1e-8relative. It also recovers the actual saved solution
energies and affine strain; a1%corruption of displacement magnitude is rejected.
P2vertex/mid-edge shape functions reproduce the quadratic probe within1e-8.
This supports investigating element order, but no P2 equilibrium solve,
quality improvement or assembled support has been qualified.

## Handoff

Four completed analysis/verifier children exit0; one initial CAD assumption
failure exits1 and remains archived. Each used4GiB virtual memory/420s hard
limits and one BLAS/OMP thread. Successful producer durations:
.721s bending,43.588s mount,2.506s bending verifier,2.758s mount verifier.
Initial failed-run duration was not instrumented. No SOFA run occurred.

Read-only integrated audit remains INTEGRATED_NOT_QUALIFIED,24errors including
22unqualified Stage2 requirements. This candidate diagnosis is not inserted
as full system evidence. The actual Palm qualification task remains READY
for a separately tagged finite mounting design, at priority3. Before another
Palm equilibrium solve, define that attachment and the whole force/moment
path, investigate small boundary features, and qualify a higher-order or
thickness-aware representation using a supported independent benchmark.
Do not repeat the same unsupported clamp or blindly refine these P1 meshes.

The scheduler now selects AK_protected_maximum_load (A); Idler load/thread
proof and actual Finger root-preload mechanics remain independent READY work.
No queue entry is RUNNING and no owned analysis child remains live. Old CAD,
BOM, results and failures are preserved. Save manifest:
`runtime/authorized_20261126_4/save_request3.json`.
