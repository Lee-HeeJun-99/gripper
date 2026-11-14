# 자유 물체 / opposing fingers

**자유6DOF/분포마찰/제한적 유지 구현 EXPERIMENTAL; 전체 파지 인증 미완료.**
Sphere/infinite-cylinder/cube SDF, reference-length trapezoidal line quadrature를 사용했다.
실제2D필름 연속 표면/네이티브 triangle collision pipeline은 NOT RUN.
kinetic friction Ft=-mu*Fn*vt/sqrt(vt²+v0²), v0=1e-5. 정지 stick이 아니라 creep 모델이다.
위치/속도 Jacobian, 실제 SOFA K/B 및 kFactor/bFactor, action-reaction/objectivity/소산 검사 PASS.
현재 실험값 v0와 creep-scale velocity의 FD도 별도 검사했다(절대오차 허용1e-7 유지).

object6DOF는 자유이며4개의 finger roots만 고정했다. 각 finger의 Y/rotX/rotZ는
명시된 planar guide이다. 이를 완전3D soft finger라고 부르지 않는다.
actual Mass API: 첫 node9.09091e-7, object.0001, total.00014,
object mass-matrix diagonal transl.0001/rot.001을 확인했다.
두 BaseMass 오류와 첫 DiagonalMass template/link 오류는 FAIL로 보존/제외했다.

이전 negative-control.001mm 기준은 유지한다. 새 연구 geometry는5mm 반지름의1%인.05mm
탄성 이동을 허용하지만 속도/각속도<1e-5, object 및 finger 힘/모멘트 잔차<1e-3,
접촉 지속을 동시에 요구한다. displacement만으로 성공으로 만들지 않는다.
1e-6 외력은 측정된 µ*sum(Fn) 약3e-6의 유의미한 비율이다.
mu0와4e-6 overload는 병진이.05mm보다 작아도 velocity/force gate에서 FAIL이다.
±X/±Y 기본 유지와 ±Z의 연장/감쇠 조건은 별도 실험이다(조건 혼합 인증 금지).
Coarse mesh/quad 실패를 보존하고 finer hold-only 시험을 별도 수행했다.
180s timeout 이후의 incomplete release를 성공으로 인정하지 않았다.
성능 수정은 마찰 wrench의1차 Jacobian에 필요 없는2차 Hessian 계산을 제거한 것이다.
수학 모델/하중/tolerance를 변경하지 않았다. 기본1201프레임 X/V/R 최대 차이 모두0,
관측 wall time55.57→46.10s(통제된 hardware benchmark 아님).
Release/ASan/UBSan 검사 후 별도 fast 바이너리로 고해상도 조건을 재실행했고
이전 slow timeout과 원시 결과는 보존했다. fine/dt 전체 인증은 최종 gate의 범위만 인정한다.
Cylinder endcaps/box seam/토크 외력 envelope/정확한 정지마찰은 미검증이다.

|장면|최종 gate|이동 mm|object 잔차|실패 항목|
|---|---|---:|---:|---|
|box_x|EXPERIMENTAL|6.5021282864563545e-06|6.332467547653791e-05|—|
|cylinder_x|EXPERIMENTAL|6.543220720800491e-06|6.312650316433072e-05|—|
|mass_smoke|NOT RUN|—|—|load phase not reached|
|sphere_fast_mesh21_full|EXPERIMENTAL|7.112224011507351e-06|6.986613642414914e-05|—|
|sphere_fast_mesh41_holdonly|EXPERIMENTAL|7.053920626276522e-06|6.932548830603686e-05|—|
|sphere_fast_regression|EXPERIMENTAL|6.543220720800491e-06|6.312650316433072e-05|—|
|sphere_halfdt|EXPERIMENTAL|6.5432727467396035e-06|6.312680701686e-05|—|
|sphere_mesh|EXPERIMENTAL|6.88481335942015e-06|6.652336141944273e-05|—|
|sphere_mesh21_q16|EXPERIMENTAL|7.112788566132622e-06|7.050326022508966e-05|—|
|sphere_mesh21_q32|FAIL|—|—|SOFA execution/log/undefined-component failure|
|sphere_mesh21_q32_holdonly|EXPERIMENTAL|7.112224011507351e-06|6.986613642414914e-05|—|
|sphere_mesh41_q16_holdonly|FAIL|—|—|SOFA execution/log/undefined-component failure|
|sphere_mu_zero|FAIL|0.017824702749010157|1.0393959431322415|velocity,force_balance,finger_velocity|
|sphere_overload|FAIL|0.012644979283862767|0.1852513216803023|velocity,force_balance,finger_velocity|
|sphere_quad32|EXPERIMENTAL|7.191493935465587e-06|7.129281074251038e-05|—|
|sphere_quadrature|EXPERIMENTAL|6.949217464580215e-06|6.715979729304601e-05|—|
|sphere_repeat|EXPERIMENTAL|6.543220720800491e-06|6.312650316433072e-05|—|
|sphere_x|FAIL|—|—|superseding invalid-physics audit|
|sphere_x_masscorrect|FAIL|—|—|SOFA execution/log/undefined-component failure|
|sphere_x_negative|EXPERIMENTAL|6.530391914338907e-06|6.29990095042804e-05|—|
|sphere_x_valid|EXPERIMENTAL|6.543220720800491e-06|6.312650316433072e-05|—|
|sphere_y_negative|EXPERIMENTAL|6.374240031307298e-06|6.307274267964133e-05|—|
|sphere_y_positive|EXPERIMENTAL|6.374240031307298e-06|6.307274267964133e-05|—|
|sphere_z_long_damped|EXPERIMENTAL|0.004782163182067044|0.00016942399838625258|—|
|sphere_z_negative|FAIL|0.007339986545237356|0.5102399231675021|velocity,force_balance,finger_force_balance,finger_velocity,finger_angular_velocity|
|sphere_z_negative_long_damped|EXPERIMENTAL|0.004782163182067044|0.00016942399838625258|—|
|sphere_z_positive|FAIL|0.007339986545237211|0.5102399231675021|velocity,force_balance,finger_force_balance,finger_velocity,finger_angular_velocity|

Convergence: `{"sphere_repeat": true, "sphere_halfdt": true, "sphere_mesh": false, "sphere_quadrature": false, "fine_quadrature": true, "fast_full_vs_holdonly": true, "fast_fine_beam_mesh": true}`

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
