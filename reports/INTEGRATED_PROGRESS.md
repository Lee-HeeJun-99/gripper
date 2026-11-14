# 통합 개발 진행 기록

기준 `ba8e0e515bd9c06c75e764dfe1dc09670e614c77`, 신규 브랜치 `development/regrip-integrated-system`.
원본/골든/기존 물리 코드 보존, 원격 push 없음.

## PHASE 0 — PASS(무결성)

NEXT_EVIDENCE_MANIFEST의 소스/바이너리/보고서/실험/그림 해시 불일치 0.
기존30mm certified와 신규 experimental 모델을 분리했다. 시작 작업 트리는 깨끗했다.
증거: `results/integrated_20261115/start.json`.

## PHASE 1 — 원인 분리 진전, 엔진 수정은 보류

- mallinfo2: 60000스텝 live_heap=195384912 bytes; trim/unload 후에도 대부분 잔류.
- child-local operator new/delete 프로파일러 제작. direct malloc/aligned allocation은 제외하며 완전한 heap profiler라고 주장하지 않는다.
- 10000스텝 프로파일링은 timeout으로 -9. 원시 실패 보존 후1500스텝 제한으로 재시도(성공, skipped=0).
- 잔류 할당 stack은 SOFA MappingGraph::build / addEdge / makeMappingGraphNode에 집중됐다.
- SDK에서 부모/자식 모두 shared_ptr인 것을 확인. 최소 graph.clear() 후 weak_ptr 9/9가 살아 있음을 실제 재현했다.
- 이는 관측 RSS만으로 내린 추정과 다르며, 해당 그래프의 강한 참조 수명 문제가 확인된 범위다.
- 외부 엔진 파일/바이너리를 변경하거나 private 멤버 const_cast로 해제하지 않았다.
- 동일 프로세스의 장시간 plateau는 아직 FAIL. 실험별 bounded process 및 종료·재수거로 진행한다.

## PHASE 2/3 — 복구 재시도

DNS/pip 격리 설치 실패를 재확인했다. 이전 캐시·ABI 진단 도구도 새 출력 루트에서 재실행 중.
실제 Optuna0trial. 원본 Python 장면 성공을 주장하지 않는다.

## 신규 구현 및 실행 중

- 별도 LayerNetwork: 2/4/8층, 선택 연결점, planar/finite3D 탄성, prescribed-pressure slider.
- 별도 RoutedCable: 정확한 material-guide 길이/장력/수축 에너지와 공간 Jacobian.
- AnalyticContact: sphere/infinite-cylinder/box signed-distance penalty, objective energy/force/Jacobian.
- 120개 C++ kernel 상태/API/소산 work balance PASS, 별도 ASan/UBSan PASS(LSan 제외).
- 첫 컴파일은 struct semicolon 누락 FAIL; 수정 후 경고 없는 빌드·시험 성공. 초기 로그 보존.
- 기존600시점 FREE 회귀와600상태 실제 C++ 검사도 새 실행 PASS.
- SOFA 다층·와이어·마찰 suite 실행 중. 실제 결과는 후속 보고서에서 확정한다.

## 통합 실행 종결 기록



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


상세 명령/실패/재개점은 INTEGRATED_01..09 및 FINAL/NEXT_TASKS에 보존했다.
