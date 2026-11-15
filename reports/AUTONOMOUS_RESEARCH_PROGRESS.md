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
