# Wrench geometry, cones and measured force capacity

Status: mathematical analysis **PASS**; two-finger full torque holding **FAIL**.
Actual three-finger research trials are separate; see compact campaign evidence.

`tools/closure_wrench.py`: G_i=[I;skew((p_i-c)/R)],R5mm. Singular values and left
nullspace are reported in normalized units. Ideal two point contacts are rank5,
unsupported torsion about the contact line. Actual distributed two-finger patch
is rank6, but rank alone is not force closure or finite-load support.

Eight-ray inscribed Coulomb cones use measured normals and mu.3. A strict positive
combination of all rays at zero plus cone rank6 verifies origin interior for this
polyhedral cone. Both unrestricted G rank and cone rank are required; μ0 regression
explicitly prevents falsely certifying closure from geometric rank6. Single-contact
left nullspace is complete. Nonnegative contact coefficients and per-point measured
normal force caps enter independent linear programs. This is fixed-patch capacity,
not ultimate structural capacity or a prediction of redistributed contact.

Actual two-finger patch: normalized rank6, cone-origin interior, but measured normal
caps cannot support ±Tz at5e-6 force·mm. Actual24s SOFA ±Tz tests fail: maximum
rotation .0188791644862rad and relative moment residual.93583841481. Other ten
same-condition force/torque holding subtests pass. No invented torsional spring used.
Higher cable preload.003 still fails; .01 exits the unchanged .005rad layer domain.

## Separate physical three-finger design

`models/closure_frame/FrameLayer.cpp` transforms the unchanged planar layer law
into fixed reference frames0,+120,-120deg aboutY. xlocal=R0^T xworld,
qlocal=q0^-1 qworld; wrenches Bf and tangent BJB^T. Pressure history commits once
in local coordinates. Energy/force/J/history covariance unit defect2.45865e-14.
This is not an arbitrary3D layer constitutive law; relative planarity limits unchanged.

Three actual100mm fingers, two layers each, same per-finger material/mass/cable,
increase total material/mass/cable count50%. Research root radius≈95.15mm is NOT
the proposed50mm body. Finger planar guides are explicit; object has no constraints.
Pilot+Tz: load5e-6, rotation.000246035599235rad, relative moment residual8.77998e-9,
relative force residual2.58610e-8; after24s zero contacts and finger rest error1.89543e-8mm.
Actual pilot patch rank6, strict cone interior and bounded LP feasible for all12
wrenches. This is not a substitute for measured12-direction dynamics/convergence.

Actual12-direction and convergence results are in `threefinger/gate.json`, with
each trial's load/config/source/binary/raw hashes. All design changes are separate
from original two-finger benchmark. No hidden object constraint or pose correction.

Important additional FAIL: whole-system root/guide reaction audit finds a Y moment
defect2.26294929813e-5force·mm at three-finger+Tz, normalized4.5258986; two-finger+Fx
global balance passes. Thus all12 local free-residual/holding/recovery checks do NOT
certify whole-structure moment balance. `balance_audit.json` explicitly separates
free residual, constrained reactions, internal resultant and external wrench.
Live per-field isolation is in `threefinger/field_balance/summary.json`; this failure
is not removed by a rank6/LP feasibility result or by increasing a denominator.

Independent live27960-step history at13.98s isolates the defect: BeamFEM Y resultant
−2.2629438920710246e-5; FrameLayer sums approximately1.94e-12,each cable torque
≤6.1e-18,contact Y torque3.95845e-20. The diagnostic reruns the actual histories,
not force evaluation with guessed/reset plastic states. Static R itself is a
reconstructed ForceField sum, not the linear solver's algebraic residual. No extra
ground torque or object pose correction is introduced to cancel the defect.
