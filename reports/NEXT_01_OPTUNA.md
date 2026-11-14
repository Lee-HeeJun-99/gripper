# NEXT 01 — Optuna

기준 60f41cf; 개발 코드 커밋 `96174a2ec8c1b75c2f11f607bdecb1d986b148f2`. 실행 중 dirty 상태는 개별 JSON에 그대로 기록했다.
원본/골든 보존, push 없음. 증거: `reports/next_evidence/`; raw/명령/전체 로그: `results/next_phase/`.


**BLOCKED**, 실제 trial **0**. 이번에도 격리 pip 설치와 실제 --trials 3 / --trials 24 진입을 요청했으나 의존성 단계에서 중단됐다.
DNS pypi.org/files.pythonhosted.org/repo.anaconda.com 모두 temporary failure. Python 패키지 호환성 충돌로 확정한 것이 아니다.
Optuna/runtime 오프라인 후보 0개. pip 설정/프록시는 값 대신 존재 여부만 기록했다(인증정보 비공개).
시스템 Python/Conda 환경은 덮어쓰지 않았다.

기존 45 gate의 source/binary/artifact 무결성과 11개 objective/guard 검사를 다시 통과했다.
실제 sampler, SQLite, 중단·재개, 실패 Trial, Pareto 재검증은 **BLOCKED/NOT RUN**.
소스에 seed=11이 있어도 실제 Optuna 재현성 검증을 통과했다고 주장하지 않는다.

별도 정적 FEM에서 k 5개×연결 패턴 4개=20개를 결정론적으로 열거했다.
현재 제한된 격자의 비지배 후보 1개: `[{"k": 100.0, "connectors": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "ratio": 1.6848450012941685, "slip": 5.0880616455578154e-08, "valid": true}]`.
이는 **Optuna가 아니고 SOFA 최적화도 아니다**. 두 목적이 함께 k/연결점 증가를 선호하므로 경계 후보가 지배하는 결과이며 전역 최적성을 주장하지 않는다.
dt는 탐색에 넣지 않았다. 실측 없는 진공압/마찰/와이어 설계의 최적값도 없다.

설치·재개 명령은 NEXT_TASKS.md. 동일 하중/평형/모델해시 gate를 우회하지 않는다.
