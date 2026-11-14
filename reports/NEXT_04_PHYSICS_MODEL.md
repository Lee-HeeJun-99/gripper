# NEXT 04 — 물리 모델

기준 60f41cf; 개발 코드 커밋 `96174a2ec8c1b75c2f11f607bdecb1d986b148f2`. 실행 중 dirty 상태는 개별 JSON에 그대로 기록했다.
원본/골든 보존, push 없음. 증거: `reports/next_evidence/`; raw/명령/전체 로그: `results/next_phase/`.


기존 30 mm 평면 에너지와 SOFA 회전 정의는 변경하지 않았다. `phi_EB=dw/dx≈-theta_y`.
평면각은 `2 atan2(qy,qw)`이고 기존 s=Delta u-h/2(theta_l+theta_u), E=k*s²/2의 gradient/Hessian은 그 정의 안에서 일치한다.
기존 45 gate를 새 모델 인증으로 확대하지 않는다.

**EXPERIMENTAL** 별도 `FiniteRotationShear`:
`d=p_u+R_u*a_u-p_l-R_l*a_l`, `t=R_l*e_x`, `s=t dot d`, `E=k*s²/2`.
물질 attachment와 tangent를 같이 회전시켜 강체 운동 객관성을 갖는다. lower tangent 선택은 신규 구성 가정이다.
정확한 SO(3) local retraction의 2차 AD로 힘/국소 Hessian을 구했다.
대칭 변분 Hessian과 공간 토크 Jacobian은 다르며 후자는 `-H-0.5*skew(torque)` 연결항을 갖는다.
실제 공간 힘 FD를 검사했고 nonsymmetric EigenSparseLU를 사용한다. 모든 상태에서 PSD/행렬 대칭을 주장하지 않는다.
수식·선택·제약: `models/finite_rotation/README.md`.

**PASS(검사 범위)**: 60개 무작위 유한 회전, 12 DOF 모든 힘/접선 FD,
에너지 FD 1.92619e-11(<1e-9), 공간 Jacobian FD 6.05088e-11(<1e-8),
객관성 4.85723e-17(<1e-13), 모멘트 4.16334e-17(<1e-13), H 대칭,
실제 addForce/addDForce/kFactor/buildStiffnessMatrix/6DOF, NaN differential/null matrix 안전 거부.
첫 컴파일 alias Base 충돌은 Inherit로 수정했고 실패 로그도 보존했다.
단위 probe의 ERROR는 의도한 invalid-input 진단이며 실제 SOFA 정상 실행의 ERROR 허용이 아니다.
별도 ASan/UBSan PASS. component gate `True`.

SOFA 기본/절반dt/21노드 동일 연결점 3개 실행 + 전체 장면 강체 좌표 변환 PASS.
변환 최대 절대차 `{"position": 6.110667527536862e-13, "velocity": 6.151300523484573e-12, "quaternion": 1.8096635301390052e-14, "residual": 2.4433353193438484e-11, "interface": 6.075140390748857e-13}`,
허용오차 `{"position": 1e-08, "interface": 1e-08, "quaternion": 1e-09, "velocity": 1e-08, "residual": 1e-08}`. 전 시점 위치/속도/quaternion/잔차/매핑 상태를 비교했다.
하중1e-4에서 planar 대비 처짐 차이 0.000756110262,
하중1e-5에서 7.4846381e-06: 작은 변형 극한에서 수렴했다.
큰 회전 커널 검사는 유한 방향 상태의 수학적 검사이며 큰 변형 그리퍼의 접촉/재료 인증이 아니다.

독립 다층 FEM은 EA/EI 분리, EB/Timoshenko, 메시/해석해/동일 A 기준을 시험했다.
사각 A=3.2와 원형 A≈.732233을 혼합해 강성비를 같은 실물 결과로 해석하지 않는다.
전체 BeamFEM 비선형 동적 에너지 수지, 다층 3D SOFA 및 실제 필름은 **NOT RUN**.
