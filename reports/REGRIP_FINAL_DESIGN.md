## Latest completed — same-Tmax HOLD and startup diagnostics1186–1206

1187/1189/1190/1199 actual NO-OBJECT50ms Hold completed;not RUNNING.
Same Tmax,release moved20..30→50..60ms. Mean skin tip-.73836mm vs original
pulse-.38082mm;different work,NOT wrapping/holding superiority.
1206 endpoint200/100/50us all-pair PASS,max.00514502%;1198 coarse family
FAIL.1204 exact0.8ms startup FAIL remains,including tiny signals;NO full
time/mesh/energy/grasp certification.1205 force precision probe is not a
high-precision trajectory. Next isolate Newton absolute residual vs dt.
1193 original50ms pulse unchanged EXACT after refactor;1192 preserved
RAW/build/SDK integrity PASS19096. No SDK edits/pushes/old-result deletions.
See [research](REGRIP_TENDON_TRANSMISSION_AND_WRAPPING.md) §7b/7c.
Actual3-finger44.4ms checkpoint:1178_plan7/three.checkpoint_344.txt.
Validated reusable Hold DLL:build/film_transmission_20261118_transmission_hold_profile1186/libReGripFilmTransmission.so.
Next-window actual DLL:build/three_film_extended_20261118_three_film_after38_actual1174/libReGripThreeFilmRecovery.so.
Current complete feature commits:1f9a339,04630f2;subsequent checkpoints
record the additional tool/report commit. No automatic background restart.

## Latest verified continuation — campaigns1169–1188 (2026-11-18)

Actual3-finger endpoint is now44.4ms (1174/1178),not38ms.1176/1177 exact
state/time/API and persistent resume PASS;1182 all64 q/v/time match the
preserved same-plan reference EXACT. Separate .1% independent endpoint
subset1173 PASS,max.0300%;not actual full contact/time certification.
Actual no-object50ms pulse1169 is API/stage EXACT,NOT complete recovery.
1185:injected pulse work is23.2744% of ONE no-object static state's stored
energy. More unloaded time cannot reach THAT state under passive-model
assumptions;not a proof against every possible contact-guided wrap.
Static shape intersects an overlaid fixed sphere (1180);it is NOT wrapping.
1183 stronger attachment static FAIL retained. Next:longer same-Tmax Hold,
not higher tension.1186 short new-control API PASS;1187 actual50ms Hold
is an in-progress experiment at this checkpoint,not a claimed result.
Details/raw/source/binary identities:[research](REGRIP_TENDON_TRANSMISSION_AND_WRAPPING.md).
Full friction/self-contact/lift/energy/grasp/Optuna remain BLOCKED/NOT RUN.
Last completed feature commit before this checkpoint:1f9a339.

## Latest continuation — transmission campaigns1139–1168 (2026-11-18)

See [transmission and wrapping research](REGRIP_TENDON_TRANSMISSION_AND_WRAPPING.md).
Actual single-film20ms q/v/time/force-stage API identity PASS1e-12.
Midpoint endpoint time FAIL0.629144%;separate unconstrained order4 Gauss
all-pair endpoint PASS0.00458128% maximum against0.1% gate. Not full time,
contact or mesh certification. Actual skin mean tip-0.16733mm versus centre
-0.02290mm shows nonuniform deformation,NOT wrapping/holding proof.
Independent nonlinear static1165 force equilibrium PASS1e-12N at unchanged
T=.0001N/rail:mean tip-43.05871mm,angle0.827697rad. Stability/contact/dynamic
arrival time unqualified. One-factor bond/route actual trials preserved.
Actual3-finger endpoint remains38ms;1164 onward are independent next-window
references,not actual continuation. Friction,lift,full energy,Optuna BLOCKED.
Raw/build/reproduction details are in the linked report. No automatic restart.
Historical RUNNING text below is not current process evidence.

# 최종 설계 판정 — 선정 보류(EXPERIMENTAL)

## Latest completed1134–1138 — exact chain and transmission/energy diagnostics

1134 independent same-plan reference matches ALL64 actual31.6..38ms q/v
and accumulated times EXACT. The different-plan endpoint clock comparison
(1.38778e-17s,velocity4.05720e-11mm/s) is NOT waived under1e-12 API gate.

1135/1136 use actual20ms q/v,public mass and root mapping without integrating
or applying signed diagnostic forces to SOFA. Frozen tendon-force affine
error8.32728e-20N;unit-force norm3.92120469 acts on Rails,unit Skin force0,
direct normal acceleration gain0. The local zero-velocity linearized delayed
reaction second-time-derivative gain norm is7.96365944/s². This does NOT mean
zero eventual control authority,nor establish nonlinear response time or
required actuator force.1138 verifies the delayed-response formula against
an independent analytic three-mass model (second-order Taylor convergence).
Larger tensions/body-only loads in1135/36 are FROZEN sensitivity inputs,
NOT new actual grasp trials,gravity simulation,or repairs of old FAILs.

1137 reconstructs192 ACTUAL FREE recovery stages31.6..38ms. Stage weights sum
EXACTLY to actual elapsed0.006400000000000017s. Actual ForceField energy error
2.71051e-19Nmm;Wt=0 (actual T0),Wext=8.11563637e-6Nmm,
Wdamp=6.25963299e-6Nmm,delta(stored+K)=1.86086141e-6Nmm.
Signed defect=+4.85802552e-9Nmm,NOT heat. Root Work NULL.
Relative to measured energy change,this defect is about0.261% (diagnostic
normalization,NOT a new acceptance criterion). Whole energy remains BLOCKED.

Current actual endpoint remains38ms/checkpoint280. No holding,lifting,
completed recovery,friction,mechanical equalizer or final design certification.
No OS/RAM exhaustion or child timeout caused these results. No automatic
post-session process/restart is provided. Next development should investigate
delayed Rail→Attachment→Skin control response and error-controlled longer
physical-time integration,not merely increase tension or delete38ms bounds.

## Additional verified1130–1133 — value-only geometry and grasp feasibility

12000 independent closest-point queries are bit-exact with original AD2.
Optional clearance-only mode (defaultOFF) leaves mechanical Force/Hessian
unchanged. Actual1131 eight-step state/stage/ForceField CSV match1124 bytewise.
Actual1132 three alternating A/B pairs all PASS strict replay and snapshots:
median4.175684s→3.310452s,20.7207% reduction,ONLY unloaded FREE recovery.
No general collision/impact speedup claim.

Actual20ms-row audit1133 finds frictionless sphere wrench rank3 and exactly
zero normal torque. Upward normal force observed5.27745e-6N is NOT a holding
capacity.100g Earth-weight reference.981N is a calculation,NOT measured lift.
Actual gravity remains0,Fz=-.001N. Friction/self-contact remain unqualified.
Thus simply extending zero-tension recovery will not establish stable grasp.
Full12-wrench dynamic trials and final design/Optuna remain NOT RUN/BLOCKED.

## Latest verified checkpoint — 2026-11-18, Campaigns1091–1129

- Actual1091 fixes the representable RK interval duration without changing forces:
  independent q/v EXACT;1092 verifies sum(stage weights)==actual elapsed time.
  Prior1076/1089 clock failures remain preserved.
- Actual unloaded recovery reaches **38ms** (1124 and seven bounded1127 plans),
  via V5 persistent clock/used-dt/next-dt/plan/counter state.1125 independent
  q/v/time EXACT;1126 four-step actual resume and checkpoints BYTE-IDENTICAL.
  Earlier1112/1113/1117 exact resumes and1114 corruption rejection also PASS.
- 1110 actual same-time800us recovery subset PASS (max all-pair0.01281255%).
  The longer independent6.4ms200/100/50us comparison1121 FAIL0.11718728%;
  separate100/50/25us1123 PASS0.02950534%. This is NOT full-cycle time PASS.
  1106's multiplied/common-time API bridge FAIL5.57e-12 is preserved;the actual
  next-dt scheduler aligns all11 contexts rather than overwriting q/v/time.
- 1096 release power inventory: mechanical tendon work -5.45816e-8Nmm,
  signed defect -1.11372e-12Nmm;not heat/full energy certification.
  Root reaction work NULL. Legacy sampled-work private origin is not restored.
- Actual1128 at38ms: skin width-mean tip z=-0.34690653mm,vz=-3.74943732mm/s;
  skin RMS displacement0.12074783mm and squared-RMS rate +1.07056815mm²/s:
  **shape recovery not completed**. Rails relax while skin continues moving.
  Body vz=-1.29190161mm/s;gravity0,Fz=-.001N,friction OFF:NOT hold/lift.
  1129 scale-one actual geometry/OBJ uses saved state,not prescribed deformation.
- Independent current-deformed frozen spectrum1087 has longest undamped
  period5.85155s;NOT measured nonlinear recovery time. A naive long rollout is
  not justified.1116's old32ms admission block was model scope,not OS/session
  exhaustion;independent work and separately qualified actual extension followed.

Reusable DLL:
`build/three_film_extended_20261118_three_film_extended_actual1124/libReGripThreeFilmRecovery.so`
SHA256 `9767481765017b112b4789afabdda3412cd556ec7b775a92b8b9cec754d4ba5c`.
Latest actual state:
`results/autonomous_film_20261118_three_film_recovery_chain1127_plan7/three.checkpoint_280.txt`.
Raw/manifests and earlier FAILs remain immutable. Actual30ms/32ms legacy caps
remain;only separate Extended Owner admits this qualified31.6..38ms window.
New sources currently based on77706b;see next feature Git commit for live code.

Next: profile/validate value-only geometry queries (do NOT alter mechanical
Force/Hessian),then choose a qualified longer-time or structural study from
actual shape response. Do not blindly extend beyond38ms or call zero tension
recovery. Full contact time/mesh/energy,friction,thickness,self-collision,
mechanical equalizer,wrapping/hold/lift/12-wrench/Optuna remain NOT CERTIFIED.
Exact replay command (unique TAG,foreground,not automatic restart):
```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/film_three_film_v5_resume.py --tag UNIQUE_TAG --parent 20261118_three_film_extended_actual1124 --step 220 --steps 4 --compare
```

Older entries below are historical,not current RUNNING processes.

## CURRENT verified — deformed release1079 and exact FREE resume1082

Actual1079 independently matches q/v EXACT at original1e-12 API; applied
normal forces nonnegative,whole-stage gap>=1.42109e-13mm,momentum3.55122e-19Ns,
outgoing normal velocity>=.00631256mm/s. Separate20us acceleration
complementarity plus remaining free-midpoint variant;old failed Lobatto
horizons remain FAIL. RK/free accumulated-clock join is EXACT after fixing
1076's reconstructed-clock mismatch9.02056e-17s. No force/velocity projection.

Actual1081 reaches27.6ms separated.1082 restores FREE V3:two subsequent
steps,q/v/stages/ForceField observations EXACT,two snapshots BYTE-IDENTICAL.
Whole quadratic midpoint numerical-path surface CCD rejects new impacts.
NOT an exact continuous nonlinear CCD/full time/mesh/energy/grasp certificate.
1083 is the next bounded24-step Unload-to30ms experiment;inspect its actual
process/summary before claiming completion. No background restart promised.
Reusable DLL:build/three_film_release_20261118_three_film_actual_clock_release1079/libReGripThreeFilmRelease.so
SHA25622add00153af4573a0e852c954af0514f444ca4d23c03a1d9f5136ab05e9cc51.
Full details:REGRIP_THREE_FINGER_GRASP_CONTINUATION.md. Older states below
are historical;full time FAIL,friction/self-contact/lift/optimization BLOCKED.


## CURRENT — typed Edge resume qualified; Unload stops at release

1059 actual Face->Edge event PASS;1060 four-step V2 resume EXACT including
byte-identical snapshots.1061 requested30ms FAILS after accepted27ms at
negative stage reaction (127.184s,not timeout).1062 independent signed
diagnostic reproduces +1.06418e-7N at27ms and -4.88759e-7N at27.05ms.
No negative reaction committed.1064 independent passive-observer regression
and query-purity PASS. Next is zero-reaction event and coupled release;
full time/energy/wrapping/lift remain UNQUALIFIED. Detailed1059–1061
evidence and reusable DLL are recorded below; earlier status is historical.


## Latest implementation — through1048,project INCOMPLETE

Persistent resume1014/1015/1016 strict1e-12 EXACT;actual C2 Hold reaches20ms
in1022. Actual Unload200us1024 and100us1033 FAIL:stage position drift and
new surface contact support.334-bit audits exclude a large geometry roundoff.
1042/1043 isolated117 Birth/shared6-row impulse kernel qualified;1044 ACTUAL
SOFA deformed124->117 support migration PASS,q/v/impulse/time EXACT,global
momentum/whole-stage clearance pass. This releases OLD ROWS,NOT the object.
1048 actual segmented work/impact inventory PASS consistency,not full energy.
1047 subsequent ordinary continuation FAILS at another event after23.6ms;
next actual development is generalized inactive-surface birth/retained-row
handling,not unchanged long-step retries.1041 time gate remains FAIL;full
Unload/object release/wrapping/holding/lift/friction/self-contact/full energy
remain unqualified. Detailed evidence/builds:REGRIP_THREE_FINGER_GRASP_CONTINUATION.md.
Lower RUNNING/checkpoint sections are historical,not current process claims.


## New persistent continuation checkpoint — through1017

Separate checkpoint/resume owner implemented;actual1014 four-step transfer,
1015 serialized retransfer and1016 through10ms match continuous1002 q/v/time
and all used stage rows EXACT under original strict1e-12. Field control,
geometry and stored energies exact in1014. No old REST counter spoofing.
1017 actual10→16ms Hold COMPLETE,scoped EXPERIMENTAL;not wrapping/lift.
1018 negative-test harness FAIL preserved;1019 read-only reassessment confirms
five invalid checkpoint guards reject before accepted commit.1020 partial
stage-work inventory PASS consistency;private legacy sampled-work is NOT
restored or joined. Overall time997 FAIL and deformed-release999 FAIL remain.
Full energy/root work/friction/self-contact/full-thickness/grasp unqualified.
Details,Raw/build and commands:REGRIP_THREE_FINGER_GRASP_CONTINUATION.md.
Next actual task:bounded Hold to20ms,then C2 Unload and genuine release analysis.
Lower checkpoint/RUNNING entries are historical,not current process assertions.


## Latest checkpoint through1011 — NOT project completion

See THREE_FILM_PEAK_AND_FIRST_ENERGY_20261118.md for actual versus independent
evidence. Actual1002 completes50x200us to FIRST C2 peak10ms;not wrapping/lift.
1006 catches an erroneous new-runner1e-11 API threshold and restores the
original STRICT1e-12. Old1002 PASS must not be used unqualified. Same-binary
clock counterfactual1008 identifies accumulated-versus-multiplied input time:
1009 matched-clock reassessment q/v EXACT,strict1e-12 PASS;old FAIL preserved.
1010 actual first-interval journal OFF/ON:eleven physical CSVs byte-identical.
1011 actual-stage first200us inventory residual-1.38829e-17Nmm,NOT heat/full
energy certificate. Root-reaction work still null.1005 observer-origin error
preserved;1007 uses existing T*(length-2L),not a new force or energy correction.
Overall time997 remains FAIL;generic release/friction/self-contact/mesh/full
energy/wrapping/lift/holding/12wrench/Grasp Optuna remain unqualified.
10ms is a diagnostic,not a complete adaptation cycle;1001 is a conditional
independent Rayleigh trial,not an actual mode or measured material result.
Lower RUNNING/next-task entries are historical,not current process claims.


## Latest implementation checkpoint — actual three-film event/continuation

See THREE_FILM_EVENT_20261118.md and THREE_FILM_POST_CONTACT_20261118.md.
960/964 actual separated three-film/ONE free sphere plastic event+remainder
COMPLETE;965 independent used-row/mapped/end-surface audit PASS,actual PNG/OBJ.
966 actual contact continues to1.6ms;reference q/v agreement5.42e-20/5.55e-16.
973 independent post-contact8/16/32 listed0.1% gate PASS,NOT actual/global time.
984 actual post-contact assessment FAIL:legacy sampled work,normal-work
residual relative error,and first changed-dt ForceField control mismatch.
Child-context NEXT-dt synchronization998 PASS,0 tension mismatch;no old
failure is overwritten.985 unique-branch IFT and992 flat-reference release
are independent mathematics only,NOT actual generic release or grasp.
Current models still lack full cycle/full energy/friction/self-contact/
full-thickness clearance/real equalizer/wrapping/lift/holding certification.
All lower next-task/RUNNING entries are historical,not current process claims.

Latest corrected actual assessment997 STILL FAIL:legacy sampled work
.7214203%,normal-work residual relative83.0143%(absolute4.41847e-24Nmm).
Actual motion/force/separate stored energy/stage-work subset passes0.1%;
first impact remains fixed,not whole-event refinement.999 deformed release
hypothesis FAIL:free acceleration remains inward,positive reactions required.
No fictitious release impulse or pose correction was applied.


## Latest continuation — actual stage work,through956 (2026-11-18)

See THREE_FILM_STAGE_WORK_20261118.md and immutable941/947/948/949/954/955/956.
Actual same-DLL16/32/64 already-touching10ms common C2 runs COMPLETE.
Stage-consistent component time gate PASS at0.1%;legacy sampled-work-inclusive
time gate STILL FAIL(16→64=.22975515%). No full-cycle/energy/grasp certification.
Read-only actual stage observer preserves nine physical CSVs byte-exact and
agrees with full AD work within2.71e-20Nmm. No force/state/tolerance changes.
Next active implementation:three-film separated birth/shared impulse and
remaining-step adapter,reusing existing single-film free midpoint and impulse.
Historical RUNNING/next-task sections below are not current process claims.
No OS exhaustion or automatic post-session continuation is claimed.


## 2026-11-18 갱신

실제3필름/자유 구체 C210ms 구동과 폭 방향 변형 계측까지 진행했다.
현재 실제 시간 Gate930는 끝점 접촉력과 기존 샘플 기반 와이어 일에서
FAIL이며,감싸기·Lift·유지·해제 파지는 미검증이다. 필름 중앙 노드와 폭
평균 변형도 다르므로 단일 Tip Motion을 감싸기 성공으로 쓰지 않는다.
최종 구조 선정은 계속 보류한다. 제작 재료/액추에이터 실측값은 없다.


## Latest measured checkpoint — actual three-film refinement,through868

Actual three-film/ONE FREE Rigid3 repeated contact860/861/862 COMPLETE8/16/32
steps over100us,T0,constantFz=-.001N. Same DLL/public mass/kernel/physical XML.
Actual time867 passes0.1% for listed common-time observables,INCLUDING the
separate tiny rail energy:base8→quarter32 rail difference0.0101266755%.
Independent actual-state energy observers864–866 and whole-stage/actual-field
kinematic audit868 PASS;energy residuals remain diagnostics,NOT heat/full energy.

Earlier independent4/8/16 time855 remains FAIL:rails0.1442388%,absolute error
3.84917e-37Nmm against2.66861e-34Nmm. No tiny-energy exemption. Frozen symmetric
modal856/858 reproduces≈fourth-order trend without events(order3.88 versus3.91),
supporting time-discretization,not event-timing,for THIS constant-load coupon.
The measured/profiler-justified32-step confirmation857 and independent859 pass
8/16/32,not retroactively4/8/16. Runtimes actual32.37/70.68/127.00s<480s each.

STILL NOT RUN/QUALIFIED:actual3finger C2 closing/impact/lift/holding/release,
shared tendon equalizer,mesh/history,generic friction/self-contact/full energy,
12wrench/multimaterial/Grasp Optuna. Current contact remains midsurface-buffer
research,not full physical skin/rail thickness clearance or final fabrication.
Next:measure actual3finger cost before extending duration/control;then preserve
strict gates while integrating actuation/event/release. No OS/session exhaustion
has been observed. Details/build/reproduction:REGRIP_THREE_FILM_CONTACT_RESEARCH.md.
The older checkpoint sections below are historical,not current RUNNING claims.


## Latest actual checkpoint — three-film shared FREE body,through851

ThreeFilmPersistentODE is now IMPLEMENTED and actually executed843/844/846/848,
not three unrelated fixed coupons. Narrow REST/T0/Fz=-.001N/100us IVP only:
three actual FilmRailTendon fields,three public film masses,ONE public FREE
Rigid3 mass/inertia,shared1953-DOF solve,proper frame pullbacks and once-only
mapped commit. Actual848 versus independent842:q<=2.83e-20mm,v<=3.48e-19mm/s.
Independent used-row/whole-stage/actual-field audit851 PASS;scale1 actual PNG/OBJ
are in that campaign. Body commit observer850 preserves nine physical CSVs.
R30.01 runtime Data policy checked;unsupported8.01 trial847 is a preserved FAIL
(configuration rejection,NOT OS exhaustion or a failed Newton solve).

Earlier three-row ambiguity was NOT established as real multiple contact:
840 Decimal80/120 resolves double0/0 into-4.24e-18/+9.75e-19mm. Value-only
113/334-bit order841 PASS;opt-in selector842 resolves this precise fixture
WITHOUT changing gap/force/Hessian/tolerances. Exact unresolved independent
supports still reject. Original836/838/839 failures remain preserved.

Actual3finger CLOSING/IMPACT/LIFT/GRASP remains NOT RUN. This is not a shared
actuator/equalizer,self-contact/friction,3finger time/mesh or full energy PASS.
R8.01/R30.01 buffer is a declared MIDSURFACE model,not full shell-thickness
clearance. Root-centre50mm is not a certified50mm outer palm. Final design and
Optuna remain BLOCKED. Exact build,commands,next priorities and scope:
REGRIP_THREE_FILM_CONTACT_RESEARCH.md. Older sections are historical context.


## Newest measured checkpoint — actual combined 1ms, campaigns821–831

Actual SOFA coupled birth+impact+Lobatto128/256/512 steps COMPLETE;all-pair
0.1% time gate829 PASS for THIS saved-state1ms IVP only. Base-quarter velocity
0.0359818%,common-window normal force0.0280782% (see829 for exact pairs),
attachment energy0.000116237%. Independent FEM versus actual states824/830
are exact;whole endpoint/stage and actual-field audits PASS. Actual frame
exports825 use saved states,scale1. Partial energy inventory826 is NOT full
energy certification. New build821 and complete commands are documented in
REGRIP_COMBINED_CONTACT_CONTINUATION.md. Earlier failure records unchanged.

Three-finger nonlinear work is EXPERIMENTAL:two-row math833 PASS,three-film
small1us835 limited PASS,but100us836 FAIL(feature transition),rescan838
FAIL(independent ambiguous supports). Three-row branch is insufficient for
this case;do not remove the guard or call this actual3finger grasp. Further
accepted-state ownership/multicontact work is required. No final structure,
full cycle,mesh,friction,self-collision,lift,12wrench or Grasp Optuna PASS.
The following older checkpoint sections are preserved HISTORICAL context.


## Latest measured continuation through820 — supersedes older NEXT/RUNNING claims

Combined event + persistent Lobatto owner is now IMPLEMENTED in actual SOFA.
Actual125us C2 PRE-state coupons811/812/813,all-pair time817 PASS at unchanged
0.1%;independent actual force/state/stage audit818 and whole accepted triangle
normal-velocity audit819 PASS. Independent1ms128/256/512 motion820 PASS only;
actual1ms/force/energy convergence remains NOT RUN,not inferred from FEM.
SparseLU is opt-in;actual parsed Data and passive observer810 PASS. Paired
125us dense/sparse802 gives1.54094x,not a statistical/long-duration benchmark.
Old strict reference782 FAIL is preserved;independently accumulated clocks796
resolve its finite-precision C2 clock mismatch without relaxing tolerances.
3finger804/809 is geometry/shared-impulse mathematics ONLY,not SOFA grasp.
R8 straight-mount negative control intersects fingers;final design NOT selected.
Full cycle,mesh,global CCD,multirow/release,friction,self-contact,lift,12wrench,
whole energy and Optuna remain unqualified. No measured material claims.
Details/build/raw/reproduction:REGRIP_COMBINED_CONTACT_CONTINUATION.md.
Next actual work:profile-bounded1ms SOFA from the SAME PRE-state,then common-time
force/energy audits;do not repeat completed125us runs or reimplement birth.
No OS/session resource exhaustion or automatic restart is claimed here.


## 최신 판정 — persistent coupon757 PASS,최종 선정은 보류

실제 SOFA의 제한된39.0625μs 지속접촉 시간 수렴 PASS를 전체 파지 성능으로
사용하지 않는다. 충돌 시각 재적분과 고차 지속접촉을 동일 경로로 결합하고
구동·유지·해제·복원 전체,마찰·자가 충돌·3핑거 자유 물체를 검증해야 한다.
Film/Rails/공통 와이어 제작 후보는 유지하되 물성·액추에이터·제작 일정은
실측/주최 측 확인 전까지 연구용 가정 또는 목표다.

## 최신 판정 — through721,선정 보류 유지

충돌 시각 재적분의 제한된 실제 SOFA 검증715/719 PASS와 전체 파지 인증은
다르다. 시간 시험705 속도·접촉력 FAIL,전체 에너지·마찰·자가 충돌·3핑거
자유 물체 파지·12방향 외란 시험이 남아 있다. 독립 고차 적분 비교721은
실제 구조 성능이 아니다. 제작 후보 Film/Rails/공통 와이어는 유지하되,
실측 PET/TPU/액추에이터 성능이나5일 제작 성공을 확정하지 않는다.

## 2026-11-17 최신 갱신

Custom coupled free-sphere의 실제 충돌·accepted-state 접촉을 구현했으나
전체 C2 시간·에너지·마찰·자가 충돌·3핑거 파지 Gate는 미완료다.
640의1ms 무장력 충돌 시간 수렴 PASS를 최종 파지 성능으로 사용하지 않는다.
선택적 midpointContact는 실험 버전이며 기존 endpoint 모델을 대체하지 않는다.
5일 제작 후보 및 액추에이터/필름 물성 미확정 상태는 그대로다.

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
## Latest verified continuation — 1059/1060; Unload1061 FAIL (2026-11-18)

Actual SOFA1059 implements bounded deformed Face->Edge transition at
23.67137720356692ms, preserving velocity without an impulse or projection.
Independent q/v/time match EXACT; whole-stage gap >= -7.21201e-13mm.
New material-edge owner stores ordered nodes [77,73], source triangle117,
birth time, exact normal/parameter and accumulated clock in REGRIP_EDGE_V2.
Actual1060 restores the V2 state in a separate Edge Owner: four subsequent
steps, all36 stage rows and ForceField observations match EXACT (legacy
sampled-work excluded with a declared new origin); four checkpoints are
byte-identical. Original strict1e-12 API gate retained.

1061 attempts 59 steps from24.1ms to30ms. FAIL after29 individually accepted
steps, latest checkpoint170 at~27ms: next bilateral stage reaction is negative.
Runtime127.184s, exit-6, NOT timeout/resource exhaustion. Unilateral guard
correctly refuses the trial; no negative reaction is committed. This is not
completed Unload, object release, wrapping, holding or lift. Existing1041
time FAIL and whole-energy/friction/self-collision/mesh BLOCKED remain.
Next: locate zero-reaction event using signed diagnostics only, remove
released material-edge rows, re-solve coupled dynamics and recheck ALL triangles.
Do not simply continue with negative force or reset velocity.

Reusable DLL:
`build/three_film_primitive_20261118_three_film_primitive_actual1059/libReGripThreeFilmPrimitive.so`
SHA256 `52d558a749f2a5288a51ab9b522b1cc128cd9b804eb1300ce62705d1310fc637`.
Raw: `results/autonomous_film_20261118_three_film_primitive_actual1059/`,
`...three_film_edge_resume1060/`, `...three_film_edge_unload1061/`.
Sources at0fa09fb plus archived feature-development source snapshots.
No completed grasp or automatic background restart is claimed.
