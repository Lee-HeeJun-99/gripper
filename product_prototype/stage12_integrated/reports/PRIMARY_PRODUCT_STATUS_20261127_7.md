# Latest primary P1 engineering — 2026-11-27, pending Supervisor save

Started at actual HEAD4a59642146745ea0793dae8e8809215e3425acbf. Selected queue
ID goal_primary_module. ONE primary is now implemented in
cad/exports/primaryP1_open9/summary.json,69actual parts with STEP assembly,
per-part references and nominal BOM. PRIMARY_PRODUCT.json is the restart state;
CURRENT_CANDIDATE.json points to it. Failed AO254 and adopted AA304 remain
preserved. This is a separate minimum Stage2 module, NOT integrated release.
Actual cycle result: validation/integrated/primary_cycle1/summary.json.

Actual CAD changes: open C-frame with root shelf and service window; split
rectangular1101 motor cradle; four-M5 finite Ground plate; source1996 hub/fourM3
and real2mm drum mounting web; AX wide Rail tabs; new Root-back mounting tabs
with RF axes moved59->64mm; original distal PET sliding and root-only pins.
Reused factory-nipple open pocket/removable cap is reflected to top of spool,
with clockwise11.25mm-radius C1 winding. No special Idler/rivet or fictional
physical limiter. Original3Finger/cartridge/jamming CAD is preserved. Current
origin-centered F0 motor CANNOT be simply120degree-duplicated: same-revision
3Finger layout/100mm target and optional dock reinstatement remain unqualified.

Final actual checks: all69reimported single valid solids; aggregate STEP69part
volume/centroid/inertia signatures independently match; no nominal volume
interference.81ordered finite insertion/fastener samples,278actual Boolean
comparisons and two nominal RF driver approaches clear.13full constant-length
cable/rotor poses0..60deg clear; wire solids valid and single-layer. These are
sampled nominal checks, NOT CCD, tolerances, thread tightening or full Stage1.
Independent closed-STL/volume, complex-step vs geometric virtual work, saved
load reproduction and perturbed-tension rejection pass bounded scopes.

Correct C1 stroke24.0671209057mm.183conditional100g-shared-three-Finger rows
(mu .2/.4/.8, typical prescribed-curvature stiffness) require .9284975495..
4.5036984622N and .0104455974...0506666077Nm.45rows FAIL general.4A current
recommendation; ideal linear speed screen alone passes. These are conditional
requirements, NOT actual finite Finger/grasp equilibrium, minimum material
allowables, a continuous motor rating, protected peak or capacity. Scalar
prescribed energy identity is NOT whole-system stored-energy closure.

Actual entire frame P1 tetrahedra4/2/1.5mm:19,562/77,367/124,820elements,
unit vertical compliance1.8690886372e-8/3.5979033873e-8/3.9573572682e-8m/N.
Independent saved affine energy/force/moment/residual and perturbation tests
pass. Mesh convergence FAIL: base-to-finest52.769272%,middle9.083180% vs1%.
Uniform+Z load uses inscribed subsets of actual RF nut footprints; supports
are four actual M5 contact patches with an explicit rigid/preloaded/stuck
connection assumption. Ground plate/bolt compliance, actual full root wrench,
motor counterpart, material minima and contact/preload remain unsolved. This
is a conditional actual-frame component reference, NOT system strength.

Failures preserved in original unique tags and failure_index.json: initial
spool-wire .543062mm3 and cap-wall16.2mm3 interference; invalid groove BRep;
serialization exit1 with original zero-byte partial loads.json; RF installation/
tool collisions with original transverse clamp screws; disconnected drum
adapter; wrong winding's .284850relative virtual-work and1.57821% wire-volume
FAIL; wrong half-turn nipple .835920mm3 overlap. Old31.221389mm stroke and
associated counterclockwise load results are INVALID as physical requirements.
Final9 corrects geometry/winding; no historical PASS/FAIL was overwritten.

Candidate readiness remains INTEGRATED_NOT_QUALIFIED(25errors); unchanged
baseline integrated gate exits2(24errors). ALL22system gate IDs remain
UNQUALIFIED, each with concrete reason in models/primary_system_gate_state1.json.
No gate/criteria/manager/security/save source changes; ledger pins verified.
SOFA runs0, no Stage3/purchase/hardware/SDK/provider selection/subagents/Git
write.27recorded engineering children completed/reaped,216.294child-seconds,
4GiB/420s each, no timeout; queue has no RUNNING tasks, no owned child remains.
STOP absent. Supervisor exact local save PENDING; no git add/commit attempted.

Concrete next ID: goal_primary_operating_window. Continue THIS P1: extract
actual root/terminal pin/slide ports; reuse existing finite/extensible/contact
kernels for separate Rail/PET finite-load continuation plus object-normal and
correct C1 cable virtual work, then recover actual terminal/root reactions.
Preserve frame mesh FAIL, motor current FAIL and material/connector/protection
unknowns. Do not return to AO height/order scans, adopt coupon loads as demand,
upsize motor before demand, or mark all geometry/system gates PASS.
Save request: runtime/goal_authorized_20261127_7/save_request0.json.

