# ReGrip 안정화 실행 보고

기준 `830fd3d00186fd9e772be802c27de7ca2100ecde`.
브랜치 `development/regrip-grasp-stabilization`; code commit `825a5d007dc990e65bcc77b1387da13cf911e781`.
최종 문서 commit은 이 보고서를 포함하는 descendant(`git log -1 --format=%H`)로 확인한다.
원격 push/강제 push/이력 재작성 없음. 이전 브랜치/원본/골든 보존.

## 작업 전후

|항목|이번 결과|
|---|---|
|잔차 회계|PASS: 실제 구성요소 합과 recorder 차이0|
|8층|static Newton 및 보상 합산 cold dynamic PASS; 표준 Euler 실패 보존|
|작은 wire/length/pressure|static 및 compensated cold dynamic PASS; 마찰 경로 차이 분리|
|2/4층 회귀|새 audit binary 실행 PASS|
|메모리|FAIL:2×120000step 후 live heap331165504bytes, FD5|
|공식 메모리 수정|PR6259 확인, 설치본/패치 실행은 미변경/BLOCKED|
|분포 접촉/마찰|C++ full18DOF/Jx/Jv/API/objectivity/소산 PASS, kernel 범위 한정|
|2핑거/free object|실제 실행 EXPERIMENTAL, 일부 조건 FAIL; 전체 파지 미인증|
|8층 fallback 탐색|15proxy,3Pareto, static-approved3/3; Optuna 아님|
|Optuna|BLOCKED,0Trial|
|SofaPython3|BLOCKED, 원본Python NOT RUN|
|전체 에너지|BLOCKED, BeamFEM API 미구현/감쇠 수지 미확보|

수정 파일: models/stabilization, diagnostics/stabilization, tools/stabilization_*, tests/test_stabilization*.
기존 integrated/finite_rotation/FEM/plugin은 read-only로 유지했다.
수정한 오류: sub-ULP Euler 위치 증분 소실, warm 분석의 rest-reference 혼동, plugin wrapper 등록명 치환, 미선행 plugin등록, 중복 BaseMass,
DiagonalMass의 실제 두-template/explicit links, event-time sample window의 dt 비교 편향.
기존 실패와 수정 전후 raw를 모두 보존했다.


최신 수치와 미검증 범위는 FINAL 및01..09 보고서를 참조한다.
