# Autonomous research log

Baseline63970172ad196e0add3ad42a67ccaee4c7a8975e,clean worktree; requested branch
created. Actual environment remains Ubuntu22.04.5/GCC11.4/CMake3.22.1/Python3.10.20.
Existing birth assessment reproduced and1845raw/source/binary hashes passed.

## Hypothesis1 — state/measurement discretization mismatch

Inspection: old `compute` integrates plastic return at interpolated active
Gauss points; `commit` instead returns and stores nodal material states.
This does not prove an implementation bug,but dissipation measured at a different
state discretization may not represent the actually committed plastic flow.

Selected contrast: fixed material-coordinate midpoints,with force/return/Commit
and dissipation at the same immutable reference points;no history interpolation,
no zero boundary anchors. Normal active-interval Gauss and constitutive birth/
Coulomb/transport kernels remain unchanged. This is an independent numerical
model,not a replacement or a claim of a new exact continuum solution.

Planned falsification: analytic uniform plane slip,actual field Jacobian/API,
Commit/query purity,then same physical three-finger profiles and independent
history/mesh/time tests. Spatial integration error remains and must be measured.
No grasp optimization is authorized by unit success.

## First measured results

New v1 compilation failed in test code(unqualified pose helper);v2 unit initially
compared separately accumulated AD/scalar totals for exact equality instead of
checking the before/after state of a pure query. Corrected the assertion to its
actual contract,not a physical gate. Both failed logs remain. v3 source snapshot
and clean build pass;analytic plane D=.000051,actual field FD6.84e-10,API/query/
Commit checks pass. First failed test-source snapshots were not archived before
correction;their reconstruction limitation is explicit. Subsequent snapshots
are automatic before build. No claim of early failed-source certification.

Prescribed moving Sphere contact(no Beam or ODE) identifies an actual energy
representation jump at old-model Commit:at h.005/200steps signed sum-1.27181e-7;
new material points give about-4.4e-20. Old jump quadruples with doubled spatial
spacing and doubles with doubled step count in this test. New queried plastic
and actually committed plastic match. This supports the mismatch mechanism but
does not by itself establish the full3finger cause or global energy closure.

Actual4s profiles31.16s(coarse)and49.56s(finest) justify four bounded history
runs,all4GiB/480s. Their full convergence results are still under evaluation.

## Measured SOFA contrast and priority update

All four history runs finished. Immutable material points make actual committed
plastic return and recorded plastic return identical,including birth and death
counts. Same-hold cumulative loss differences are .129703%,.279753%,.049621%
for h=.01/.005/.0025/.00125,all below the original1% line. Motion differences
are4.61737%,1.01697%,.0300247%;the first two remain FAIL. Thus the hypothesis
is supported for the loss/state mismatch,not as a complete convergence cure.

Repeated fine run has exactly identical hold motion and loss.11→21→41nodes
still gives4.95984%,2.80102% translation differences,FAIL1%;rotation and loss
differences are smaller. Local hold force/moment gates pass,not global grasp
certification.24s base and fine-repeat recover/release;18s cases cannot certify
the complete24s sequence even though their local hold gate passes.

dt-half on the fine history has motion difference.0977366% and loss difference
.0999735%,both narrowly under.1%. A4s quarter-dt profile151.79wall seconds
predicts683.07seconds for18s. One bounded900s exception,4GiB,was selected to
test whether that borderline result is robust.41node profile133.92seconds
similarly justified a single900s run,which completed in635.76seconds. No
unchanged failed high-resolution campaign was blindly relaunched.

## Independent falsification and partial energy

Prescribed geometry calls actual old/new ForceField APIs with no Beam/ODE.
New maximum absolute pre/post Commit energy jump8.70e-20 vs old1.02e-6;
new queried/committed D agree exactly. Both old and new loss converge below1%
on this simpler path,so it does NOT prove every old full-model error has one
cause. Endpoint work residual decreases with smaller dt but remains nonzero.
It is not labeled friction or fitted numerical heat.

A seeded10000step scalar spring-slider test verifies the DERIVED identity
W_endpoint−ΔU−F1Δp=.5k(Δe)^2 with max residual1.02e-17. This scalar capacity
model includes no vacuum-chamber work and cannot close global SOFA energy.
Actual native-driver birth/no-contact scenes pass;resolved through-chord
contact is explicitly rejected as expected,not accepted as physical success.

## Next hypothesis: contact centerline interpolation

Fixed cubic cantilever geometry gives linear-centerline normal-integral errors
4.834%,1.468%,.1049% at11/21/41nodes against independent SciPy quadrature.
The prescribed cubic Hermite representation reproduces that cubic. Offline
reconstruction of actual SOFA states gives linear/director-Hermite normal
integral differences3.085%,.1008%,.04865%;these are NOT re-solved equilibria.
This motivates a kinematic investigation,not an attribution of all remaining
Beam nodal-solution error to interpolation.

Implemented a separate objective director-Hermite virtual-work pullback kernel,
including nodal torques,geometric tangent and left-SO(3) connection.60states
pass FD1.56e-9,normal-energy derivative3.47e-10,objectivity6.11e-16 and
force/moment1.73e-17. Sparse analytic assembly agrees with dense AD2 reference
within2.78e-17. It is NOT integrated into SOFA contact yet;linear current
campaign remains unchanged. No production speedup is claimed without profiling.

## Preservation correction and regression

During tool addition an existing tools/research_trial.py name was accidentally
reused. Restored its exact6397017content and moved new runner to
tools/autonomous_trial.py. Hash-based preservation test passes. First campaign
commands using the old path refer to the intermediate621266c source revision;
reproduce via the new runner path. Historical physics/raw/golden were not edited.
The restoration is retained in Git history,not concealed by rewriting commits.

Python89tests and3existing C++ suites pass;new actual Beam61state and dense100
equivalence checks pass. Two independent600step FREE golden runs pass all
9recorded metrics with unchanged1e-10+1e-6|reference| tolerances. The original
45physics gates are not rerun or expanded into new-contact certification.

## Final temporal cross-check

Quarter-step completes679.151s/144000steps,actual queried/committed D equal,
local hold force/moment gate PASS. Half→quarter motion.015950% and loss.074528%
pass.1%. However base→quarter accumulates.113702% motion and.174427% loss,
both FAIL.1%. Added the nonadjacent cross-check instead of presenting adjacent
PASS as full base-dt qualification. Hence time remains incompletely qualified
alongside the independently unresolved spatial error. Quarter-step detachment
inventory relative differences also remain large;no global energy claim.

## 2026-11-16 actual continuation,not a completed research objective

Termination audit:the previous turn had no recorded session/resource failure;
all children had exited normally. Ending at the campaign checkpoint was the
agent's own premature decision,not a forced stop or achieved final objective.

Implemented independent models/curved_contact with the verified Hermite
virtual-work map,physical nodal torques,consistent spatial Jacobian and a
conservative4/27director sag envelope. Both normal and tangent use immutable
material midpoints;the prior models/builds/raw remain unchanged. API FD6.27e-10,
90actual ForceField covariance/force/moment/Jacobian checks pass. Independent
curved normal integration reference converges. Initial CMake dependency and
namespace compile failures are snapshotted in new campaign build_v1/v2;v3passes.
The copied v3unit test has a nonphysical multi-character-newline warning;
it is not claimed warning-free. No physical threshold was changed.

Actual18s11/21/41runs completed252.37/394.69/722.51wall seconds. Keeping the
inherited all-node layout gives6.0498%/2.6847% translation differences,FAIL1%.
Hold local force/moment gates pass. Half-dt motion.077264% and loss.073839%
pass the adjacent.1%line,not a complete temporal certificate.

New cause found in source/XML audit:LayerNetwork stiffness is explicitly a
POINT stiffness,while empty connectorIndices creates all nonroot nodes.
Refinement changes10→20→40connectors at unchanged k=1 and kn=.001;total
elastic couplings double. Cable guides also change11→21→41. These old
comparisons are therefore not pure Beam refinement at fixed physical layout.
Their numerical FAILs are retained,not rewritten. Added fixed10mm connector/
cable-guide controls and separate one-factor ablations,now actually running.
No stiffness scaling or fabricated compensating force is used.

Also testing strict-FP native ISA build(no fast-math,reassociation or FMA
contraction)against actual generic raw states before any cost-qualified
quarter-step run. At most4long physics children;each4GiB/default480s or
profile-qualified single900s attempt. No automatic restart is installed.
