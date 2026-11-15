# BEAM08 — independent native surface experiment

Status: **EXPERIMENTAL.** `scenes/beam_native_surface.py` uses Triangle/Line/Point,
RigidMapping,FreeMotionAnimationLoop,BlockGaussSeidelConstraintSolver and
FrictionContactConstraint. New beam and Frame plugins were separately rebuilt
against the INSTALLED SDK. The patched SDK lacks collision libraries, so its
libraries were NOT mixed with installed native-contact binaries.

Finite film collision width8mm/thickness.2mm are explicit research assumptions;
they do not recalibrate the circular beam EA/EI into a measured film section.
Hard normal compliance/contact buffer.001mm differs from the SDF penalty law.
Their displacement numbers cannot be treated as identical physical-condition
validation. Native and SDF contact forces are not simultaneously applied.

Actual sphere +Tz trial36000steps/18s at surface latitude12 passed sustained
contact and object tail residual subchecks: force2.29922344507e-5,
moment1.37132977325e-5,<1e-3,minimum3positive normal contact multipliers.
1800frames archived. Physical reaction uses Jᵀλ/dt, not λ as force or the number
of candidate rows as active contacts. `native_lat12/recovered_result.json` is a
read-only recovery after NumPy bool serialization failed; expensive original
raw/logs were not overwritten or rerun to hide this tool error.

Additional projected-only root/guide accounting in `native_lat12/24/balance.json`
initially FAILS with normalized missing moment1.0. The parent constraint matrix
already projects away guide DOFs; its impulse cannot recover blocked reactions.
This was an observer incompleteness, not evidence of an extra beam torque defect.

Separate `native_physical12/24` reruns record ORIGINAL child-surface Jacobians.
Their Jᵀλ is mapped through actual point arms to nodal forces/torques BEFORE
projective removal. Sparse unused trailing columns are zero-padded; the first
unpadded attempts `native_unprojected12/24` emittedERROR and remain FAIL.
No external-load cancellation or artificial torque is inserted into physics.
Free mapped impulses agree with the parent to6.857e-19.
Corrected global force residuals3.71699e-5/3.65374e-5 and moment
.000311609266/.000316213571 PASS1e-3. Corrected12mesh actual state hash is
identical to its original experiment: observer accounting changed,not dynamics.
Latitude12→24 hold-displacement difference.0000968413%,rotation increment
.000137924%,below1% diagnostic. This is one sphere-surface refinement result,
not complete Beam mesh/dt/contact-buffer/native-law convergence.

Raw/result/balance files and `native_surface_comparison.json` distinguish failed
first audits,failed sparse mapping attempts,and corrected bounded subchecks.
Cylinder,box,plane and all12wrench directions with NEW beam are NOT RUN.
No new native24s release/recontact/control campaign or installed-engine memory
qualification is claimed. Prior native calibration remains historical evidence.
