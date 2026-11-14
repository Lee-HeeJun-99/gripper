# 환경 및 검증 보고서

점검일: 2026-11-14 (Asia/Seoul). 물리 검증 결과는 없음.

## 확인된 환경

SOFA 설치: `/home/ubuntu/SOFA/v26.06.00`.
`bin/runSofa-26.06.00 --help` 정상 실행.
CMake 3.22.1, GCC/G++ 11.4.0, Git 2.34.1 확인. Ninja는 PATH에서 발견되지 않았으나 Make 빌드가 가능하므로 필수 누락으로 판단하지 않는다.
SOFA `include/Sofa.Core/sofa/core/behavior/ForceField.h` 및 `lib/cmake` 개발 설정 존재.
핵심 라이브러리는 `lib/`, 플러그인 라이브러리는 `plugins/*/lib/`에 있다.
runSofa의 ldd 의존성에 `not found`가 없었다. 전체 Development 빌드 가능성은 아직 검증하지 않았다.

## 실행 확인과 결함

XML 빈 scene을 GUI 없이 `--noautoload -g batch -a -n 2`로 2스텝 실행했다.
`--nbIterations 2`는 이 버전에서 적용되지 않고 기본 1000스텝이 실행되는 것을 확인했다.
라이브러리와 실행 로그로 실제 옵션이 `-n` / `--nbIter`임을 확인했다.

SofaPython3 파일 및 CPython 3.12 바인딩은 존재하지만
`libpython3.12.so.1.0 => not found`로 로딩에 실패한다.
기본 Python은 miniconda 3.14.6, `/usr/bin/python3`는 3.10.12이다.
Python scene 로딩 실패 시에도 runSofa 종료 코드 0을 관찰했으므로 로그 오류와 성공 마커를 함께 검사한다.

관리자 권한 없이 프로젝트 내부 conda Python 3.12 + numpy 환경 생성을 시도했다.
`repo.anaconda.com` DNS 해석 실패로 종료 코드 1. 설치는 완료되지 않았다.
로컬 miniconda 캐시에 Python 3.12 패키지를 찾지 못했다.

## 인수인계 및 기준 모델

작업 루트에는 SOFA 설치 파일과 읽기 전용 빈 관리 폴더만 있었으며 Git 저장소가 아니었다.
홈 디렉터리 깊이 6까지 이름에 ReGrip이 포함된 파일/폴더를 검색했으나 원본을 찾지 못했다.
깊이 4 이내 압축 파일 목록에서도 명시적인 ReGrip 인수인계 파일을 찾지 못했다.
다른 이름 또는 다른 위치의 패키지가 없다는 뜻은 아니다. 정확한 경로가 필요하다.
V1.0.6 전단 모델, V1.0.9 FREE FEM, V1.1.0 ForceField 및 오류 이력은 미분석이다.

사용자 제공 Windows 비교값(직접 재검증하지 않음):

| dt (s) | 시간 (s) | 스텝 수 | 끝단 처짐 (mm) | 최대 X 상대 미끄럼 (mm) |
| --- | --- | --- | --- | --- |
| 0.0005 | 0.3 | 600 | 0.04121379 | 0.00082281 |

Ubuntu 지표, 플랫폼 차이, 허용오차 및 정적 평형 여부는 미확인이다.
원본의 단위, 처짐 부호/측정 노드, 상대 미끄럼 정의, 하중, 경계조건, 재료,
mesh 및 solver 설정을 고정한 후 반복 실행과 dt 수렴성으로 허용오차를 정한다.
현재 임의 허용오차를 통과 판정에 사용하지 않는다.

## 진행 제한

기준 모델이 검증되지 않았으므로 사용자 지시에 따라 이후 단계는 실행하지 않았다.
C++ addForce/addDForce/buildStiffnessMatrix, 행렬 일관성, 물리 실험,
Optuna, 최적 파라미터 및 비교 그래프는 모두 미완료다.
`results` CSV는 환경 점검 결과이며 FEM 실험 결과가 아니다.
