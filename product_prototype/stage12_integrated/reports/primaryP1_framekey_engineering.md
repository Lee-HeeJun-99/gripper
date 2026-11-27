# P1 finite compliant chain and positive Frame/Ground path

Starting actual HEAD: 581f6de37e7937be60fc490c02f2e438b77f8188.
Selected exact task: goal_primary_compliant_wall_cradle_frame.
Same primary P1, 78 parts; current continuation primaryP1_framekey19.
AO/adopted AA, original three-finger/cartridge/jamming models, all previous
CAD/results/failures and source-pinned manager/security/gate code are preserved.

## Actual product change

Only OPEN_FRAME and GROUND_PLATE are changed. The Frame has an integral
8 x 6 x 3 mm key at [56,5,40] mm and four R0.5 concave root fillets. The
Ground has an underside pocket with 0.2 mm roof clearance, R1 corner tool
reliefs, and a 0.6 mm 45-degree entry relief. These are actual exported,
reimported STEP/STL solids. The full 78-part STEP/BOM binds all unchanged
parts, including the existing source-backed motor1101/hub1996, factory cable,
original Root shoulder, motor side lands, and keyed Ground/Base fixture.
No new purchased part or architecture is introduced.

The old frictionless planar Frame/Ground seat with axial M5 connectors cannot
carry the actual +0.408610416667 N x-force. The new finite key surfaces admit
that full load wrench with nonnegative contact forces and axial retention.
Removing the key rejects equilibrium. This is a necessary rigid-body load-path
witness; LP reaction magnitudes are not preload, elastic distribution or capacity.

Finite key x-face contact area is 9.6 mm2 each, y-face contact area is 14.4 mm2
each, and the remaining Frame/Ground seat is 5059.487380938695 mm2. Corner tool
reliefs and entry chamfer reduce contact from the raw rectangular dimensions.
Independent displaced-solid Boolean volumes at 0.001/0.002 mm contain a linear
chamfer correction in V(h)/h. The first finite-quotient area check failed and
is immutable; zero-step Richardson extrapolation passes the unchanged 1e-6
relative area criterion. No tolerance was relaxed.

New changed-parts nominal density contrast gives total 0.9888237838650752 kg.
The required full external Base wrench is [-0.408610416667,0,9.697048760040,
-0.076674165019,-0.219347805982,0] N/Nm. This updates the original fixture15
mass for both the prior motor lands and current key/pocket, at Frame2700 and
Ground7900 kg/m3. It is not a measured mass, a source minimum, or an anchor rating.

## Actual assembly scope

Reimported78 valid single solids, 191 Boolean broad-phase pairs, no final volume
interference. Six Frame insertion samples into Ground/Base/fixture are clear.
The original lateral Finger, vertical drive/Cap and RF fastener assembly samples,
RF driver approaches, five nominal route poses, independent aggregate/STL check,
and one saved gravity-demand32 catenary/rotor pose are rerun on this CAD.
Finite samples are not continuous CCD, tolerance/process or thread tightening.
The original internal Ground hardware remains smooth fastener envelopes;
actual socket/hex access, engagement and source-minimum capacity are unqualified.

## Separate-body physical model

The existing Gmsh/scikit-fem P1 tetra linear elastic/contact kernels are reused.
RootBack/Frame/Cap are separate elastic bodies; the full-chain variant adds
separate finite Ground and Base. The motor has six rigid DOFs as an explicit
conditional proxy, never a fabricated elastic modulus. All normal contact is
unilateral and frictionless. Finite actual Root seat/wall, motor bottom/top/side
lands, new Frame/Ground key/seat and existing Ground/Base key/seat are retained.
Six Root/Cap connectors, four original Ground connectors and four fixture
connectors are tension-only axial minor-core springs on actual head/nut patches.
No nominal major-cylinder tie, shared-M5 fixation or hidden motor DOF is used.

A separately triangulated curved head/nut footprint can have a slightly different
quadrature centroid at its two ends and create an artificial internal moment.
The first saved state exposed this and is rejected by independent rigid work.
Corrected footprint weights remain positive and reproduce the common physical
bolt-axis centroid. They are conditional averaged bearing fields, not solved
thread flanks, bearing compliance or engagement capacity. Basic minor-core
geometry and explicit compliance lengths are recorded in each inputs.json.

Existing corrected gravity-loaded Finger/free-swivel/string full Root and Motor
forces AND couples are transported. Finite elastic body gravity is integrated
from tetra volumes. Remaining fixed Rail/PET/clamp masses enter the aggregate
Root port; hardware weight is transported to the Base external port in the
chain contrast. This preserves full force/moment/mass accounting but does NOT
solve the omitted hardware's local weight/bearing stress or feed deformed
support motion back into the Finger/string equilibrium.

A finite Base top external traction balances the actual demand; six Base rigid
motion gauges must carry negligible reactions. It is a mathematical wrench port,
not a physical laboratory anchor. Root and motor free-Y slip and Cap free-X/Y/yaw
are unloaded coordinate gauges; they do not certify lateral retention.

OSQP warm starts are followed by an exact sparse active-contact KKT solve of
this SAME quadratic elastic/contact energy. Every original gap, contact sign,
bolt branch, body wrench and residual remains checked. OSQP iteration-limit
statuses are preserved independently from the KKT result. The independent
verifier recomputes affine tetra forces/energy/stresses without importing the
producer, checks bolt law/contact complementarity and rigid virtual work, and
rejects a perturbed displacement. A local static identity is not global energy.

## Preserved failures and limitations

The initial RootFront/RootBack direct-contact assertion was wrong; Rail/PET and
pins intervene. The aggregate Root resultant now acts on the actual RootBack
x50.5 face; this does not certify local Rail/pin traction. The initial numerical
serialization error, later syntax failure and fixed-mass field-name error are
preserved with source hashes/logs; none is counted as physical success.
Original coarse Cap volume error exceeds1%; an increased angular boundary
quadrature with a smaller local size resolves geometric volume, not stress
convergence. The 100000-iteration OSQP result remains a failed execution.
An early KKT postprocessor used the wrong sign for the auxiliary bolt dual;
the saved physical field is independently inspected, while its original FAIL
summary and saved incorrect diagnostic residual remain immutable.

All22 whole-system gates remain UNQUALIFIED. Old Frame52.7693%, Rail1.30247%,
Ground/Base mesh failures, previous420s gap timeout, friction/time/global-energy,
material minima, real motorcase/bearing, protector and three-finger Stage1
failures remain. There is no strength, protected peak, payload, physical
assembly, hardware measurement, full same-revision release or Stage3 claim.

## Completed nominal full-chain numerical result

The actual19 nominal chain has 74040 DOFs, five finite elastic bodies plus the six-DOF rigid motor. OSQP reached its4000iteration limit; a separate three-iteration exact active-set KKT solve closes ALL original constraints and both producer and independent direct-tetra checks pass. This is conditional local static validation, not an OSQP success or whole-product release.

Producer relative stationarity 1.52147205916e-11; independent direct-tetra residual 1.68910417176e-11; independent static identity 1.78743079419e-10.

Representative axial forces, in RF0/RF1, four Cap, four Ground and four fixture order [N]: [0.8170608060061539, 0.812145842256098, 0.8960196687396389, 0.40994118226286896, 0.0, 0.48907311036006085, 2.823000524421813, 1.0786652093485989, 1.0157034513088292, 1.0010445771018561, 4.068064798282124, 4.352263475895917, 3.952808120405535, 4.103216868639082]. These are conditional averaged elastic reactions, not preload or strength.

Conditional unsmoothed peak von Mises [MPa]: {"OPEN_FRAME": 3.1825905096424694, "F0_ROOT_BACK": 0.10852756201452055, "MOTOR_CAP": 0.4363927246619693, "GROUND_PLATE": 0.4528177331709423, "TEST_BASE": 0.49342109199465467}. There is no stress mesh convergence or source allowable certificate.

Mesh-integrated required Base external wrench [N,Nm]: [-0.408610416666667, 3.440071228173105e-18, 9.701546171535597, -0.07670847805742019, -0.21948036372497748, 2.4074910799904776e-18]. It differs from the exact-CAD mass wrench because own-body gravity is integrated on polygonal tetra meshes. Each body volume error is below1%; that is a geometric quadrature check, NOT stress/motion mesh convergence.

Scope correction: the inherited JSON key external_FrameGround_port identifies TEST_BASE in chain=true. Its part field, execution source and actual output wrench are authoritative. Generic inputs.boundary Frame wording is stale; no actual Frame fixation is used in this full-chain solve. Hardware gravity goes through the Base external port; fixed Rail/PET/clamp portions go through aggregateRoot. Their local weight/bearing stresses remain unresolved.

Fine237165DOF execution entered the420s limit branch, then os.killpg raised ProcessLookupError because the process group was already absent. Wrapper exit1 is known; exact analysis exit code and elapsed time are unknown, with a420s lower bound. No saved field/summary exists. This is INCOMPLETE/limit evidence, not a successful or converged fine solve. The original plan/producer/inputs/log are immutable; no retry was made. From this event onward only existing-task termination, saved-field inspection, release audit and exact-byte handoff are performed.

## Final saved-field review and remaining fit failure

Two nominal gauge variants agree in actual strains/stresses/forces and elastic energy. Relative elastic energy difference 1.3034684442914113e-11; max axial reaction difference 9.71454028331209e-11N. The direct strain review passes1e-8 in every body. This is mathematical coordinate equivalence, not physical support or stiffness improvement. Both savedfields have separate independent direct-tetra/negative-control certificates.

The already-started74040DOF0.02mm lateral-gap contrast also reached the420s limit branch and the same ProcessLookupError race. It has inputs/producer/log but NO field/summary. Exact analysis exit code and elapsed time are unknown; wrapperexit1 and420s lower bound are known. It is incomplete and receives no performance reward or fitPASS. No preload contrast was launched after the first limit event. The two limit cases are not retried.

All owned tool sessions/namespaces have ended. Exact wrapper counts, known durations, two separately identified unknown durations/lower bounds and failure records are in primary_cycle9 and primaryP1_cycle9_closeout. No physical experiment was launched after the first limit; saved-field inspection and the unchanged release gate are save-only checks.

Concrete next task goal_primary_framekey_fit_feedback keeps this sameP1: replace the internal smooth Ground fastener envelopes with actual source-backed socket/hex retention and adequate thread projection/tool access, then update same-part CAD/mass/contact footprints and feed saved Root/Motor support poses into the existing gravity Finger/string model. Do not automatically retry the fine/gap limit runs or claim unchanged normal force at moved supports. Physical Base anchor, real case/bearings, thread/material minima, friction/protector/globalenergy/full3Finger gates remain blocked.
