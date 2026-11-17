# 구조 비교 — 정량 기하/해석 선별, 실제 파지 비교 미완료

## 최신 실제 물리 시험 — through763

실제 단일 필름/자유 구체의 충돌 직후39.0625μs 지속접촉에서 새로운 Lobatto
적분의4/8/16스텝 시간 검사757가0.1% 기준을 통과했다. 이는 자유 물체
들어올리기·전체 구동/해제·3핑거·Baseline 성능 비교 결과가 아니다.
기존 긴 시간 구간 FAIL과 마찰/전체 에너지 차단을 유지한다. 구조의
우수성이나 최종 선정,5일 제작 성공,실측 소재 성능을 선언하지 않는다.

## 최신 물리 개발 범위 — through721

실제 단일 필름/자유 구체의 충돌 시각 재적분과 공유 충격량을 구현했다.
그러나 실제 시간 시험705의 속도0.171685%,접촉력1.486946%는0.1% 기준 FAIL.
독립 FEM721의 고차 적분 비교는 구조 우위나 실제 SOFA 파지 성능이 아니다.
Baseline 대비 파지 성능·자유 물체 들어올리기·3핑거 비교는 미완료이며,
새 필름 구조의 우수성/최종 선정/실측 재료 성능을 주장하지 않는다.

## 2026-11-17 최신 물리 개발 범위

실제 단일 Film/Rails/Tendon과 자유 구체를 Custom Owner로 결합했다.
1ms 무장력 충돌의 실제 시간 세분화640은 제한 범위 PASS다. 기존 C2
구동 시간 수렴607은 FAIL이며,신규 접촉 평가 방식643/648은 별도 시험이다.
이 결과는3핑거 파지,들어올리기,재료 실측 또는 Baseline 대비 성능 우위를
증명하지 않는다. 최종 구조·Optuna 선정 보류를 유지한다. 현재 직사각형
쿠폰과 최종 테이퍼 카트리지/50mm 본체의 차이도 유지한다.

## Current measured checkpoint — whole-surface and mixed-body continuation through566

**Project NOT COMPLETE. Functional commit59254b9; whole-surface mechanics327e212.
No physical child process is currently running at this checkpoint.**
All numbers below are actual SOFA unless explicitly marked independent.

- Whole-surface earliest numerical-path birth,simultaneous owned rows,common
  original C2 control,impact,recontact and sustained midpoint are implemented.
  This is NOT exact continuous FEM CCD or BDF2-resume certification.
-531 fixes a demonstrated final-converged Newton trial rejected by merit;
  tolerance unchanged.536/543 trace-on/off physical CSVs match exactly.
-537 exposes catastrophic cancellation in direct kinetic subtraction for
  tiny impulses.540 records positive impulse work separately from momentum
  energy defect and subtraction residual;no heat/force correction is added.
- Same-binary local4/8/16 grids550/551/546 COMPLETE to1s;553 time FAIL remains.
  Local4->16 velocity1.615247%,attachment.206775%;8->16 velocity.356271%,
  attachment.049632%. Event-time/impulse improvements do NOT certify time.
  These are local grids,not uniform base/dt/quarter certification.
- Actual free Rigid3 supplied-impact548/555 and shared film/body instantaneous
  API552 PASS only their stated reference scopes. Custom event-owner moving
  body guards are intact;no free-body whole-surface integration is claimed.
- New independent ReGripRigidBE corrects real Rigid Coord/Deriv arithmetic
  failure556.558 preserves failed typed Vec3 correction;559/560 demonstrate
  actual mixed Film/Rigid3 dynamics with global GenericConstraintCorrection.
 563 checks BE spin and both-state impulse identities.565 Vec3-only old/new
  regression PASS:maximum state difference5.96312e-18.
-566 passive probe-only extension regression passes exact film state/energy
  CSVs and all preexisting body columns across8/16/32steps;two binaries,
  NOT a same-binary toggle. No diagnostic force/pose change is hidden.
- Actual original C2 free-body Native control562 completes1s/400steps59.286s,
  body z motion.000165366mm,but buffered gap -2.18155e-5mm FAILS.
 564 identity audit and saved actual OBJ/PNG are NOT clearance/grasp PASS.
  Native and custom event laws remain separate physical models.
- Full time/energy,changing-normal friction,self-collision,3finger free
  grasp,12wrench and Optuna remain FAIL/BLOCKED/NOT RUN as applicable.
  No final design superiority or measured-material performance is certified.

Next priority: couple actual free-body mass/J to the custom accepted owner
rather than removing its fixed-body guard;first validate shared multirow
momentum and accepted whole-surface clearance in short tests. In parallel,
isolate post-impact modal/restart/contact discretization error from553.
Do NOT repeat completed long grids or relabel Native562 as successful grasp.
Detailed sources,failures,commands and raw paths:
[whole-surface research](REGRIP_WHOLE_SURFACE_EVENT_RESEARCH.md).


## Latest verified continuation through521 / code534338e,tools2d5e21c

Actual original-C2800step513 now completes first impact,sustained contact,
separation and reimpact. At checkpoint534338e,the36 archived compiled files
in510 matched that checkpoint,not all later source changes. Owner/actual ForceField displacements
match exactly;514/516 owned-row audits pass. This is NOT full-cycle grasp.
Time515 remains FAIL:400->800 attachment2.460337%,velocity7.975552%,event
count1 versus2. Midpoint is an unapproved opt-in contrast,not a replacement
for old BE.503/507 internal512-search-budget failures are preserved;508
isolates real recontact and509/510 fix the loose global-speed search bound,
without raising budgets or changing gap tolerances. No OS exhaustion occurred.
Independent frozen-FEM518/519 support unresolved impact-excited temporal
modes;they are NOT nonlinear SOFA validation. Existing EventStepClock is
reused with a fresh Installed-SDK build;520 XML-order failure is preserved,
521 local-grid clock/C2/time sampling passes. Selected regression524 passes10
groups;not global physics certification. See REGRIP_WHOLE_SURFACE_EVENT_RESEARCH.md.
Next priority: complete/analyze local-grid comparisons before any longer run;
retain full time/energy/friction/free6DOF/3finger/12wrench/Optuna blocks. A
fixed-sphere coupon or local-grid PASS must not be relabeled free-object grasp.



## Latest whole-surface continuation — 2026-11-17

Implementation checkpoint `b65db64`: new whole-triangle quadratic numerical-path
birth search,many-row plastic impulse,shared C2 control and sole SOFA ODE owner.
Actual original C2 Closing492 completes1s/400steps including first impact and
10 sustained steps;this is limited fixed-object operation,NOT grasp/time PASS.
Same-binary488/489/490 refinement491 FAILS:5->20 shell .213327%,attachment
4.835848%;event time/impulse individually pass .1%. Historical471 .11165505%
attachment FAIL remains.484 fails outer Newton;485 compressed-control contact
tangent fails;both preserved. Selected regression494 passes10 groups.
Full energy,friction,self-contact,free object,3finger,12wrench and optimization
remain unqualified. No final design or performance superiority is certified.
See [whole-surface research](REGRIP_WHOLE_SURFACE_EVENT_RESEARCH.md) for actual
raw/build identities,methods,limitations and executable commands.
Next: finish original-C2 refinement,partition event/restart versus structural
energy errors;do NOT repeat completed old campaigns or bypass moving-body guards.


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

## 2026-11-17 actual comparison limits

No final structure superiority is selected. Actual routing studies show an
early arch also exists in linear transients. Slower control improves inward
no-object bending, but broad Sphere wrapping remains unqualified. A fixed
faceted Cylinder supports locations spanning11.243deg: object-shape dependence,
NOT fair Baseline-versus-ReGrip grasp superiority. Object-mesh force/kinetic
and coupled time remain FAIL. Added guides' mass/loss/interference are not
included in equal core-volume accounting. See routing report20261117.


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
