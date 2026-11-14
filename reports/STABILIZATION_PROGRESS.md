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

## Final campaign snapshot



|항목|이번 결과|
|---|---|
|잔차 회계|PASS: 실제 구성요소 합과 recorder 차이0|
|8층|static Newton 및 보상 합산 cold dynamic PASS; 표준 Euler 실패 보존|
|작은 wire/length/pressure|static 및 compensated cold dynamic PASS; 마찰 경로 차이 분리|
|2/4층 회귀|새 audit binary 실행 PASS|
|메모리|FAIL:2×120000step 후 live heap331165504bytes, FD5|
|공식 메모리 수정|PR6259 확인, 설치본/패치 실행은 미변경/BLOCKED|
|분포 접촉/마찰|C++ full18DOF/Jx/Jv/API/objectivity/소산 PASS, kernel 범위 한정|
|2핑거/free object|실제 실행 EXPERIMENTAL, 일부 조건 FAIL; 전체 파지 미인증|
|8층 fallback 탐색|15proxy,3Pareto, static-approved3/3; Optuna 아님|
|Optuna|BLOCKED,0Trial|
|SofaPython3|BLOCKED, 원본Python NOT RUN|
|전체 에너지|BLOCKED, BeamFEM API 미구현/감쇠 수지 미확보|


Details: FINAL,01..09,NEXT_TASKS.
