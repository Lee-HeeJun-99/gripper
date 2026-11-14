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

## 핵심 수치/범위

8층 static k100 ON/OFF≈6.47221548, Hermite slip≈8.98388108e-8mm.
이는 재료량이 증가한8층 static spring model이며 실제 진공 성능값이 아니다.
보상 합산 cold8층 처짐.00060356765483mm, 잔차1.64997286e-5.
halfdt/21node/18s 잔차2.15210501e-5/1.98673897e-5/1.45721222e-5,
반복 tip 차이0;2/4층 기존 tip와 차이 각각3.61e-16/4.23e-16mm.
모든 힘/모멘트 기준은 유지하며 sub-ULP 증분 보상은 자유 물체에는 사용하지 않았다.
추가 dt1/4 cold-start는180s timeout FAIL이며 평형/수렴 미검증이다. dt절반 PASS와 구분한다.
기본 free-object +X 이동6.54322072e-6mm, mu0 약.0178247mm,
overload 약.012645mm. 후자의 이동이.05mm보다 작아도 force/velocity에서 FAIL.
기본±Z는 transient FAIL, 연장/α=2 damping 연구 조건은 별도 평가한다.
정확한 최종 gate와 모든 방향/수렴 결과는 STABILIZATION_05_GRASPING.md.
coarse mesh/quad 실패 및 fine timeout을 숨기지 않았다. 고해상도 hold-only에는 release NOT RUN.

## 한계/미완료

정확한 static stick, finite cylinder caps, 진짜 필름 surface/contact torque,
완전3D unconstrained soft fingers, 전체 beam/damping energy closure,
수정 SDK 비교, 실제 물성/압력/마찰/하드웨어 파지는 미완료다.
모듈 검사 PASS를 전체 물리모델/실물 성능 PASS로 합산하지 않는다.
이번 실행은 worker≤2, child4GiB/180s, 신규 출력 고유 경로로 제한했다.
fine-grid full sequence timeout 후 제한을 늘리지 않고 hold-only 범위를 별도 검증했다.
추가 미검증 파지 최적화는 실행하지 않고 차단했다. 재개 명령은 NEXT_TASKS.

실제 시계열 그래프: [object motion](stabilization_evidence/object_motion.png).
설정별 작은 CSV: [trials](stabilization_evidence/trials.csv).
소스/빌드/결과 전체 재검사: `PYTHONPATH=.:tools python tools/stabilization_verify_evidence.py --raw`.

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
