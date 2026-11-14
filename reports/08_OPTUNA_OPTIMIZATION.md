# 08 — Optuna 최적화

이번 실행: `results/revalidation_20261114T132734Z`. 시작 커밋 `8ee78f0c84d042812537655583cb98ed037f310e`, 검증 중 dirty=true. 별도 브랜치와 소스/바이너리 SHA256으로 추적한다. 과거 `results/physics_validation`은 회귀 비교 인용에만 사용했고 이번 gate의 성공값을 재사용하지 않았다.

**BLOCKED**: Optuna 미설치. 이번 isolated pip 설치도 exit=1이며 DNS/네트워크 및 오프라인 캐시 조사에서 설치 가능한 패키지를 확보하지 못했다.
3-trial smoke와 24-trial 명령은 각각 실제로 실행했으나 의존성 검사에서 중단됐다.
실제 Optuna trial 수 **0**, SQLite study 없음, Pareto 후보 없음, Optuna 최적값 없음.
독립 고정 sweep 결과를 Optuna 결과로 바꾸어 보고하지 않는다.

| 요구 사항 | 상태 |
| --- | --- |
| 물리 gate/소스/바이너리/결과 무결성 차단 | PASS, 의존성 없는 11개 시험 |
| 실제 OFF/ON 평형 측정에서 목적함수 재계산 | PASS |
| 실패/미평형/NaN/상이한 하중의 성능값 거부 | PASS |
| 3회 sampler/trial, SQLite, 중단/재개 | BLOCKED / NOT RUN |
| 최소 24회 본 최적화 | BLOCKED / NOT RUN |
| Pareto 생성 및 후보 dt/6초/21노드/반복 검증 | NOT RUN(코드 경로만 준비됨) |

탐색 변수는 k, 1~10개 결합점 및 3 mm 격자 위치이며 dt는 제안 변수에 없다.
목적함수는 평형 OFF/ON 강성비 최대화와 OFF 기준 최대 X 미끄럼 최소화다.
각 후보의 dt 절반/6초, Pareto의 21노드/독립 반복을 요구하며 실패에는 성능값 없이 prune한다.
study identity에 소스와 optimizer 해시를 추가했고 변경된 metrics 및 중복 설계를 거부하도록 보강했다.
실제 Optuna API 경로는 실행하지 못했으므로 sampler 상태의 재개 재현성, 중단 복구 및 동시 study 동작은 검증된 것으로 주장하지 않는다.
seed=11은 설정되어 있으나 중단 재개가 연속 실행과 동일한 제안 순서를 만드는지는 추가 검증해야 한다.

재개(패키지를 격리 경로에 확보한 후):
```
REGRIP_BUILD_ROOT=/home/ubuntu/LHJ/ReGrip/build/revalidation_20261114_final PYTHONPATH=/home/ubuntu/LHJ/ReGrip/.python-deps /home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/optimize.py --gate /home/ubuntu/LHJ/ReGrip/results/revalidation_20261114T132734Z/physics_release/gate.json --out results/optuna_new --trials 3
```
smoke/restart 검증 후 별도 study/output에서 --trials 24를 수행해야 한다.
결합점 위치·개수는 현재 격자의 이산 변수, k는 [0.01,100] 범위의 연속 변수다.
이 제한된 혼합 탐색 공간의 결과만 보고하며 전역 최적성을 주장하지 않는다.
