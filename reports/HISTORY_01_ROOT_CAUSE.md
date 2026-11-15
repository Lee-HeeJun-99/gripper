# HISTORY 01 — independent root-cause isolation

Campaign: `results/history_20261115`; baseline commit
`5dd3eafbbd459abcdc1c2c3ad9654f00c01545fa`. Original models and evidence remain
unchanged. New source is on `development/regrip-contact-history-convergence`.

PASS independent reproduction of two numerical mechanisms, **not** proof that
they uniquely explain the complete old three-finger error:

1. Original `ActiveIntervalContact` integrates a piecewise-linear, narrow
   material-history field with one Gauss rule across the entire active patch.
   A prescribed triangular elastic extension has exact integrated tangent force
   6e-6. Original q8/q16/q32 errors are 26.0019%,5.22859%,3.01725%.
   Splitting at material-cell boundaries gives 6.000000000000002e-6 for all
   three normal orders. Beam and ODE errors are absent in this test.
2. Interpolating vectors stored on differing normals then projecting onto the
   query tangent plane loses 3.9469503% squared norm in a prescribed ±.2rad
   example. Transporting both vectors first has zero loss in that example.
   This does NOT establish general energy-conservative interpolation.

New negative control also identifies an unresolved **birth-time error**:
flat box, skin .02, previous material point (0,1.03,0), current (0,1.01,.02).
Contact begins halfway through the step. Continuous prescribed motion gives
.01 tangential extension; the production v3 newborn rule returns zero because
it initializes at the endpoint. Smaller steps/material grids alter this error.
The new experimental `models/contact_birth/BirthIncrement.h` locates crossing
and differentiates the implicit root; its independent test gives .01 and
Jacobian error 2.746e-10. It is **NOT SOFA-integrated**, not used to relabel v3.

Evidence: `build_v3/unit/stdout.log`, `prescribed_reference_final/run/stdout.log`
under the campaign. The old failures quoted in BEAM06 remain historical;
current homogeneous-v3 measurements are in `history_evidence/convergence.json`.
History h=.005→.0025 and temporal refinement still fail existing criteria.

Development failures preserved: initial compile/API mistakes, fixed endpoint
history erasure, and missing Python `steps` in first campaign postprocessing.
Completed engine output was not overwritten: original FAIL exception remains in
`campaign_v3.json`; separate recovered metrics explicitly reconstruct exit0
from the failed short-circuit condition, with unknown wall time. The repeated
run independently persists the real OS result and exactly reproduces the state.
