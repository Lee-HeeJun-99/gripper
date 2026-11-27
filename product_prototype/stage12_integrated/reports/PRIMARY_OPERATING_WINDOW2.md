# Latest P1 actual finite-load continuation — 2026-11-27, pending Supervisor save

Actual starting HEAD cfcf3fd71a91585b230a9e72d6e1aaef1c34889c.
Selected exact queue ID goal_primary_operating_window. ONE primary remains
primaryP1_open9: actual69parts, Motor -> stock1996 hub/fourM3 -> Drum ->
whole factory cable -> terminal/AX Rail/PET -> Root/RF -> open frame ->
fourM5 -> finite Ground plate. Failed AO and all3Finger/cartridge/jamming
extension originals are preserved. Actual changed CAD this cycle: NONE;
all STEP/BOM/assembly bytes stay fixed. This is ACTUAL_PRODUCT_VALIDATION,
with changed finite product boundary/contact/load implementations, not a
new design-solid claim. Full result: validation/integrated/primary_cycle2/summary.json.

Actual STEP port/section extraction verifies Root lowerZ=-7mm, Terminal
upperZ=-84mm:77mm free Rail, not the reused88mm endpoint datum model.
PET remains86.2mm with separate axial strain/free distal sliding and actual
finite walls. Both actual Rails retain .6mm2 area/.002mm4 Iyy per strip.
Finite circular-arc Rail/PET reuse existing rod/material/contact kernels;
actual cable force and eccentric terminal moment enter the energy. Rigid
Root and terminal Rail grips, typical moduli, planar symmetry and frictionless
material-pair normal witnesses are conditional assumptions, not certified joints.
No general-purpose simulator/SDK/physical criterion change was made.

12final8/16/32 states at .2/.5/1/2N are saved. Independent complex-step
kinematics/energy/virtual work, Jacobians and actual deformed PET/Rail/Terminal
BReps accept ONLY the three .5N reduced states under all current checks.
Their normal force is .1561263465/.1562342032/.1562614854N;8->32 error
.0864825%<1%. Finest force-equivalent residual1.93809e-15N. This normal is
below the CONDITIONAL100g shared-three-Finger mu.8 requirement .4086104167N;
no payload,100mm free grasp, finite friction/material minimum or operating PASS.
Typical nominal finest Rail face strain .0005854331 (112.9886MPa) and PET
.0009331868 (3.26209MPa) are NOT strength/allowables/notch/fatigue evidence.

At .5N, required frame Root force(X,Z)=(.0862697092,.4950769145)N and
Y couple .00339395866Nm; motor cradle force=(.0699917762,-.4950769145)N,
Y couple .005625Nm. External frame total=(.1562614854,0)N and Y couple
-.01513697027Nm. Port wrench sums independently balance; these are required
external resultants, NOT solved bolt/clamp/bearing/Ground reaction distributions.
Four saved32element loaded Terminal/swivel/cable/rotor poses actually execute
104Boolean comparisons: valid single-solid,constant-volume,single-layer cable
and rotor clear. Failed equilibrium states stay failed despite pose clearance.

Failures are immutable in failure_index.json. Initial import exit1 retained;
existing local OCP path reused with no install. Numerical-derivative88mm
endpoint trial TIMEOUT420s killed/reaped, partial rows untouched. Analytic
Jacobian/active-equality Newton candidates retain all original inequalities
and independently recover nonnegative multipliers; no QR cone equivalence
or numerical success is promoted to product acceptance. Actual1N penetration
.1602474444mm3 is independently real (inner-width lower bound .159509942).
Adding all actual Terminal wall range and feature roots reduces finest1N
penetration to1.2524165234e-5mm3, STILL FAILS1e-8.8element1N feature gap
-5.1372538nm FAILS1nm.16element2N branch/divergence and2N mesh/actual-BRep
FAIL,4.5N failed/invalid states all retained. No tolerance relaxation or CAD
machining is justified by an unresolved corner normal-cone/numerical conflict.

Newly qualified system gates: NONE. ALL22remain UNQUALIFIED, with updated
reasons in models/primary_system_gate_state2.json. Original frame mesh FAIL,
45/183 prescribed-current screen failures, source minima/connector/protection,
full3Finger layout/Stage1, contact/history/time and global-energy barriers remain.
Unchanged read-only integrated release exits2 with24errors. SOFA runs0;
no dt/whole-system energy qualification. No Stage3/purchase/hardware/SDK/
provider/credential/subagent/manager launch/Git write. Source pins verified.
22analysis children reaped;1267.324022child-seconds,
one preserved420s timeout; each4GiB/420s and <=4concurrent long children.
No RUNNING queue task or owned analysis child remains. STOP absent.

Concrete next exact ID: goal_primary_terminal_feature_contact. Continue THIS actual P1
from32element1N state and frozen material witnesses. Resolve finite lip seam/
corner face-normal cone; recheck feature gaps AFTER Newton and actual
inscribed/outer BRep before demand roots or motor upsizing. Preserve all
failed coarse/2N/4.5N cases; do not return to AO scans or isolated coupons.
Supervisor save request: runtime/goal_authorized_20261127_7/save_request1.json.
Supervisor exact local save PENDING; no git add/commit attempted.

