# 구조 비교 — 정량 기하/해석 선별, 실제 파지 비교 미완료

## 최신 실제 구현: 직사각형 동등 코어 체적 쿠폰

추가 고정 구체 Native 접촉 및1초 실제 구동 실행: 접촉력은 발생하지만
중간부가 위로 아치형 변형하여 의도한 감싸기를 아직 달성하지 못했다.
동일 입력 무접촉 BE도 시간 Gate FAIL이다. 필름 후보가 Baseline보다
우수하다고 결론 내릴 근거는 아직 없다. 임의 기구학으로 이를 보정하지 않았다.

Film–Rails–Tendon의 독립 DOF·5개 부착점/레일·편심 와이어 가이드 힘 전달을
실제 SOFA로 실행했다. 100×24×.05 mm Skin, 두 100×1.32233×.1 mm Rail이며
코어 체적146.4466 mm³/핑거다. 기존 tapered equal_volume_v2와 다른 연구 형상이다.
작은 장력에서 구동·해제·8초 복원 관측, 큰 장력은 세분 시간 격자에서2초 실행.
물체 감싸기·자유 물체 유지·Baseline 대비 성능 우위는 아직 검증하지 않았다.
부착부 에너지 시간 수렴 FAIL, 자가 충돌·제작 부착 강도 미검증이다.
상세: FILM_CONTACT_DYNAMICS_20261116.md. 개념 도면과 실제 좌표 그림을 구분한다.

## Updated physical evidence — no baseline/grasp superiority certification

Nonlinear coupon development now fixes tolerant force caching, trial tangent
selection and BDF line-search kinematics. Actual 11/21/41 final force residuals
pass, but 11→41 energy/area and full transient convergence fail. This does not
validate equal-volume Film+Rails, its attachments, tendon actuation or grasp.
Homogeneous rectangular film coupon results cannot replace the three-finger
baseline or demonstrate selective-jamming advantage. All previous volume,
radius and concept-versus-simulation distinctions remain unchanged.
Actual post-fix coupon states/curves are in
designs/visualizations/film_newton_20261116_v1/.

## 추가 실제 결과 — 동일 체적 쿠폰,그리퍼 비교와 구분

L100mm,E250,ν0,core146.4466mm³/핑거의 직사각 단일필름 두 개를 실제
SOFA에서 고정 평면 스토퍼로 시험했다. W10/t.1464466 대W24/t.0610194,
같은 모델하중1e-6F와kn1e-5F/mm³다. 초기 Euler11노드 결과 Aref29.458→
51.050mm²(1.733배),참조면적당 평균반력.748배를 관측했다. 이는 실제 자유물체
감싸기/손상 방지/파지력/원본3핑거/테이퍼rail구조의 우위 증거가 아니다.
coarse→fine 에너지/접촉면적과 일부동역학평형 FAIL 때문에 승인을 보류한다.
초기 실행기의 Static/BDF요청이XML에반영되지않은오류도발견·수정했다.
해당 raw는 실제Euler로 재분류하며 원래 summary를 덮어쓰지 않았다.

비교 추가 후보:equal_volume_v2 skin+두rail core439.33979mm³/3핑거.
기존2520mm³안도보존한다. 동일체적 신규안의 파지/미끄럼/압력/해제는 NOT RUN.
전체비교/오류/재현은FILM_SHELL_PHYSICS.md와REGRIP_COMPETITION_TECHNICAL_BASIS.md.

|지표|기존 Baseline|넓은 필름|선택 재밍 필름|
|---|---:|---:|---:|
|본체/root 반지름 mm|95.148|50 목표|50 목표|
|길이 mm|100|100|100|
|실제 구현된 접촉|중심선|표면 메시 로딩|동일 표면 메시 로딩|
|명목 외피 면적 mm²|모델에서 미정|6300|6300|
|실제 접촉면적/압력|미검증|NOT RUN|NOT RUN|
|등가 Beam/필름 체적 mm³|439.340|2520|2520|
|재료량 배수|1|5.73588|5.73588|
|물리 재밍 회로|연구 모델|공통 구동|prox/mid/dist 공유3회로|
|가정 기구학 tendon당김 mm|기존 라우팅 참조|1.155|1.155|
|파지 힘·토크·슬립·에너지 우위|미승인|미검증|미검증|

면적6300은 undeformed mesh의 기하 면적,접촉 면적이 아니다. 기존모델의
중심선 접촉에서 가상의8 mm 폭을 곱해 접촉면적 개선율을 만들지 않는다.
재료/밀도/구동/물체가 다른 상태이므로 아직 공정한 성능 비교가 아니다.

동일 재료량 제약으로 폭/층수만 유지하면 필름두께8.717 μm가 필요한다.
현0.05 mm 후보를 그대로 채택하지 않으며, 실제 필름 취급/접착/찢김/밀봉을
측정하거나 폭·층수·부분 적층 면적을 다시 선정해야 한다. 비슷한 질량이면서
접촉 폭만 확대한 hollow rib+film skin도 다음 대안이다.

샘플 station 간 폭 clearance 최솟값11.1489 mm는 같은 s에서의 이웃 간
거리−폭뿐이다. 전체 surface/self/hose collision 통과를 의미하지 않는다.
구체 R20,center(0,−75,0)와 prescribed curl은 형상 선별용 가정.

최종 성능 비교는 동일 Sphere/Cylinder/Box 크기·질량·마찰·구동력·재료량을
고정하고,실제 active triangle 면적,압력 분위수/최댓값,감싸기 각도,파지 힘/
토크,슬립,물체 손상 proxy,케이블일,유지 에너지,복원과제작복잡도를 측정한다.
가정 강성배수16에 대한 EB 계산은 선택 제어의 영향 분석이지 파지 우위가 아니다.

증거:designs/visualizations/concept_v2/comparison.json,
results/autonomous_design_20261116_v3/summary.json. 초기 v1/v2 FAIL 보존.
