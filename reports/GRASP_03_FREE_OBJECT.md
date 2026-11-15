# GRASP 03 — 자유 물체 유지/해제

**EXPERIMENTAL:** 연구용 elastic-stick 대향2핑거의 동일 조건6방향 bounded hold 및24s 복원 PASS.
**FAIL:** 공간 접촉 수렴성. **NOT RUN:** 완전6DOF wrench closure, 외부 torque 방향 시험, 연속3D 접촉면 파지 인증.
파지 목적 최적화는 BLOCKED. 이동량만으로 성공 처리하지 않는다.

## 공통 조건과 사전 판정

각 핑거 길이100mm,2층×11 Rigid3d. Root4개 고정, 핑거Y/rotX/rotZ 가이드 명시.
물체는 별도6DOF, 고정/위치보정/compensation/숨은 복원력 없음; XML도 독립 검사했다.
sphere반경5mm, 질량.0001 연구단위, I/m=(10,10,10)mm². 원통/박스는 각각 올바른 관성을 사용한다.
기존 E250/ν.32/circular-equivalent beam, dt=.0005, EigenSparseLU, Rayleigh stiffness.1/mass2.
μs=μk=.3, normal/tangent line k=.001, 장력.001, 압력.001. 실물 물성/장력/진공 측정이 아니다.

스케줄: 초기0, cable ON.5s, pressure ON3s, 외력 ON6s/OFF14s, pressure OFF15s, cable OFF16s, 최종24s.
접근은 연구용 초기 proximal placement+와이어 굽힘이며 실제 로봇 base 접근 제어는 NOT RUN.
외력은 모든 방향 같은 |F|=1e-6. 10배 overload와 제로/저마찰 실패로 검출 민감도를 확인했다.
힘 잔차 max|Rtrans|/|F|<1e-3, 물체 모멘트 max|Rrot|/(|F|r)<1e-3;
핑거 자유DOF는 장력*.2/100 및 그×100으로 정규화하고 고정DOF 반력과 분리한다.
병진/각속도<1e-5, finger domain<.005rad 및qx/qz<1e-8, 물체회전<.01rad, contact≥2,
마찰한계 ratio≤1+1e-10, 끝.1s drift ratio<1e-4를 검사했다.
이동.05mm는 반경의1%인 사전 연구 탄성 이동 기준; 이전 negative-control .001mm는 변경하지 않았다.
최종 복원 기준은 실행 전에 `release_criteria.json`에 기록: 접촉0, 속도/각속도<1e-5,
핑거rest 병진<1e-4mm,회전<1e-5rad. 자유 물체를 원위치로 리셋하는 기준은 없다.

## 실제 24초, 동일 조건 결과

|외력|최대 이동 mm|상대 물체 힘 잔차(hold)|hold/해제/핑거복원|
|---|---:|---:|---|
|+X|0.00048237948651319584|1.77633037e-8|PASS/PASS/PASS|
|-X|0.0004823798705757554|약1.78e-8|PASS/PASS/PASS|
|+Y|0.00048218148848658114|약1.23e-8|PASS/PASS/PASS|
|-Y|0.00048218148848658114|약1.23e-8|PASS/PASS/PASS|
|+Z|0.004782163313643664|0.00016942388818|PASS/PASS/PASS|
|-Z|0.004782163313643664|0.00016942388818|PASS/PASS/PASS|

각 hold는 velocity/ω/핑거DOF잔차/모멘트/마찰한계도 모두 통과하고 tail-slip0, 상대접선속도<1e-5.
24s 최대 핑거 속도 약8.65e-8mm/s,rest 오차 약7.65e-9mm,접촉0.
정확한 값/각 체크/토크/변위는 `gate.json`, 각 `final_sphere_*/metrics.json` 및 raw state/contact.csv.
초기 alphaMass.2 18s ±Z 잔차.04968245 FAIL을 보존했다. mass2는 별도 공통 damping 연구 조건이며
다른 감쇠의 결과를 같은 조건으로 합산하지 않는다. mass2 18s는 유지PASS이나 복원속도≈.001mm/s FAIL;
같은 물리 조건으로 관측만24s까지 연장하여 복원이 통과했다.

## 중요한 미달 범위

유지 구간의 unrestricted contact point wrench matrix 최소rank=5/6이다.
반대 두 점 접촉은 한 축 torque를 지지하지 못할 수 있다. 6개의 힘 방향 PASS는 6DOF force closure 증명이 아니다.
가이드 반력/감쇠가 있는 구조에서 정적 힘만 만족하는 결과를 일반 안정 파지로 확대하지 않는다.
접촉 공간 수렴성 FAIL과 전체 에너지 BLOCKED도 남아 있다.

## 대조군/형상

μ0 수정본: 실제 적분 완료,이동.0389485869430mm,힘잔차1.084701 FAIL(위치만 기준이면 오판).
μ.001:이동.02224646mm,잔차1.03776 FAIL. 와이어OFF/접촉점부족/배치불량/감싸기부족은
이동.03750000mm,잔차1 FAIL. overload F1e-5는.15298445mm,잔차.72219 FAIL.
재밍OFF는 이 작은 하중에서 wire만으로 유지 가능하여 EXPERIMENTAL hold PASS; 실패를 강요하지 않았다.
재밍효과/지지외력 증가 증명으로 사용하지 않는다.
원통+X 이동.0004823794865mm,박스+X .0001269693994mm,둘 다 hold PASS/18s 접촉 해제 관측;
동일6방향/24s 복원 전체는 NOT RUN. Edge/corner SDF 단위 검사는 파지 전체 검사와 다르다.
