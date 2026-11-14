# 개발 환경 보고서 — 2026-11-14

| 항목 | 확인 결과 |
| --- | --- |
| OS | Ubuntu 22.04.5, Linux 6.8.0-138-generic |
| SOFA | /home/ubuntu/SOFA/v26.06.00 |
| 실행 파일 | bin/runSofa-26.06.00 |
| SDK | include, lib, lib/cmake, plugins/*/include 및 lib 존재; 실제 플러그인 빌드 확인 |
| Compiler | GCC/G++ 11.4.0 |
| CMake | 3.22.1 |
| 빌드 도구 | /usr/bin/make 사용; Ninja 미발견 |
| 기본 Python | miniconda 3.14.6 |
| 시스템 Python | /usr/bin/python3 3.10.12 |
| 분석 Python | /home/ubuntu/miniconda3/envs/robot_ws/bin/python 3.10.20 |
| 분석 패키지 | NumPy 1.26.4, Matplotlib 3.10.9 |
| Optuna | 미설치, 설치 시도 실패 |
| SofaPython3 | CPython 3.12 바인딩 존재, libpython3.12.so.1.0 누락 |

핵심 헤더: include/Sofa.Core/sofa/core/behavior/ForceField.h.
SOFA 26.06 강성행렬 선언은 같은 behavior 폴더의 BaseLocalForceFieldMatrix.h에 있다.
lib/cmake/Sofa.Core, Sofa.DefaultType, Sofa.Helper, Sofa.Component.StateContainer 등을 사용했다.
C++ 플러그인과 관측 플러그인의 ldd에서 누락 라이브러리가 없었다.
SofaPython3는 ldd 자체 종료 코드가 0이어도 `not found`가 있으므로 로딩 가능한 상태가 아니다.

네이티브 batch 옵션은 `-g batch -a -n <steps>` 또는 `--nbIter`이다.
`--nbIterations`는 적용되지 않아 기본 1000스텝을 실행하는 현상을 확인했다.
Python scene 로딩 실패에도 runSofa가 0으로 종료했으므로 로그와 실행 증거를 함께 검사한다.

관리자 권한 없이 프로젝트 내부 conda Python 3.12+NumPy 환경 생성을 시도했으나
repo.anaconda.com DNS 해석 실패로 중단됐다.
Optuna는 기존 환경/로컬 파일에서 찾지 못했고 프로젝트 내부 pip 설치도
`No matching distribution found for optuna`로 실패했다.
현재 native XML+C++ 실행에는 SofaPython3가 필요 없으므로 물리 검증은 진행할 수 있었다.

두 C++ 프로젝트의 configure/compile 및 CTest 로그는 results/build_logs,
환경 명령·의존성·원본 컴파일 실패 로그는 results/development_environment에 있다.
전체 Development SDK의 모든 선택 컴포넌트를 빌드한 것은 아니다.
사용한 헤더·라이브러리와 플러그인 경로의 실제 컴파일/링크/로딩을 검증했다.
