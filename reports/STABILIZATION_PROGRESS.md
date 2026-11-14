# Stabilization campaign log

Baseline: `830fd3d00186fd9e772be802c27de7ca2100ecde`.
Branch: `development/regrip-grasp-stabilization`. No push/history rewriting.
Original integrated evidence verified before mutations: 1061 hashes, zero errors.
Raw output root: `results/stabilization_20261115` (ignored).

## Residual isolation

- Added independent component force audit in isolated `models/stabilization` plugin.
- Per-component sum versus original recorder: exactly zero maximum difference in inspected static scenes.
- Root constraints excluded; translation and rotation denominators remain F/Layers and F*Length/Layers.
- Newton static continuation: 8-layer FREE/k1/k10/k100/base/halfdt/quarterdt/mesh/repeat physical equilibrium PASS.
- Tiny tension/length/pressure+cable physical residuals PASS under static solver.
- Original dynamic cold-start failures are preserved, not relabeled. Friction continuation history differs.
- Length-control Newton internal L2 stopping still emits failures despite meeting external physical infinity-norm criteria; reported separately.

## Memory

Two consecutive 120000-step minimal-scene runs in the same process completed, with unload/reload.
Live heap: 846256 → 166003056 → (unload)165848624 → 331165504 bytes.
FD count stays5. Memory plateau remains FAIL.
Official issue: https://github.com/sofa-framework/sofa/issues/6230
Official merged fix: https://github.com/sofa-framework/sofa/pull/6259 (2026-09-03).
Installed SDK not overwritten; private ownership containers not modified.

## Contact development

Distributed segment quadrature normal contact + regularized kinetic Coulomb friction implemented separately.
Actual18DOF force/Jx/Jv finite differences, SOFA stiffness/damping API, kFactor/bFactor, objectivity,
action-reaction and dissipation tests PASS for sphere/infinite-cylinder/box smooth branches.
This is not a static-stick law or a validated grasp certificate.
First opposing-finger scene incorrectly used two BaseMass objects: excluded as invalid physics.
First DiagonalMass port had template/link errors despite exit0: FAIL and preserved.
Corrected explicit Rigid3d,Rigid3d mass links pass scene loading; actual grasp sequence in progress.
