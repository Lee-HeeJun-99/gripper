# ReGrip 다음 단계 개발 최종 보고서

종합 상태: **EXPERIMENTAL / 부분 완료**, 외부 의존성 **BLOCKED**, 장시간 메모리 plateau **FAIL**.
PASS는 실제 시험 범위만, FAIL은 실제 실패, BLOCKED는 외부 의존성, NOT RUN은 미실행을 뜻한다.

## 1. 브랜치·코드·환경

기준 60f41cf; 개발 코드 커밋 `96174a2ec8c1b75c2f11f607bdecb1d986b148f2`. 실행 중 dirty 상태는 개별 JSON에 그대로 기록했다.
원본/골든 보존, push 없음. 증거: `reports/next_evidence/`; raw/명령/전체 로그: `results/next_phase/`.


Ubuntu22.04.5/SOFA26.06/GCC11.4/CMake3.22.1/Python3.10.20/NumPy1.26.4.
최종 문서 커밋은 이 보고서를 포함하므로 `git log -1 --format=%H`와 최종 응답으로 확인한다.
전체 새 소스/바이너리/증거 해시는 NEXT_EVIDENCE_MANIFEST.json에 있다. 기존 manifest도 그대로 검증했다.

## 2. 기존 브랜치 대비 변경

기존 plugin/골든/native_scene/run_trial/trial_validation 물리 코드는 수정하지 않았다.
새 models/finite_rotation(별도 C++), models/multilayer(독립 정적 FEM), models/gripper_100mm(미확정 입력),
experiments/(모델 라벨·JSON 계약), tools/next_*(bounded 검증/보고/진단), diagnostics/headless(대조 실행)를 추가했다.
중간 코드 커밋 702c5a7/7a11ed1을 보존했다. 원본56개 재검사 PASS, 원격 작업 없음.

## 3. 새로 해결한 문제

유한3D attachment 에너지와 공간 Jacobian을 독립 구현했다. 모델/실험 혼합 없이 길이·다층 연구가 가능해졌다.
잘못된 JSON/비정수 step/NaN differential/중복 출력/손상 checkpoint를 거부한다.
실행 루트 `REGRIP_NEXT_OUT`으로 새 세션의 덮어쓰기 방지 및 재개 지점을 지원한다.
RSS 증가를 새로 검출했지만 해결했다고 표시하지 않는다.

## 4. 기존 모델 보존·C++ 안정성

기존45 gate는 소스·바이너리·raw artifact 무결성을 검증해 유지했다(45개 전체 재실행이 아님).
기존 자동화20/guard11 재실행 PASS. 신규 C++60 상태/API/수치미분/ASan·UBSan PASS.
전체 SOFA ASan 및 LSan는 별도 미실행/차단이며 메모리 누수 없음 인증이 아니다.

## 5. 신규 수학·SOFA 검증

새 3D component gate PASS; 전체 장면의 전 시점 강체 좌표 변환도 PASS.
새 모델의 대칭 Hessian과 nonsymmetric 공간 tangent를 구분한다. 세부 수식/예산은 NEXT_04.
Python 연구/계약/runner 검사 17개 PASS. 전체 lint/type 분석 NOT RUN.
그림 생성 시 Matplotlib Axes3D import 경고가 있었다. 이번 2D PNG 두 개는 저장·확인했으며 3D 시각화는 NOT RUN이다.

## 6. 100 mm 실제 SOFA 측정

F1e-6에서 FREE=0.015628199522761 mm, k100=0.00929173481386614 mm,
강성비=1.68194635725, ON X slip=1.01808339537e-07 mm.
dt/동일 연결 위치 메시/반복/18초 연장 PASS. 상태·잔차·회전은 측정 CSV와 NEXT_05에 있다.
이 수치를 실물 그리퍼 성능으로 확대 해석하지 않는다.

## 7. Optuna 및 후보

BLOCKED, 실제0trial. sampler/SQLite/중단 재개/Pareto 검증 NOT RUN.
대신 별도 정적 FEM 20점 결정론적 열거에서 비지배 후보1개를 얻었다. Optuna 또는 SOFA 최적값이 아니다.
제한된 연구 탐색일 뿐 전역 최적성 없음. dt는 설계 변수 아님.

## 8. SofaPython3

BLOCKED, CPython3.12 공유 runtime/stdlib/NumPy 미확보. exit0의 장면 로딩 실패를 확인했다.
원본 FREE/전단 대 이식본 직접 비교 NOT RUN.

## 9. 다층·와이어·접촉·진공 연구

독립 정적 FEM 39case, EB/Timoshenko 해석해, 이상적 tip moment 및 penalty contact 계산/검사 PASS.
압력-마찰 cap 및 hysteresis/dissipation, JSON checkpoint 재개 검사 PASS(가정된 연구 모델).
실측 물성/압력·seal·와이어 경로/3D 물체 접촉/실제 안정 파지는 NOT RUN.

## 10. 장시간 안정성 실패·잔여 문제

30초 simulation +12회 child 정리/FD PASS, **RSS plateau FAIL**.
새 ForceField·관측기를 제거한 기계 장면과 native driver에서도 단계별 RSS 증가가 남았다.
기계 상태가 없는 empty scene은 증가0이었다. 정확한 allocation owner/해제 지연 대 진짜 누수는 미확인.
물리 결과를 조작하지 않고 상한에서 종료했다. 장시간 수 시간 검증은 NOT RUN이다.

## 11. 재현 및 다음 우선순위

NEXT_TASKS.md의 새 경로 명령을 사용한다. 실제 명령은 각 trial command.json, build *.command.json에 있다.
우선순위: 할당 profiler/엔진 원인 분리 → 의존성 복구와 실제 Optuna smoke →24회/Pareto →
원본 Python 비교 → 다층3D/와이어·접촉 통합 → 실측 보정. 기존 검증 정의는 보존한다.
설정 JSON: experiments/baseline/research_100mm.json, experiments/convergence/sofa_100mm.json.
raw는 로컬에 보존하고 Git에는 작은 JSON/CSV/그림/로그만 둔다.

## 12. 근거와 한계

NEXT_01~05, next_evidence/sofa_measurements.csv, static_research.json, finite_unit.log,
finite_asan_ubsan.log, objectivity.json, stability.json 및 memory_controls.json 참조.
이번 실행은 bounded numerical research 기반을 확장했지만 전체 실물 그리퍼/Optuna 목표를 완료하지 않았다.
외부 패키지 차단과 지속 RSS 증가로 무제한/시간 단위 실행은 보류했고, 세션 재개 경로를 남겼다.
