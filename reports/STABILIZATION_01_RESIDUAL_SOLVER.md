# 잔차 및 Solver

**힘 합산/정적 평형 PASS; 보상 합산 Euler cold-start 회귀 PASS. 기존 표준 Euler 실패는 보존.**

독립 SolverTelemetry의 실제 Ax-b 상대 잔차≈8.77e-16인데 재구성 정적 잔차는.00118188이었다.
동일 조건의 최악 X좌표70mm에서 dt*v=-8.64e-15mm, ULP=1.42e-14mm였다.
장기 실행에서는 증분이.212ULP까지 작아졌다. 좌표 반올림으로 소실되는 Euler 증분을
long-double carry에 누적하는 별도 CompensatedEulerPositions를 구현했다.
힘/목표 위치/허용오차를 읽어 보정하는 방식이 아니며 회전과 고정 루트는 그대로다.
자유 물체/접촉/정적 solver에는 helper가 사용을 금지한다. 파지 장면에 적용하지 않았다.
24000개의1e-15mm 증분 단위시험에서 naive는 전부 소실, compensated 오차0이었다.
같은 warm 시작의 잔차.00118188→1.33529e-5, 이후 독립 cold-start9조건 모두 PASS.
초기 warm helper가 seed를 rest로 해석한 분석 오류는 수정 후 별도 디렉터리에서 재검증했고
수정 전 원시 결과는 보존했다. 실제 정적 힘 잔차와 solver native residual은 다른 양이다.
별도 ForceAudit가 각 실제 ForceField를 zero-velocity scratch에 호출했다.
기존 recorder 합과 최대 차이는 검사한 장면에서0이다. 이는 힘 회계 검증이지 BeamFEM의 독립 구현은 아니다.
BeamFEM/LayerNetwork/RoutedCable/ConstantForceField/UniformMass를 분리했다.
중력은 장면에 명시적으로0, 케이블은 제약이 아닌 에너지 기반 힘, 접촉은 이 정적 비교 장면에는 없다.
고정 루트의 반력은 별도 합산하고 자유 DOF 잔차에 넣지 않았다.
병진 분모 F_ref/layers, 모멘트 분모 F_ref*100/layers. 작은 하중 분모를 증가시키지 않았다.

8층 기본 absolute free force7.60030e-12, moment1.90477e-13.
작은 T absolute force2.01701e-13; length3.57694e-13; wire-pressure2.58278e-13.
최대 병진 잔차는 X방향 내부 축력 상쇄에서 관측됐다. 긴 동적 실행의 실패를 힘 누락으로 설명할 근거는 없다.
이 증거는 검사한 구조 Euler 장면의 정밀도 장애를 설명하며 모든 SOFA 장면에 일반화하지 않는다.

StaticSolver+NewtonRaphsonSolver는 실제 SDK API로 실행했다. EigenSparseLU, SparseLDL,
CG(Iterative plugin 선로딩), SparseLU(CSparseSolvers 선로딩) 대조를 수행했다.
CG/SparseLU 최초 등록 실패는 보존하고 필요한 플러그인을 먼저 로딩한 새 실험에서 재검증했다.
대칭 solver는 대칭 planar spring 장면에서만 사용한다. 비대칭 spatial/contact Jacobian에는 LU를 유지한다.

최초20-step(.02s) 정적 시험은 tail에 초기 상태가 포함돼 drift=1로 FAIL.
.15s continuation은 같은 .1s tail 기준으로 PASS(허용오차 변경 아님).
length의 더 엄격한 mixed-DOF L2 stop은 내부 Newton 경고를 남겼다.
별도 length_inf_sufficient_stop은 L2 threshold=F_ref/layers*1e-3로,
각 force DOF의 기존 infinity-norm 기준을 충족시키는 충분 조건을 사용했다.
외부 물리 기준/분모를 바꾸지 않고 경고 없는 재실행을 확인했다.


|실험|원시 판정|처짐 mm|상대 잔차|
|---|---|---:|---:|
|L8_free|PASS|0.0039062499942386156|7.841473083558953e-07|
|L8_k1|PASS|0.001050366825802361|8.220745927454867e-05|
|L8_k10|PASS|0.0006538903051483795|6.360810270224248e-05|
|L8_base|PASS|0.0006035414003754021|6.0802400955869626e-05|
|L8_halfdt|PASS|0.0006035414003754021|6.0802400955869626e-05|
|L8_quarterdt|PASS|0.0006035414003754021|6.0802400955869626e-05|
|L8_mesh|PASS|0.0006035416537933241|2.2742505503879715e-05|
|L8_repeat|PASS|0.0006035414003754021|6.0802400955869626e-05|
|small|PASS|4.6874265960311634e-05|0.00020170092038710008|
|length|PASS|9.289132134399081e-05|0.0003576944451925865|
|wire_pressure|PASS|0.0003326901806414012|2.5827772628547758e-05|


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
