# 재개 지점 / 실행 명령

## 먼저 읽고 검증

```bash
cd /media/ubuntu/99419895-2058-45b4-b746-b36ea7112e4e/research/LHJ/ReGrip
git status --short
git log -5 --oneline
export PYTHONPATH=.:tools
export OPENBLAS_NUM_THREADS=1
/home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/grasp_verify_evidence.py --raw
/home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/stabilization_verify_evidence.py --raw
build/grasp_20261115/release_final/test_grasp_stick
```

기존 raw/binary/source version map를 유지하고 새campaign을 선택한다. 예시경로가 존재하면 다른고유이름 사용.

```bash
export REGRIP_GRASP_OUT="$PWD/results/grasp_followup_01"
export REGRIP_STICK_PLUGIN="$PWD/build/grasp_20261115/stick_v4/libReGripStickSlip.so"
/home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/grasp_campaign.py directions_settled
/home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/grasp_final_sequence.py
```

위는 현재법칙 재현명령이지 아래 미완료물리를 해결하지 않는다. out루트를 바꾼 상태의 grasp_publish/evaluate는
필수세트가 없어 실패할 수 있다. 부분 새결과에는 별도analysis, 완전 기존campaign 분석에는 기존OUT를 사용한다.

## 최우선 미완료 개발

1. 좁은활성접촉구간 SDF 교차분할/적응적분 또는 유한3D표면 보정. q32성능을 기준설계로 승인하지 않는다.
   수학단위→동일spacing11/21/41노드→q독립세분화→dt/잔차→실제SOFA 순서.
2. 반대점 rank5해소: 유한접촉패치/다중비공선접촉/근거있는 물리torsion저항을 독립 연구모델로 구현.
   자유6DOF물체 외부torque시험;숨은constraint/위치보정 금지.
3. 새모델 sphere6방향+release 재검증후 원통·박스 동일6방향/24s복원. 그다음 파지최적화gate 판정.
4. BeamFEM 실제force와 일치하는energy/closed-work-loop, actuator/parameter/Rayleigh일.
   .5dKlocald를 일반potential로 채택하지 않는다.
5. patched SDK는 최소엔진/골든/8층만PASS. 최신파지플러그인을 새빌드에서 동일SDK로 빌드후
   grasp/memory회귀. 설치엔진/기존ABI 혼합금지. 수시간 검사는 별도 자원계획 후 실행.

## 해결한 의존성 재사용

Optuna `.python-deps/grasp`와 Python312 `.runtime/python312`는 재설치하지 않는다.
원본복구환경은 results/grasp_20261115/python_recovery/environment.json.
새out에서 `tools/grasp_python_recovery.py`, 이후 `grasp_python_xml_compare.py`로 재실행 가능.

Optuna를 추가 탐색하려면 **새study와새out**를 사용한다(기존SQLite manifest보존):

```bash
REGRIP_BUILD_ROOT=build/revalidation_20261114_final PYTHONPATH=.python-deps/grasp:.:tools /home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/optimize.py --gate results/revalidation_20261114T132734Z/physics_release/gate.json --out results/grasp_followup_optuna_01 --study planar_followup_01 --trials 3
```

기존 validated_planar_20261115 study 재개는 이번세션에서 실제 검증했으나 현재 불변SQLite를 추가변경하지 않는다.
SDK 재현은 동일7c18e95소스+공식PR6259의3파일 수정+grasp_evidence/patched_CMakeCache.txt 옵션 참조.
기존build read-only 메모리시험:

```bash
build/grasp_20261115/sofa_patched/bin/memory_lifetime build/grasp_20261115/sofa_patched scenes/integrated/minimal_mapping_graph.scn
```

stdout은 새로그에 저장하고 기존audits를 덮지 않는다. 개별물리4GiB/최대480s,최대2개병렬 원칙.
실물장비/유료/기밀/파괴적원격Git 작업은 범위밖.
