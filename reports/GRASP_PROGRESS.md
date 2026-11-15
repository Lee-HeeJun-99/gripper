# GRASP 신규 캠페인 — 2026-11-15

기준9b95d0c03e0557829ec3f6bab095935144bb9a63, 새 브랜치 development/regrip-validated-grasp.
새 실제 저장소 경로 사용. 이전 검증 증거1243개 해시 일치, 원본 모델/골든 수정 없음.
raw는 results/grasp_20261115, build는 build/grasp_20261115이며 기존 결과를 덮어쓰지 않는다.

## 초기 실행 완료

- 신규 elastic stick / equal-mu Coulomb return mapping: 별도 models/grasp.
- 독립 C++ 무접촉/Stick/Slip/해제/재접촉/객관성/작용반작용/모멘트/이력 순수성/API PASS.
  smooth branch FD maxJ1.09249e-10, maxMoment2.71051e-20.
- 평면 접촉 이산 에너지: work3.044e-5, D2.7555e-5, algorithmic1.625e-7.
  알고리즘 감쇠항을 물리 마찰 소산과 구별한다.
- sphere_x_probe 실제18s, alphaMass.2, F1e-6, hold6→14s:
  변위.000565682682307056mm, 상대 힘 잔차2.3535685227983605e-5,
  속도2.7435773259016662e-8mm/s; hold 접촉2/Stick2/Slip0,
  friction capacity ratio≈.30423,18s 접촉0. EXPERIMENTAL, 전체 파지 인증 아님.
- Optuna4.6.0은 .python-deps/grasp 격리 설치 및 import 성공. 실제 최적화는 아직 미완료.
- CPython3.12/NumPy는 .runtime/python312 설치 성공. SOFA 내장 실행은 아직 미검증.
- 설치 SOFA와 같은7c18e95 source/공식PR6259 patch를 .runtime에 수령. 패치 엔진 빌드/회귀는 아직 미검증.

## 진행 중 / 미완료

동일 조건6방향, 실패 대조군, 메시/적분점/dt, 전체 energy, 별도 SDK,
실제 Optuna3+24와 후보 검증, SofaPython3 원본 장면 비교, 선택적 재생 장면.
정확한 Lagrange Stick Constraint 및 진짜3D film surface는 아직 구현/인증하지 않았다.
