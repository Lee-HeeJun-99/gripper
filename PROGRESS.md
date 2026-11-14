# 진행 현황 — 2026-11-14

## 완료

- 인수인계 외부 ZIP 및 내부 ZIP 4개 수령·분리 보관, 56개 원본 항목 바이트 일치 확인.
- V1.0.6 정적 FEM, V1.0.9 FREE/이전 Python 크래시 경로, V1.1.0 C++ 및 기존 오류 이력 분석.
- SOFA 26.06 SDK, GCC/G++ 11.4, CMake 3.22, Make 확인.
- Python 3.12 없이 실행 가능한 동일 물리 XML 어댑터 및 17자리 상태 기록기.
- Windows CSV 600개 시점 회귀 2회 재현 및 잔차 관측 추가 후 재확인.
- C++ 헤더·SReal API 호환 수정, .so 빌드/등록/로딩.
- 실제 addForce/addDForce/buildStiffnessMatrix, 힘/모멘트 부호, kFactor, 에너지/접선 근사오차, 연결점 선택 검사.
- 물리 실행 19개, FREE 기준 실행 및 의도한 timeout 분류 검사.
- 정적 평형, dt 절반·두 배, 반복, 실행 연장, 하중 선형성, 메시 세분화, 연결점 위치 비교.
- 원형 등가단면과 사각단면의 축강성 불일치 원인 확인; 검증 모델을 임의 변경하지 않음.
- 총 45개 gate 항목 통과; 실행별 CSV/로그/설정, 비교 PNG 2개, sweep 후보 JSON 작성.
- Optuna 코드 구현, 물리 gate·소스/바이너리 해시 확인 및 의존성 부재 차단 동작 확인.

## 미완료 및 차단

- SofaPython3 원본 Python scene 실행: libpython3.12.so.1.0 누락.
- Python 3.12 설치: conda 저장소 DNS 해석 실패.
- Optuna 설치/실제 최적화: pip가 사용 가능한 Optuna 배포본을 받지 못함.
- Optuna 실제 실행 횟수 0, 최적 파라미터 없음. k=100 결과는 고정 sweep 후보뿐이다.
- 작은 회전 근사 밖의 정확한 3D 회전 에너지/접선, 실제 PET 물성·단위 보정,
  진공 마찰, 압력-강성 매핑, 100 mm 핑거 및 실물 파지는 미검증.

## 다음 작업

1. 설치 가능한 환경 또는 오프라인 wheel로 Optuna와 의존성을 프로젝트 내부에 확보.
2. 기존 gate/해시 확인 후 Optuna 실행 및 Pareto 후보의 추가 dt·시간·메시 검증.
3. Python 3.12 공유 라이브러리/표준 라이브러리/NumPy를 확보해 원본 SofaPython3 scene 회귀.
4. 향후 별도 모델에서 사각 단면 축강성과 정확한 회전 운동학을 검증하고 기존 원형 FREE 기준은 보존.

검증 프로토콜과 실제 수치는 VALIDATION.md 및 results/physics_validation/gate.json 참조.
