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


# Product/native checkpoint — 2026-11-19

방향 전환 시작 b63ac48. 초기 제품 commit e5675c9,주요 기능 commit d6c4580.
이후 coupon050,메타데이터 수정,추종/지지대 진단과 문서를 별도 커밋한다.
정확한 최종 커밋은 `git log -3 --oneline`으로 확인한다.

## 구현/증거

- cad/generate.py,export_freecad.py,publish.py;drawings/candidate_v3/에 치수도,
  부분 분해도,BOM,SCAD,검사 JSON. meshes/product_outboard14_v3/에4종 폐곡면 STL.
- 실제 실행 Scene:sofa/scenes/native_three_finger_v1/,800스텝 exit0.
- 모든 고유 trial:results/native_*/,분석:results/analysis_*.
- 재사용 가능 입력/로깅 DSO:
  cad/build_native_single_generic_045/libReGripProductSequence.so.
  이 빌드는 정상이나045의 제거된 GenericConstraintSolver Scene은 FAIL이다.
  같은 DSO의050 수정 BlockGaussSeidel 직선 coupon은 실제800스텝 PASS.
- product 결과는 기존 자체 Solver/SDK와 분리. legacy Checkpoint 재사용하지 않음.
- 044 support withdrawal,048 분석:Holding FAIL,종료 objectdrop40.2mm.
  지지대 중간 시각 API 경로 오차.2mm로 STRICT시험도 FAIL;원인 미확정.
- 050 straight cable 실제 경로 추종 PASS,max1.77809e-17m. FEM/외측 매핑/두케이블
  조건에서는8mm 명령을 추종하지 못한다. 다음 개발 병목이다.
- 010/011/012 전체 출력 Time Gate0.1% FAIL,021 Lift FAIL,
  pressure/area/root reaction/full energy NULL. 모터/실측 재료/Equalizer 미정.
- FreeCAD/OpenSCAD/OCC 미발견으로 STEP/전체 어셈블리 검증 미실행.

## 다음 정확한 명령

```bash
cd /media/ubuntu/99419895-2058-45b4-b746-b36ea7112e4e/research/LHJ/ReGrip
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
git status --short
git log -3 --oneline
$PY product_prototype/sofa/cable_coupon.py --tag UNIQUE_STRAIGHT_CHECK
$PY product_prototype/sofa/run_native.py --tag UNIQUE_FEM_BASELINE
$PY product_prototype/sofa/analyse.py --tag UNIQUE_FEM_AUDIT --cases UNIQUE_FEM_BASELINE
```

050 재현은 원리 시험이다. 다음 **새 개발**은 단일 케이블과 쌍 케이블을
동일 FEM에서 비교하는 opt-in 장면을 추가하고,외측 Barycentric 경로와 표면상
경로를 한 변수씩 비교하는 것이다. 실제 Guide 길이/명령/반력/단계 선형화 오차를
기록한다. 물리 장력/마찰/허용오차를 바꾸어 기존 FAIL을 PASS로 변경하지 않는다.
기존 기본 단일 Scene은 지오메트리6개 Guide/케이블,C2/5mm 명령이다.
기존 CSV가 guide로그를 갖지 않으면 길이 측정은 NULL이며 0으로 채우지 않는다.

독립 Holding 재현(지지대 실제 구동,물체와 핑거 형상은 처방하지 않음):

```bash
$PY product_prototype/sofa/run_native.py --tag UNIQUE_HOLD --fingers 3 --object free --radius 20 --gravity --floor --outboard 14 --intersection LocalMinDistance --stroke 8 --center-z -80 --support-shape sphere --support-gap .4 --withdraw-support
```

재개는 기록된 물리 checkpoint가 아니라 **새 Native 초기 상태의 신규 trial**이다.
개별 프로세스4GiB/480초,동시 장시간4개 이하. 모든 실행은 종료되었으며
세션 이후 자동 재시작은 설정하지 않았다. OS 자원 고갈을 주장하지 않는다.
제품 완성은 미달성이다. 현재 산출물은 다음 개발로 이어갈 구현 체크포인트이다.
