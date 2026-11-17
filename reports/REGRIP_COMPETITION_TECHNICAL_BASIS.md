# 경진대회 기술 근거 — 연구 결과와 제작 목표 구분

## 최신 연구 근거 — through763,지원서 성능 과장 금지

실제 단일 필름/자유 구체의 충돌 시각 재적분과 제한된39.0625μs 지속접촉의
시간 수렴757를 검증했다. 이는3핑거 파지 성공률/들어올림/손상 방지 실측이
아니다. 본선용 교체형 필름·보강 레일·공통 와이어는 여전히 제작 후보이며,
지급 액추에이터 사양과 PET/TPU 물성·팀 구성은 임의로 확정하지 않는다.
기존 지원서 문항·글자 수와 미검증 기능의 목표 표기를 유지한다.

## Latest measured impact continuation 445–474 (2026-11-17)

Project NOT complete. Independent projected impulse,event root/IFT,root-map
mass,pre/post velocity and multistep restart now exist in models/film_impact.
Actual SOFA supplied-film and isolated-birth/remainder prototypes execute;
this is NOT the whole-triangle C2 event owner required by434/437.
See REGRIP_IMPACT_SOLVER_RESEARCH.md for equations,scope,failures and raw paths.
Actual same-binary464/466 midpoint startup reduces20→80 attachment time
error4.38155%→0.901492%,but remains FAIL0.1%. Finer47140/80/160 has
adjacent PASSs but40→160 attachment0.11165505% FAIL. Do NOT certify time
from the adjacent comparisons or replace the original C2-time FAILs.
Independent469 root+impulse velocity tangent FD error1.66e-9. Actual470/472
accepted whole-triangle clearance and actual FF/owner state-energy agreement
pass LIMITED audits,not swept CCD or full physical energy. Actual474 rejects
additional mass/moving colliders;12 physical journals match468/471 bitwise.
Selected regression473 passes12 groups,not global45 gates. First feature
commit1b2b18c;subsequent guard/evidence commit is recorded by Git.
All launched children through474 have exited;no OS exhaustion/480s timeout.
Whole energy,friction,self-contact,free6DOF/3finger/12wrench/multimaterial,
design superiority and graspOptuna remain BLOCKED/NOT RUN. No SDK edits,
remote push,hardware or automatic/background resumption.


## Latest actual continuation — candidate closure/C2 (2026-11-17)

Project NOT complete. New implementation and measured results are in
[FILM_CANDIDATE_CLOSURE_20261117.md](FILM_CANDIDATE_CLOSURE_20261117.md).
Actual411 completes16s/1600steps in263.082s with whole-triangle buffer
gap >=-9.467e-11mm (unchanged1e-10 gate).392/411 use6 genuinely added-row
records;owned Jacobian/impulse/barycentric audits pass limited checks.
C2 tail-cancellation failure393 is preserved;fixed405 completes8s and
all800 ForceField/owner applied tensions match exactly. Full C2 dt/2
comparison427 still FAILS0.1% (force5.698%,tip3.753%,attachment .6038%).
Pre-contact ONLY C2 BDF2 .1s160/320/640 passes .1% in435;no contact
occurs there.434/437 complete1s/800/1600steps.438 passes ALL pre-entry
metrics but entry force64.35%/impulse11.01% FAIL.441 actual accepted
normal velocity flips -1.34057/+0.296019mm/s despite good endpoint gaps;
442 independently demonstrates the position-level BDF2 impact issue.
No whole-cycle BDF2 PASS.443 rejects unexecuted3200steps/687s by POLICY,
not OS exhaustion. All launched physics children have exited.
Selected NEW-binary regression433 PASS12 scoped groups,not45 global gates.
Short same-binary cost431 gains3.721% median over3 alternating pairs;
all5 physical CSVs match. No compounded/global speedup is claimed.
Whole energy,friction,self-contact,3finger/free6DOF/12wrench/multimaterial,
final-design superiority and graspOptuna remain BLOCKED/NOT RUN.
Actual saved-state figures: designs/visualizations/film_native_20261117_closure_recovery_actual423/.
No SDK edits,remote push,hardware,paid service or automatic restart.
Older RUNNING/final-checkpoint notes below are historical,not live status.



## Latest 2026-11-17 checkpoint through372 (NOT project completion)

Local source/tool commits through3181ce8. Actual fixed-sphere356 completes
8s;366 completes16s/1600steps in268.204s. Final tip -0.00672mm,max speed
0.00854mm/s,T=0,contact multipliers0. This is frictionless FIXED-object
release/near-rest recovery,NOT free6DOF/3finger grasp or design superiority.
Actual states: designs/visualizations/film_native_20261117_sphere_recovery_actual372/.
Full-cycle buffer-clearance audit358 FAILS (-0.00013543mm at7.99s);the gap
to the radius8 zero-thickness sphere remains positive0.00986457mm. BothSide
contrast367 is REJECTED as a fix:all5 physical journals byte-identical in370.
Time348/351 still FAIL0.1%;full energy/friction/free grasp/Optuna BLOCKED.
Next REAL implementation is candidate-complete triangle contact with its own
row-observer interface;independent temporal work is a shared C2 tendon
profile. No candidate-complete or C2 implementation is claimed yet.
See FILM_TEMPORAL_COUPLING_20261117.md and LONG_RUN_RESEARCH_CHECKPOINT.md.
Historical activity notes below are not live process status.


## 2026-11-17 actual continuation through343 — project NOT complete

Local feature commit518208f adds current closest point/gradient/Hessian and
SQP line-search globalization,without changing accepted forces or tolerance.
Actual333 completes4s/400steps:70.0995s runtime;whole-triangle buffered gap
defect2.21e-11mm versus0.000531mm in307. Radial moment and force pullback
checks pass in limited scope. Discrete force-location covering arc73.208deg
is NOT contact area/pressure/holding performance. Fixed-object,frictionless,
single-finger only;NOT free6DOF or full-energy certification.
Failed320/322 and rejected remedies325/328/329 are preserved. Same-binary
short time comparison337 FAILS0.1%,including pre-contact motion/energy;
the contact event alone cannot explain all time error. Full-window344 and
subsequent development must be judged from their actual final result files.
Details/reproduction: FILM_TEMPORAL_COUPLING_20261117.md and
LONG_RUN_RESEARCH_CHECKPOINT.md. Grasp Optuna remains BLOCKED;no fabrication
or actuator performance is claimed. Historical notes below are not live status.


## 2026-11-17 latest actual checkpoint through305

Project NOT complete. Work continued beyond the old campaigns. Source feature
commits through29ef7e4 are local only; current-sphere geometry is an additional
experimental implementation, not a replacement certification.

Actual fixed-cylinder270 closes over4s;275 completes8s closing/hold/release.
282 completes16s including settling (1600steps,281.424s): final tip -0.007395mm,
maximum speed0.009374mm/s, zero prescribed tension and no positive contact
impulses. These are actual research-parameter results, NOT free-object grasp.
The first800 rows of282 match275 bitwise (state/contact/momentum/coupled CSV).
Sphere284 closes4s but supports locations over73.148deg versus Cylinder
123.752deg. Discrete force-bearing location spans are NOT contact area,
continuous wrapping angle, pressure or holding capacity.

Whole-cycle275/288 time comparison292 remains FAIL at0.1%: tip2.3268%,
normal force14.4819%,attachment energy1.1316%,kinetic energy8.3910%.
Inherited failures remain. Same-binary cache benchmark281 has3 alternating
pairs, all5 physical CSVs bitwise identical, median runtime ratio0.77813
(22.19% reduction);704 mechanical evaluations become402, with302 exact reuses.
This is scoped performance qualification, not physical convergence.

Measurement issue isolated: main journal.x is WORLD, not displacement.
Late world-minus-rest force reconstruction loses precision. Near-rest
prescribed probe293 gives relative impulse residual0.00419962 in294 world
reconstruction versus2.78543e-8 in295 direct local-displacement reconstruction.
296 recorder ON/OFF physics CSVs match bitwise.291's earlier attempt wrongly
interpreted main x as displacement and is INVALID postprocessing, not physics.
Old whole-cycle raw lacks exact local coordinates: do not retro-certify it.

New root cause298: frozen begin normals give accepted exact-sphere radial-law
moment deviation0.6430% in the wide Sphere test. New SphereStep uses actual
current radial gaps/normals and TRUE constraint geometric tangent. Independent
FD relative error2.21e-15;actual30120-step test and302/303/304/305 partial
equation checks pass their LIMITED scopes: accepted radial-law defect1.59e-15,
force-row reconstruction4.97e-17, impulse residual3.49e-6,derived BE identity
4.02e-10. This is a NEW fixed-support sphere model, not native-contact
equivalence, friction, CCD, contact-area convergence or free6DOF certification.
300 source-archive omission is preserved as prephysics FAIL;301 fixes it.

Current actual extension306: inspect summary/result before interpreting its
prefix. No tolerance relaxation, fake forces, SDK edits, hardware, remote push
or paid service.299 rejects unsupported moving colliders before accepted rows.
Three fingers/free6DOF/12-wrench/multimaterial, full energy, final structure
superiority and grasp Optuna remain BLOCKED/NOT RUN.

## 2026-11-17 actual continuation through264 — supersedes older status

Project NOT complete. Functional commits: b8b9cc3 (profiling/routing),
6172967 (cache recovery),9354793 (nonlinear contact),74175ca (BDF2 alternative),
ed40987 (mandatory accepted-stage owner). Sources/builds/raw remain separate.

Actual235/243 complete400/800-step fixed-cylinder closing;246 time FAIL:
force9.27393%,tip0.163093%,attachment0.169901%,kinetic4.73995%.
Independent240/241 confirm accepted impulse equations and the derived BE
identity, NOT whole energy or global force/moment certification. BDF2 actual
244/247/248 also FAIL250; do not adopt it as a qualified time fix.

Actual251 higher-tension one-factor capacity probe fails free Newton at2.95s.
Available2.94s state has73.122deg load-bearing location span, but partial-run
diagnostic258 and plot259 are EXPERIMENTAL/PARTIAL FAILED, not wrapping/grasp
approval.263 with single-Newton predictor gets past that stage to3.36s, then
FAILS the coupled Newton30-iteration budget. This is algorithmic failure,
NOT OS memory/runtime exhaustion. No tolerance/iteration inflation was used.
Short260 accepted impulse/energy checks and actual negative-owner guard264
pass their LIMITED scopes.265 tests previous accepted velocity initialization;
inspect summary/result before using its data. No automatic restart is assumed.

Read FILM_TEMPORAL_COUPLING_20261117.md and LONG_RUN_RESEARCH_CHECKPOINT.md.
Remaining: robust complete closing/hold/release, mesh/history/dt, current-normal
angular consistency, reactions, whole energy, self-contact, free6DOF/3finger/
multimaterial/12-wrench grasp. Final-design superiority and grasp Optuna remain
BLOCKED/NOT RUN. Research parameters are not measured PET/actuator properties.

## 2026-11-17 evidence update

Actual fixed Sphere/Cylinder contact, limited shape-dependent wrapping,
measured cost optimization and short coupled equations are now available.
They do NOT establish free-object or multimaterial grasp performance.
All application performance figures remain targets; team/actuator details
remain unknown. No certified pressure, safety or final superiority is inferred.


## 최신 근거의 범위 (2026-11-16)

고정 구체의 실제 표면 접촉까지 실행했지만, 중간 필름이 위로 아치형 변형하여
의도한 감싸기는 입증하지 못했다. 두 적분법의 통합 시간 Gate가 남아 있어
이를 지원서의 파지 성공률·힘·토크 성과로 사용하지 않는다. 선택적 재밍과
지급 구동부 성능도 아직 검증/확인되지 않았다.

실제 SOFA 단일 핑거에서 유연 Skin–Rails 부착과 편심 와이어 힘 전달 및
저장력 해제·복원을 계산했다. 자유 물체 파지 성공/성능 개선 성과로 쓰지 않는다.
통합 시간 수렴은 부착 에너지에서 FAIL이며, 실제 재료/체결 강도/액추에이터는
미측정이다. 5일 제작 가능성은 여전히 계획·목표이며 확정 납기 성과가 아니다.
지원서의 미확인 팀원/액추에이터 사양 및 정량 파지 성능을 임의로 채우지 않는다.
실제 계산·독립 수학·가정 구분: FILM_CONTACT_DYNAMICS_20261116.md.

## New simulation evidence and application boundary

Actual film coupon simulation now has diagnosed Newton-stage fixes and limited
endpoint force-balance checks. Whole transient convergence and complete grasp
are still unqualified. These are engineering development results, not measured
grasp capacity, damage avoidance, success rate or superiority over baseline.
Keep all quantitative gripper performance statements as targets. Actuator
specifications, measured material data, team composition and organizer rules
remain unconfirmed; no new hardware specification is inferred.

2026-11-16. 지원서 답변은 별도 `REGRIP_COMPETITION_APPLICATION_DRAFT.md`.
실제 주최 측 규정/지급품 명세/팀원 정보가 제공되지 않았다. 아래는 사용자
제시 조건에 근거한 제작 후보와 검증 계획이며 본선 성능 달성 보고가 아니다.

## 기술적 지원 동기와 다물성 문제

강체는 작은 접촉면의 미끄럼·회전에,유연체는 과도한 압착과 형상 변화에,
하네스는 가는 지름과 탈출 경로에,취성물은 국부 압력과 충격에 취약하다.
미공개 물체까지 단일 고정 형상·높은 파지력으로 해결할 수 있다고 보지 않는다.
형상 적응과 하중 지지를 분리하고 손상된 접촉부를 교체하는 구조를 검증한다.
접촉압 감소만으로 실제 취성 파손 방지를 인증하지 않는다.

## 5일 기본 제작 후보(잠정,성능 선정 아님)

100 mm 교체 카트리지3개,목표 root 반지름50 mm,공통 케이블 equalizer,
연속 접촉 Skin과두 edge backing strip,복원띠,분할 루트 클램프.
동일 core 체적 후보:가정0.05 mm Skin,0.10 mm×2.07233 mm backing2개,
테이퍼24→12 mm. 전체 core439.33979 mm³로 기존 등가 Beam과같다.
외피/체결/와이어/구동부 체적·질량은 제외되므로 완성품 동일 질량은 아니다.
실제 공급 두께·절단 공차·찢김·최소 굽힘 반경·층간 마찰은 미측정이다.

기본안은 공통 케이블로 저속 적응 파지하고 탄성 복원한다. 선택 잠금은
근위 구간의 기계적 압착 latch를 옵션으로 둔다. 자동 latch 구동은 지급품
스트로크와 허용 추가 구동부 확인 후 결정한다. 수동 latch가 자동 운반 규정에
맞는지는 확인 필요하다. 밀봉/밸브/배관3회로의 독립 진공 재밍은 연구안으로
보존하지만5일 기본 기능의 필수 경로로 두지 않는다. 진공을 수치 강성배수로
바꾼 민감도 해석을 실제 잠금 메커니즘 검증으로 부르지 않는다.

## 현재 확보한 정량 근거와 한계

- 실제 SOFA 단일 필름 ROM:막 인장+굽힘/비틀림,전체 격자3D 변위,고정 평면
  접촉 힘/에너지/참조 접촉면적. OBJ 로딩 단계에서 실제 변형 단계로 진전.
- 독립 작은 변형 캔틸레버:일관된 기울기 구속11/21/41노드 이론오차
  약0.300/0.100/0.0283%. 실제 장치 하중 성능이나파지 인증이 아니다.
- 동일 core 체적 좁은/넓은 직사각 단일 필름 쿠폰의 초기 Euler 시험에서
  접촉면적비1.733,평균압력비0.748 관측. 고정 평면/가정 물성/미세 모델하중의
  결과이며,원본3핑거·실제 적층카트리지·자유물체 성능 비교가 아니다.
- 공간 에너지/접촉 수렴,일부 힘 잔차와시간/마찰 소산은 FAIL/BLOCKED.
  따라서 파지 우위·최종 구조·실제 운반 하중·Optuna최적값은 미승인.

## 측정 가능한 목표(성과가 아닌 목표)

|목표|판정 방법|현재|
|---|---|---|
|root 반지름≤50 mm,핑거약100 mm|조립 도면/실측,구동 시 간섭 확인|개념 기하,제작 미실시|
|core 체적≤439.34 mm³,완성 질량 별도 기록|부품별 CAD/두께/질량 측정|기하 산술만 충족|
|동일 조건 평균 접촉압20%이상 감소|수렴된 동일물체 접촉/실측 압력 비교|쿠폰 가설,파지 미검증|
|2종 이상 물성,각5회 중5회 유지·해제|하중·이동거리·유지시간은 지급품 확인 후 사전 고정|NOT RUN|
|카트리지 교체60초 이내|무부하 안전 교체 영상/시간 측정|NOT RUN|
|해제 후 끝단 복원90%이상|동일 측정 시점·처짐 정의를 사전 고정|NOT RUN|

## 구동·센서 시나리오와 제어

액추에이터 종류/정격·최대토크/속도/스트로크/전압/드라이버/허용전류/개수는
미확정이다. 회전형이면 spool 반지름r에서 T_cable≤ητ/r,필요회전은Δl/r;
직동형이면 스트로크≥필요 당김량+가이드 손실을 검증한다. η/마찰은 실측한다.
허용 장력을 초과하는 설계는 채택하지 않는다. 전류 피드백이 있어도 토크상수와
마찰/감속 손실이 보정되기 전에는 전류를 실제 파지력으로 변환하지 않는다.

상태기계:접근→저속 와이어 적응→안정화→선택 잠금→들기→운반→내려놓기
→잠금 해제→와이어 해제→복원. 위치 feedback이 없으면 시간/이동량을
사전 교정한 open-loop로 제한하고 접촉이 감지됐다고 주장하지 않는다.
장력/전류/압력 센서는 실제 지원되는 항목만 closed-loop에 사용한다.
어떤 경우에도 교정된 최대 당김·전류·시간 제한과 중지/해제 경로를 둔다.
센서가 없으면 미끄럼 자동 감지/자동 재시도는 미지원이다. 운반 로봇 인터페이스가
없다면 들어올림·이동은 운영자 절차이며 자동 제어 구현이라고 기록하지 않는다.

## 제작 위험과 대응

필름 찢김→가이드 모서리 둥글림/소모 Skin;주름·좌굴→폭/보강 위치 시험;
와이어 편주→equalizer/양쪽 guide;층 전체 접착→미끄럼을 남기는 root clamp;
진공 누설→기본 공통 구동으로 기능 축소;복원 부족→교체 복원띠 실측;
정전·과전류→기계적 낙하 방지 받침/정지 및안전 해제. 실제 취성물은 보호받침과
시험 승인 없이 파손 실험하지 않는다. 하드웨어 구동은 별도 사용자 승인 사항이다.

## 5일 일정(예정)

1일:규정·지급품 확인,단일 카트리지 절단/클램프/복원 시험.
2일:공통 구동/equalizer·3카트리지 조립,무부하 스트로크/장력 한계 교정.
3일:강체·유연체·케이블 대조 시험,안전 제어/보호 패드 보정.
4일:필요한 경우만 근위 잠금 추가,유지·운반·해제 반복/실패 복구.
5일:미공개 물체 적응/예비 카트리지·와이어 준비,영상·수치 정리.
자동 잠금·진공 회로는3일 기본기능 성공 후에만 선택하며 실패 시 축소한다.
실제 조립 시간·팀원 수는 미제공이므로 이 일정은 실측 공정 견적이 아니다.

## 주최 측 확인 항목 및 팀 역할

지급 액추에이터 전체 명세/개수/드라이버와 통신,전원·추가 센서·진공원 사용,
허용 재료/공구/가공,수동 보조·추가 액추에이터 허용 여부,물체 크기·질량 범위,
취성물 안전 기준,성공 유지시간/운반 거리/재시도,예산·공급품 반입을 확인한다.
팀원 수·이름·전공·실제 담당은 미제공이다. 기구/구동제어/시뮬레이션/
시험기록 역할을 실제 명단 확인 후 배정한다. 가상의 팀원 경력은 작성하지 않는다.

골판지 수동 시연은 별도 `REGRIP_PROTOTYPE_PLAN.md` 조건을 따르며,
그 성공을 진공 적층/모터 구동의 정량 성능으로 전용하지 않는다.
