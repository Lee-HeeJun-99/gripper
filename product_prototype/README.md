# ReGrip native product prototype

기존 자체 물리 연구와 독립된 제품 후보. 새 물리 Solver는 만들지 않았다.
기구 설계 및 SOFA 기본 기능 검증을 우선한다.

시작:[제품 설계](reports/REGRIP_PRODUCT_DESIGN.md),
[조립 사양](reports/REGRIP_ASSEMBLY_SPEC.md),
[Native 검증](reports/REGRIP_SOFA_NATIVE_VALIDATION.md),
[도면/분해도](drawings/candidate_v3/),
[CAD 소스](meshes/product_outboard14_v3/assembly.scad).

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
# 새 출력 태그 필수. 기존 Raw/Checkpoint를 이어 쓰지 않는다.
$PY product_prototype/sofa/run_native.py --tag UNIQUE_SINGLE
$PY product_prototype/sofa/run_native.py --tag UNIQUE_THREE --fingers 3 --object free --gravity --floor --outboard 14 --intersection LocalMinDistance --stroke 6 --support-radius 35 --support-gap .4 --center-z -75
$PY product_prototype/sofa/run_native.py --tag UNIQUE_CYLINDER --fingers 3 --object free --gravity --floor --outboard 14 --intersection LocalMinDistance --stroke 6 --shape cylinder --support-radius 35 --support-gap .4 --center-z -75
```

기본 주기0-.5s Closing,.5-1s Hold,1-1.5s Release,1.5-2s Recovery.
--slow-cycle은0-1/1-2/2-3/3-4초의 다른 물리 입력이다.
--lift는1-1.5초 Root/Palm 및 케이블 원점을20mm 올리는 별도 실험이다.
핑거 형상이나 자유 물체 위치를 Prescribed하지 않는다. Lift 성공은 미입증.

설치된 SofaPython3는 Python3.12용이며 libpython3.12를 찾지 못했다.
XML과 입력/로깅 C++ Controller만 사용하므로 Python SDK ABI를 섞지 않는다.
물리 계산은 Native EulerImplicitSolver,TetrahedronFEMForceField,
SoftRobots CableConstraint,BlockGaussSeidelConstraintSolver,기본 충돌/매핑이다.

STEP/전체 CAD kernel 검증·모터 선정·전체 에너지/시간/메시 수렴·실제
감싸기/독립 Holding/Lift·제작 준비는 미완료다. Raw는 results/,개별 Build는
cad/build_*에 보존하며 Git에는 소스·도면·증거 Manifest를 보관한다.
