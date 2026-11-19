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


# Native SOFA product validation — 2026-11-19

## 판정

|요청 항목|실제 상태|
|---|---|
|CAD CREATED|PARTIAL: 파라메트릭 SCAD/FreeCAD 소스,개별 Skin/Rail/결합 Finger STL|
|ASSEMBLY VERIFIED|NOT VERIFIED: CAD kernel 미설치,전체 간섭 미검증|
|SOFA SCENE RUNNABLE|PASS: 저장 Scene을 실제800스텝 재실행,10.424초|
|SINGLE-FINGER ACTUATION PASS|구동·복원 OBSERVED;변위 추종/전체 시간 수렴 NOT QUALIFIED|
|THREE-FINGER CONTACT PASS|실제 자유 물체 접촉 OBSERVED EXPERIMENTAL;물리 인증 미완료|
|WRAPPING PASS|NOT PROVEN:연속 하중 지지 접촉 범위/면적 미검증|
|HOLDING PASS|FAIL:044 지지대 제거 시 물체가40.2mm 내려감|
|LIFT PASS|FAIL:021 Root20mm 상승 시 물체가 따라오지 않음|
|PHYSICAL FABRICATION READY|BLOCKED:STEP/전체 간섭/구동부/재료/성능 미확정|

## 실제 모델

설치된 SOFA v26.06.00와 SoftRobots만 사용. SI m/kg/s/N/Pa.
EulerImplicitSolver,SparseLDLSolver,TetrahedronFEMForceField(large),
CableConstraint,BarycentricMapping,기본 충돌 및 BlockGaussSeidelConstraintSolver.
Controller.cpp는 입력과 공개 API 상태 기록만 담당한다. 새 FEM/적분/접촉 Solver 없음.
Single Skin+두 Rails는 공유 Tetra 노드를 통한 연속 접합이다. 독립 적층/재밍이 아니다.
형상은100mm,24→12mm,단층0.1mm,Rails2×0.5mm,체적410mm³/핑거.
E250MPa,nu.3,질량1g/핑거,구체100g은 연구용 가정값이다.
주기0-.5/ .5-1/1-1.5/1.5-2초,각 케이블 독립 변위 명령이다.
동일 명령은 Mechanical Equalizer가 아니다. 모터 토크/스트로크 사양 미정.

## 실행 및 실패 증거

Raw/소스 스냅샷/바이너리 해시/명령/SDK/실행시간은 ../results/<case>/.
결과를 끝까지 실행한 것과 물리 PASS를 구분한다.

- 010 단일 핑거:800스텝2초,tip 최대41.593mm,마지막2.53e-12mm.
  최소 Tetra 체적비.98086. 단순 구동·복원 관찰이지 시간/물성 인증 아님.
- 010/011/012 동일 바이너리,dt2.5/1.25/.625ms,모든 공통 시점 비교:
  기존0.1% Gate **FAIL**,최대194.582544%(속도,절대차1.22636e-4m/s).
  작은 값에 floor를 더하지 않았다. 끝단 상태만으로 전체 PASS 처리하지 않음.
- 013/015/018 기존/Outboard10:실제 유한 와이어–구체 간섭 FAIL.
- 020 Outboard14,5mm명령:와이어 여유+2.678mm이지만 Skin 접촉 없음.
- 023/024 6/8mm명령:접촉 증가와 동시에 와이어 간섭 발생. 최종 선정 불가.
- 025 원통:비유한 상태로 실패. SIGABRT는 OS 메모리 고갈이 아니다.
  후속028 초기 지지대 여유.4mm 조건은 별도 물리 배치이며 기존 실패를 대체하지 않음.
- 033/036/037:올바른 우수 좌표계,경계 삼각형 전용 충돌 Child,
  R30 구체/원통/Box 실제 자유 강체 접촉. 모두 최종 파지 미인증.
- 039 느린4초 주기도 R20 유지 실패. 구동 시간 증가만으로 해결되지 않음.
- 041 R20 둥근 지지대:물체가 남아 있어도 지지대 지지이므로 Holding 아님.
- 042 조밀한10개 Guide/와이어:와이어 간섭−.79mm,Skin 침투 약−1.2mm.
  구조 변경의 개선이 확인되지 않아 기각. 기본6개 Guide와 별도 조건.
- 044 지지대를1–1.5초 사이40mm 내린 실제 중력 시험:
  물체가 함께 내려가므로 독립 Holding **FAIL**. 물체/핑거 형상은 지정하지 않았다.
  실제 support.csv로 지지대 운동을 검증한다. 지지대 구동 일 미측정.
- 045 GenericConstraintSolver 비교는 실제 factory 오류로 **FAIL**.
  v26.06에서 제거된 이름이었다. 헤더 존재는 factory 등록을 보장하지 않는다.
  BlockGaussSeidelConstraintSolver를 유지하며 미래 CLI는 해당 제거 이름을 거부한다.

## 와이어 추종 결함

050 독립 직선 Cable–Spring–Mass 시험은 실제800스텝/2초에서 모든 경로 단축 명령
오차 최대1.77809e-17m,STRICT1e-12 기준 PASS(실행.267초).
049는 SubsetMapping topology 옵션 누락으로 실패했고 보존했다.
050은 handleTopologyChange=0을 명시한 수정 시험이다. 단순 Cable 입력 자체보다
외측 Barycentric Guide/FEM/두 Cable 결합 조건을 다음 조사 대상으로 좁힌다.
이는 Finger FEM/접촉/파지 검증이 아니다.

044에서 실제 mapped Guide와 PullPoint의 전 경로 길이를 합산했다.
Hold 끝2초:명령8mm,실제 단축5.36008/5.79309mm(두 케이블).
명령과의 오차−2.63992/−2.20691mm. 단순히 tip이 움직였다고 Cable 명령
구현 PASS를 부여하면 안 된다. CableModel displacement는 단계 중 기록값이므로
최종 실제 경로 길이와 별도 기록한다. 원인은 미확정이다.
다음 작업은 stock CableConstraint의 작은 단일 경로에서 명령/실제 길이/선형화/
제약 오차를 분리하는 것이다. 허용오차 완화나 자체 Solver 재개발로 우회하지 않는다.

044 지지대의 종료40mm 이동은 확인됐지만,중간 시점 예상 경로와 공개 API 사이
최대.2mm 차이로 별도 STRICT1e-12 지지대 시간 동기화 시험은 FAIL이다.
물체가 지지대에 의존한다는 관찰과 지지대 API 시점 정확도는 구분한다.

## 접촉·에너지 측정 범위

구체에 대한 전체 저장 삼각형 최근접 거리와 와이어 유한 반지름 간격을 검사했다.
이는 저장 시점 검사이며 연속 시간 swept clearance 인증이 아니다.
근접 삼각형 수/접촉 Row 수는 실제 Contact Area/Pressure가 아니다.
물체 Jᵀλ는 지지대 접촉도 포함한다. 고정 물체의 투영된0을 반력0으로 해석하지 않음.
CableModel.force는 설치 헤더상 충격량 Ns이므로 **실제 dt로 나누어 N**을 계산한다.
Root Reaction,압력,접촉면적,전체 에너지/일 인증은 NULL/NOT MEASURED.
SOFA 기본 마찰계수는 연구용 가정이며 Changing-normal friction 인증을 대신하지 않는다.
기존 자체 모델과는 Geometry/재료/접합/접촉/적분이 달라 직접 성능 비교를 보류한다.

## 재현

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY product_prototype/sofa/run_native.py --tag UNIQUE_NATIVE_SINGLE
$PY product_prototype/sofa/run_native.py --tag UNIQUE_HOLD --fingers 3 --object free --radius 20 --gravity --floor --outboard 14 --intersection LocalMinDistance --stroke 8 --center-z -80 --support-shape sphere --support-gap .4 --withdraw-support
$PY product_prototype/sofa/analyse.py --tag UNIQUE_ANALYSIS --cases UNIQUE_HOLD
```

기존 results는 덮어쓰기를 거부한다.4GiB/480초,SDK 변경 없음.800스텝 실행한 Scene은
../sofa/scenes/native_three_finger_v1/scene.scn.절대 로컬 경로를 포함하므로 다른 환경에서는
run_native.py로 새로 생성한다.기존 기록에 재실행하지 않는다.
