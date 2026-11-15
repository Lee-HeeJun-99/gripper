# GRASP 01 — 객관적 elastic stick/slip

**PASS:** 독립 kernel/실제 SOFA의 elastic stick, Coulomb return mapping, 해제·재접촉, query 순수성.
**EXPERIMENTAL:** 가이드 평면 핑거의 자유 물체 접촉. 정확한 Lagrange stick, 다른 μs/μk,
rolling/접촉패치 torsion 저항은 NOT RUN. 기존 저속 정규화 운동마찰도, 정확한 무변위 제약도 아니다.

신규 models/grasp/StickSlip.{h,cpp}는 기존 Distributed.cpp와 분리했다. 원본/골든은 변경하지 않았다.
구/유한 원통/박스 SDF의 smooth branch 법선과 전체18DOF spatial Jacobian을 계산한다.
원통 축 위의 매끈한 endcap 오류를 수정했다. medial-axis/edge seam에서 유일한 미분을 주장하지 않는다.

## 식과 상태

물체 material coordinate a=Rᵀ(p−xO), 법선 n, 이전 탄성접선변위 u를 물체 material frame에 저장한다.
최소 Rodrigues 회전 T로 n_old→n 운반: u_trial=T u_old+(I−nnᵀ)(a−a_old).
antipodal normal은 표시된 시간 이산화 특이점으로 거부하며 임의 축을 고르지 않는다.
Fn=kn max(skin−SDF,0), cap=μ Fn, Ft_trial=−kt u_trial.
kt|u_trial|≤cap이면 stick, 초과하면 u=cap u_trial/(kt|u_trial|)로 radial return.
μs=μk이며 기준 μ=.3. μ=0에서는 명시적으로 탄성 history를0으로 돌려 zero-capacity singularity를 방지한다.
normal/tangent line stiffness .001은 reference-length trapezoidal weight로 적분한다. 무가중 점스프링이 아니다.

법선E=.5kn gap², 접선탄성E=.5kt|u|², plasticD=cap|u_trial−u|≥0.
해제 시 history를 지우고 소실 저장탄성E는 별도 release dissipation으로 기록한다.
AnimateEnd에서만1회 commit; addForce/addDForce/matrix/energy/observer는 history를 진행시키지 않는다.
점힘·반력과 물체 lever-arm torque를 함께 계산한다. spatial Jacobian을 대칭 energy Hessian과 혼동하지 않는다.
AD1 normal fast path는 AD2 energy+rotation connection 변환과 force/J 차이<1e-14로 비교했다.

## 실제 검증

final_checks/2/stdout.log: max Jacobian FD1.09235e-10, net moment2.71051e-20.
SOFA addForce/addDForce/buildStiffnessMatrix/kFactor2.5 검사 PASS.
평면접촉 discrete work3.044e-5, 마찰D2.7555e-5, 알고리즘항1.625e-7을 구별하여 검증했다.
무접촉/정지/임계이하/한계/Slip지속/재Stick/해제/재진입/강체변환은 tests/test_grasp_stick.cpp에서 검사한다.
clean release build3단계 PASS/컴파일경고0. ASan/UBSan/LSan 실제 PASS.
최초 sandbox LSan ptrace 실패를 보존하고 허용된 외부 실행으로 통과했다. 전체 SOFA가 instrumented된 것은 아니다.

실제 SOFA final_sphere_*는6방향 모두 비영 정지접선력/tail Slip0/상대접선속도<1e-5를 확인했다.
초기 μ0 crash를 적절한 negative control로 사용하지 않았다. 수정 후 적분 완료·물리 FAIL, 상세03.
접촉 파라미터/토폴로지는 각 trial 내 고정이며 실행중 topology-history remapping은 미인증이다.
최신 단위 재현: build/grasp_20261115/release_final/test_grasp_stick.
tools/grasp_audit.py unit의 이전 v2 경로와 구별한다. clean build/테스트 exact command는 final_checks에 보존했다.
