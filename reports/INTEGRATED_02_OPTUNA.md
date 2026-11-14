# Optuna 및 대체 탐색

**Optuna BLOCKED, 실제 Optuna Trial=0.** pypi.org/files.pythonhosted.org/repo.anaconda.com DNS 실패.
프록시/pip index 환경 설정 없음, 로컬 wheel 후보0. 격리 pip --target 재시도와
Conda offline/online 모두 실패했다. 시스템 Python 변경/정책 우회는 하지 않았다.
실제 Optuna의3 smoke/24 trial, pruning, SQLite study는 NOT RUN이다.

별도 결정론적 EB FEM grid는30개 물리 설계 완료+고장 주입1개 실패이다.
seed11, layers2/4, k=(.01,.1,1,10,100), 연결점패턴=(5,10)/(2,4,6,8,10)/(1..10).
고정 dt는 SOFA 후보 검증 변수이며 탐색 변수가 아니다. 동일 F=1e-6, 재료 E=250,
동일 family의 FREE 기준을 사용한다. 8층 및 미평형 equal-material family는 차단했다.

SQLite physical-design unique hash, source/binary identity, 실패 objective=None,
실제 SIGTERM 후 resume, seed 반복, 손상 metric/result hash 거부 등7/7 workflow 검사 PASS.
이는 Optuna 검사로 계수하지 않는다. 기존 nodal metric study와 새 Hermite metric study를 분리했다.
원래 stiffness↑/slip↓를 유지하고 complexity=(layers-1)*pointcount↓는 별도 연구 목적이다.
총 재료량이 다른2/4층 결과를 동일 재료 설계 우열로 해석하지 않는다.

Hermite Pareto6개 중 현재 완료6개, SOFA 독립 재검증 승인6개.
대리 FEM 탐색 결과 자체를 SOFA/Optuna 최적화라고 주장하지 않는다.
후보마다 base/repeat/dt절반/21노드(연결 물리 위치 고정)/18s(+6s), 평형과 미끄럼을 확인했다.
명령: `python tools/integrated_search.py --help`, `python tools/integrated_candidates.py`.
정확한 설정/목적함수/모든 실패는 search_hermite/summary.json 및 candidate_validation에 보존했다.

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
