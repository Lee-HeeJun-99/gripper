# 통합 에너지 감사

**접촉 힘/토크/소산 법칙 PASS; 전체 에너지 수지 BLOCKED.**
정상접촉 E=.5*w*kn*min(gap,0)², friction power=-mu*Fn*|vt|²/sqrt(|vt|²+v0²)<=0.
actual component의 Jx/Jv와 action-reaction/net moment를 검사했다. 마찰을 보존 에너지 Hessian으로 해석하지 않는다.
raw rigid velocities 및 실제 질량/관성으로 kinetic energy를 계산하고,
sampled cable work=-∫T d(sum(length)), 외부하중 일=F*Δu, 두 friction dissipations를 기록했다.
이 값은 time-sampled numerical work이며 정확한 연속 적분 또는 측정 에너지가 아니다.
시간변화 T*length의 parameter work를 beam stored energy로 혼동하지 않았다.

실제 deformed scene의 BeamFEM getPotentialEnergy 호출은 'not implemented' 경고를 냈다.
따라서 Beam elastic energy와 Rayleigh dissipation을0으로 넣지 않았다.
전역 energy closure는 BLOCKED이며 component_energy는 layer/cable/normal penalty만 포함한다.
중력은 장면에 명시적으로0이다. 가상의 비보존력 에너지 보존 성공을 주장하지 않는다.
단위별 partial measured work는 energy_audit.json에 있다. 실물 모터/진공 전력은 NOT RUN.

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
