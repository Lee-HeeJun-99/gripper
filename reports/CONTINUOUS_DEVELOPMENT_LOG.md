# ReGrip 연속 개발 기록

기준: `60f41cfcbf64c94e26a02324526900c4ef69eb15`. 작업 브랜치: `development/regrip-next-phase`.
기존 검증 브랜치/main/원본/골든은 변경하지 않는다. 원격 push 없음.

## 단계 1 — 기존 증거 확인 및 의존성 복구

- 실행: `REGRIP_BUILD_ROOT=$PWD/build/revalidation_20261114_final /home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/next_environment.py`.
- 보고서/작은 증거 manifest 해시 불일치 0. 기존 45 gate의 소스·바이너리·실험 artifact 검사 통과.
- pypi.org, files.pythonhosted.org, repo.anaconda.com: DNS temporary failure.
- 격리 pip Optuna 설치, Conda Python 3.12 offline/online 및 SofaPython3 smoke 재시도. BLOCKED.
- 로컬 wheel/runtime 후보와 로그는 `results/next_phase/environment/summary.json`에 보존.
- 시스템 Python/네트워크 설정/보안 정책 변경이나 우회 없음.

## 단계 2 — 독립 모델 구현 및 단위 검증

- 신규 `models/finite_rotation`: 정확한 3D attachment/convected tangent 에너지, 2차 AD, 공간 회전 Jacobian, 별도 SOFA 컴포넌트.
- 첫 컴파일 FAIL: SOFA_CLASS가 정의하는 Base와 alias 충돌. Inherit로 수정. 초기 실패 로그 보존.
- 60개 무작위 유한 회전 상태: 에너지 FD 1.92619e-11, 공간 Jacobian FD 6.05088e-11,
  객관성 에너지 차이 4.85723e-17, 전체 모멘트 오차 4.16334e-17. 실제 API/6DOF 조립/kFactor 검사 PASS.
- 별도 ASan/UBSan 검사 PASS(detect_leaks=0). 기존 LSan ptrace 장애 해결 또는 전체 SOFA 메모리 인증이 아님.
- `models/multilayer/beam.py`: EA/EI 분리, 다층 Euler–Bernoulli/Timoshenko,
  이상적인 편심 팁 모멘트, penalty 접촉, 주어진 압력의 마찰 return mapping.
- 독립 기준/해석해/마찰 한계 등 9개 Python 검사 PASS. 실물 PET 물성 검증 아님.

## 단계 3 — 실행 중

- 실제 SOFA 100 mm 길이 확장, dt/메시/반복/연장, 신규 finite-rotation SOFA 비교 진행.
- 기존 자동화 20개 및 최적화 guard 11개 재실행 PASS.
- bounded live-SOFA soak 및 실험 요약/민감도/마찰 사이클의 새 증거 생성 중.

## 최종 delta 실행 기록

- 코드 96174a2ec8c1b75c2f11f607bdecb1d986b148f2; 100mm SOFA ratio 1.68194635725; finite C++/SOFA/객관성 검사 PASS.
- 신규 invalid differential guard 및 JSON checkpoint 해시/중단 재개 검사 후 영향 범위 재실행.
- 최종17 Python 검사 PASS, 39 FEM case/20 deterministic enumeration. 실제 Optuna0trial.
- 장시간 RSS 증가 FAIL 발견. writer/전단 제거, native driver, timer clear, empty/mass/explicit 대조 수행.
- explicit 첫 로딩 FAIL은 plugin 순서를 고친 새 폴더에서 재검증. 원시 실패 로그 보존.
- 기존45 gate는 무결성 재확인해 유지했고 전체 재실행으로 과장하지 않음. 원본56 항목 재확인.
- 마지막 작업은 작은 evidence/CSV/그림과 manifest의 local Git 보존. 바이너리/raw/cache/venv 미추적.
