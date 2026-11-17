# 최종 설계 판정 — 선정 보류(EXPERIMENTAL)

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

## 2026-11-17 design remains provisional

Actual film/rails/routed-tension contact and short coupled solves exist, but
no grasp-qualified final structure. Larger2/5mm offsets add fabrication/
interference questions. Whole energy, Sphere wrapping, free6DOF/three-finger
and time qualification remain open. Single-finger coupons do not certify the
50mm body target or five-day feasibility. No final grasp Optuna is claimed.


## 2026-11-16 실제 구현 갱신 — 선정 보류 유지

단일 핑거 Film+flexible Rails+실제 경로 Tendon 힘 전달과 복원은 SOFA에서
구현했다. 이는 50 mm 본체의 3핑거 조립/파지 검증이 아니다. 동등 코어 체적
직사각형 쿠폰은 tapered 후보와 구분한다. 시간·자가 충돌·물체 접촉·강도 Gate가
남아 최종 설계를 확정하지 않는다. 작은 장력 복원 결과를 실제 지급 액추에이터
성능이나 PET 물성 검증으로 주장하지 않는다. 상세 FILM_CONTACT_DYNAMICS_20261116.md.

## Current qualification update — final design still deferred

Actual SOFA film Newton defects were corrected and coupon endpoint balance
recovered. Full dynamic convergence, coupled Film+Rails force transfer, wire
wrapping and free-object tests are not qualified. Therefore the provisional
common-wire/cartridge candidate remains a fabrication candidate, not a proven
winning gripper. Neither new solver implementation nor endpoint force balance
changes unknown actuator/material/rule constraints or proves a five-day build.

## 5일 제작용 잠정 기본 후보 — 성능 최종 선정 아님

공통와이어 equalizer+교체 Skin/edge backing카트리지+탄성복원으로 기능을
단순화한 기본안을 우선 제작 검토한다. equal_volume_v2도면은0.05mm Skin,
0.10mm×2.07233mm backing두개로439.33979mm³ core를맞췄다. 공급재료/구동부/
규정/팀역량확인 전 제작 확정은 BLOCKED다. 목표 본체R50mm는계속설계제약이다.
선택적 근위 기계압착은옵션,3구간진공은 기본기능성공후연구안으로둔다.
동일체적 쿠폰의 넓은 접촉 가설은 실제 SOFA에서 일부 관측했지만 전체공간/
동역학/파지 Gate실패가남아 최종성능우위/Optuna최적후보를선정하지않았다.

[동일체적 단면](../designs/film_contact/equal_volume_v2/section.svg),
[실제 SOFA 쿠폰 상태](../designs/visualizations/film_actual_v1/actual_coupon.png),
REGRIP_COMPETITION_TECHNICAL_BASIS.md 및 별도 APPLICATION_DRAFT.md 참조.
지원서의 성능숫자는목표이며실제파지달성실적으로사용하지않는다.

최종 제작 설계나 최적 설계는 아직 선정하지 않았다. baseline을 최종안으로
확정하지 않고,Concept v2의 **tapered film cartridge + 선택 재밍 sleeve**를
후속 비교 후보로 유지한다. 넓은면적은장점가설,5.74배재료량/밀봉/배관/
얇은필름주름/마모는명백한위험이다. 성능 우위는 입증되지 않았다.

구현한 것은 재현가능한 기하 생성,실제 OBJ/XML/SVG/PNG,메시검사와SOFA
로딩,독립EB순응도선별이다. 실제Shell파지·접촉압·자유6DOF유지·복원은
NOT RUN. 공통 마찰시간 Gate와에너지 미완료로 최종 파지Optuna는 BLOCKED.

선정전 요구:동일재료량/힘조건에서Baseline,film,selective의Shell/Contact
수렴 비교;압력회로의실제봉합/진공누설/층간마찰시험;Sphere/Cylinder/Box
힘·토크12방향과해제복원;에너지계측. 제작용PET/TPU물성·두께·마찰·와이어
가이드손실·고정강성은모두미측정이다.

도면:

- [3D 기하 투영 PNG](../designs/visualizations/concept_v2/assembly.png)
- [정면·측면·평면·등각 SVG](../designs/visualizations/concept_v2/assembly_views.svg)
- [단면·와이어·3구간 회로 SVG](../designs/visualizations/concept_v2/mechanism_section.svg)
- [기구학적 접근·첫접촉·해제 순서](../designs/visualizations/concept_v2/sequence.svg)

그림은Concept Design/Implemented Mesh Geometry이며Actual SOFA Result
형태의변형그림이아니다.처방곡률을실제시뮬레이션성공처럼표시하지않는다.

재현(기존버전덮어쓰기금지):

```
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/design_regrip.py --tag UNIQUE
$PY tools/design_validate.py --version UNIQUE --tag UNIQUE
$PY tools/design_render.py --version UNIQUE
$PY tools/moving_sphere_run.py --tag UNIQUE
```
