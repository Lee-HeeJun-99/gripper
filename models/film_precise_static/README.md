# Independent precise-bond static contact/transmission research

Latest opt-in thickness model:SphereEquilibrium::setThicknessEnvelope assigns
half part thickness to all320 topology rows;default remains legacy BYTE EXACT.
g=distance(triangle,sphere centre)−R−.01−halfThickness. This conservative
Minkowski-ball envelope contains constant-thickness normal facet prisms but is
NOT a finite-strain thickness law. New fixture+.2mm world-Z sphere offset is
explicitly separate from old+.0001mm.1780/1784 full static100uN PASS;baseline
wire geometry/unload FAIL,profile4.5/outboard10 sampled geometry/unload PASS.
Actual1782 observer is PASSIVE ONLY and never applies contact forces. Same
binary ON/OFF states/stages/Field journals and old1743 are BYTE EXACT. No dynamic
thickness contact,wrapping,holding or final design certification follows.
See reports/REGRIP_THICKNESS_CONTACT_20261119.md for scopes and next code.

This is NOT the actual SOFA dynamic Owner or a replacement for the old3-finger
checkpoint. `CoupledPlaneStep` is reused for its constant root reduction only;
its mass,h and damping terms never enter the static force equations.

Let U=U_skin+U_rails+U_attachment+Phi_tendon. The fixed-sphere static problem is
grad(U)-C lambda=0, g>=0, lambda>=0, complementarity,where each g is the SAME
closest point of one complete triangle surface and C=dg/dq transposed through
the root map. All320 triangles own topology IDs. lambda is FORCE[N],not impulse.
The true Lagrangian tangent is K-sum(lambda_i*d2g_i). No artificial stiffness,
mass or accepted-state correction is introduced. A positive FULL tangent is a
solver limitation,not a proof that other constrained equilibria are unstable.
Newton30/line-search16 and existing force1e-12N/gap1e-10mm gates remain.

The independent unit preflight checks1D,duplicate-row and coupled2D closed forms.
At the rest closest-feature ties,central FD has an O(h) term:1751–53 FAILs are
preserved. The C1 Richardson2D(h/2)-D(h),h1e-4,has error4.26204e-10 within the
unchanged1e-8 gradient gate in1754. This is NOT a classical Hessian/IFT proof at
feature transitions. Mechanical force/Hessian/objectivity/balance gates are
separately tested with the original tests in1759/1764/1765.

`Potential.h` evaluates the existing dead-load potential directly from element
energies,not a rounded200mm cable-length subtraction. It is NOT cable stored
elastic energy or motor work. Baseline callback refactoring regression1760 versus
1755 states/rows/wrenches/Newton CSVs is BYTE EXACT.

`Profiled.h` reuses the known1431 objective guide geometry plus precise shell/
attachment terms. Existing .5mm free50ms worse-arch result is not revoked. New
static-only amplitudes0/.5/4.5 and outboard6/8mm are explicit independent designs;
the old Field guards/SDK are not loosened. Amplitude0/outboard6 delegates EXACTLY
to the qualified precise tendon. Nonzero profiles still use global-coordinate
guide geometry;their ultra-small-signal/time/SOFA precision is NOT qualified.
Core material volume is unchanged,not finite hardware volume/mass. Work and
initial cable lengths are NOT matched. Prescribed tension is NOT an equalizer.

Results:1754 low-load contact PASS;1755 static load/unload toT0 PASS.1756 baseline
full100uN FAIL,last80.31uN;1757 smaller tail FAIL,last90.15uN.1766 profile4.5/
outboard8 completes100uN static;1768 seeded64-stage static unload PASS. These
are NOT dynamic recovery,actual SOFA,wrapping or grasp evidence. Contact remains
one point,area/pressure/holding capacity NULL.1770 audits all64 loaded states:
wire centreline actually intersects the sphere at the peak and the .01mm buffer
does not protect .025mm Skin half-thickness. Thus this candidate is NOT accepted
as a physically cleared final design. See the precise validation report.

No old dynamic checkpoint is imported. No friction,self contact,full thickness,
dynamic stability,free-body grasp or final design certification is supplied.
Latest domain extension: outboard10mm is independently force/Hessian tested
in1772. Full-load1773 FAILS;1774 clearance covers only its committed prefix
through80.3086uN.8mm full-load design fails wire clearance1770. Both fail
skin half-thickness clearance. Neither is a selected or SOFA-qualified design.
