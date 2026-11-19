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


# 초기 어셈블리 사양 — NOT FABRICATION READY

기준 파일:drawings/candidate_v3/assembly.scad와 config.json.
개별 part 선택은 SCAD의 part 변수:skin,rail_left,rail_right,palm,mount,
clamp,guide,anchor,pulley,coupling,motor_plate. explode=15는 Clamp 분해 표시.
이는 CAD 설계 소스이며 CAD kernel 렌더/STEP 변환은 실행되지 않았다.

## 부품 연결

1. Palm annulus R64/R30,두께8mm,z5..13. Root radius50,3x120도.
2. Mount는 Palm 하부와 z5에서 접한다. Palm 볼트는 세계 Z축 방향.
3. Cartridge Root Clamp는 Skin 상면에서 시작한다.5x36x3mm,M3
   임시 clearance3.4mm,local x2.5/y±14. Clamp 볼트는 Skin normal 방향.
4. Skin0.1와 Rails0.5를 연속 접착한다고 가정한다. 레이어 재밍이 아니다.
5. 양측 가이드 위치10/30/50/70/90/98mm. OD3/ID1.2,Wire radius0.25mm는
   모두 설계 입력이다. 실제 공급 재료/가이드 반경/찢김 강도 미확정.
6. 말단 앵커,가이드 지지대,풀리 R8,커플링 bore6은 후보 소스만 있다.
   실제 모터 샤프트,베어링,모터 플레이트 지지대,브랜치 배관은 미완료.

초기 소스의 Palm–Mount 축 불일치,Clamp–Skin/브래킷 겹침,반사 좌표계와
오른쪽 Rail STL winding을 검토·수정했다. 과거 버전은 보존했다.
CAD kernel Boolean 간섭 검사와 동작 전 범위 하드웨어 검사가 필요하므로
ASSEMBLY VERIFIED가 아니다. Guide 지지대는 Native FEM에서 모델링하지
않았고 가이드는 질량 없는 BarycentricMapping 점이다.

## 구동과 조립 순서

Skin/rail 절단→접착 지그/평면도 확인→Root Clamp 체결→Mount/Palm 체결→
가이드/앵커 장착→두 와이어 독립 장력 확인→카트리지 교체 시험→
저속 무부하→고정 물체→중력/하중 시험 순서. 실제 하드웨어는 구동하지 않았다.

6개 Native CableConstraint에 같은 변위 명령을 쓴다. 실제 공통 Motor,
Mechanical Equalizer,Passive Differential이나 폐루프 장력 제어가 아니다.
모터 토크/속도/스트로크/전류·센서·팀원 정보는 미확정. Native 단일 핑거
5mm 실험의 Peak 장력 약3.67N/와이어는 가정 모델의 요구량일 뿐 모터 사양이
아니다. 이 수치로 부품 구매·안전·취성물 파손 여부를 승인하지 않는다.

## 조건부5일 제작 작업

Day1 소재·액추에이터·규정 확인,쿠폰/와이어 시험과 치수 확정.
Day2 Palm/Clamp/Cartridge 가공 및 구동부 인터페이스.
Day3 독립 와이어 저속 구동,간섭·마찰·복원 측정.
Day4 물체별 접촉/유지/해제 시험과 실패 수정.
Day5 반복 운반·수리·시연 준비. 조달/장비/인원이 미확정이므로 일정 보장 아님.

STEP 생성은 FreeCAD 환경을 제공한 뒤 별도 새 경로에서 실행:

```bash
REGRIP_CAD_OUT=/absolute/new/output FreeCADCmd product_prototype/cad/export_freecad.py
```

FreeCAD 스크립트는 실행 검증 전이며,가이드 지지대/드라이브라인 전체 연결은
STEP 어셈블리에도 추가 구현이 필요하다. 입력값을 확정하지 않고 제작하지 않는다.
