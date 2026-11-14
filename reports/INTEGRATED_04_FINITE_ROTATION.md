# 유한 회전 및 구조 검증

독립 기존 finite kernel은 SO(3) 지수 chart와 회전된 attachment point를 쓴다.
에너지의 chart Hessian은 대칭이지만 공간 torque Jacobian은 connection 항을 포함한다:
`F=-dE/d(delta)`, `J=-H-.5*skew(torque)`(각 회전 block).
일반 공간 Jacobian의 비대칭을 에너지 비보존 오류로 혼동하지 않았다.
기존60상태 실제 실행 PASS: energy FD1.92619e-11, spatial Jacobian FD6.05088e-11,
objectivity4.85723e-17, net moment4.16334e-17. invalid-input 의도적ERROR와 성공을 구분했다.
신규120상태 contact/cable kernel 및 실제 API kFactor/6DOF 검사 PASS,
전체 routed cable18DOF FD도 energy1.51464e-11/J9.49002e-11로 PASS.
원래 작은 회전 `s=du-h*(theta_l+theta_u)/2` 극한과 좌표 정의는 유지한다.
EB에서는 phi=dw/dx, SOFA y회전은 R_y(theta)e_x=(cos(theta),0,-sin(theta))라
theta=-phi이다. 따라서 EB식 du+h*(phi_l+phi_u)/2와 같은 에너지다.
노드별 변환 T=diag(1,1,-1)에 대해 f_SOFA=T^T f_EB, K_SOFA=T^T K_EB T이며
회전 부호만 달라졌다는 설명을 실제 `beam.py`의 B행렬 및 quaternion 복원과 대조했다.

SOFA pure-end-moment **uncoupled BeamFEM**를 독립 circular-arc elastica와 비교했다.
theta=.004/.1/.5 rad, large21node 및 halfdt 모두 선언1% 오차 이내 PASS.
theta=.5 tip24.4931894386mm, 상대오차.000396260, 21node24.4859755502mm,
halfdt24.4931894390mm. 이 검사는 큰 회전 전단/필름/접촉 전체의 인증이 아니다.
별도 objective_connector/summary.json은 실제 유한 회전 연결의 로딩·적분·평형 결과를 기록한다.
작은 회전 coupled tip.009290642533mm, moderate tip4.475530251109mm,
halfdt4.475530251202mm 모두 평형 PASS. 이는 특정 연구 하중의2층 연결 검증이다.
최종 검토에서 postprocessor가 mode2에도 평면 slip 식을 쓰던 문제를 발견했다.
역사 raw/metrics는 보존하고 정확한 `t_lower dot (p_u+R_u*a_u-p_l-R_l*a_l)`로 별도 재분석했다.
moderate 최종 exact slip.003496672754612mm, C++ recorder와 전시점 최대 차이1.04e-17mm.
평형·처짐 판정은 이 지표 수정으로 바뀌지 않는다. 이전 finite raw의 평면 slip 숫자는 성능에서 제외한다.
유한 회전 마찰은 구현하지 않았으며 planar slider에 큰 회전 결과를 섞지 않았다.
직접적인 공간회전 변환 검사는 kernel에서 수행했으며 전체 고정중력/경계 장면의 임의 회전은 NOT RUN.


|실험|판정|처짐 mm|상대 잔차|최종 속도 mm/s|최대 회전 rad|
|---|---|---:|---:|---:|---:|
|small|PASS|0.1999997383|1.669065644e-06|3.808225721e-10|0.005335258395|
|medium|PASS|4.995913824|8.654859153e-08|9.536694256e-09|0.1333843573|
|large|PASS|24.49318944|4.69527482e-07|4.183587421e-08|0.6672524376|
|large_mesh|PASS|24.48597555|4.432252233e-08|1.289341131e-08|0.6614234452|
|large_halfdt|PASS|24.49318944|5.113547292e-07|4.530257614e-08|0.6677219528|


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
