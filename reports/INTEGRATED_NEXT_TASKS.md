# 재개 우선순위 및 명령

1. MappingGraph 공유소유권 cycle을 외부 SOFA 이슈/수정 SDK에서 해결하고 최소60000step 재검증.
   기존SDK를 직접 고치거나 private member를 해제하지 않는다. bounded process 우회 유지.
2.8층 residual floor 원인 규명(물리조건/tolerance 고정), force balance·solver conditioning 분석.
   기존 실패 raw를 보존하고 새 campaign root에서 독립 재시도.
3.허용된 네트워크/offline wheels가 생기면 Optuna/CPython3.12 격리 설치.
   실제 Optuna3+24 및 원본 Python 장면은 여전히 해야 함.
4.현재 point-contact 연구를 continuous surface sampling/물체 마찰/기하학적 enclosure로 확장,
   자유 물체3방향 외력, 반복/수렴/해제까지 통과하기 전 grasp optimization 금지.
5.실측 PET E/두께/마찰/압력분포/와이어 경로 입력 후 불확실성 분석.

## 재현 명령(새 출력 루트 필수)

```bash
cd /home/ubuntu/LHJ/ReGrip
export PYTHONPATH=.:tools
export OPENBLAS_NUM_THREADS=1
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
export REGRIP_INTEGRATED_OUT=$PWD/results/integrated_new_campaign
$PY tools/integrated_build.py --logs "$REGRIP_INTEGRATED_OUT/build"
$PY tools/integrated_build.py --sanitize --logs "$REGRIP_INTEGRATED_OUT/build_asan"
cmake -S diagnostics/integrated -B build/integrated_20261115/diagnostics -DCMAKE_PREFIX_PATH=/home/ubuntu/SOFA/v26.06.00
cmake --build build/integrated_20261115/diagnostics -j2
$PY tools/integrated_memory.py
$PY tools/integrated_minimal.py
$PY tools/integrated_suites.py multilayer
$PY tools/integrated_suites.py tendon
$PY tools/integrated_suites.py friction
$PY tools/integrated_suites.py contact
$PY tools/integrated_grasp_gate.py
$PY tools/integrated_finite.py
$PY tools/integrated_objective.py
$PY tools/integrated_finite_metrics.py
$PY tools/integrated_residual_audit.py
$PY tools/integrated_residual_retry.py
$PY tools/integrated_sensitivity.py
$PY tools/integrated_additional.py
$PY tools/integrated_search.py --out "$REGRIP_INTEGRATED_OUT/search_hermite" --metric hermite --limit 3 --inject-failure
$PY tools/integrated_search.py --out "$REGRIP_INTEGRATED_OUT/search_hermite" --metric hermite --limit 30 --inject-failure
$PY tools/integrated_search_checks.py
$PY tools/integrated_candidates.py
$PY -m unittest discover -s tests -p test_integrated_python.py
```

search CLI의 --metric hermite와 새 SQLite 경로를 사용한다. v1 결과를 v2study에 섞지 않는다.
위 명령은 원본 v1의 재실행이 아니라 현재 guard-hardening 소스의 새 campaign이다.
동일 process plateau/8층/자유 파지 실패가 재현되면 성공으로 만들기 위해 허용오차를 바꾸지 않는다.
