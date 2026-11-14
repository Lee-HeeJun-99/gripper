# 04 — V109 FREE 회귀

이번 실행: `results/revalidation_20261114T132734Z`. 시작 커밋 `8ee78f0c84d042812537655583cb98ed037f310e`, 검증 중 dirty=true. 별도 브랜치와 소스/바이너리 SHA256으로 추적한다. 과거 `results/physics_validation`은 회귀 비교 인용에만 사용했고 이번 gate의 성공값을 재사용하지 않았다.

**PASS**: 최종 clean-build 관측기로 두 번 독립 600스텝 실행. CSV는 byte-identical이다.
dt=.0005 s, t=.3 s, 처짐 0.041213791606346278 mm,
최대 X slip 0.00082280720342708946 mm,
끝단 vz -0.014380704053554549 mm/s.
허용오차 `1e-10 + 1e-6*abs(golden)`를 유지했다. 작은 0 근처 값에는 절대오차 바닥이, 큰 값에는 1 ppm 상대오차가 적용된다.
실제 차이가 이 예산보다 매우 작아 현재 비교에는 적절하며 허용오차를 완화하지 않았다. 이는 물리 정확도나 dt 수렴성 인증 자체는 아니다.

| 전체 600개 시점 지표 | 최대 절대차 | 상태 |
| --- | --- | --- |
| time_s | 2.22045e-16 | PASS |
| tip_deflection_mm | 1.38778e-16 | PASS |
| tip_velocity_z_mm_s | 1.41553e-14 | PASS |
| max_mapped_movement_mm | 2.25514e-16 | PASS |
| max_rigid_movement_mm | 2.25514e-16 | PASS |
| mean_abs_rotation_quat_xyz | 3.57787e-18 | PASS |
| max_x_slip_mm | 0 | PASS |
| max_y_rel_mm | 0 | PASS |
| max_z_rel_mm | 2.22045e-16 | PASS |

AST로 원본 장면의 상수·초기 위치·topology·하중을 추출하여 XML의 질량, E/nu/radius,
고정 루트, 하중 노드, 감쇠, solver, mapping과 비교한 14개 구조 검사가 모두 PASS다.
원본은 시각화/불필요 iterative 플러그인과 Python Recorder가 추가되어 있고 XML은 native 관측기로 대체되어 있다.
이 차이를 물리 일치로 가정만 하지 않고 골든의 가용 지표로 검증했다.
**NOT RUN**: Windows의 모든 22노드 raw 위치/속도 벡터와 직접 비교. 제공 CSV에 raw 벡터가 없고 파생 지표만 있어 비교 자료가 부족하다.
모든 raw 벡터를 비교했다고 주장하지 않는다. 이번 raw 벡터는 별도 보존했고 root/mapping/유한값/시점 검사에 사용했다.
원본 Python 직접 비교는 09의 BLOCKED 항목이다.
실행 명령과 설정은 `results/revalidation_20261114T132734Z/physics_release/baseline/command.json`, `scene.scn`, `comparison.json`.
0.3초는 여전히 평형이 아니므로 이 값을 강성비의 분모로 사용하지 않았다.
