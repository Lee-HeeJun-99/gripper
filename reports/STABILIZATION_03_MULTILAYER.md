# 100mm8층

**Newton 정적 family PASS; compensated cold dynamic family PASS. 표준 Euler 실패는 보존.**
8층 총 질량8e-5, 각 층의 단면/재료 동일(총 재료량 증가 비교).
고정 총 재료량8층 비교는 이번 NOT RUN이며 과거 실패를 변경하지 않았다.
FREE/k1/k10/k100, halfdt/quarterdt/21node/반복/18s 정적 continuation을 실행했다.
정적 solver의 dt는 가상 continuation 간격이다. 이것을 관성 동역학의 dt 수렴이라고 부르지 않는다.
기존 Euler18s/halfdt/mesh 실패는 별도 원시 증거 그대로 유지한다.
원래 rest geometry와 cold start를 유지했고 이번 정적 family는 독립 FEM seed를 사용하지 않았다.
독립 EB FEM과 같은 EA/EI/연결 위치를 쓴8층 static grid와 비교했다.
static ON/OFF 비 약6.47221548은 같은8층의 동일하중 평형끼리 계산했다.
2/4층 새 audit-plugin 회귀는 기존 처짐과 일치했다. 양을 늘린8층을 동일 재료량 최적이라고 주장하지 않는다.


|실험|원시 판정|처짐 mm|상대 잔차|
|---|---|---:|---:|
|L8_free|PASS|0.0039062499942386156|7.841473083558953e-07|
|L8_k1|PASS|0.001050366825802361|8.220745927454867e-05|
|L8_k10|PASS|0.0006538903051483795|6.360810270224248e-05|
|L8_base|PASS|0.0006035414003754021|6.0802400955869626e-05|
|L8_halfdt|PASS|0.0006035414003754021|6.0802400955869626e-05|
|L8_quarterdt|PASS|0.0006035414003754021|6.0802400955869626e-05|
|L8_mesh|PASS|0.0006035416537933241|2.2742505503879715e-05|
|L8_repeat|PASS|0.0006035414003754021|6.0802400955869626e-05|
|small|PASS|4.6874265960311634e-05|0.00020170092038710008|
|length|PASS|9.289132134399081e-05|0.0003576944451925865|
|wire_pressure|PASS|0.0003326901806414012|2.5827772628547758e-05|



|실험|원시 판정|처짐 mm|상대 잔차|
|---|---|---:|---:|
|extended18|PASS|0.0006035414003754021|6.0802400955869626e-05|
|LDL|PASS|0.0006035414003754021|6.080239993943009e-05|
|CG|FAIL|—|—|


## 보상 합산 cold-start 실제 실행


|실험|원시 판정|처짐 mm|상대 잔차|
|---|---|---:|---:|
|L8_base|PASS|0.0006035676548299951|1.6499728587911634e-05|
|L8_halfdt|PASS|0.0006035680703937243|2.1521050066034312e-05|
|L8_mesh|PASS|0.0006035539470759625|1.986738965575267e-05|
|L8_extended|PASS|0.0006035439162010332|1.457212223503314e-05|
|small|PASS|4.687433262798302e-05|0.0001625883840813958|
|length|PASS|9.289142936536043e-05|0.00035769444413379445|
|L2_regression|PASS|0.009291734813866429|1.7547802539383608e-06|
|wire_pressure|PASS|0.00037339101558397925|3.40117625155357e-05|
|L4_regression|PASS|0.0023799673824457038|9.290136509130186e-06|


추가 수렴 판정: `{"checks": {"required_cold_records": true, "required_followup_records": true, "length_equilibrium": true, "L8_extended_equilibrium": true, "L8_halfdt_equilibrium": true, "L2_regression_equilibrium": true, "L8_mesh_equilibrium": true, "L8_base_equilibrium": true, "wire_pressure_equilibrium": true, "L4_regression_equilibrium": true, "small_equilibrium": true, "follow_k1_equilibrium": true, "follow_quarterdt_equilibrium": false, "follow_repeat_equilibrium": true, "follow_k10_equilibrium": true, "follow_free_equilibrium": true, "halfdt_tip": true, "mesh_tip": true, "extended_tip": true, "repeat_tip": true, "quarterdt_tip": false, "L2_regression_tip": true, "L4_regression_tip": true}, "comparisons": {"halfdt": {"base": 0.0006035676548299951, "value": 0.0006035680703937243, "absolute_difference": 4.155637292613257e-10, "relative_tolerance": 0.001}, "mesh": {"base": 0.0006035676548299951, "value": 0.0006035539470759625, "absolute_difference": 1.3707754032560304e-08, "relative_tolerance": 0.01}, "extended": {"base": 0.0006035676548299951, "value": 0.0006035439162010332, "absolute_difference": 2.3738628961850194e-08, "relative_tolerance": 0.001}, "repeat": {"base": 0.0006035676548299951, "value": 0.0006035676548299951, "absolute_difference": 0.0, "relative_tolerance": 1e-10}, "quarterdt": {"status": "FAIL", "reason": "SOFA exit/error/completion failure"}, "L2_regression": {"original": 0.009291734813866068, "compensated": 0.009291734813866429, "absolute_difference": 3.608224830031759e-16}, "L4_regression": {"original": 0.002379967382446127, "compensated": 0.0023799673824457038, "absolute_difference": 4.2327252813834093e-16}}, "all_pass": false, "scope": "cold-start structural Euler; no free objects; original force/velocity/rotation gates unchanged"}`

## 공통 증거/범위

환경: Ubuntu22.04.5, kernel6.8.0-138-generic, GCC11.4, CMake3.22.1,
Python3.10.20(robot_ws), SOFA v26.06.00(`/home/ubuntu/SOFA/v26.06.00`).
실물 측정값0건. 연구 단위 F/mm/s와 기존 E=250, A≈.732233mm², I=.0426667mm⁴를 사용한다.
기존 plugin/integrated/finite_rotation/multilayer 원본과 골든 파일을 변경하지 않았다.
raw: `results/stabilization_20261115/`; 작은 증거: `reports/stabilization_evidence/`.
설정/명령은 실험별 config.json/command.json/scene.scn, 결과는 metrics.json과 artifact hashes.
정적 잔차<1e-3, 병진/각속도<1e-5, tail drift<1e-4를 유지했다.
실행 성공과 평형/파지 검증을 구분한다. EXPERIMENTAL은 실물 인증이나 전체 모델 PASS가 아니다.
기존45 gate는 이전 소스/바이너리 무결성으로 승계하며 신규 모델에 합산하지 않는다.
