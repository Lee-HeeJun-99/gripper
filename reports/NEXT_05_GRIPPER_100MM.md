# NEXT 05 — 100 mm 연구 확장

기준 60f41cf; 개발 코드 커밋 `96174a2ec8c1b75c2f11f607bdecb1d986b148f2`. 실행 중 dirty 상태는 개별 JSON에 그대로 기록했다.
원본/골든 보존, push 없음. 증거: `reports/next_evidence/`; raw/명령/전체 로그: `results/next_phase/`.


**EXPERIMENTAL**, 수치 검증된 길이 확장이며 실제 그리퍼 제작/성능 검증이 아니다.
기존30mm 골든/하중/단면은 그대로 보존했다. 별도 비교 실험은 양쪽 길이에 같은 F=1e-6를 적용했다.
이는 작은 회전 영역에서 길이 효과를 분리하기 위한 연구 하중이며 실제 파지 하중 사양이 아니다.
E250, 동일 원형 등가 A/I, 층간격.4를 상속했다. 동적 총질량2e-5는 고정 연구값이며 100mm 실물 질량으로 보정하지 않았다.

| SOFA case | tip mm | X slip mm | relative residual | status |
| --- | --- | --- | --- | --- |
| L30_free | 0.000421874999917 | 8.43750000001e-06 | 2.01083e-05 | PASS |
| L100_free | 0.0156281995228 | 9.37679308493e-05 | 6.96897e-05 | PASS |
| L100_on | 0.00929173481387 | 1.01808339537e-07 | 8.05308e-05 | PASS |
| L100_repeat | 0.00929173481387 | 1.01808339537e-07 | 8.05308e-05 | PASS |
| L100_halfdt | 0.00929173511291 | 1.01808616648e-07 | 0.000265787 | PASS |
| L100_mesh | 0.00929186159859 | 3.36300317372e-07 | 7.35476e-05 | PASS |
| L100_extended | 0.00929173202065 | 1.01808673492e-07 | 0.000356785 | PASS |
| finite_L30 | 0.0301894247801 | 0.000226422777274 | 2.12957e-07 | PASS |
| finite_L30_halfdt | 0.0301894247801 | 0.000226422777914 | 4.24975e-07 | PASS |
| finite_L30_mesh | 0.0301887492211 | 0.000228122266851 | 3.94345e-07 | PASS |


100mm FREE/ON 강성비 **1.68194635725**, 같은 평형/하중에서 계산했다.
FREE 길이 처짐비 37.0446210983, EB cubic 예측 37.037037037.
dt/시간 .1%, 메시1%, 반복1e-10 상대 기준 유지. 21노드는 동일10개 물리 연결 위치를 사용했다.
전체 small-planar 회전<.005와 기존 속도1e-5/잔차1e-3/drift1e-4 평형 조건 유지.
모든 표의 수치는 새 SOFA 실행 측정값이며 해석 추정이 아니다.

정적 연구 FEM 39개(L30/60/100, 1/2/4/8층, k0/1/100 + wire/contact/Timoshenko) 및 20개 제한 설계 열거 수행.
아래는 **독립 FEM 계산값(SOFA 아님)**:

| case | tip mm | small rotation |
| --- | --- | --- |
| L100.0_layers1_k0.0 | 0.0312500000002 | True |
| L100.0_layers1_k1.0 | 0.0312500000002 | True |
| L100.0_layers1_k100.0 | 0.0312500000002 | True |
| L100.0_layers2_k0.0 | 0.0156250000002 | True |
| L100.0_layers2_k1.0 | 0.0096892481444 | True |
| L100.0_layers2_k100.0 | 0.00927385010975 | True |
| L100.0_layers4_k0.0 | 0.00781250000009 | True |
| L100.0_layers4_k1.0 | 0.00276747479468 | True |
| L100.0_layers4_k100.0 | 0.00236523339941 | True |
| L100.0_layers8_k0.0 | 0.00390625000004 | True |
| L100.0_layers8_k1.0 | 0.000848248610394 | True |
| L100.0_layers8_k100.0 | 0.000594485382216 | True |


와이어는 T*e 이상적 팁 모멘트, 접촉은 알려진 gap의 평면 penalty이며 각각 해석해 단위 검사 PASS.
압력 마찰은 prescribed N=p*A, cap=mu*N, elastic/plastic return mapping으로 별도 구현했다.
constant-pressure load loop에서 비음수 소산/잔차 및 단일 slider work balance를 검사했다.
JSON 상태 중단/재개와 모델/상태 해시 불일치 거부도 실제 Python 계산에서 검사했다(Optuna/SOFA 재개 아님).
±20% 민감도와 A∝t,I∝t³의 두께 일관 변화는 가정된 탐색 범위이며 실측 신뢰구간이 아니다.
L/E/I/load 영향과 k의 포화 민감도를 따로 기록했다.

미확정 물성·와이어 경로·진공압·마찰·밀도·체결은 `models/gripper_100mm/assumptions.json`의 null로 보존했다.
반지름50mm/1~8핑거는 목표 구조만 기록했다. multi-finger assembly/카트리지 외피/3D tendon/3D object contact/
seal·압력 분포/실물 안정 파지는 **NOT RUN**. full pressure-work thermodynamics나 PET 성능을 검증했다고 주장하지 않는다.
