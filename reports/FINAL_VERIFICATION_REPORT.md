# ReGrip 최종 재검증 보고서

종합 상태: **BLOCKED / 부분 완료**. 접선 연구모델의 재검증과 자동화 보강은 완료했으나,
실제 Optuna 최적화와 원본 SofaPython3 복구는 외부 의존성 문제로 완료하지 못했다.
PASS=실행·통과, FAIL=실행·실패, BLOCKED=환경·의존성 차단, NOT RUN=미실행, NOT APPLICABLE=현재 연구모델 대상 아님.

이번 실행: `results/revalidation_20261114T132734Z`. 시작 커밋 `8ee78f0c84d042812537655583cb98ed037f310e`, 검증 중 dirty=true. 별도 브랜치와 소스/바이너리 SHA256으로 추적한다. 과거 `results/physics_validation`은 회귀 비교 인용에만 사용했고 이번 gate의 성공값을 재사용하지 않았다.


## 1. 소스와 실행 환경

검증 브랜치 verification/full-revalidation-20261114. Ubuntu 22.04.5, SOFA 26.06.00,
GCC/G++ 11.4, CMake 3.22.1, 분석 Python 3.10.20/NumPy 1.26.4.
최종 C++ 플러그인 SHA256 `53d789548979944460f6995bee6619173564b1255c2a9bd59e595d9e4d49e6da`,
관측기 `99140ef4358690ed76b98e7d2944f46a20fc17d2d91690f7ade89c620e78f0f3`.
시작 커밋은 위 값이며 최종 로컬 커밋은 응답과 git log에 보고한다. 실행 중 dirty 상태와 소스 해시를 숨기지 않았다.

## 2. 이전 상태와 새 검증

| 항목 | 이번 결과 |
| --- | --- |
| 원본/골든 보존 | PASS, 56개 archive member 바이트 일치 |
| C++ clean build / 등록 / 로딩 | PASS |
| 힘/에너지/Jacobian/kFactor/입력 안전성 | PASS, k=0..100의 600개 무작위 검사 + 고장 probe |
| FREE 600개 시점 회귀 2회 | PASS, 기존 오차 예산 유지, 동일 CSV |
| 기존 물리 gate | PASS, 45/45 새 실제 실행 |
| 추가 반복/힘·모멘트 균형 | PASS |
| 자동화 | PASS, 최종 20개 검사 |
| 최적화 guard/목적함수 | PASS, 실제 새 측정값 사용 11개 검사 |
| ASan/UBSan 단위 검사 | PASS; LSan는 BLOCKED |
| Optuna 3회 smoke / 24회 본 탐색 | BLOCKED, 실제 trial 0 |
| Pareto 후보/검증 | NOT RUN, 후보 없음 |
| SofaPython3 | BLOCKED, CPython 3.12 런타임 부재 |
| 실물 진공/파지/100 mm 핑거 | NOT APPLICABLE(이번 연구모델 검증 범위 밖) |

## 3. 수정과 수학적 근거

수정 전 high-k 에너지 FD FAIL, NaN force FAIL, null matrix SIGSEGV를 실제 재현했다.
작업 C++의 각도 복원을 2*atan2(qy,qw)로 맞춰 원래 선형 각도 전단식에 힘과 행렬을 일치시켰다.
원본 V110 자료는 변경하지 않았다. 물성·하중·회귀 허용오차도 변경하지 않았다.
runner와 관측기의 입력/출력/중단/무결성/해시 처리를 보강했다.
정적/수치 gate, baseline, 20개 자동화 검사를 수정 후 새 폴더에서 다시 실행했다.

## 4. C++ 빌드 및 플러그인 로딩

깨끗한 별도 디렉터리에서 두 .so와 실제 C++ 테스트를 빌드하고 runSofa 로딩을 확인했다.
소스-바이너리 manifest 불일치와 무효 입력은 실행 전에 거부한다.
실제 힘·미분력·조립 행렬을 k=0~100의 총 600개 무작위 평면 상태에서 검사했다.
상세 수치와 ASan/UBSan/LSan 범위는 03 보고서 및 revalidation_evidence/cpp_native.log 참조.

## 5. FREE 기준 회귀

FREE 0.3초 처짐 0.041213791606346278 mm,
X slip 0.00082280720342708946 mm,
vz -0.014380704053554549 mm/s.
전체 시점 최대 처짐 차이 1.38778e-16 mm.
회귀 허용오차는 1e-10+1e-6|golden|다.

## 6. 수학·물리·수치 검증

FREE 3초 평형 처짐 0.042187419375712826 mm.
k=100 평형 처짐 0.025170333837966546 mm,
강성비 1.67607706943, 최대 X slip 3.06235645198e-06 mm,
잔차 1.41870131e-06, 최대 회전 0.00128974549 rad.
이는 **고정 sweep 결과**이며 Optuna 최적값이 아니다.
사각 A=3.2와 원형 등가 A≈.732233의 EA 차이가 약 3.97배 대 1.68배 차이를 설명한다.

## 7. 자동 시뮬레이션·로그·설정·재현 명령

실험 19개 평형 gate + 추가 4개 설계/고강성 반복 실험의 지표 CSV:
[measured_experiments.csv](revalidation_evidence/measured_experiments.csv).
각 행에 metrics 경로가 있고 그 디렉터리에 config.json, command.json, stdout.log, stderr.log,
raw 상태, timeseries.csv, metrics.json 및 artifact SHA256이 있다.
작은 핵심 JSON/단위 로그는 [revalidation_evidence](revalidation_evidence/)에 Git 관리한다.
큰 raw/시계열/빌드/의존성은 ignored 로컬에 남겼다.

```
/usr/bin/python3 tools/build.py --build-root build/revalidation_new --logs results/revalidation_new/build
REGRIP_BUILD_ROOT=$PWD/build/revalidation_new /home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/validate_physics.py --out results/revalidation_new/physics
```

위 새 경로는 예시이며 이미 생성된 실험 경로를 덮어쓰지 않는다.
이번 실제 경로는 `/home/ubuntu/LHJ/ReGrip/build/revalidation_20261114_final`와 `/home/ubuntu/LHJ/ReGrip/results/revalidation_20261114T132734Z/physics_release`다. gate/로그에는 실제 명령이 있다.
물리 gate와 artifact 해시 검증 없이 최적화를 재개하지 않는다.

## 8. Optuna 설치 및 최적화

isolated pip 설치, 로컬 wheel/캐시 조사 및 3/24-trial 명령을 실제로 시도했다.
Optuna 의존성 부재로 실제 trial은 0회다. SQLite 저장·중단 재개·sampler 경로는 NOT RUN이다.
11개 의존성 없는 guard/목적함수 검사는 통과했지만 이를 실제 최적화로 계산하지 않는다.

## 9. Pareto 후보 비교

Optuna Pareto 후보는 생성되지 않아 비교는 NOT RUN이다.
k=100, 연결점 10개는 고정 sweep에서의 후보일 뿐이며 최적값·전역 최적값이 아니다.
해당 고정 후보의 dt/메시/6초 연장/독립 반복 검사는 별도로 통과했다.

## 10. SofaPython3 복구

CPython 3.12 ABI와 libpython3.12.so.1.0 부재를 재확인했다.
오프라인 Conda는 패키지를 찾지 못했고 온라인 설치는 DNS 실패였다.
원본 Python 장면의 복사본을 실행 요청했으나 로딩 ERROR로 실패했으며 exit=0을 성공으로 처리하지 않았다.
원본 Python의 기계적 상태·CSV·XML과의 직접 비교는 BLOCKED/NOT RUN이다.

## 11. 잔여 문제 및 미검증 항목

Windows raw 상태 벡터 부재, 전체 BeamFEM 에너지 API 미구현, LSan ptrace 제약,
장시간 soak 미실행, 실제 Optuna sampler·SQLite 재개 경로와 SofaPython3가 남아 있다.
작은 평면 회전 범위 외의 3D/큰 회전, 실제 PET 단위·마찰·진공·파지 성능은 인증하지 않았다.

## 12. 다음 개발 단계와 우선순위

1. 외부 패키지를 쓸 수 있는 환경/오프라인 wheel로 Optuna 및 의존성을 확보한다.
2. 3회 smoke에서 SQLite/중단 재개/실패/prune/Pareto 경로를 실제 확인한 뒤 최소 24회 본 최적화를 실행한다.
3. Pareto 후보 dt 절반/6초/21노드/반복을 확인한다. 현재 후보가 없으므로 비교 표를 꾸미지 않았다.
4. CPython 3.12 공유 런타임+표준 라이브러리+NumPy를 프로젝트 내부에 복구해 원본 Python을 비교한다.
5. full BeamFEM 에너지, 큰 회전/3D, 실제 PET 단위·마찰·진공 보정은 별도 연구로 수행한다.

Windows CSV는 raw 22노드 상태를 제공하지 않아 파생 지표 회귀까지만 가능했다.
3D 큰 회전과 실물 성능은 주장하지 않는다. LSan, 긴 soak 및 Optuna 실제 API 경로의 미검증도 남는다.
원격 push/이력 재작성/원격 브랜치 삭제/시스템 전체 변경은 수행하지 않았다.

## 상세 보고서

- [01_SOURCE_AUDIT.md](01_SOURCE_AUDIT.md)
- [02_ENVIRONMENT_VALIDATION.md](02_ENVIRONMENT_VALIDATION.md)
- [03_CPP_FORCEFIELD_VALIDATION.md](03_CPP_FORCEFIELD_VALIDATION.md)
- [04_BASELINE_REGRESSION.md](04_BASELINE_REGRESSION.md)
- [05_PHYSICS_VALIDATION.md](05_PHYSICS_VALIDATION.md)
- [06_STIFFNESS_AND_SLIP.md](06_STIFFNESS_AND_SLIP.md)
- [07_AUTOMATION_VALIDATION.md](07_AUTOMATION_VALIDATION.md)
- [08_OPTUNA_OPTIMIZATION.md](08_OPTUNA_OPTIMIZATION.md)
- [09_SOFAPYTHON3_RECOVERY.md](09_SOFAPYTHON3_RECOVERY.md)
- [10_FINAL_CODE_REVIEW.md](10_FINAL_CODE_REVIEW.md)
