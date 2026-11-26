# AK collet conditional contact-wrench cycle — 2026-11-26

Starting HEAD: c5e3920d61babc661d4e04ac6b49a76caec08997. One actual analysis
cycle for AH_collet_and_axial_capacity, authorized_20261126_4 cycle0.
Supervisor local save PENDING; no worker staging, commit or new commit SHA.
Official RevAA and actual AK235 CAD/BOM remain unchanged.

Actual new model: scripts/ak_collet_contact_bound.py reads the AK input-hub
STEP and supplier dimensional contract. Minimum shaft radius2.494mm, actual
bore radius2.52mm, engagementY4.8..14.5mm. Latest possible flat startY1.75mm
precedes the entire engagement. Prescribed circular first-touch closure26um
still leaves0.588mm at flat center. This is NOT a solved hub deformation.
The D-flat is not a mating torque key in this circular first-touch model.
Nominal unclosed circular geometry has no shaft contact; loaded closure cannot
be inferred from nominal bore clearance or longer grip alone.

Finite axial/azimuth contact locations are admitted only where actual bore
material exists and the D-shaft retains its circular surface. Nonnegative
inscribed Coulomb traction rays balance all3force and3moment components, with
one unit total normal load and dimensionless unit shaft/face friction controls.
A centerline spring axial force and clutch torque are explicitly applied;
zero radial external load is a declared conditional boundary condition.
No bolt preload is equated to normal load. No material friction, pressure cap,
available normal load or safe tendon force is assigned. Point tractions can
concentrate arbitrarily; no finite elastic pressure field has been certified.
This tests one imposed wrench, NOT6DOF wrench closure.

48/96/192azimuth grids with16/32/64Coulomb rays and3axial positions produced
three actual LP states; exit0 and successful HiGHS optimality messages retained.
Normalized tendon/normal values0.209185935,0.211289655,0.212284614.
Independent analytic upper0.212311263 gives finest relative interval width
0.0125517%. Combined grid/ray refinement change0.470899% passes the predeclared
1% numerical check. This is NOT independent convergence in each discretization
variable, axial pressure convergence, physical contact or system convergence.

Independent scripts/verify_ak_collet_contact.py reconstructs forces/moments
from saved weights/points without importing the LP producer or using its saved
matrix for acceptance. Actual active-point BRep eligibility, nonnegative weights
(up to numerical1e-10), unit normal budget, circular Coulomb disks and analytic
upper bound pass all3states. Maximum independent residual5.568e-14.
A1% axial-traction corruption is rejected in every state (residual>=0.002835).
Input hashes pass. Initial verifier exits1 with PosixPath subscripting TypeError;
failed script/log/summary preserved in AK_contact_wrench_verify1_failure.
Corrected verifier exit0 in AK_contact_wrench_verify2. No physical solve retry.
Predeclared local output was renamed acceptance.json after execution without
changing contents to avoid the reserved criteria filename. Exact executed
producer snapshot remains unchanged; current runner uses acceptance.json.
No existing criteria.json was modified.

Actual outputs under validation/transmission/AK_contact_wrench1, independent
AK_contact_wrench_verify2, and preserved verifier failure. Input identities
were written before analysis. Logs and execution metadata retain4GiB virtual
limit,420s timeout and single-thread settings. No SOFA or Native simulation
was executed or claimed. The existing candidate readiness audit on actual AK
BOM/STEP identities (validation/integrated/AK_collet_release1) remains
INTEGRATED_NOT_QUALIFIED,25errors including22unqualified Stage2 criteria.
Its exit0 is not a release acceptance.

AH_collet_and_axial_capacity remains READY with unmet actual loaded contact,
elastic hub/bolt proof, material, motor axial, spring/friction and transient
maximum evidence. Do not repeat this normalized LP as a new cycle. Next actual
C track: AI_whole_palm_support, using whole AK geometry and real load ports;
then cover executable B actual_finger_load_ports within the three-cycle group.
No full Palm/Finger strength, force cap, hardware or digital release PASS.
All old failures and unrelated untracked CAD/BOM are preserved. No SDK, manager,
security/save controls, Stage3, hardware, purchase or remote actions.
No RUNNING tasks or owned analysis children remain. Save is pending manager
validation and explicit local save; the worker will exit after its manifest.
