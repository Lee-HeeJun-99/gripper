# Same P1 motor lateral bearing continuation, 2026-11-27

Starting actual HEAD: `1ed7a296c698b03e757b86779bef9af03f051b5c`.
Selected queue ID: `goal_primary_gravity_port_interfaces`.
Final ONE primary: `primaryP1_interfaces18`, 78 parts, same P1 specimen.
Failed AO, adopted AA and original 3-Finger/cartridge/jamming extensions remain
unchanged. Hardware NOT MEASURED. No Stage3 authorization or release.

## Actual design and correction

Final18 changes only OPEN_FRAME STEP/STL. Two integral 10x6mm lateral bearing
lands close the original nominal 0.05mm gaps to the simplified source-backed
Pololu1101 gearbox envelope at x=+/-5mm, y=-21.5..-11.5mm, z=14..20mm.
Added actual volume is 5.999999999891mm3. The motor, stock1996 hub, all standard
hardware, drum, cable, Finger, Root and outer Ground/Base remain unchanged.
New full ASSEMBLY.step, BOM.json and identity5 CSV bind every actual part/hash.
These are machined Frame design changes; no purchase or hardware substitution.

The first16/17 iterations added a6x12x2mm Root key/pocket,17with fourR1 blind
corner reliefs for nominal2mm cutter access. They are withdrawn, not current
product candidates. Initially lifting the entire Finger3mm before insertion
caused41.4470140006mm3 RootFront/Frame interference atshift[-40,0,3]mm.
Later lifting only atx=-14mm cleared finite samples, but the extra key itself
was unnecessary: the first wrench model had omitted an existing160mm2 Root
end-face/Frame wall contact atx=68mm. Its key-omission failure is therefore NOT
proof that the physical product needed a new key. The new wall audit restores
that contact and finds a keyless frictionless equilibrium. Final18 reuses the
original Root and lateral assembly path, preserving all16/17 CAD/results/logs.
This corrects a physical model omission, not a relaxed force or geometry gate.

## Actual assembly and loads

Final18 reimport:78 valid single solids;190 exact Boolean pairs, no volume
interference above unchanged1e-8mm3 criterion. Actual module assembly81sampled
poses/296comparisons, twoRF driver approaches and five straight-route poses
pass bounded nominal checks. Independent78solid aggregate volume/centroid/
inertia-signature matching and selected closed-STL/volume tests pass. These
are finite nominal checks, not CCD, fit/tolerance, process, real thread
rotation/tightening, physical assembly or final3-Finger Stage1 release.

One stored corrected gravity-loaded32element demand case is rechecked with
actual catenary/free-swivel/rotor solid geometry:26comparisons, zero wire or
rotor interference, single valid full WIREsolid, relative constant-volume error
1.69154446e-9. Finger boundary geometry and77partSTEP references are unchanged;
this is reuse of the previous conditional equilibrium at fixed Root/Motor
boundaries, not a new fully coupled equilibrium or a new convergence campaign.

New finite-face frictionless models use corrected gravity demand ports2 full
Root/Motor XYZ force AND couple, actual RootBack weight at7900kg/m3, and separate
Cap weight at2700kg/m3. Motor/rotor/string/Finger weights already included in
those ports are not added twice. Root seat526.377949207mm2 and existing wall
160mm2; motor top/bottom80mm2 each and new lateral lands60mm2 each. Independent
volume-overlap derivatives at0.001/0.002mm reproduce every contact area within
3.60e-12relative. This also establishes real bearing contact rather than merely
a near face or fictitious tie.

Nonnegative uniform pressures on finite actual subfaces plus axial bolt forces
balance all three bodies independently (Root, Motor and Cap), at mu=0. Stored
field force residual <=4.45e-16N and moment residual <=4.59e-17Nm. Independent
external-wrench/mass reconstruction, twelve rigid virtual motions per model,
pressure*area integration and10mN corruption rejection pass. Removing the
existing Root wall or motor side lands makes the corresponding zero-friction
frozen-pose equilibrium infeasible. The original Root wall, rather than a new
key, supplies the relevant positive-Fx bearing path.

For the chosen minimum-total-reaction LP objective, representative Root RF
axial sum is3.939174941N; MotorCap axial sum2.229259095N. These are admissible
necessary load fields, NOT minimum preload, unique elastic reactions, screw
capacity, prescribed tightening torque, strength or guaranteed load sharing.
No pressure allowable, thread flank/core engagement rating or case allowable
was invented. Actual gearbox contact-land geometry/case stiffness and bearing
ratings remain unresolved, despite the existing primary manufacturer source.

Exact Frame added mass is16.2mg at conditionalAl2700, conditional total mass
0.989911291786kg. Independent updated required Base external wrench is
[-.408610416667,0,9.707713569597,-.076588846545,-.219987694554,0]N/Nm.
This includes the changed actual Frame centroid, not an arbitrary external
cancellation. It remains a required physical Base grip/anchor port, not a
qualified physical anchor. Connector selfweight split/contact compliance still
need a coupled model. Nominal zero lateral gap is not a manufacturing fit;
clearance/preload must be solved with actual displacement and unilateral contact.

## Remaining gates and concrete continuation

Newly qualified whole-system gates: NONE. All22 remain UNQUALIFIED in
models/primary_system_gate_state9.json. Actual unchanged integrated gate audits
release11/release12 both return INTEGRATED_NOT_QUALIFIED,24errors,exit2. The
trusted gate still audits its existing AA baseline/contract; the new P1 has no
full same-revision release evidence and is not promoted into that contract.

No new FEM/SOFA/dt/global-energy/strength certificate. Prior Frame52.7693%,
Rail1.30247% and Ground/Base mesh failures,420s gap timeout, friction/cable
bending/elasticity, material minima, physical protector and3-Finger failures
remain. Previous local Rod mesh results do not qualify these changed interfaces.
Initial17generic wrench limitations mention side/key gaps; final18 has NO new
Root key: the actual unqualified fits are the existing wall and motor side lands.

NEXT exact ID: `goal_primary_compliant_wall_cradle_frame`. Continue final18:
separate actual RootBack/Frame/Cap DOFs; finite wall/seat/side-land contact;
rigid motor proxy explicitly conditional until actual case data are supported.
Use existing tetra/contact kernels for zero-gap versus0.02mm clearance and
preload, with justified minor-core axial/head/nut connectors. Carry full paired
wrenches plus all weights through finite Frame/Ground/key/Base without fixing
sharedM5 DOFs. Independently verify active contact/action-reaction/rigid work,
then physical stress/motion convergence and actual Base anchorage. Do not repeat
LP meshes as elastic validation or retry the old timeout automatically.

All16 bounded analysis children reaped,62.0197061275childseconds total,0timeouts;
each4GiB/420s, at most3simultaneous in this cycle. The initial broad read-only
inventory was interrupted before research source/CAD creation (exit130); it is
not an analysis success and left no owned child. No RUNNING queue task. STOP
absent at handoff; source pins unchanged. No Git add/commit/push/history rewrite,
SDK, manager/security/save/guard/gate source edits, purchase, hardware,
credentials, provider choice, subagents or recursive launches.

Main: validation/integrated/primary_cycle8/summary.json.
Authoritative final counts/release: validation/integrated/primaryP1_cycle8_closeout/summary.json.
Supervisor exact-byte save request: runtime/goal_authorized_20261127_7/save_request7.json.
Save remains PENDING; no new commit is claimed.
