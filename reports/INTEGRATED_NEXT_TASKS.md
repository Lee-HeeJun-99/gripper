# Bounded cycle — finite extensible free-tip reference (2026-11-26)

Started from a46536d2ec628e76c1da4d859aee83787d0bf1c1. Supervisor local save
PENDING; no git add/commit or commit SHA claimed. One actual design/analysis
cycle: scripts/extensible_rod_reference.py and validation/finger/extensible_reference1.
Rail and PET are separate finite planar extensible rods, root x/y/rotation fixed,
free axial tip, prescribed spatial dead transverse force, zero terminal moment.
These are explicit reference boundary conditions, NOT the actual assembly guide.
Independent axial strain is eliminated by exact stationarity e=(F dot t)/EA;
rotation remains nonlinear. Conditional typical material/projected section basis
and candidate RevAD lengths are unchanged. No CAD/BOM adoption or material fit.

Six body/load cases (0.1uN,1mN,20mN) and16/32/64 midpoint meshes give18 actual
solutions. Independent continuous BVP comparison passes predeclared0.1% finest
tip/rotation reference limits: largest finest tip difference0.006104%.
Small-load linear limit, finite virtual work and rotated-load objectivity pass.
Independent saved-state complex-step energy derivatives, axial equilibrium,
kinematic compatibility, stored energy reconstruction and input hashes pass
all18 states; deliberately perturbed terminal rotation is rejected.
All discrete optimizers report success and residuals are finite; original
individual child exit codes were not separately captured (outer log-reading
shell exit0 is NOT used as acceptance). Full logs/metadata retained.
PET20mN finite tip differs8.76519% from linear, Rail0.456074%; this provides an
actual finite-rotation reference rather than reinterpreting old linear states.

Read-only extensible_release1 remains INTEGRATED_NOT_QUALIFIED (24 audit errors,
including22 unqualified Stage2 criteria). Reference PASS is not contact, actual
BRep, strength, friction, dynamic/global assembly energy or system release PASS.
All prior failures and pre-existing untracked CAD/BOM remain unchanged.
READY flexible_rail_contact now requires coupled separate finite bodies, actual
guide axial boundary conditions, and actual geometry contact re-evaluation.
Alignment and fixture tracks remain independent READY work. No Stage3, SDK,
criteria, manager or save-control changes. No RUNNING queue records or live
analysis children at handoff.4GiB/420s bounds and STOP were respected.

# Bounded cycle — distributed elastic Rail/PET (2026-11-26)

Started from19e9ea67e34edc8bbaf43bd6738b58508043fbc6. Supervisor local save PENDING;
worker did not stage/commit or change manager controls. RevAA remains adopted.
New actual output: validation/finger/flexible_distributed2/summary.json.
Nine RevAD-length small-load separate-DOF linear cases use the existing beam/QP
kernel with distributed unilateral interface, continuous cubic extrema and moving
tip-tangent terminal walls. Overall FAIL(exit2):8element +/-1mN PET Green tip
errors0.272/0.180nm exceed declared0.1nm. All16/32cases pass; finest motion
relative error max3.483e-7. All9force/moment/gap/complementarity/static-energy
checks pass. This is conditional typical-material projected geometry only.
Independent saved-state verifier passes, input hashes checked, release audit
remains INTEGRATED_NOT_QUALIFIED with22unqualified Stage2 criteria.

New mechanism evidence: terminal-only -1mN interface gap -0.200001mm;
distributed contact changes Rail tip from -0.279148 to -0.243442mm. Small
+10uN open-contact case matches independent terminal Green reference.
This excludes terminal-only reference as a distributed-surface certificate.
First attempt serialization failure(exit1) preserved in flexible_distributed1
with original producer/input hashes/log; first state was not serialized.
No old failures, CAD/BOM, criteria or SDK changed. No full finite deformed BRep,
finite rotation, friction, strength or global dynamic energy PASS.
Next READY: independently validated finite-rotation actual Rail/PET geometry;
preserve coarse Green failures and quantify discretization separately. Do not
repeat this9case linear experiment as new progress. No RUNNING queue records
or live analysis children at handoff. Save manifest contains cycle files only.

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
