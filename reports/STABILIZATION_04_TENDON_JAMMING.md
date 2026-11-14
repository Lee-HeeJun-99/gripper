# Tendon / pressure history

작은 tension/길이제어/pressure+tendon의 **정적 및 보상 합산 cold dynamic 평형 PASS**.
실제18s 잔차는 각각.0001625883841/.0003576944441/.00003401176252로 기존1e-3 미만이다.
표준 Euler 실패는 별도 보존하며 마찰 경로별 결과를 섞지 않는다.
원래 routed cable 에너지/힘 커널은 재작성하지 않았다. Static loading은 friction의
history를 동적 loading과 다르게 만들므로 서로 다른 tip 결과를 단순 회귀 오류로 해석하지 않는다.
LayerNetwork force/Jacobian 호출은 history를 누적하지 않고 AnimateEnd에만 commit한다(기존 검증 승계).

2핑거 실제 장면: tension0→.5s 구동→3s pressureON→6s 외력→하중해제→pressureOFF→tendonOFF.
pressure는 prescribed p*A, 같은 정지/운동mu 가정인 층간 slider다. 실제 vacuum/contact opening solve가 아니다.
각 finger100mm2층, 각 layer tension.001, offset±.2, pressureON.001F/mm²는 연구 가정이다.
양쪽 finger의 와이어는 독립 요소이고 object의 위치를 보정하거나 고정하지 않는다.
기본 α=.2, 정상방향 재시험 α=2는 기록된 수치 감쇠 변화이며 물성/하중/잔차 조건은 유지한다.
감쇠 변형의 과도응답을 기존 값과 같은 동역학이라고 주장하지 않는다.
복원/해제의 실제 데이터는 contact.csv/object.csv/state.txt에 있다.
실제 와이어 마찰/모터 stroke/3D pressure friction은 NOT RUN.

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
