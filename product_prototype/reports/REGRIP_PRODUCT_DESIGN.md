## Latest Skin-contact continuation — 2026-11-19

Source commits fbc9754,0ec92f0; details: product_prototype/reports/SKIN_CONTACT_CONTINUATION_20261119.md.
Trials147–175 use unique Raw paths; legacy and earlier FAILs unchanged.

-150/152: first finger impulse1.07s coincides with−.214888mm cable error.
 Assembled J matches previous geometry (~1.25e-16),not current geometry;
 reported linear error3.33e-9 does not certify geometric shortening.
-Backside guide149/151 (normal−3mm,unchanged hardware size) fails:no finger load,
 object follows support40mm. This routing is not selected.
-Outboard4 candidate155 initially meets functional holding and child-J row-load
 criteria, but these are NOT physical Skin holding. Geometry168 FAIL:
 Skin gap>=3.394mm despite active row influence;child/FEM coordinates match0.
 Detector173 confirms object–GUIDE pairs and NO object–Skin pairs through.4s.
 Child Jacobian influence is NOT direct contact provenance;169 is not grasp PASS.
-Read-only mapping logger171 and native detector174 give EXACT state equality
 (STRICT1e-12) over their respective2s/.4s scopes. Split-vs-unsplit172 FAIL:
 contact partition changes dynamics and is not a passive observer substitution.
-Base/Half/Quarter155/162/163 all completed2s;all-pair/all-common-time167 FAIL at
 unchanged.1% gate. No100g/Lift or final CAD selection is authorized by these results.
-Minimal Rigid3/DiagonalMass158 FAILs factory/state/topology initialization;
 not proof the entire SOFA capability is unsupported. Full bridge remains BLOCKED.
-CADv5 retained;STEP/assembly kernel/moving hardware/wire swept clearance,
 full energy/contact area/pressure remain NOT QUALIFIED/NOT MEASURED.

Next:bind actual Contact collision-model pair and response Constraint row identity,
 not mechanical-J influence. Use public detector provenance first,then eliminate
 Guide-first contact without disabling hardware collision. No custom solver rewrite.
Exact commands/Raw/Build identities are in the new detailed report.
All launched physics children completed;no automatic continuation is promised.


## Native continuation checkpoint — 2026-11-19 (supersedes priorities below, not historical results)

Functional commit: `ff21719` (preceded by 3f600b7, af356fb, e29719f, 956d6c3).
Detailed evidence: `product_prototype/reports/NATIVE_CABLE_COUPLING_AND_HOLDING_20261119.md`.
New native trials051–146 are separate from legacy Campaign numbering.

- Cable error isolated: exterior lateral Barycentric extrapolation (weights −29..37,
  amplification73) plus lagged native cable linearization produces a two-state cycle.
  Mapping/Jacobian arithmetic is consistent; straight/surface coupons pass. Existing044 FAIL retained.
- Stock RigidMapping/SubsetMultiMapping guide hardware replaces extrapolated guide mechanics
  in opt-in scenes. No custom force/contact/ODE solver added. No-contact131 hold shortening
  error ≤2.33e-10mm; transient error .00365mm means NOT whole-time cable certification.
- R30/50g conditional holding124: support force0, support clearance about44mm,
  low measured speed. Weight is borne by GUIDE HARDWARE, not Skin. This is
  experimental hardware-only holding, NOT film wrapping or final grasp PASS.
  Matched100g132 FAIL. No maximum holding capacity or fabrication claim.
- End-clock support adapter124/127: declared versus actual path error0m.
  Half/quarter-dt assessment133 retains0.1% gate: FAIL, including substantive object-motion
  differences (~1.44mm), not only tiny-value relative errors. Contact cable errors at
  base/half/quarter remain .21489/.09091/.05674mm.
- Public initial mass API140 PASS; opt-in query purity four steps difference0.
  Frozen scene replay141: all1200 steps q/v/quaternion/support differences0, STRICT1e-12 PASS.
  Repeatability is not physical accuracy. Input guards146 PASS (no physical trial).
- Cross-guide bridge136–138 current DiagonalMass configuration fails initialization;
  only that candidate BLOCKED, not proof all native diagonal mass is unsupported.
- CAD sources/STL/drawings/BOM: native_guides_v5. FreeCAD/OCC unavailable;
  STEP/kernel assembly NOT GENERATED. Moving full hardware interference NOT qualified.
- Lift BLOCKED by contact/time gates and mapped-root actuation path; no Lift run.
  Skin wrapping, general friction, self-collision, full energy/pressure/area and fabrication
  readiness remain unverified. Legacy results/SDK preserved; no push.

Next implementation: isolate native contact-transition cable linearization on a short
recorded failure interval, then revise guides so Skin, not hardware, bears load.
Before bridge dynamics, reproduce its native Rigid3 DiagonalMass initialization in a
minimal scene. Before Lift, implement a verified free-subset root fixture and pullPoint
motion; do not bypass current guards. Existing tests should be reused, not blindly repeated.

Reproduction commands and exact Raw/Build identities are in the detailed report and
`product_prototype/reports/evidence_native_coupling_v2/manifest.json` (once published).
All trials are stopped; no automatic continuation is configured. This is an incomplete
product-development checkpoint, not OS resource exhaustion or project completion.


# ReGrip product prototype — 2026-11-19

제품 우선 방향 전환에 따라 별도 구현했다. 기존 models/,Golden,Raw,
Checkpoint1644,자체 Solver와 검증 결과는 수정하지 않았다.

## 생성한 기준 후보

Single Skin + two bonded Rails + two edge cables,100mm 길이,폭24→12mm,
테이퍼 시작50mm,Root-centre radius50mm,0/120/240도 배치.
설정 원본은 config/design_v1.json. product_outboard14_v3는 동일 재료 단면의
Outboard14mm 비교 후보다. 최종 선정은 아니다.

제작 취급성을 검토하기 위해 Skin0.1mm/Rail0.5mm×2mm를 잠정 입력했다.
기존 연구의0.05mm/0.1mm나8층 ConceptV2와 다른 설계다. 물성은 미측정:
Native FEM E250MPa,nu0.3,핑거당 질량1g 가정. 실제 PET/TPU 인증값 아님.
코어 체적410mm³/핑거,1230mm³/3핑거. 기존439.34mm³와 동일 재료량이
아니므로 기존 모델 대비 성능 우위를 주장하지 않는다. 하드웨어 질량 미포함.

## 실제 산출물

- cad/generate.py:공유 형상에서 SCAD,양의 체적 Tetra 메시,STL,SVG,BOM 생성.
- meshes/product_outboard14_v3/:최신 파라메트릭 CAD 소스와 개별 Skin/Rail STL.
- drawings/candidate_v3/:치수도,부분 분해도,조립 SCAD,권위 BOM,기하 검사.
- cad/export_freecad.py:실제 BRep/STEP/STL/FCStd 생성용 FreeCAD 스크립트.
  문법 검사만 실행했다. FreeCAD/OCC/OpenSCAD가 시험 환경에서 발견되지
  않아 CAD kernel 실행·STEP·Assembly STEP·전체 Assembly STL은 미생성.
- sofa/run_native.py:SOFA 기본 FEM/CableConstraint/접촉/적분 Scene 생성·실행.
- sofa/scenes/native_three_finger_v1/:실제로800스텝 재실행한3핑거 Scene.
- results/:실제 CSV,Source/Binary/SDK 해시,로그,실패 증거,Accepted-state PNG.

STL 검증:Skin210mm³,각 Rail100mm³,합체410mm³. 모두 watertight,
consistent winding,양의 체적.3개 좌표계 determinant1,직교 오차<=1.62e-16.
이는 전체 어셈블리 간섭·가공 공차 검증이 아니다.

## 기구 관측과 변경

기본 가이드 normal3/outboard4mm,5mm Stroke에서는 실제 변형 중 와이어가
R30 물체와 약2.55mm 간섭했다. Outboard10mm도 약0.82mm 간섭.
Outboard14mm/5mm Stroke는 샘플 간섭 여유 약2.68mm지만 접촉 부족.
6mm Stroke에서는 접촉이 증가하나 약0.36mm 와이어 간섭이 다시 발생.
한 변수 변경 시험이며,동일 Stroke이지 동일 장력/Work 비교는 아니다.
가이드 질량,지지대,실제 가이드 마찰/마모,전 시간 CCD는 미검증.

Object 중심 깊이65mm,R30이면 지지면 깊이95mm가100mm 핑거보다 높아
닫힘을 방해한다.75mm 깊이 배치로 별도 시험했다. R20은80mm 배치.
초기 좌표를 바꾼 실제 물리 시험이지 저장 형상을 렌더링에서 옮긴 것이 아니다.

## 결정

초기 제작 후보만 유지한다. 실제 wrapping,독립 holding,lift와 제작 준비
완료는 승인하지 않는다. 다음은 와이어를 접촉면 밖으로 유지하면서 필요한
곡률을 만드는 가이드/앵커/Root angle의 단일 변수 기구 비교다.
자체 Solver 신규 개발보다 이 기구 문제와 Native 접촉 설정을 우선한다.
8층 필름/진공/Selective Jamming은 기본 파지 기능 이후의 교체형 확장안.
