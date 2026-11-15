# GRASP 02 — 접촉 수렴성

**FAIL: 공간 접촉 수렴성 미확보.** dt·반복 및 일부 동일 접촉 간격 메시 비교는 PASS지만 전체 파지 인증에 사용하지 않는다.
모든 아래 값은 실제 SOFA sphere +X, F=1e-6, μ=.3, alphaMass=2, dt=.0005,
100mm/대향2핑거/핑거당2층, 장력.001, 압력.001, hold6→14s의 최대 물체 이동량이다.
접촉은 beam centerline+skin=.1mm SDF 적분으로 실제 3D 필름 표면이 아니다.

| beam 노드 / 선분 subdivisions | 이동량 mm | 실행 |
|---|---:|---|
|11/8|0.00048237948651319584|완료|
|11/16|0.0009586270711281486|완료|
|11/32|0.0006765220193187815|완료|
|21/16|0.0006711276278394962|완료|
|21/32|0.0008292860671588187|fast v4 완료|
|41/16|0.0008250694720871451|fast v4 완료|
|41/32|0.0008949877748140363|fast v4 완료|

samples=q는 각 beam 선분의 q개 구간/q+1개 점이며, 전체 q점으로 오해하지 않는다.
11/32와21/16은 동일한 물리 간격에서0.7974% 차이,21/32와41/16은0.5085% 차이.
반면21/16→21/32는23.566%,41/16→41/32는8.474% 차이.
진단용1%선 아래에 들지 않아 적분점 수렴 FAIL. 오차 감소의 일부 경향은 있지만 비단조 좁은 접촉 패치의
활성점 변화가 지배한다. 현재41/32도 연속해로 승인하지 않는다. 허용오차를 늘리지 않았다.

dt절반(11/8) 이동.0004825802882351127mm, 상대차.0416273%; .1% 진단선 PASS.
v1→v4 동일식 최적화 후 repeat 이동량 bit 동일; 반올림 수준 잔차 차이만 존재.
초기21/32와41/16은240s TIMEOUT을 보존했다. AD1 등가 fast path/분리점 AD 생략 뒤
동일 수학 모델·물리 조건으로 최대480s bounded 실행을 완료했다. dt나 물성 완화가 아니다.

법선강성 .0005/.002, μ=.001/0, x94.5/110mm, radius5.01mm, baseZ5.5mm 대조군도 수행했다.
각 설정/로그/실패는 `results/grasp_20261115/trials/`, 비교는 `gate.json`과 `reports/grasp_evidence/measured_trials.csv`.

## 독립 실제 표면 prototype

`scenes/grasp_native_surface.py`는 SOFA triangle/line/point collision, RigidMapping, FreeMotionAnimationLoop,
BlockGaussSeidelConstraintSolver, FrictionContactConstraint를 실제 실행한다.
기존 SDF 커널과 분리했으며 연구용 너비8/두께.2 skin은 Beam 등가 A/I에 맞춰 보정된 실물 기하가 아니다.
v5 3600step/1.8s,180개 상태, 최대 constraint rows6; 매스텝 반력 진단의 nonzero는1step뿐이고 최대 λ=1.9520517436587522e-7.
샘플된 λ는0이었다. 따라서 충돌/일시 응답 관측은 가능했으나 지속 접촉·정지마찰·파지 PASS가 아니다 (**EXPERIMENTAL**).
λ의 물리 힘 단위/Jᵀλ 전체 균형, 접촉면 수렴, 전체 시퀀스는 NOT RUN.
초기 구 API/누락 SciPy/초기화 오류·SIGFPE 실패를 지우지 않았다. 마지막은 source snapshot을 고정한 실행이다.

다음: SDF 경계 교차 위치를 찾아 활성 구간을 분할하는 적응 적분 또는 제대로 보정된 유한 접촉면 모델,
동일 공간 간격의 독립 mesh/q 증가, 접촉 반력 단위·수렴 검증. 단순 q증가만 무한 반복하지 않는다.
