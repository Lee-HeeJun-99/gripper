# 최적화

**Optuna BLOCKED(실제0Trial), 추가 결정론적8층 static proxy15개 + 후보3개 검증.**
격리 pip retry0/8s, pip cache, DNS/프록시, Conda offline 재검사 모두 의존성을 확보하지 못했다.
3 smoke/24 Optuna/실제 Optuna pruning·resume는 NOT RUN이다. host DNS 장애를 패키지 비호환으로 잘못 분류하지 않는다.
이전30개 결정론적 grid/SQLite guard 결과는 소스 무결성을 확인한 이전 증거이며 새 Optuna 결과가 아니다.

새8층 grid는k(.01,.1,1,10,100)×연결 패턴3개, seed11. dt는 설계변수가 아니다.
같은 재료/하중의 static Newton family를 gate로 사용하며 dynamic/grasp family와 구분한다.
SQLite에 proxy를 보존했다. 후보마다 static base/repeat/halfdt/21node/6s 연장,
정적 잔차와 tip/slip 수렴을 검사했다. 모든 작은 gate/설정/원시 해시는 보존한다.
세 번째 complexity 목적은 원래 stiffness/slip 목적과 별도 연구 비용이다.
정지마찰/전체3D 파지/미검증 목적함수는 여전히 최적화 차단이다. 전역 최적성은 주장하지 않는다.

- k=100, points=[5, 10], ratio=4.783907117920339, slip=1.5812265939335493e-06, static-approved=True
- k=100, points=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], ratio=6.472215479847667, slip=8.983881080523509e-08, static-approved=True
- k=100, points=[2, 4, 6, 8, 10], ratio=6.167460643591852, slip=2.968186016952268e-07, static-approved=True
## 공통 증거/범위

환경: Ubuntu22.04.5, kernel6.8.0-138-generic, GCC11.4, CMake3.22.1,
Python3.10.20(robot_ws), SOFA v26.06.00(`/home/ubuntu/SOFA/v26.06.00`).
실물 측정값0건. 연구 단위 F/mm/s와 기존 E=250, A≈.732233mm², I=.0426667mm⁴를 사용한다.
기존 plugin/integrated/finite_rotation/multilayer 원본과 골든 파일을 변경하지 않았다.
raw: `results/stabilization_20261115/`; 작은 증거: `reports/stabilization_evidence/`.
설정/명령은 실험별 config.json/command.json/scene.scn, 결과는 metrics.json과 artifact hashes.
정적 잔차<1e-3, 병진/각속도<1e-5, tail drift<1e-4를 유지했다.
실행 성공과 평형/파지 검증을 구분한다. EXPERIMENTAL은 실물 인증이나 전체 모델 PASS가 아니다.
기존45 gate는 이전 소스/바이너리 무결성으로 승계하며 신규 모델에 합산하지 않는다.
