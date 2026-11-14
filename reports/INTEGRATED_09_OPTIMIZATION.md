# 설계 탐색 및 승인 범위

**정적 EB 결정론적 grid30개 + SOFA Pareto 재검증; Optuna/통합 파지 최적화 BLOCKED.**
검증 완료 후보6/6. 최적성은 이 discrete grid에 한정하며
실제 제작 최적 설계·전역 최적·진공 파지 최적이라고 주장하지 않는다.
각 후보의 실행 로그/설정/모든 gate는 candidate_validation/<id>/decision.json에 있다.
기존2목적 stiffness/slip와 별도 complexity 목적을 분리해서 해석한다.
k100은 이 grid 상한이며 k포화의 전역 증거는 아니다. 저k와10→100 차이는 study전체표에 남는다.
조건수는 혼합 mm/rad 좌표의 raw 행렬값으로 차원독립 안정성 인증에 사용하지 않는다.

별도 independent EB FEM +/-10% OAT15개 민감도 연구(실측 불확실성 분포 아님):
4층k100의 h(centroid gap) 변화에 강성비2.95890..3.60769,
A변화3.11745..3.43991, I변화3.13171..3.45842,
E변화3.28137..3.28393, k변화3.28123..3.28381이다.
고k 부근 k보다 geometry/EA/EI에 민감하며 독립 A/I 변경은 실제 단면 형상의 제조가능성 보장이 아니다.

|후보|층/연결점수|SOFA 강성비|재구성 미끄럼 mm|승인|
|---|---|---:|---:|---|
|11e142755fb0|4/5|3.217402811160416|5.914701862464428e-07|True|
|2a22d1e0c8d5|4/2|2.8629000180302024|3.158468772516093e-06|True|
|3ef989452185|2/2|1.6117577733717148|6.240715222620045e-06|True|
|8cc7560b0f7f|2/5|1.671920664297129|1.1414361600080698e-06|True|
|a971778ce347|4/10|3.283280248713343|1.785898602014493e-07|True|
|e2bb7fe6eac4|2/10|1.6819463572549445|3.3620899562729457e-07|True|

물성/압력/레이어두께/와이어경로/파지외력을 동시에 최적화하는 단계는 BLOCKED:
자유 물체 파지 gate와 실측 범위가 아직 확보되지 않았다. 독립 모듈 연구를 통합 파지 인증으로 합산하지 않는다.
실패 trial에 가짜 목적값을 주지 않았고 모든 정적 seed/solver 재시도는 별도 기록이다.

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
