# 재개 지점

환경:
```bash
cd /home/ubuntu/LHJ/ReGrip
export REGRIP_BUILD_ROOT="$PWD/build/revalidation_20261114_final"
export OPENBLAS_NUM_THREADS=1
```

1. 설치 가능한 경우 격리 의존성 확보 후 기존 gate를 그대로 통과시켜 실제 Optuna smoke/24 trials:
```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m pip install --target .python-deps 'optuna>=3.6,<5'
PYTHONPATH="$PWD/.python-deps" /home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/optimize.py --gate results/revalidation_20261114T132734Z/physics_release/gate.json --out results/optuna_next_available --trials 3
```
smoke의 실제 SQLite 재개/실패/seed/Pareto를 검증하기 전 24-trial 성공을 주장하지 않는다.
2. CPython 3.12 shared runtime/stdlib/NumPy를 격리 설치한 뒤 원본 장면 복사본 비교.
3. `tools/next_build.py`, `tools/research_trial.py`, `tools/next_experiments.py`로 별도 모델 실행.
4. 장시간 RSS 증가의 allocation owner를 조사한다. empty scene은 증가0, mass/implicit 및 beam/explicit에서도 증가했다.
   BatchGUI/관측기/신규 ForceField 하나로 단정하지 않는다. heaptrack/valgrind 부재이며 임의 엔진 수정은 하지 않았다.
   RSS 제한을 해제하거나 시간을 무한 연장하지 않는다.
5. 실측 E/밀도/두께/마찰/압력·누설/와이어 경로/접촉 구조는 아직 미확정. 실물 성능 인증은 보류한다.

## 새 세션의 delta 재현 (새 출력 루트)

```bash
export REGRIP_PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
export REGRIP_NEXT_OUT="$PWD/results/next_session_001"
export PYTHONPATH="$PWD:$PWD/tools"
export OPENBLAS_NUM_THREADS=1
"$REGRIP_PY" tools/next_environment.py
/usr/bin/python3 tools/next_build.py --out "$REGRIP_NEXT_OUT/build_certified"
/usr/bin/python3 tools/next_build.py --sanitize --out "$REGRIP_NEXT_OUT/build_sanitized"
"$REGRIP_PY" tools/next_quality.py --out "$REGRIP_NEXT_OUT/quality"
"$REGRIP_PY" tools/next_experiments.py sofa
"$REGRIP_PY" tools/next_final_checks.py
"$REGRIP_PY" tools/next_limit_check.py
"$REGRIP_PY" tools/next_experiments.py static
"$REGRIP_PY" tools/next_stability.py
"$REGRIP_PY" tools/next_memory_probe.py
cmake -S diagnostics/headless -B build/next_headless -DCMAKE_PREFIX_PATH=/home/ubuntu/SOFA/v26.06.00 -DCMAKE_BUILD_TYPE=Release
cmake --build build/next_headless -j2
"$REGRIP_PY" tools/next_headless_check.py
"$REGRIP_PY" tools/next_memory_isolation.py
"$REGRIP_PY" experiments/run.py experiments/baseline/research_100mm.json "$REGRIP_NEXT_OUT/contract_static"
"$REGRIP_PY" experiments/run.py experiments/convergence/sofa_100mm.json "$REGRIP_NEXT_OUT/contract_sofa"
```

같은 출력 루트의 이미 완료된 단계를 다시 호출하지 않는다. 새 루트 또는 개별 `--out`을 지정한다.
위 stability는 약30초 simulated time/12회 반복의 bounded 검사이며 수 시간 안정성 인증이 아니다.
`generate_next_reports.py`는 이번 캠페인의 중간 실패 로그까지 포함하는 기록 패키징 전용이다.
새 세션에서는 새 증거에 맞게 보고서를 갱신하고 이전 실패 로그를 새 성공으로 재사용하지 않는다.

기존 바이너리를 새로 빌드하거나 legacy source가 바뀌면 기존45 gate를 재사용하지 않는다:
```bash
export REGRIP_BUILD_ROOT="$PWD/build/legacy_rebuilt_next"
/usr/bin/python3 tools/build.py --build-root "$REGRIP_BUILD_ROOT" --logs "$REGRIP_NEXT_OUT/legacy_build"
"$REGRIP_PY" tools/validate_physics.py --out "$REGRIP_NEXT_OUT/legacy_physics"
```
이 경우 Optuna의 --gate도 새 `legacy_physics/gate.json`으로 바꾼다. 해시 검사를 우회하지 않는다.

## 미완료 우선순위

1. 장시간 메모리 할당/해제 원인 분석 및 수정 후 같은 대조/soak 재검증.
2. Optuna 의존성 복구 → 실제3trial smoke(SQLite/실패/seed/중단재개) →24trial → 실제 Pareto 재검증.
3. CPython3.12 전체 런타임 → 원본 장면 복사본의 FREE/전단 회귀.
4. 현 실험적 finite3D/다층FEM의 SOFA 다층 통합과 큰 변형·와이어·물체접촉의 별도 gate.
5. 실측 기반 물성/정상압력/마찰/이력/와이어·카트리지 모델 보정. 현재 null을 임의 확정하지 않는다.
