# Experimental native contact observation

Read-only observation of public child constraint Jacobians and solver impulse
multipliers. Positions are physical rest+u, not displacement DOFs. CSV records
begin/free/accepted configurations separately; native collision uses the begin
geometry. On a fixed frictionless sphere, measured begin-stage body torque
about the sphere center is approximately2.2e-19 F mm; using later geometry
would incorrectly introduce a moment defect.

IMPORTANT: `sphere_force` in the raw v1 CSV is the PROJECTED Jacobian result.
A FixedProjectiveConstraint eliminates that sphere Jacobian. Its zero is NOT
a zero physical reaction. The assessor reports fixed reaction as null/BLOCKED,
not an action-reaction PASS. Candidate multiplier row count is NOT an active
contact count. Minimum vertex gap is not triangle closest distance, contact
area, penetration tolerance or wrapping angle. No projected zero reaction is
used to certify force balance.

The patched SDK has no built collision modules. Installed-SOFA trials rebuild
core, assembly and observer separately, with ldd audits; no installed collision
library is mixed into the patched process. This separate native hard-contact
law has mu=0 and buffer .01 mm. It is NOT the SDF normal compliance and cannot
certify changing-normal Coulomb history. Only backward Euler compliance is
enabled; BDF2/theta=.5 constrained history is explicitly unsupported.

Actual100/200/400-step .5s fixed-sphere tests execute but time convergence FAIL.
No grasp, wrapping, self-collision or free-object certificate is claimed.
