# 07 — 자동 실행 및 결과 무결성

이번 실행: `results/revalidation_20261114T132734Z`. 시작 커밋 `8ee78f0c84d042812537655583cb98ed037f310e`, 검증 중 dirty=true. 별도 브랜치와 소스/바이너리 SHA256으로 추적한다. 과거 `results/physics_validation`은 회귀 비교 인용에만 사용했고 이번 gate의 성공값을 재사용하지 않았다.

**PASS**: 최종 자동화 시험 20개, failures=0/errors=0.
초기 19개 시험 중 2개는 기대 메시지 문자열이 실제 사유와 달라 FAIL이었다. 분류 범주는 맞았으며 assertion을 실제 진단 문자열에 맞추고,
계면 속도 NaN 검사도 추가하여 20개를 새 디렉터리에서 다시 수행했다. 초기 FAIL JSON과 최종 로그를 모두 보존했다.

추가된 처리: finite 입력 검사, 폴더 원자적 소유권, 실행 전 명령/설정/소스 해시 저장,
실행 중 incomplete 기록, C++ 소스와 실제 빌드 바이너리 manifest 검증, stdout/stderr 분리, timeout/KeyboardInterrupt의 프로세스 그룹 종료 및 wait,
중간 시점 검사, root/mapping/범위 검사, CSV 및 전체 artifact SHA256 무결성 검사.
기존/부분 생성 디렉터리는 재사용하지 않으며 재시작은 새 디렉터리로 수행한다.
실험 결과를 재사용할 때는 manifest와 설정/바이너리를 다시 확인한다.

| 검사 | 시험 방식 / 결과 |
| --- | --- |
| timeout / interrupted | 실제 SOFA 자식 종료, 유효 강성 없음, wait 후 PID 소멸 PASS |
| crash | 별도 fault 프로세스의 SIGSEGV, 비정상 종료 거부 PASS |
| 로그-only ERROR | 실제 runSofa의 없는 플러그인, exit=0인데도 거부 PASS |
| NaN/Inf, diverged, invalid_physics | 새 정상 SOFA raw 출력의 명시적 손상 fixture, 올바른 분류 PASS |
| not_converged | 실제 .01초 SOFA 실행, execution_completed=true / stiffness=None PASS |
| 중복 실행 | 같은 폴더에 두 독립 CLI 실행, 하나만 소유권 획득 PASS |
| 손상 CSV / 누락 파일 / 비단조 시점 | manifest/parser가 거부 PASS |
| 프로세스·FD | 24회 launcher 반복 후 자식 모두 reap, FD 수 동일 PASS |

6초 연장 SOFA에서도 완료/평형을 확인했다. 수 시간 또는 수천 회 장시간 soak: **NOT RUN**.
상한/물리 범위 검사는 실행 후 출력 평가이므로 모든 발산의 즉시 중단을 보장하지 않는다.
주소 공간 제한 4 GiB, 기본 timeout 60초는 유지했다.
각 실험의 Git/dirty/소스/.so/config/명령/stdout/stderr/시간/시계열/지표/실패사유/평형 판정은 로컬 raw 디렉터리에 있다.
raw와 대용량 CSV는 Git에 추가하지 않았다.
