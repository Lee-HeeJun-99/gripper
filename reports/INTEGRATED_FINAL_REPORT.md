# ReGrip 통합 개발 최종 실행 보고

기준 commit `ba8e0e515bd9c06c75e764dfe1dc09670e614c77`.
브랜치 `development/regrip-integrated-system`; 보고서 생성 시 code commit `67be4ac37e26db94f4a4b0bc361e4a14fcad4cd4`.
문서/manifest commit SHA는 `git log -1 --format=%H`로 확인(자기참조 hash는 넣지 않음).
원격 push/이력 재작성 없음. 이전 검증 branch/main/골든 보존.

## 결과

|대상|판정|새 실행 근거|
|---|---|---|
|이전 NEXT manifest 무결성|PASS|불일치0, start.json|
|기존600시점 FREE 회귀|PASS|독립2회; 처짐 max error1.38778e-16, 속도1.41553e-14, 원래 tolerance1e-10+1e-6abs(golden)|
|기존 C++/finite kernel|PASS|600상태/60상태 실제 실행|
|기존45 gate|이전 PASS 유지|무결성 확인; 이번 전체45개 재실행 아님|
|기존 automation/guard|PASS|20/11개 새 실행|
|신규 Python 계약 검사|PASS|8개 실제 실행, skip0|
|메모리 원인 재현|PASS|MappingGraph ownership cycle, 최소장면4/4 retained|
|동일 process plateau|FAIL|live heap 증가 지속; 엔진 미수정|
|C++ 신규 수학/API|PASS|120상태+전체 cable FD+ASan/UBSan, LSan제외|
|100mm2/4층|PASS(선언 범위)|동일 조건 SOFA/EB 비교 및 후보 수렴|
|8층 수렴|FAIL|coarse실행과 달리 halfdt/mesh/18s 잔차 미달|
|와이어/압력 마찰|EXPERIMENTAL / 일부 FAIL|nonzero load 잔차 강화 후 tiny tension/length/wire-pressure 평형 미달|
|고정 물체 접촉|PASS(선언 범위)|3형상 검출/응답|
|자유 물체 파지|FAIL|1.440985mm 이동 >.001mm hold gate|
|Optuna/SofaPython3|BLOCKED|DNS/캐시부재, libpython3.12없음; Optuna0 trial|
|결정론적 grid|PASS|30완료/주입실패1, workflow7/7|
|SOFA Pareto 후보|6/6 승인|원래 위치/halfdt/mesh/repeat/+6s|
|전체 파지 설계 최적화|BLOCKED|grasp gate 미달, 조작한 성능값 없음|

인수인계 archive member56개도 실제 byte-for-byte 재검사 PASS(originals.json).
수정 전 guard 실패와 수정 후 ASan/UBSan 및 실제 SOFA3장면 회귀 PASS.
별도 유한 회전 slip 후처리 식 수정은 C++ recorder 전시점 대조로 검증했다.
tiny cable load 잔차의1e-6 하한도 제거했다. 초기18/18,20/20 선언 검사 결과를
최종 물리 인증으로 그대로 재사용하지 않으며 residual_audit가 우선한다.

## 측정과 한계

100mm2층 FREE/ON .0156281995228/.00929173481387mm, 비1.681946.
4층 FREE/ON .00781409989937/.00237996738245mm(재료량 증가 비교).
T1e-4 routed tip .00468096413837mm; high-pressure slider .0100308675154mm.
순수 moment theta=.5rad BeamFEM tip24.4931894386mm는 별도 구조 실험이며
30mm 작은 평면 모델의 검증 범위 확장이 아니다.
실측 PET/압력/마찰/장비 데이터는0건이다. independent FEM, 수학 검증, SOFA 출력,
가정된 파라미터를 각 상세 보고서에서 구분했다.

수정 파일은 `git diff --stat ba8e0e5..HEAD`와 manifest 참조.
신규 `models/integrated/`, `diagnostics/integrated*`, `tools/integrated_*`, tests만 추가했다.
초기 컴파일 실패, profiling timeout,8층 실패, invalid-input 수정 전후 증거를 보존했다.
별도 입력 검사는 수정 전 stride0 SIGFPE(exit−8), NaN contact 입력2개 미거부를 재현했다.
v2에서 zero-stride guard, NaN 검사, finite+planar-confinement 금지, 미선택 노드 회전범위 검사,
부분 CSV 덮어쓰기 금지 및 엄격한 JSON 타입 검사를 추가했다. 수정 전 결과는 v1 manifest에 귀속한다.

## 재현 환경/명령

Ubuntu22.04.5/GCC11.4/CMake3.22.1/SOFA26.06,
분석 Python `/home/ubuntu/miniconda3/envs/robot_ws/bin/python`3.10.20.
전체 명령 순서는 `INTEGRATED_NEXT_TASKS.md`와 각 raw command.json에 있다.
설정에는 모델/하중/경계/mesh/dt/solver, 결과에는 git dirty/source/binary 해시를 남긴다.
v1 결과는 v1 manifest에 귀속하며 입력 guard 수정 뒤 v2와 자동 혼합하지 않는다.
작은 증거/CSV/비교그림은 integrated_evidence, 큰 raw/빌드/SQLite는 ignored results에 보존한다.

## 남은 개발

엔진 MappingGraph lifetime 패치의 외부 버전 검증,8층 수치 정밀도/잔차 원인,
Optuna/CPython offline 의존성, 물체 마찰/다방향 enclosure/외력검증,
접촉 mesh/dt 수렴, 정상압력·필름 개구 모델, 실제 물성/마찰/케이블 계측이 필요하다.
현재 시스템은 연구용 기반이며 사용자 최종 요구의 검증된 통합 실물 그리퍼는 **미완료**다.
검증되지 않은 grasp optimizer를 실행해 수치를 만드는 대신 eligibility gate로 차단했다.

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
