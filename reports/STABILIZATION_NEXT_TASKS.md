# 재개 지점

1. 정확한 정지/운동 마찰과 객관적 history transport를 독립 검증 후 통합. 현 kinetic creep를 static stick으로 부르지 않는다.
2. fine hold-only의 mesh/quad/dt/전체 release 수렴 및 동일 damping에서6방향 envelope. 아직 전체 파지 optimizer 금지.
3. BeamFEM force/energy 및 Rayleigh damping의 전체 수지. API미구현을0으로 대체하지 않는다.
4. 검증된 structural compensated Euler 범위를 유지하고 복잡한 제약/접촉에는 별도 수학 검증 전 적용 금지.
5. 공식 MappingGraph1c8a469를 포함한 matched SDK를 별도 full build로 확보하고60k/120k 및 골든 회귀.
6. network/offline packages 확보 시 Optuna3+24, CPython3.12/SofaPython3 원본 장면 복구.
7. 실제 E/필름두께/마찰/압력/경로 측정 후 연구 입력의 불확실성 축소.

## 재현(새 출력 루트, 기존 결과 덮어쓰기 금지)

```bash
cd /home/ubuntu/LHJ/ReGrip
export PYTHONPATH=.:tools OPENBLAS_NUM_THREADS=1
export REGRIP_STABILIZATION_OUT=$PWD/results/stabilization_new
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
cmake -S models/stabilization -B build/stabilization_20261115/plugin -DCMAKE_PREFIX_PATH=/home/ubuntu/SOFA/v26.06.00 -DCMAKE_BUILD_TYPE=Release
cmake --build build/stabilization_20261115/plugin -j2
cmake -S models/stabilization -B build/stabilization_20261115/contact_v2 -DCMAKE_PREFIX_PATH=/home/ubuntu/SOFA/v26.06.00 -DCMAKE_BUILD_TYPE=Release
cmake --build build/stabilization_20261115/contact_v2 -j2
build/stabilization_20261115/contact_v2/test_stabilization_contact
$PY tools/stabilization_dependencies.py
$PY tools/stabilization_trials.py static
$PY tools/stabilization_static_extras.py
$PY tools/stabilization_trials.py regression
$PY tools/stabilization_compensated_suite.py
$PY tools/stabilization_compensated_followup.py
$PY tools/stabilization_compensated_checks.py
$PY tools/stabilization_audit.py
$PY tools/stabilization_eight_search.py
$PY tools/stabilization_grasp.py sphere_x_valid
$PY tools/stabilization_grasp_suite.py
$PY tools/stabilization_grasp_refine.py
$PY tools/stabilization_grasp_fine.py
$PY tools/stabilization_fast_fine.py
$PY tools/stabilization_grasp_gate.py
$PY tools/stabilization_energy.py
$PY -m unittest discover -s tests -p test_stabilization.py
```

Memory/probe CMake는 diagnostics/stabilization, 실제 process 명령은 저장된command.json/result.json을 따른다.
추가 바이너리는 같은 CMake source를 별도 build/stabilization_20261115/compensated,
telemetry, contact_fast 디렉터리에 configure 후 각각 ReGripCompensated/test_compensated,
ReGripTelemetry, ReGripDistributed/test_stabilization_contact target으로 빌드한다.
fast 실행 시 REGRIP_CONTACT_PLUGIN=$PWD/build/stabilization_20261115/contact_fast/libReGripDistributed.so를 설정한다.
위 명령은 현재 소스의 새 실행이며 수정 전 실패 로그를 덮어쓰지 않는다.
외부 의존성과 원본 실행의 BLOCKED가 해소되기 전 성공으로 기록하지 않는다.
