# SOFA routed tendon

**연구용 구현/초기 선언 검사18/18 PASS; 강화 잔차 감사에서 일부 FAIL, 실제 와이어 성능 EXPERIMENTAL.**
초기 F_ref에1e-6 하한이 있어 tiny cable load의 상대 잔차를 과소평가했다.
최종 분석기는 nonzero-load floor를 제거했다(하중/tolerance 완화 아님).
small T1e-6 tail residual.00871474 및 length control.00585318로1e-3 기준 FAIL.
T1e-5 tail.000842208, T1e-4 .000142102는 강화 기준 PASS.
과거 표의 PASS는 당시 정의이며 최종 물리 승인에는 residual_audit/strict_residual_retry가 우선한다.
18s 독립 재실행도 별도 기록하며 초기 결과/CSV를 덮어쓰지 않는다.
SoftRobots 플러그인 로딩은 실제 성공했지만 CableConstraint는 Vec3/Vec2 계열이므로
Rigid3 재료 guide에 맞는 독립 RoutedCable을 구현했다. SoftRobots 케이블 결과로 주장하지 않는다.
`a_i=p_i+R_i*(0,0,offsetZ)`, `ell=sum norm(a_(i+1)-a_i)`.
prescribed tension E=T*ell, 수축 E=.5kc max(ell-rest+shortening,0)².
힘·torque·consistent spatial tangent는 정확한 에너지 미분이며 전체 cable FD를 통과했다.
T0, 증가, small-moment EB limit, 길이 제어, 해제 복원을 실제 실행했다.
guide offset−.2mm는 연구 가정. 접촉면 와이어 마찰/실제 actuator stroke/motor energy는 NOT RUN.
release는 transient EXPERIMENTAL이며 강성비에 사용하지 않는다.


|실험|판정|처짐 mm|상대 잔차|최종 속도 mm/s|최대 회전 rad|
|---|---|---:|---:|---:|---:|
|zero|PASS|0|0|0|0|
|small_tension|PASS → FAIL (strict)|4.688322204e-05|1.742947484e-05|5.957759833e-09|1.251346214e-06|
|tension_1e5|PASS|0.0004687652116|1.677911548e-05|5.920160067e-08|1.2509015e-05|
|tension_1e4|PASS|0.004680964138|1.690532714e-05|5.552637184e-07|0.0001246473953|
|length_control|PASS → FAIL (strict)|9.29090462e-05|1.164132824e-05|8.584242729e-09|2.478507243e-06|
|release|EXPERIMENTAL|-2.531180358e-07|2.601414147e-05|8.415954526e-07|1.2509015e-05|



## 강화 잔차 및18s 재실행



|실험|판정|처짐 mm|상대 잔차|최종 속도 mm/s|최대 회전 rad|
|---|---|---:|---:|---:|---:|
|small_tension_18s|not_converged|4.687433263e-05|0.008682219714|4.778718536e-10|1.251346214e-06|
|length_control_18s|not_converged|9.289142937e-05|0.005853181829|9.375779892e-10|2.478507243e-06|
|wire_pressure_18s|not_converged|0.0003733910155|0.001315431084|7.980268337e-12|9.298030836e-06|


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
