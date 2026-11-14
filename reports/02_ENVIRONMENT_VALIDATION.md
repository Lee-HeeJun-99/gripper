# 02 — 환경 재검증

이번 실행: `results/revalidation_20261114T132734Z`. 시작 커밋 `8ee78f0c84d042812537655583cb98ed037f310e`, 검증 중 dirty=true. 별도 브랜치와 소스/바이너리 SHA256으로 추적한다. 과거 `results/physics_validation`은 회귀 비교 인용에만 사용했고 이번 gate의 성공값을 재사용하지 않았다.

Ubuntu 22.04.5, Linux 6.8.0-138-generic, GCC/G++ 11.4.0, CMake 3.22.1을 실제 명령으로 재확인했다.
SOFA: `/home/ubuntu/SOFA/v26.06.00`; include 및 lib/cmake의 SDK로 clean build와 링크를 확인했다.
CPython 분석 환경: `/home/ubuntu/miniconda3/envs/robot_ws/bin/python` 3.10.20.
NumPy 1.26.4, SciPy 1.15.3, Matplotlib 3.10.9; Optuna 미설치.
시스템 Python 3.10.12와 기본 Conda Python 3.14.6을 변경하지 않았다.
자원 snapshot: 논리 CPU 20, RAM 31 GiB/가용 약 21 GiB, 디스크 가용 약 63 GiB. 전체 실험 데이터는 프로젝트 내부에 보존했다.

| 항목 | 상태 | 증거 |
| --- | --- | --- |
| SDK, 플러그인 의존성 | PASS | final_plugin_ldd / final_diagnostics_ldd 로그, 누락 없음 |
| C++ ABI | PASS(사용 경로) | compiler `['#define _GLIBCXX_USE_CXX11_ABI 1']`, 실제 .so 로딩·계산 수행 |
| SofaPython3 | BLOCKED | CPython 3.12 ABI, libpython3.12.so.1.0 not found |
| Optuna 설치 | BLOCKED | pip exit 1; 배포본 없음. curl exit 6, DNS lookup exit 2 |
| 로컬 캐시 | BLOCKED | Python 3.12/Optuna wheel 미발견. 일부 권한 없는 폴더는 읽지 못했으며 우회하지 않음 |

Conda 오프라인 생성은 PackagesNotFoundInChannelsError, 온라인 생성은 repo.anaconda.com DNS 오류였다.
isolated pip와 프로젝트 내부 --target을 사용했고 시스템 재설치나 Python 대체는 하지 않았다.
환경 기본 pip 실패와 직접 DNS 증거를 구분하며 pip 메시지 하나만으로 원인을 단정하지 않는다.
명령 로그: `results/revalidation_20261114T132734Z/commands/`. 핵심 작은 증거 사본: `reports/revalidation_evidence/`.
