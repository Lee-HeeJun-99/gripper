# 03 — C++ ForceField 및 관측기

이번 실행: `results/revalidation_20261114T132734Z`. 시작 커밋 `8ee78f0c84d042812537655583cb98ed037f310e`, 검증 중 dirty=true. 별도 브랜치와 소스/바이너리 SHA256으로 추적한다. 과거 `results/physics_validation`은 회귀 비교 인용에만 사용했고 이번 gate의 성공값을 재사용하지 않았다.

**PASS**: 깨끗한 `build/revalidation_20261114_final`에서 두 프로젝트 configure/compile, CTest 및 실제 batch 로딩.
컴파일 옵션 -Wall -Wextra -Wpedantic; 해당 clean build 로그에서 warning/error를 찾지 못했다.
초기 재빌드/교정 빌드/최종 빌드는 서로 다른 디렉터리이며 기존 build와 원본 소스는 유지했다.

## 재현한 실패와 수정

| 입력 / 검사 | 수정 전 | 수정 후 |
| --- | --- | --- |
| k=100, theta=.0049 에너지 FD | FAIL, 오차 1.20056e-9 > 기존 1e-9 | PASS, 오차 2.09197e-16 |
| NaN stiffness | FAIL, nonfinite force | PASS, 오류 보고 후 거부 |
| null matrix | FAIL, exit -11(SIGSEGV) | PASS, 오류 보고 후 거부 |
| 음수 k, n=0, 잘못된/중복 연결점, 비정규 quaternion, 범위 밖 회전, null MechanicalParams | 과거 미검사 | PASS, 안전한 거부 |

원래 의도한 식 `s=Delta u-h/2*(theta_l+theta_u)`, `E=1/2*k*s²`를 유지했다.
이전의 `theta≈2*q_y`는 실제 SOFA 각도 좌표가 아니므로 힘에 누락된 cos(theta/2) 차이를 만들었다.
작업 사본에서는 평면 각도를 `2*atan2(q_y,q_w)`로 복원하여 기존 선형-in-angle 식과 상수 Jacobian `-k*b^T*b`가 일치하도록 고쳤다.
이는 저장 quaternion 근사를 바로잡는 수정이며, 물성·하중·허용오차를 바꾸지 않았다. 원본 V110 ZIP/소스는 유지했다.
엄밀한 에너지 함수는 이전 q 기반 근사와 O(theta³)의 slip 차이가 있으므로 결과 차이도 숨기지 않고 06 보고서에서 비교한다.

```
REGRIP_BUILD_STIFFNESS
REGRIP_ADD_FORCE
REGRIP_ADD_DFORCE
PASS actual addForce/addDForce/buildStiffnessMatrix, 600 random small-angle checks across k=0..100; max energy-gradient error=8.97252e-12, max tangent error=1.21024e-09
```

기존 에너지 FD 1e-9, 접선 FD 1e-7, kFactor 1e-14 예산을 유지했다.
힘 부호, y/z 직접 힘 0, y 모멘트, 실제 addDForce, 6-DOF 조립, 대칭, PSD 및 연결점 선택을 검사했다.
행렬 식은 조립 시 추가 kFactor를 적용하지 않으며 addDForce에만 인자 kFactor를 한 번 곱한다.

오른손 좌표계에서 `Ry(theta)e_x=(cos(theta),0,-sin(theta))`이므로 V106의 `phi=dw/dx≈-theta_y`.
따라서 V106의 `Delta u+h/2*(phi_l+phi_u)`와 V110 부호는 일치한다.
실제 매핑의 sin(theta)와 선형 전단식 theta의 차이는 남는다. 이번 인증은 작은 평면 회전(<.005 rad, qx/qz<1e-8)에 한정하며 정확한 3D/큰 회전 모델을 인증하지 않는다.

관측기는 기계적 벡터를 직접 수정하지 않고 scratch 힘을 합산하지만 ForceField 내부 캐시가 갱신될 수 있다. 이 경로를 포함한 FREE 회귀와 장시간 결과를 재검증했다.
관측기 기존 파일 덮어쓰기를 거부하고 실제 context 시간을 기록한다.

ASan+UBSan 계측 C++ 단위 검사: **PASS**, detect_leaks=0, UBSAN halt_on_error=1.
LeakSanitizer: **BLOCKED**(ptrace 환경 fatal error). 누수 미검출로 바꾸어 보고하지 않는다.
SOFA 배포 라이브러리 전체의 재계측: **NOT RUN**. 계측 단위 범위와 프로세스/FD 검사 범위를 구분한다.
명령 로그: `results/revalidation_20261114T132734Z/commands/`. 핵심 작은 증거 사본: `reports/revalidation_evidence/`.
