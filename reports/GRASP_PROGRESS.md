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

## 최종 실행 스냅샷 (위 초기 기록을 보존)

- 신규 자유물체 SOFA trial46개(실패/timeout 포함)를 별도 raw에 저장했다. 실제 source/binary 버전별로 구분한다.
- v1→v2 cap-axis/API 검사, v3 μ0 극한 처리, v4 AD1 등가 최적화. 기존 plugin/골든은 변경하지 않았다.
- 동일조건 sphere6방향24s hold/해제·핑거복원 하위gate PASS. 완전 파지 EXPERIMENTAL,point-wrench rank5.
- 41노드/32subdivisions까지 완료했으나 q세분화8.474%차이로 공간수렴 FAIL. 파지최적화 BLOCKED.
- 8층 patched-SDK base/half/quarter 실제PASS,독립 force 합산차0. 이전timeout은 보존했다.
- Optuna 실제27시도/24COMPLETE/3PRUNED,기존30mm모델;Pareto 강성비1.66441253010351,dt/mesh/9s/반복PASS.
- SofaPython3 복구 및 원본600시점/adapter비교PASS. source copy hashes 일치,시스템Python 변경없음.
- 별도 matched SOFA patch build/graph잔존0/240000step/unload/reload 최소엔진 plateau PASS;수시간 full engine NOTRUN.
- clean C++ warning0,67Python PASS,ASan/UBSan/LSan자체unit PASS,기존C++5개 새실행PASS.
- Beam 단순energy후보는 force derivative 불일치;전체에너지 BLOCKED. native3D표면은일시반력만EXPERIMENTAL.
- 실제2401frame재생PASS,GUI NOTRUN. raw/build/env모두외장디스크,원격push없음.
- 최종수치/실패전후/commands는 GRASP_FINAL_VERIFICATION_REPORT.md와 evidence manifest.
- 다음: 적응적 접촉 적분/유한패치와 torque closure,동일조건 재검증,에너지폐합. 전체목표를 완료로 표시하지 않는다.
