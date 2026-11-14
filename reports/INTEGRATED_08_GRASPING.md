# 접촉 및 파지 gate

**접촉 kernel/고정 물체 응답 PASS; 자유 물체 hold FAIL; 안정 파지 NOT RUN.**
Sphere/infinite local-y cylinder/box signed-distance penalty 에너지와 힘·토크·Jacobian을 검증했다.
고정 물체3종에서 접촉 발생과 실제 변형을 확인했지만 물체 고정으로 파지가 증명되지는 않는다.
현재 평면 y=0에서 sphere/cylinder가 같은 결과인 것은 예상되며 유한 cylinder endcap 검증이 아니다.
충돌 검출과 힘 응답은 추가 C++ 시험에서 각각 독립적으로 검사했다.

자유 물체 negative control:6s, object F=1e-7, 이동1.4409853133441768mm,
사전 정의 hold limit.001mm를 초과하여 FAIL. 정적 평형도 미달한다.
접촉 node sampling, box edge 비매끄러움, 물체 tangential friction 부재,
3방향 외력 envelope/다중 핑거 enclosure 부재로 안정 파지·지지 외력은 인정하지 않는다.
`tools/integrated_grasp_gate.py`가 고정 물체를 성능에서 제외하고 full grasp optimizer를 차단한다.
작은 하중에서 움직임이 작아도 자의적으로 성공 판정을 내리지 않는다.


|실험|판정|처짐 mm|상대 잔차|최종 속도 mm/s|최대 회전 rad|
|---|---|---:|---:|---:|---:|
|sphere|PASS|0.005750919944|2.343436511e-05|1.287902104e-11|9.419342141e-05|
|cylinder|PASS|0.005750919944|2.343436511e-05|1.287902104e-11|9.419342141e-05|
|box|PASS|0.005750919942|2.323941945e-05|1.291128834e-11|9.419342102e-05|
|free_object_negative_control|EXPERIMENTAL|0.01594273901|0.2|0.4018029373|0.0002712606224|


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
