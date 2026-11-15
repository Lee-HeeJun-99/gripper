# ReGrip — validated grasp 개발 실행 보고

## 결론

**전체 목표 미완료 / EXPERIMENTAL.** 정지마찰 연구 모델, 동일 조건6방향 유지·해제·복원 하위gate,
8층 quarterdt, 실제 Optuna, 원본 SofaPython3 회귀와 별도 SDK 메모리 수정 시험을 수행했다.
그러나 접촉 공간 수렴성 FAIL, 렌치행렬rank5, 전체 에너지 BLOCKED로
일반6DOF 자유 파지/실물성능/파지 설계 최적화 성공을 선언하지 않는다.

## Git·환경·변경

시작 `9b95d0c03e0557829ec3f6bab095935144bb9a63`, 브랜치 `development/regrip-validated-grasp`.
기능커밋6b838c5,9395845,3f0b735,ad639e0 이후 문서/증거 후속커밋.
최종 SHA는 `git rev-parse HEAD`; manifest의 evidence_code_commit은 문서커밋 직전 코드버전이며 자기해시 순환을 피한다.
원격push/force/이력삭제 없음. 기존브랜치/골든/원본/기존검증코드를 보존했다.
실제ROOT는 외장디스크 `/media/ubuntu/99419895-2058-45b4-b746-b36ea7112e4e/research/LHJ/ReGrip`.
Ubuntu22.04.5/kernel6.8.0-138-generic/GCC11.4/CMake3.22.1/robot_ws Python3.10.20/SOFA26.06.
실행시 source/binary/config/raw artifact SHA와git dirty도 기록한다. 구체환경은 `grasp_evidence/environment.json`.

새 파일: models/grasp/,diagnostics/grasp/,tests/test_grasp_stick.cpp 및 test_grasp_campaign.py,
tools/grasp_*.py,scenes/grasp_native_surface.py·grasp_replay.py,본 GRASP 문서와 작은증거/그림.
기존 plugin/,models/integrated/stabilization/finite_rotation/multilayer,handoversrc는 변경하지 않았다.
변경이유: 독립 elastic friction,0마찰퇴화/cap-axis/관측API 오류수정,동일식AD경량화,격리의존성,
독립잔차/공간수렴·렌치rank 판정,실제결과기반재생/보고. 버전별 바이너리를 덮지 않았다.

## 새 실행 핵심 결과

|대상|판정|측정/근거|
|---|---|---|
|elastic stick/slip/API/FD|PASS|maxJ1.09235e-10;netMoment2.71051e-20|
|clean C++/Python|PASS|warning0;Python67/67;ASan/UBSan/LSan 자체unitPASS|
|sphere 동일조건±X/±Y/±Z|하위gatePASS/전체EXPERIMENTAL|변위약.000482/.000482/.004782mm;잔차최대.000169424|
|24s해제/핑거복원|PASS|contact0;rest오차최대7.65e-9mm;속도약8.65e-8mm/s|
|공간접촉수렴|FAIL|41/16→41/32 변위8.474%차이|
|완전6DOF wrench closure|미인증|최소rank5;6방향힘시험≠torque closure|
|100mm8층 quarterdt|PASS|tip.000603568280592mm,res1.69381e-5;227.603s wall|
|별도patched SDK메모리|한정PASS|2×120000step;후반live+96bytes;graph잔존0/4|
|원본PythonFREE|PASS|600시점 기존tol;tip.04121379160634628mm|
|Optuna|PASS(30mm만)|27시도/24완료/3중복PRUNED;SQLite재개|
|Pareto재검증|PASS(30mm만)|강성비1.66441253010351,slip1.87641e-5mm;dt/mesh/연장/반복|
|총에너지|BLOCKED|단순BeamE 후보는 큰변형에서 힘미분불일치|
|native3D표면|EXPERIMENTAL|1.8s진단;반력nonzero1step뿐,지속접촉미검증|
|SOFA선택재생|PASS|실제2401frame;GUI실행NOTRUN|
|실물성능|NOT RUN|실물측정0건|

## 과거결과와 새결과

기존45물리gate 및2·4층/8층기본·mesh/extended는 이전검증으로 승계한다.
`stabilization_verify_evidence.py --raw` 1243검사/오류0를 다시 확인했다.
동일소스 기존C++5개도 새실행 PASS. 기존45에 신규 파지gate를 합산하지 않는다.
새patched SDK FREE600×2,Python원본600,XML비교,8층3dt,신규마찰/자유물체는 이번 실제측정이다.
독립FEM36계산은 SOFA측정이 아니며 단면가정4종/민감도별도;실물PET데이터 아니다.

## 실패·수정과 남은 한계

초기μ0singularity→zero-capacity처리→적분완료/물리FAIL로 정상분류.
원통cap-axis오류→smoothcap허용/실제특이점거부.
고해상도timeout→동일식AD1 fastpath→41/32까지 완료했으나 물리수렴FAIL유지.
감쇠.2의±Z FAIL을 mass2조건PASS와 혼합하지 않았다.18s복원미달→24s관측연장PASS.
기존fixture경로충돌PythonFAIL→새namespace67PASS. 의도적invalidAPIERROR는 unit에만 정확매칭.
native표면 구API/SciPy/초기화실패와 재생colorAPI실패는 로그보존후 수정,전체파지성공으로 확대하지 않았다.
SDK첫buildtimeout/Projective누락→matchedtarget 재빌드→물리회귀PASS.

현재 가이드평면finger/점-선피부접촉/같은μsμk/작은회전LayerNetwork라는 제약이 있다.
Sphere 다른torque,원통/박스6방향전체복원,자유파지에 대한8층확장,연속3D표면 정지접촉,
전체beamenergy·제어일·감쇠일 폐합,수시간fullengine무누수는 미완료.
실물재료·압력분포·진공누설·와이어배치·실제필름접촉면은 가정이며 인증하지 않았다.
파지최적화는 차단하고 검증된30mm 스프링모델의 강성/미끄럼 탐색만 수행했다. 전역최적성 주장없음.

## 증거·재현·재개

- raw/build/격리환경은 외장디스크 results/grasp_20261115,build/grasp_20261115,.runtime,.python-deps에 보존/Git제외.
- 작은JSON/CSV/로그: reports/grasp_evidence;실제그림:reports/grasp_figures.
- 각 config.json/scene.scn/command.json/stdout·stderr/state/contact/metrics에 출처와 판정이 있다.
- 전체파일SHA는 GRASP_EVIDENCE_MANIFEST.json;검증: `PYTHONPATH=.:tools python tools/grasp_verify_evidence.py --raw`.
- 보고서01~10은 수학/조건/허용오차/실패/로그를 설명한다. 기존raw 덮어쓰기는 금지한다.
- 정확 재개명령/우선순위는 GRASP_NEXT_TASKS.md.

이번 유한campaign은 최대41노드/32subdivisions,24s,trial당4GiB/최대480s로 제한했다.
제한내 새검증을 완료하고 실패상태를 저장했다. 다음은 동일실험 무한반복이 아닌 접촉적분/유한패치 렌치모델 개선이며
현재 프로젝트를 목표달성 완료로 닫지 않는다.
