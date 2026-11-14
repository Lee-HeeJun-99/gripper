# Prescribed pressure 마찰 연구

**독립 slider·초기 SOFA 선언 검사20/20 PASS; wire_jamming 강화 잔차 FAIL, 실제 진공 재밍 EXPERIMENTAL.**
순수 pressure/force 실험은 강화 잔차도 PASS. wire_jamming은 작은 구동력 정규화의
floor를 제거하면 tail residual.001457>1e-3로 FAIL이며 성능값으로 승인하지 않는다.
N_i=p*A_i, Fcap=mu*N_i, elastic-perfectly-plastic return mapping.
tributary area는 연결점 사이를 분할한 width8mm × length100mm의 가정이다.
정지/운동 mu동일, solver force/tangent 조회는 history를 바꾸지 않고 AnimateEnd에만 commit한다.
단일 slider cycle work balance5.55e-17, 소산 비음성·단조성 PASS.
pressure0 FREE 일치, high-pressure stick은 k1 탄성 결과와 일치, p/mu 변화,
30s ON/OFF/하중 cycle과 tendon 결합을 실행했다.
component energy는 전체 BeamFEM 에너지/구동 일/감쇠를 포함하지 않는다.
전체 closed-system energy audit, 분리된 정지/동마찰계수, 접촉 opening/법선압력 solve,
실제 PET mu·vacuum leakage·손상·실측 이력은 NOT RUN이다.
normal_k는 별도 작은 평면 bilateral confinement이지 vacuum solver가 아니다.
현재 cap=mu*p*A라서 마찰 제한만 관측하면 mu와 p를 독립 식별할 수 없다(수학적 모델 한계).


|실험|판정|처짐 mm|상대 잔차|최종 속도 mm/s|최대 회전 rad|
|---|---|---:|---:|---:|---:|
|off|PASS|0.01562819952|6.968969047e-05|2.127587673e-06|0.0003463971465|
|low|PASS|0.01560982114|4.259234524e-05|1.751535033e-07|0.0002579776206|
|high|PASS|0.01003086752|3.387809433e-06|1.935762485e-07|0.0002101203381|
|mu_low|PASS|0.015574448|1.97898447e-05|1.739299473e-07|0.0002513072157|
|mu_high|PASS|0.01546568419|9.919386475e-06|3.208497913e-07|0.0002726816501|
|on_off_cycle|EXPERIMENTAL|0.01548646497|0.0002163381141|5.452688963e-05|0.0003463971465|
|wire_jamming|PASS → FAIL (strict)|0.0003733903072|2.913998494e-05|3.099111097e-09|9.298030836e-06|


## 공통 범위 및 판정

모든 신규 수치는 연구 단위 F, mm, s의 시뮬레이션이며 실물 측정값은 없다.
원본 `plugin/`, `models/finite_rotation/`, `models/multilayer/beam.py`, 골든 데이터는 변경하지 않았다.
기존 45개 gate는 시작 manifest 무결성을 확인한 **이전 검증**이며 새 모델의 인증으로 합산하지 않는다.
신규 평형 판정은 sampled static residual <1e-3, 최종 병진/각속도 <1e-5,
tail relative drift <1e-4이다. 실패를 숨기기 위해 하중·재료·허용오차를 바꾸지 않았다.
평면 slider/선형 연결은 회전 <.005 rad 및 |qx|,|qz|<1e-8만 인정한다.
초기 v1의 nonzero-load residual floor 때문에 일부 tiny-cable PASS는 강화 감사에서 FAIL로 바뀌었다.
최종 판정은 residual_audit/strict_residual_retry가 우선하며 과거 raw의 상태를 수정하지 않는다.
Raw 위치: `results/integrated_20261115/`; 작은 증거: `reports/integrated_evidence/`.
`metrics.json`은 소스/바이너리 해시, 설정, 명령, 로그, 원시 상태 파일 해시를 포함한다.
PASS는 명시된 검사만 의미하며 EXPERIMENTAL transient의 프로그램 종료는 평형 PASS가 아니다.
