## New precise-tendon actual200us common-output state/shape PASS —2026-11-19

1717 actual new Field API PASS.1718/1719/1720 actual SAME binary
4f860ce0a79ad7f65a26eb11e4ddc2c337e5903c1b04753cf936e5f2517048d5
run8/16/32 PUBLIC steps,each with8 private Gauss4 microsteps. ALL256/512/1024
actual stages match independent same-law reference within STRICT1e-12.
1721 checks ALL common public output clocks,not only endpoint:PASS0.1%,
worst0.0201771235% Skin mid total curvature at12.5us,absolute8.22130e-51/mm.
NO absolute floor;actual clock interpolation distances<=1.35525e-19s are
recorded,raw clocks/states unchanged. Between-output continuum accuracy,
1ms/all-cycle time,mesh/contact/energy/grasp are NOT certified by this test.
Old Attachment-only all-time1708/1710 FAIL194.297% remains preserved.

1722 offline actual-stage observer PASS:all recomputed physical forces EXACT,
Field stored/kinetic energies within~1e-31Nmm. Tendon/damping/stored/kinetic
endpoint energy all-pair errors PASS0.1%. Signed partial residual still FAILS
relative200%,absolute9.86076e-32Nmm;NO heat reclassification,root workNULL.
Field Legacy Sampled Work/rounded cable length are NOT full work certification.
1723 actual material-displacement PNG/CSV produced,NO displacement scaling or
concept pose. Skin displacement is still microscopic;NO wrapping/holding/lift.

Reused actual build:`build/precise_startup_20261119_precise_tendon_actual1718/`.
Exact fresh reproduction (unique tag mandatory):
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/film_precise_startup_sofa.py --tag UNIQUE_TENDON --precise-tendon --steps 8 --reuse-build 20261119_precise_tendon_actual1718`

This NEW free single-coupon formulation must NOT be spliced into old three-film
checkpoint1644 at56.4ms. Existing free-body/contact/three-finger SDK,Raw and
checkpoints are preserved. Final design/holding/lift/friction/12-wrench/Optuna
remain unqualified or BLOCKED. Latest functional commit before this entry:b234bab.
1724 SAME new tendon1ms at1e-24Ns FAILS line search,last accepted0.85ms;
80/160-step cases NOT RUN. The value fix is NOT the sole late Newton remedy.
1725 separately tests1e-22Ns (still stricter than historical1e-18),and1ms
40/80/160 ENDPOINT state/shape comparisons PASS,worst0.00000544569%.
This is NOT all-time or actual SOFA certification. Old24-setting FAILs remain.
All owned physics children for these completed campaigns have recorded exits;
no background restart or continued work after the session is promised.

Next priority:combine the qualified early24-setting localized refinement with
a separately validated later-window solver plan,then reassess ALL common times,
stage work and contact before changing the old three-finger production model.
Do not rerun the old25us/1ms failed configurations unchanged. Existing executable
candidate (fresh tag) for independent numerical-study continuation:

`/home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/film_precise_transmission_window.py --tag UNIQUE_PRECISE_WINDOW --provider 20261119_precise_tendon_gauss1715 --newton-tol 1e-22`

This command reproduces1725;it is NOT new research by itself. New localized
method implementation is required before a longer certified actual run.


## Historical all-output FAIL;new tendon-value candidate isolated —2026-11-19

IMPORTANT:1691/1706 PASS is ENDPOINT q/v/shape all-pairs ONLY.1708 checks
all common physical outputs in200us and FAILS;1710 checks1ms using explicit
fine-state time interpolation and FAILS. Worst50us right-mid Rail curvature:
relative194.297%,absolute1.098643e-30/mm. No absolute floor.1709 clock
alignment analysis was incomplete;its failure is preserved. Actual raw clocks
were not overwritten. Whole Time/Energy/Contact/Grasp certification remainsFAIL/BLOCKED.

1700 independent1ms40/80/160 endpoint test PASS at1e-22Ns;1702/1703/1704
actual SOFA same binary87112e71b1578ec14cf820753642ab7428d8d608587094878ba04a1b5b987073
match same-law numerical reference STRICT1e-12.1701 factory registration
failure preserved. All160/320/640 real stages recorded,not legacy two-stage
placeholders. These real free-coupon results are NOT new three-finger recovery
or contact/wrapping/lift. Old three-finger checkpoint remains1644 at56.4ms.

1707 builds NEW-model rest Jacobian and verifies balanced continuous linear
flow1-vs4 at1e-8. Direct Skin tension gradient and instantaneous acceleration
sensitivity0;Rail gradient norm9.34631774. Actual Skin tip at1ms-1.31998e-8mm,
Rail tip-1.03773e-5mm,Skin curvature5.27490e-10/mm. Linear/nonlinear state
relative differences are measured,not automatically solver errors or wrapping.

1712 isolates tendon force VALUE quantization,FAIL. Separate
models/film_precise_tendon algebraically telescopes constant-tension linear
terms before AD assembly;NO force/stiffness/state correction.1713 tiny-value
and1714 original FD/Hessian/objectivity/balance gates PASS.1715 stage FD/query
purity PASS.1716 independent25us8/16/32 refinement PASS,worst0.0111928%;old
Attachment-only1711 FAIL22.3772%. New tendon actual SOFA NOT RUN yet.
All previous models and failures remain immutable;no final design selected.


## Historical endpoint-only actual precise-startup PASS;NOT all-time PASS —2026-11-19

1694 offline observer reproduces every actual stage force EXACT and Field
energies within~1e-31Nmm. All tested tendon/damping/stored/kinetic energy
all-pair differences PASS0.1%,but signed partial-defect relative error FAIL200%
(absolute9.86076e-32Nmm).1697 decimal100 reduction demonstrates summation
sensitivity but cannot recover binary64 input precision;FAIL preserved,NO heat
reclassification and root work remainsNULL.1693 missing<iostream> compile
failure and1695 plot-key failure preserved;1696 actual displacement PNG/CSV
completed. No concept deformation or displacement amplification was used.

1698 1ms extension at1e-24Ns Newton setting FAILS line search after37accepted
microsteps (last recorded0.925ms);80/160steps NOT RUN. This is algorithmic
failure,NOT OS exhaustion.1699 separately tests1e-22Ns (still stricter than
historical1e-18),200us state/shape all-pairs PASS0.07672095%. Its old scope
literal says1ms incorrectly;SCOPE_CORRECTION.json explicitly limits it to
recorded200us without editing old summary.1700 is a separate1ms candidate,
never a replacement PASS for1698. Physical0.1% gate remains unchanged.


1688/1689/1690 SAME actual SOFA binary595d2e39eac51d545082cbc14b2919304e86d6bca1cd7af9af0836ac1741b04b,
200us with8/16/32steps,all32/64/128 physical stages journaled. Each run matches
its independent same-law reference within STRICT1e-12.1691 actual all-pair
state/shape time assessment PASS0.1%;worst0.060082213% centre-mid Skin
value,absolute5.72146e-35mm;NO absolute floor. This is a very short free-coupon
startup,NOT whole-time/contact/energy/wrapping/holding/lift certification.

1686 compile succeeded but runner scene path was wrong;actual SOFA NOT RUN.
Failure preserved.1687 corrected runner reused the identical compiled sources,
then1688 rebuilt the independently qualified8/16/32 bound. No SDK edits.
1692 observer setup failed before compilation because its diagnostics folder
was absent;failure preserved.1693 offline stage-power audit is separate.

Reusable actual startup build:
`build/precise_startup_20261119_precise_startup_base1688/`.
Reproduce fresh (unique tag mandatory):
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/film_precise_startup_sofa.py --tag UNIQUE_STARTUP --steps 8 --reuse-build 20261119_precise_startup_base1688`

Actual three-finger recovery checkpoint remains1644 at56.4ms;new attachment
startup must NOT be spliced into that old-model checkpoint. Original rail-aspect
10ms time FAIL and full contact/friction/energy FAIL/BLOCKED remain preserved.
No final design selection or automatic background execution is claimed.


## Attachment value precision isolated;independent regression PASS —2026-11-19

1684 same-new-nonlinear-model8/16/32 refinement PASS all tested q/v/shape
with0.1% gate,no absolute floor;worst0.0600822% Skin centre-mid displacement.
1685 actual SOFA Force/dForce/matrix/FD/query-purity PASS. Energy/work and
full-cycle time remain NOT ASSESSED/FAIL;these results do not certify grasp.
That preliminary verification was completed by1687..1691;see newer section above.


Campaign1678 isolates a constitutive VALUE defect without any time solver:
for uniform Rail dz=1e-18mm,legacy Skin force is0 while the analytic5*k*dz
is5e-21N and the AD derivative remains.005N/mm. Rigid translation also
creates a spurious tiny force. Original absolute FD/Golden results remain valid
within their tested scope;1678 remains FAIL.

Separate models/film_precise_attachment uses displacement differences and a
reference-exact flat attachment potential,including a rationalized normal
increment. NO stiffness/material/accepted-state correction or epsilon normal.
Shell and routed tendon remain historical.1679 constitutive tiny-value tests
PASS through1e-30mm.1680 original regression PASS:forceFD1.010812e-11N,
HessianFD2.178568e-10N/mm,baseline E/F/H6.505213e-18,
rigid-objectivity1.082867e-11,with unchanged original gates.
This is NOT yet actual SOFA integration,time convergence or grasp PASS.

Gauss4 independent kernel1668/1672 passes stage FD and query purity, but
1671 nonlinear8/16/32 time comparison FAIL. Tightening Newton tolerance
alone does not fix it:1677 at1e-22Ns still FAIL. The separate precision
variant is now being tested before any production replacement. Frozen linear
reference1666 is not exact nonlinear truth for extremely small remote fields.

Latest actual qualified recovery remains56.4ms,checkpoint378 under1637
provider (1644 actual run). No wrapping,holding,lift,full recovery,friction,
whole-energy or final design certification. No automatic background restart.
See immutable results/autonomous_film_20261119_attachment_precise1679/,
results/autonomous_film_20261119_attachment_math1680/ and prior1648 chain audit.

## C2 indirect-transmission startup defect isolated;full time FAIL retained —2026-11-19

1659/1660 actual100/50us free-coupon10ms trials PASS strict API against
independent same-stage references using SAME1654 SOFA binary. This is NOT
time convergence.1662 all-pair assessment at recorded physical clocks FAILS
for all rail designs;no absolute floor. Worst Skin tip at200us:relative187.44%,
absolute3.28049e-13mm. Legacy sampled work max9.54%,stage work max12.66%
also FAIL. Interpolation distances at most3.12250e-17s are recorded;no row-index
or time overwrite. Endpoint-only design differences are NOT certified superiority.

1663 independent100-digit two-DOF cubic-load counterexample:
Rail q leading exacth5/20,Gauss2h5/18;indirect Skin exacth7/840,
Gauss2−h7/864 (opposite sign,ratio−35/36). Direct high-precision linear stages
have NO Newton threshold. Gauss3 still has5% Skin leading coefficient error;
Gauss4 reproduces this leading coefficient. This is NOT a full FEM certificate.

1664 frozen-FEM exponential reference fails its split gate and is preserved.
1665 balances the augmentation clock and inverse forcing together (exact
coordinate change,NO physical/tolerance change).1666 additionally checks ALL
reported shape observables under1-vs4 flow segmentation at1e-8 relative;PASS.
Atfirst200us actual nonlinear Skin displacement vs direct LINEAR Gauss differs
2.87428e-9 relative,but both differ from continuous frozen reference by~133.964%.
This independently isolates a Gauss temporal/stage error at startup;Newton
and nonlinear physics are not the dominant difference at this particular step.
It does NOT explain every later/contact/global time failure.
1667 compares order/subdivision remedies on this SAME frozen FEM before
nonlinear/SOFA adoption. No damping/stiffness/T tuning or design selection.

## Actual56.4ms recovery and physical rail-aspect SOFA candidates —2026-11-19

Latest committed functional checkpoint c65aa0ae5b1693c418947f4fa7e6b90f5ecaa690;
new rail-aspect work uses that commit plus complete archived source hashes.
Actual typed stationary Gauss chain1637→1639→1641→1643→1644 completes
128nominal50us steps from50ms to.05639999999999999s.
1648 audits byte-exact typed links,q/v checkpoint identity,ALL stage clocks/
weights and same-binary ownership. Each actual segment q/v/stages EXACT versus
its independent nominal-dt reference. End numerical-path gap bound+.284651749mm.
Relative final film q/v versus the aligned independent1634 reference:
8.64314e-15/2.61633e-12;clock difference1.66533e-16s is recorded,NOT bit identity.
Latest checkpoint:
results/autonomous_film_20261119_stationary_gauss_to564_1644/three.checkpoint_378.txt.
Reuse1637 DLL SHA f4dec6d84184b24c71736e0c85ea3d94b6944a32f11bf9fd05aaa049a9392cec.
Its56.4ms domain guard is intentional;do NOT edit header/time/step or claim
unqualified continuation beyond that domain.

Actual56.4ms1645/1646:Skin mean tip−.389086840mm,centre−.540641173mm,
maximum discrete centreline curvature.00457220/mm;rails tips−.328249699/
−.341392343mm. Skin75vz−3.72106mm/s,Rail75vz+7.19295mm/s.
Skin Attachment power+.00129377,Rail−.000800778Nmm/s while tension0.
This is internal delayed energy exchange,NOT wrapped/fully recovered/holding.
1648 partial inventory:U.0002136677141,K.0001271362864,Damping3.525975879e-6,
signed defect5.874239897e-14Nmm;root workNULL,NOT heat/whole Energy PASS.
1645 scale1 PNG/OBJ and1648 actual energy plot use saved SOFA states.

Physical rail-aspect model1649/1654 preserves core439.339791775mm³/three,
skin/material/mass/T/root/bond/route;only rail thickness75/100/125um varies,
with width adjusted at fixed cross-sectional area. Assumed1g/finger is independent
of core material density,NOT measured PET/TPU. No final design selected.
Independent nonlinear1652 and ACTUAL10ms1658 reproduce a trade-off:
75um gives about13% higher Skin curvature but42% greater stage tendon work;
125um bends less and uses less work. SAME tension,NOT matched actuation work.
1654 actual Force/dForce/matrix/FD/query-purity PASS for all3;1657 actual profile
and1658 peak states/stages/Field energies pass strict API comparisons.
This is a FREE NO-OBJECT coupon,NOT coupled contact/wrapping/grasp.
Build:build/film_rail_aspect_20261119_rail_aspect_api1654/libReGripFilmRailAspect.so
SHA d5fa365f88cc8cc563981a5207ca4dc850f2ac05e2ce68bec78f1da1c56f3126.
1653 missing relative header,1655 missing mass topology,1656 missing mass
geometryState initialization failures remain preserved;they are NOT Newton
convergence failures. Corrected Scene retains static NEW-design mass-reference
geometry and removes the inapplicable old world mapping. Actual deformed
geometry is Field x=rest+u;1661 reconstructs it to7.06211e-15mm,scale1.

Next actual all-pair assessment includes every recorded time,legacy sampled
work AND stage-consistent work;keep0.1% gate and all previous failures.
Run:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/film_rail_aspect_time.py --tag UNIQUE_TIME_ASSESSMENT`
Grasp/lift/friction/selfcollision/full thickness/global energy/mesh/Optuna
remain NOT RUN or BLOCKED as previously recorded. No automatic background service.

## Fine-window core time PASS;typed actual Gauss resume PASS —2026-11-19

1632 independent50/25/12.5us1.6ms core state/energy/shape/work pairs PASS;
maximum.06733945%.1634 completes50→56.4ms in322.679s (forecast440.126<480).
All core pairs at eight common epochs PASS;maximum film velocity.07671273%.
Signed partial-defect relative time STILL FAIL:maximum99.6681%,absolute
5.10659e-14Nmm at that pair. This is NOT heat or whole Energy/Time PASS.
1638 plots these INDEPENDENT trajectories,not actual SOFA long-window states.

1636 actual four-step continuation worked,but suffix init FAILED at the old
FREE footer50ms guard. Original parser/guard is unchanged. A separate bounded
Gauss typed footer is added;1640 roundtrip+seven invalid fixtures PASS,including
explicit old-reader rejection above50ms.
1637 actual4 vs2+2 PASS:all q/v differences0,all Gauss stage forces/states EXACT,
accepted rows EXACT,final checkpoint BYTES EXACT. Legacy sampled-work history
is NOT resumed;do not splice its cumulative values.
Build:build/stationary_gauss_resume_20261119_stationary_gauss_resume1637/
libReGripStationaryGaussContinuation.so
SHA256 f4dec6d84184b24c71736e0c85ea3d94b6944a32f11bf9fd05aaa049a9392cec.
Identity6a4d1d2dc924d02bdf50c7f7ab1889be53ce28f518e98d2b26f375df5eff5b48.
Actual1639 extends to.05179999999999986s,32steps50us:independentq/v/stages/
accumulated clocks EXACT,actual tension0,minimum numerical-path gap+.325142mm.
Latest qualified typed Gauss checkpoint:
results/autonomous_film_20261119_stationary_gauss_to518_1639/three.checkpoint_286.txt.
Old50ms midpoint FREE seed is preserved;never mix the schemas or edit dt tokens.
Source commit at execution4ed7083 plus complete archived compiled source hashes.

1633 contact-phase26.8ms actual wire CENTRELINE gap+.455272mm;length agrees
with actual Field to5.68434e-14mm. Finite radius/guide solids/selfcollision NOT RUN.
No actual wrapping,holding,lift,full recovery or final design selection.
Next bounded actual segment targets53.4ms using the SAME qualified binary.
Reproduce (new unique tag):
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/film_stationary_gauss_window.py --tag UNIQUE --provider 20261119_stationary_gauss_resume1637 --parent 20261119_stationary_gauss_to518_1639 --checkpoint-step 286 --steps 32`
Resume owner supports only separated zero-load/no-spin fixture;new contact rejects.
Actual work/geometry/friction/selfcollision/mesh/global energy gates remain separate.

## Cumulative recovery FAIL and exact parallel scheduling PASS —2026-11-19

Actual stationary wire-driven cycle remains qualified only to50ms;isolated
Gauss actual pilot reaches50.8ms. No wrapping/holding/lift or full recovery PASS.
1619 baseline cumulative window fails Newton line search.1620 passive trace
locates residual stagnation near1e-18 despite linear residual near1e-33.
1621/1622/1623 isolate temporal summation alternatives,without changing tolerance,
AD/material/damping.1626 both-sums candidate passes existing directional FD.
1624 both-sums800/400/200us completes50→56.4ms but film velocity differs up to
.365871%;1629 at200/100/50us still fails .104112% and .101918% pairs.
Signed partial-defect relative time also FAILS;absolute defect is NOT heat.
1624/1625 helper_sha256 was taken after execution while helper was edited;
their archived generated C++/compiled model hashes remain authoritative.
1629 snapshots and hashes the helper BEFORE compilation.

1630 independent separated Gauss scheduling is EXACT.1631 actual SOFA six
alternating1/3-worker runs use ONE binary,immutable numerical snapshots and
serial observer/reduction. Physical CSVs and full checkpoint bytes EXACT,
also actual q/v/stage-force/clearance CSVs EXACT versus qualified1618.
Median process wall1.67018→1.16878s (ratio.699791);inclusive kernel
.979441→.471747s (ratio.481650).Do not add nested timings or combine unrelated
optimization percentages. This is NOT contact parallelism or time certification.
Build:build/stationary_gauss_parallel_20261119_stationary_parallel_actual1631/
libReGripStationaryGaussParallelPilot.so
SHA256 db160df7472247f5a29d2b77c59f54a9eeba1866f505ff0fdc813e254f189ebc.
Its output is a distinct isolated pilot schema,NOT a qualified reusable resume.

1627 actual49.4→50ms wire-segment screen agrees with ForceField length to
2.84217e-14mm;minimum wire-centreline R30 sphere gap+.464539mm.
Wire radius and guide solids NULL;self-collision/continuous wire clearance NOT RUN.
1628 REST-basis projection supports investigating high-frequency velocity phase
error,but is NOT a modal causal proof for nonlinear recovery.

Reusable seed remains results/autonomous_film_20261119_stationary_free_to50_chain1596_part12/three.checkpoint_250.txt.
Next:bounded fine-window refinement using exact parallel kernel;keep ALL prior
time failures and whole-energy/root-work/friction/self-collision gates.
Reproduce scheduling with:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/film_stationary_gauss_parallel_sofa.py --tag UNIQUE_ACTUAL_PARALLEL`
No background continuation service is running or promised.

## Stationary wire-driven cycle to50ms;actual Gauss pilot50.2ms —2026-11-19

Latest verified functional commit da3988ad6c462d11659c33fd85ab0e4ba6f0a116.
1616 extended800us state/energy pairs PASS;1617 film/curvature all-pairs PASS,
maximum relative.09115055%.1618 ACTUAL explicit200→800us one-step transition
PASS:restored physical q/v/quaternion unchanged,11 clocks verified;accepted
q/v and ALL Gauss film stage forces/states EXACT against independent nominal
800us reference. End .050799999999999811s,gap lower bound+.289799852mm,
momentum6.39628e−23Ns. Original checkpoint dt/time/step tokens are NOT edited.
Build `build/stationary_gauss_20261119_stationary_gauss800_actual1618/libReGripStationaryGaussPilot.so`,
SHAc015160274aad8017e2d93cf23050f3a3a2251259c572cf0a4f9a50f2ac016eb.
Pilot output step251 is NOT interchangeable with1614 step251:distinct schema,
dt and absolute time. No pilot resume reader is qualified. Reusable seed remains
stationary FREE50ms step250.1619 tests cumulative50→56.4ms at common800us
epochs,including damping work and signed partial defect;inspect completed
summary before approving any longer window. Full trajectory/energy/grasp NOT PASS.

Prior functional commit c803a7556ee8b7461937cd4ae5cd89aab66038cb
(previous181229f strict deformed release/unload).1596 FOREGROUND chain completed:
all13 segments to .049999999999999808s PASS,not a continuing background service.
Every segment checks actual q/v,midpoint stages,C2 tension,physical clock and
checkpoint identity.1591 suffix replay remains EXACT. No incoming-body splice.

Latest REUSABLE stationary FREE checkpoint:
`results/autonomous_film_20261119_stationary_free_to50_chain1596_part12/three.checkpoint_250.txt`.
Qualified FREE provider20261119_stationary_free_actual1590,
`build/lateral_free_20261119_stationary_free_actual1590/libReGripStationaryRelease.so`,
SHAea8283ac84dd0538e30177bc573f8bc4e6b2715b29f4afbd549093404d6b7e4e.
50ms Skin mean tip−.384746mm,centre tip−.584968mm,Rail tips−.228824/−.233135mm,
maximum film speed47.3383mm/s.1598/1599 show delayed Skin deformation,
NOT completed recovery/wrapping/holding/lift. Scene gravity/external force0.

1614 ACTUAL isolated Gauss-film/midpoint-body50→50.2ms pilot PASS:
q/v and ALL film Gauss q/v/force stages EXACT vs same-nominal-dt reference;
numerical-path gap lower bound+.318303mm,momentum residual6.06522e−23Ns.
Build `build/stationary_gauss_20261119_stationary_gauss_actual1614/libReGripStationaryGaussPilot.so`,
SHA5c71e3a999f81fa10d4362091441de467a76dd938ca1033972cb02058335ebae.
Output REGRIP_STATIONARY_GAUSS_PILOT_V1 is NOT a qualified resume schema.
Use the reusable50ms FREE seed for follow-up,not a silent pilot conversion.
1612 strict preflight rejection preserved:old refinement used endpoint-minus-clock,
1.2e−18s shorter than nominal200us;1614 SAME nominal-dt observer ON/OFF EXACT.

1597 actual release partial energy inventory PASS,not whole energy certification.
1602 frozen linear reference:actual projected mass EXACT;linear velocity time
error still exceeds.1%;nonlinear/contact differences are NOT isolated solver errors.
1603/1605 limited local1/2/4 midpoint observables PASS,1604/1607 extended32 FAIL:
sum of reduced residual norms2.53917e−17Ns>1e−17;clock/gap PASS,NOT OS exhaustion.
1608/1611 Gauss local1..32 state/energy/shape comparisons PASS;NOT global time.
1615 initial800us Gauss probe PASS;its old scope text incorrectly says200us:
span_us800 and endpoint50.8ms are authoritative.1616 extended800us is a new
trial;inspect completed summary before accepting any step expansion.
1610 force-only ASSEMBLY kernel is bit-exact,7.82% faster in that microbenchmark;
NOT integrated/end-to-end gain,original AD2 unchanged.1609 compile FAIL preserved.
1613 is a conditional energy scale,NOT actual gravity/lift or capacity evaluation.

Next:finish all-pair800us qualification before any dt-transition owner;retain
strict1e−12 API/.1% time/1% mesh-history gates. Independent exact assembly A/B
is available but not adopted yet. Whole energy,global time/mesh,friction,
self-collision,thickness,equalizer,holding/lift/12-wrench/Optuna remain unqualified.
No final structure selected. No OS/session exhaustion or automatic restart claimed.

## Historical checkpoint:stationary C2 unloading30ms —2026-11-19

1587 actual face release PASS;1590/1592/1594/1595 actual separated continuation
reaches .029999999999999929s with independent q/v,ALL midpoint stages and actual
Field tension EXACT.1591 suffix replay q/v/stages/full checkpoint tokens EXACT.
No incoming-body state/history is spliced. Public mass/root/quaternion/clock
and known last impact provenance remain checked.1595 gap+.007675162795734991mm.
Actual30ms Field tension is3.4217820030178116e−46N,NOT rounded to0:accumulated
clock lies just below exact .03s;subsequent stages use the original C2 law.
1595 maximum film speed25.93963933656778mm/s,so recovery NOT completed.
1593 limited64/128 local release-grid observables PASS;NOT global macro-dt,
ALL-pair,stored-energy/tendon-work or whole time/energy certification.

Latest verified checkpoint:
`results/autonomous_film_20261119_stationary_unload30_1595/three.checkpoint_150.txt`.
Qualified FREE build:
`build/lateral_free_20261119_stationary_free_actual1590/libReGripStationaryRelease.so`,
SHAea8283ac84dd0538e30177bc573f8bc4e6b2715b29f4afbd549093404d6b7e4e.
Reuse provider20261119_stationary_free_actual1590;schema REGRIP_STATIONARY_FREE_V1.
1596 is a FOREGROUND bounded30→50ms continuation plan;inspect its completed
summary/last checkpoint before using it. It checks every segment and stops on
FAIL/reimpact;no automatic background restart service exists.

Example independent next short continuation (use a UNIQUE new tag):
`$PY tools/film_lateral_free_sofa.py --tag UNIQUE --stationary --parent 20261119_stationary_unload30_1595 --checkpoint-step 150 --steps 2 --reuse-build 20261119_stationary_free_actual1590`.
Wrapping,holding,lift,friction,self-collision,full thickness,whole energy,
global time/mesh convergence,mechanical equalizer and final design remain
unqualified. Existing FAIL/Raw/SDK unchanged;no remote push.

## Historical checkpoint:actual stationary face release27ms —2026-11-19

1587 ACTUAL SOFA PASS:26.8→.026999999999999948s. Final q/v and ALL256
acceleration-RK q/v/force/time/weight/mask stages match independent1582 EXACT.
Gap−5.8690829973784275e−12mm,outgoing normal velocity+.012739307327679385mm/s,
summed reduced momentum bound8.066896214799044e−19Ns;no tensile force or reset.
This is a numerical release composition,NOT exact continuous exit-time certification.
1582 uses10us local window64 divisions,unchanged material/C2/200us macro step/gates.
40us32/64/128 failures1576/1577/1580 and10us32 failure1581 remain preserved.
1583/1584 compile failures,1586 initialization failure and1589 FREE stream duplicate
initialization failure remain preserved;none is a physics PASS.
1585 exact FREE provenance roundtrip and7 invalid fixtures PASS.
1590 tests the corrected inherited-stream FREE continuation;inspect its summary.

Latest verified actual release checkpoint:
`results/autonomous_film_20261119_stationary_release_actual1587/three.checkpoint_135.txt`.
Release build:
`build/stationary_release_20261119_stationary_release_actual1587/libReGripStationaryRelease.so`,
SHAbaf961e02d262aff4ad3ceebbefe0990f647899220733c5a3de010e7cc715504.
Schema REGRIP_STATIONARY_FREE_V1;last global impact22.623148278ms preserved.
Its initial FREE subclass has a journal-open defect fixed separately in1590;
reuse this binary for RELEASE only,not as a qualified FREE continuation.
No arbitrary q/v/time/quaternion change;only provenance identity token changes.

Actual26.8ms force/shape metrics1578/1579 show wire-driven contact but NOT wrapping:
Skin width-mean tip−.287573mm,centre tip−.091175mm,Rail tips≈−.383mm;
Rail distal arch and Skin width warp persist. Geometry image and OBJ are actual
scale1,not prescribed deformation. Contact area/pressure/holding load NULL.
Zero gravity/external load is NOT lift. Global time/mesh/energy,friction,
self-collision,thickness clearance,equalizer,holding/lift/Optuna remain unqualified.
Next:qualify typed FREE continuation and exact suffix replay,reach C2 unload30ms,
then analyse delayed Skin response/recovery and separately local time refinement.
No session/OS exhaustion or automatic restart is claimed.

## Historical checkpoint:stationary-origin C2 contact26.8ms —2026-11-19

Verified functional commit4fc720026cf1c521b97d158825ff3d8c20625878.
1565 independently resolves an additional EDGE115→FACE117 contact birth at
22.62314827800726ms (six independent impact rows);1566 ACTUAL SOFA matches
pre/post states,impulses,global recovered-impulse inventory and stage rows EXACT.
Recovered root impulse is NOT an independent SDK reaction/work measurement.
1567 verifies ALL common frozen physical sources during the support-owner handoff.
1569/1570/1571/1573 continue actual stationary-origin C2 contact to
.026799999999999949s.1573 q/v and ALL contact-stage rows EXACT;
minimum whole-stage gap−1.1691980716932449e−11mm,reduced momentum bound
9.765636736557555e−19Ns. These are not full time/mesh/energy/grasp gates.

Latest ACTUAL checkpoint:
`results/autonomous_film_20261119_stationary_to268_1573/three.checkpoint_134.txt`.
Reusable build:
`build/stationary_persistent_20261119_stationary_persistent1555/libReGripStationaryImpact.so`
SHA0ba20b83089d6a7f305e65c7d5227790a9b8cf4881ca3b29df68b41482cafb19.
Stationary initial q/v,external force0,gravity0;NEVER splice incoming-body cases.

1568 policy forecast542.7s BLOCKED before physics,NOT OS resource exhaustion.
1572 longer reference FAIL:positive-only contact cannot continue after reaction
changes sign;that longer ACTUAL horizon NOT RUN.
1574 archived fixture-anchor preflight failure preserved;1575 edge-only reference
rejects actual FACE116/6 ownership.1576 tests the SAME non-tensile release
equations using existing fixed-smooth owned face Gap/J/H pullback.
Do not infer release PASS until its completed summary and actual API comparison.
Next priority:qualify zero-load face release,then typed free continuation and
actual curvature/transmission metrics. Full wrapping/holding/lift,friction,
self-collision,thickness clearance,whole energy,time/mesh convergence,mechanical
equalizer and final design selection remain BLOCKED/NOT RUN as appropriate.
No automatic background restart is promised.

## Historical checkpoint:actual contact to22.6ms —2026-11-19

Last verified functional commit0b55c2d;prior9e5126f first wire-driven impact.
NEW stationary-origin IVP:initial sphere/films at rest,external force0,gravity0.
Same assumed material/masses/geometry/lateral6mm route/C2 input as documented.
1541 actual10ms strict API PASS after public-mass reference binding;1543
proves actual model/binary/physical CSV bytes unchanged from preserved1539FAIL.
1547 first-birth guard rejects its uncommitted20.2..20.4ms step.
1549 qualifies ONLY18 accepted prefix steps and isolated numerical birth.
1550 reference and1552 ACTUAL impact/remainder PASS:q/v/pre/post/impulse and
ALL contact-stage rows EXACT,event20.364869768894265ms,6rows/rank3.
Not globally earliest continuous CCD,area/pressure/holding/lift certification.

1555/1558/1561 actual persistent continuation reaches
.022599999999999974s. q/v/control/clocks and ALL contact-stage rows EXACT.
1560 suffix replay also reproduces full checkpoint tokens and stages exactly.
Latest completed STATIONARY contact checkpoint:
`results/autonomous_film_20261119_stationary_to226_1561/three.checkpoint_113.txt`.
Build `build/stationary_persistent_20261119_stationary_persistent1555/libReGripStationaryImpact.so`,
SHA0ba20b83089d6a7f305e65c7d5227790a9b8cf4881ca3b29df68b41482cafb19.
Schema REGRIP_STATIONARY_CONTACT_V1;NEVER splice incoming-object/free histories.

1559 longer reference FAIL:depth5 in22.6..22.8ms;that actual SOFA horizon
NOT RUN.1563 passive trace reproduces failure with accepted-prefix/state/force
rows EXACT and geometry requery error0;Edge115/3 and Face117/6 alternate.
This is algorithm depth budget,NOT OS exhaustion. No budget/tolerance increase.
1564 first transfer adapter FAIL retained because archived FACE extrapolation
is invalid for an old EDGE.1565 tests the corrected physical edge branch;
inspect its completed summary before deciding whether birth or smooth transfer.

Original incoming lateral IVP separately reaches30ms C2 unload (1534);
1544 suffix replay exact. Its initial velocity-1mm/s/Fz-.001N is NOT capture
from rest. Original/quadratic/free50ms histories remain separate.
Distributed joints1515 have mixed bending/warp/work results,NOT selected.
Legacy stationary render captions1542/1554 incorrectly said Fz-.001N;
1556/1557/1562 use actual Scene force0,geometry/OBJ unchanged.
Use corrected1562 actual scale1 image,not the erroneous legacy caption.

All whole Time0.1%/Mesh/Energy/friction/thickness/self-collision/Equalizer/
gravity lift/12-Wrench/Grasp Optuna gates remain FAIL/BLOCKED/NOT RUN.
First contact occurs AFTER the20ms Hold end;this motivates control-time-scale
study,not a claim that longer Hold guarantees wrapping. Final design deferred.
Details:REGRIP_TENDON_TRANSMISSION_AND_WRAPPING.md.
Next exact inspection command (do not duplicate a completed campaign):
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool results/autonomous_film_20261119_stationary_edge_face1565/summary.json`
Then qualify support-transition math/actual owner,not a larger depth budget.
Checkpoint writing does NOT end the ongoing research. Older text is historical.

## Historical actual lateral release / candidate comparison —2026-11-19

Latest completed actual lateral checkpoint is27.2ms,NOT wrapping/holding/lift:
`results/autonomous_film_20261119_lateral_release_actual1522/three.checkpoint_136.txt`.
1522 SOFA release PASS: q/v and512 RK force/state/time/weight/mask evaluations
EXACT to1518 independent reference; gap−1.55644e-11mm,
outgoing normal velocity+.02381532mm/s,segment momentum norm bound7.38836e-19Ns.
Runtime229.561s<480s. Build
`build/lateral_release_20261119_lateral_release_actual1522/libReGripLateralRelease.so`,
SHA bf6a7f2f534c5635398ea03e8db34fa0124c5369b2f763b9633324cbb93ba9db.
No exact continuous exit-root/whole time/energy/recovery claim.
1513/1517 release32/64 velocity FAIL preserved.
New typed FREE_V1 has explicitly UNMEASURED edge birth history;do not
feed it to quadratic FREE_V3 or invent history. FREE extension is separate
validation;1525 compile FAIL preserved. Inspect1526 summary/process before reuse.

Feature commits ce86695 passive stage/work observer and9082bb1 distributed
attachment candidate.1497 passive labels preserve prior physical CSV/tokens
exactly.1499 measured-micro work is PARTIAL,root workNULL.
1515 actual distributed-joint NO-OBJECT50ms coupon API/stages PASS:
mean tip bends more,centre tip bends less,tip warp increases;1520 work
decreases.1524 virtual sphere intersection−.0354186mm is NOT contact dynamics.
Candidate NOT selected;no superiority/area/pressure/holding inference.
Same core/material/route/input,not matched adhesive hardware or equal work.

Current evidence/detail/reproduction:
[REGRIP_TENDON_TRANSMISSION_AND_WRAPPING.md](REGRIP_TENDON_TRANSMISSION_AND_WRAPPING.md).
Existing full Time/Mesh/Energy,friction,self-collision,full-thickness clearance,
Mechanical Equalizer,gravity lift,12-Wrench and Grasp Optuna remain BLOCKED.
Older sections below are historical,not current running-process claims.

## Historical actual lateral contact continuation to24.4ms —2026-11-18

Feature commit0c1d40d:bounded contact-admissibility reintegration and
isolated six-row birth,independent references AND actual SOFA.
1469/1472 actual controlled prefix through23.4ms has ALL micro-stage
q/v/force/time EXACT to reference.1475/1476 nonquadratic test exposed a
positive active-stage gap omission;1477 STRONGER two-sided active-stage
check passes circle analytic and sine independently-refined RK references.
1480 actual stronger-guard replay PASS,without changing accepted old prefix.
These are NOT general error-controlled time integration or whole energy PASS.

1470/1473 longer reference FAIL is124→117 NEW CONTACT BIRTH,not object
release. Rejected signed forces were NEVER applied or committed.
1478 isolated reference and1481 ACTUAL SOFA event at
.023503224464179916s PASS:6rows,3retained,impact loss4.54963e-12Nmm,
momentum1.05928e-20Ns,global angular balance4.34163e-24Nmm*s.
Actual q/v/event time/impulses EXACT. This is an externally isolated
numerical branch,NOT global earliest continuous-trajectory CCD.
1483 actual post-impact and1485/1486 continued to.024399999999999963s:
ALL micro stages/absolute clocks exact,gap−3.90123e-11mm,
momentum1.02815e-18Ns. Existing1458/1459/1460/1470/1473 FAILs preserved.
Latest COMPLETE actual lateral state:
results/autonomous_film_20261118_lateral_post_birth_four_actual1486/three.checkpoint_122.txt
Build:build/lateral_controlled_20261118_lateral_post_birth_actual1483/libReGripThreeFilmResume.so
SHA22bf301e5f55a1d5d8210164b3563512876f9d46cd7eb8d0698c2373ccab2731.
SDK /home/ubuntu/SOFA/v26.06.00,unchanged runner/ABI. Binary reuse1486
requires EXACT ALL-model source identity to qualified1483,not relaxed parity.

1487 actual endpoint force inventory:at24.4ms,T6.11425e-5N/rail,
direct Skin tendon force0,Attachment Skin power+.00164815Nmm/s,
Rail power−.00230185Nmm/s;Skin75vz+9.46331,Rail75vz+18.78199mm/s
(positive local z is AWAY from object). Thus coupling transmits energy,
but the observed deformation is NOT certified wrapping.
Nodal force norms are NOT resultant grasp capacity.
Attachment net-force/moment residuals<3.87e-20N/3.18e-18Nmm;
actual Field cable length error0. Root work/contact area/pressure remainNULL.
Actual scale1 PNG/OBJ1484/1488. No invented wrap pose.
Current profiled FREE50ms candidate remains unselected:more work AND worse
75mm arch. Original,quadratic,lateral and profiled histories remain separate.

Next bounded reference1490 is a NEW24.4ms IVP;inspect completed summary
before any actual continuation. If PASS,reproduce with unique actual tag:
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/film_lateral_controlled_sofa.py --tag UNIQUE --reference 20261118_lateral_after244_four1490 --parent 20261118_lateral_post_birth_four_actual1486 --reuse-build 20261118_lateral_post_birth_actual1483
No wrapping/holding/gravity lift,full time/mesh/energy,friction,selfcollision,
full thickness,mechanical equalizer,12-Wrench or final Optuna certification.
No OS/RAM/disk exhaustion is claimed;no automatic background restart.

## Previous transmission comparison and contact limit —2026-11-18

Feature0337fe2 lateral resume/actual energy diagnosis;bcd2de7 separate
distributed-profile route and actual short regression. No remote push.
Actual lateral coupled Hold1440/1447 passes to19.6ms;1448/1450 and
1451/1457 pass Unload through22.799999999999973ms:q/v/clock/normal force
EXACT to same-IVP reference,Field energy differences<3e-19Nmm.
Latest FULLY qualified lateral checkpoint:
results/autonomous_film_20261118_lateral_unload_next1451/three.checkpoint_114.txt
Same1420 DLL SHA526872e0d040f77b37b5f950c79b24dfc94d5b5cb9033311a1253ef395fb3dc3.
1458/1459 intended24.4ms horizon FAIL;only one accepted23ms prefix exists.
1461 verifies that prefix q/v/time/checkpoint EXACT,but does NOT certify
the failed horizon. At rejected23.1ms MID stage selected triangle124/face
gap−1.05835e-10mm,endpoint+1.97957e-11mm;normalv~1e-14,momentum5.93e-19Ns.
Same selected surface,not evidence of a missing triangle.1460 uniformhalf
reference also FAIL endpoint drift. No rejected state was committed.

1436 separate profiled route API PASS;1437/1438 and1442/1443 actual short
no-object dynamics PASS;1444 zero-profile versus original lateral6 EXACT.
1445 actual294step50ms PASS execution/API,NOT time convergence.
1454 SAME core/Tmax/C2:mean tip−.743267→−.761872mm;75mm centre upward
arch+.372966→+.399852mm;mid mean−.097787→−.134871mm.
1455 actual stage mechanical work.000167955009Nmm versus baseline1394
.000149076386Nmm (~12.7% MORE),not matched-work superiority.
1456 virtual fixed-sphere overlay on NO-OBJECT states has minimum buffer
gap−.0185480mm;NOT valid contact/wrapping solution. Wire centreline
gap+.263898mm does not certify finite wire/guide clearance.
Candidate NOT selected as a wrapping improvement.
Actual equal-aspect scale1 PNG/SVG/OBJ:
results/autonomous_film_20261118_profiled_surface50_1465/
Coordinate comparison1454 explicitly labels unequal-axis geometric ratio.

New EndpointControlledRows is isolated,never replaces old law silently.
It discards entire inadmissible uncommitted steps and reintegrates halves
using SAME forces/gates;NO q/v projection or fabricated reaction.
Only explicit endpoint-drift observation or returned whole-stage gap failure
admits subdivision. Release/ambiguous geometry/other errors propagate.
1463 unit-mass circle fixture FAIL line search;1464 dimensioned1g fixture
fails incorrect test expectation of endpoint rejection.1466 correct circle
test PASS:7stage rejections,15attempts,gap6.36e-11mm,analytic position
error3.58e-12mm. These failures remain preserved.
1467 same ACTUAL23ms-IVP independent one-macro reference PASS with
unchanged gates. Actual controlled-owner qualification is still separate;
do not claim general adaptive-time or whole-energy PASS.

No final wrapping/holding/gravity lift,friction,selfcollision,full-thickness,
whole time/mesh/energy,mechanical equalizer,12-Wrench or Optuna certified.
Original-route44.4ms,quadratic-route50ms,lateral22.8ms and profiled FREE50ms
are DIFFERENT histories and must not be spliced.
For an EXACT same-state short lateral replay inside known qualified history:
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/film_routed_resume_continue.py --tag UNIQUE --parent 20261118_lateral_unload_next1451 --checkpoint-step 110 --steps 4 --end-time .0228 --reuse-journal-rows

## Previous lateral transmission/contact qualification —2026-11-18

Feature c369746 binds SAME objective6mm lateral cable to actual Field,
implicit force/tangent and active shared event path.1416 THREE real films
plus FREE Rigid3 reach10ms C2 peak,actual q/v/impulse/time EXACT to reference.
1420 persistent replay and1422/1426 transfers retain exact physical state,
quaternion/public clock/root/mass ownership.1428 actual Hold to
.011600000000000004s;1430 strict API comparison PASS:q/v/force/control error0,
stored/kinetic inventory difference4.7434e-20Nmm.
Gap minimum−3.62377e-13mm,momentum2.04578e-19Ns.
This is NOT actual holding capacity or wrapping certification.
Latest lateral checkpoint:
results/autonomous_film_20261118_lateral_hold_short1428/three.checkpoint_58.txt
Build:build/routed_resume_20261118_lateral_resume1420/libReGripThreeFilmResume.so
SHA526872e0d040f77b37b5f950c79b24dfc94d5b5cb9033311a1253ef395fb3dc3.
Prior lateral stage-work origin NULL;never splice quadratic-route work.
Actual scale1 geometry:results/autonomous_film_20261118_lateral_coupled_shape1425/.

1419 frozen REST actual-mass basis has lowest period5.297s,but is NOT an
actual nonlinear completion-time estimate.1427 complete-basis reconstruction
of actual50ms motion is exact;fast tip−.743267mm vs frozen-static−41.5368mm.
Actual response still includes positive75mm skin arch.1417 lower-load static
witness passes residual at9.375e-5N,but full-load1374/1376 FAIL remains;
virtual object penetration means static FREE branch is not contact solution.

1421/1423/1424 ACTUAL saved-state energy decomposition:100/50/25us cumulative
signed defects2.85848e-10/7.12760e-11/1.78801e-11Nmm are dominated by
potential-chord single-midpoint quadrature,not momentum/cancellation.
Momentum-energy terms~1e-19Nmm,chord4/8-point diagnostic errors~1e-18Nmm.
Diagnostic quadrature does NOT alter physical forces or time integration.
1411 relative-defect time FAIL remains FAIL;root work NULL,whole energy BLOCKED.
Slow40ms-ramp1404 is a DIFFERENT C2 input;less arch AND less bending,not
proven superior wrapping.1418 corrected unequal-axis chart captions preserve
original1406 evidence and explicitly report geometric exaggeration.

1431/1432 isolated quarter-guide profile [5.5,5,4.5,5,5.5]mm plus same6mm
outboard passes independent FD/objectivity/zero-profile parity. Initial wire
centreline gap+.366772mm,core unchanged,hardware mass/finite-wire clearance
unknown. Actual profile dynamics NOT RUN until separately qualified build.
No final grasp,lift,friction,selfcollision,full thickness/full time/mesh/energy,
mechanical equalizer,12-Wrench or Optuna certification.

Exact next bounded lateral continuation (new unique tag):
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/film_routed_resume_continue.py --tag UNIQUE --parent 20261118_lateral_hold_short1428 --checkpoint-step 58 --steps 8 --end-time .013200000000000008 --reuse-journal-rows
$PY tools/film_routed_hold_reference.py --tag UNIQUE_REF --parent 20261118_lateral_hold_short1428 --checkpoint-step 58 --qualification 20261118_lateral_hold_api1430 --reuse 20261118_lateral_hold_reference1429
$PY tools/film_routed_hold_api.py --tag UNIQUE_AUDIT --case UNIQUE --reference UNIQUE_REF
Do not extrapolate isolated/free trajectories into object holding.

## Previous actual quadratic-route FREE continuation to50ms —2026-11-18

Feature commit:defd292(strict rotating numerical-path exclusion/resume).
1391 completes original C2 Unload at accumulated.02999999999999993s.
1392 separate FREE-only endpoint50ms build changes ONLY the virtual horizon
limit,not physical force/control or accepted step counter.1393 actual to31.6ms;
1395 repeat-resume q/v,ALL stages and physical checkpoint tokens EXACT.
1396 twelve bounded segments reaches.04999999999999981s;1399 actual scale1
shape,1403 ALL-join audit PASS:all q/v/time/mass/root/quaternion bridges,
ForceField input0 difference,rest reconstruction7.11e-15mm.
This is NOT complete recovery:skin mean tip−.1623459mm,maxspeed42.5619mm/s,
body vz−1.379764mm/s. All actual tendon inputs zero after30ms;no lift claim.
Signed31.6..50ms inventory defect3.3253e-8Nmm is NOT heat or whole energy PASS.
Latest complete checkpoint:
results/autonomous_film_20261118_routed_free_to50_chain1396_part11/three.checkpoint_250.txt
Build:build/routed_free_window_20261118_routed_free_window1392/libReGripThreeFilmRelease.so
SHA2561b9e370100e260ad759d40eca432b59a8b4793fcd268861db6375d63c67b5024.
Original-route44.4ms and new quadratic-route50ms are different histories.

Lateral6mm route:1363/1372 actual50ms base/half PASS execution/API only;
1384 ALL epochs FAIL centre-mid z20.8ms .121871773% (abs1.25791e-11mm).
1388 local0..3.2ms ALL3pairs PASS max.03712239%,not50ms.
1386 quarter50ms forecast529.913s>480s:policy BLOCKED,not OS exhaustion.
1374/1376 static continuation FAIL final1e-12N force gate/budget.
1394/1397 actual Gauss-stage cable-work inventories measured separately,
NOT matched work or whole energy. Slow40ms C2 ramp is a DIFFERENT physical
input:1398 separate build/API,1400/1401 short actual PASS,1404 full50ms
must be inspected by completed result/process before any success claim.
No final wrapping,holding,gravity lift,friction,selfcollision,full thickness,
full time/mesh/energy,mechanical equalizer,12-Wrench or Grasp Optuna certified.

Actual images:
results/autonomous_film_20261118_routed_recovery_shape1399/actual_geometry_curvature.png
results/autonomous_film_20261118_routed_recovery_audit1403/actual_recovery_inventory.png
Reproduce a NEW same-state short suffix audit,not a historical rerun:
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/film_routed_free_continue.py --tag UNIQUE --provider 20261118_routed_free_window1392 --parent 20261118_routed_free_to50_chain1396_part11 --checkpoint-step 248 --steps 2 --compare 20261118_routed_free_to50_chain1396_part11
Next:inspect1404 and compare same-core/Tmax10vs40ms C2 response,then qualify
control/time/work separately. Do not extend beyond compiled50ms window blindly.


## Previous actual release and outboard-route comparison —2026-11-18

Feature commits:df6748f exact-query reuse;60a0341 edge resume;
32849a7 bounded actual release;d766032 outboard route.
1336 actual face→edge transfer PASS at25.34324085354ms;1338/1342
resume to27ms with1341/1344 strict q/v/time identity.1346/1347 longer
horizon FAIL;1349 certifies ONLY its accepted prefix through27.2ms.
1360 actual deformed three-row release27.2→27.4ms PASS local gates:
all512 RK stages/final q/v/clock EXACT to1355,minimum gap−5.11235e−12mm,
outgoing normal speed+.0005288796mm/s. No state projection or negative
unilateral force.1350/1352 grids32/64 remain FAIL;no time-convergence claim.
Latest completed actual quadratic-route checkpoint:
results/autonomous_film_20261118_routed_release_actual1360/three.checkpoint_137.txt
Build:build/routed_release_20261118_routed_release_actual1360/libReGripThreeFilmRelease.so
SHA25651b1554482e714c185d3f788abd90df1b536d4b04a7a1ad1d2944df2e63bb808.
1364 FREE setup FAIL frozen-cap mismatch;corrected1365 FREE and1371
interval-exclusion variant FAIL original surface-event algorithm budget512,
NOT OS exhaustion. No actual accepted state beyond27.4ms on this route.
Original-route44.4ms remains separate;never stitch different geometries.

New OUTBOARD6mm route preserves5mm normal lever and same CORE volume,
not total hardware mass.1353 math/1356 SOFA API PASS;1362 zero-route
regression q/v EXACT.1363 actual294-step50ms NO-OBJECT coupon PASS,
all state/stage/context clocks EXACT to same-kernel reference.
1367 comparison294 exact epochs:skin width-mean tip−.738359→−.743267mm,
root-tip3D angle.0639264→.0643616rad;centre75mm remains positive arch
+.370615→+.372966mm. NOT wrapping or holding superiority.
1368 VIRTUAL sphere overlay:wire centreline min gap+.341364mm but
triangle buffer min gap−.0170890mm. Free trajectory is NOT contact proof.
Actual scale1 comparison:results/autonomous_film_20261118_lateral_hold_comparison1367/actual_route_comparison.png.

1351 opt-in exact query cache qualification:byte-identical9CSVs,
two opposite serial orders7.16%/6.46% bounded runtime reduction.
Not applied automatically to current release DLL or universal speed factor.
Whole time/energy,friction,selfcollision,full thickness,mechanical equalizer,
wrapping,holding,gravity lift,12-Wrench and Grasp Optuna remain unqualified.
Root work/contact area/pressure/holding load remain NULL when unmeasured.
Next bounded work:inspect1373 read-only dense path and1372 actual50ms
half-step comparison;do not repeat failed long FREE runs or relax gates.
See models/film_lateral_tendon/README.md and detailed transmission report.


## Latest actual routed simultaneous birth/impact —2026-11-18

Prior feature commit:d095b67.1325 FaceEdgeTransfer FAIL identified an
independent surface birth BEFORE face-edge boundary.1327 old detected
birth trial FAILs when the full bracketing trial leaves the old face.
Separate1328 analytically continues ONLY root-bracketing trials and
requires ALL accepted pre-impact stages strictly inside the physical face.
No force/tolerance/state projection change.1328 isolated transfer PASS.
1329 ACTUAL SOFA same kernel:24.237106380844455ms event,6owned rows,
3new active rows;old124 release/new117 contact,not full object ungrasp.
q/v/time/impulse EXACT vs reference. Minimum gap−1.45661e−13mm,
momentum5.88299e−21Ns,loss1.13763e−13Nmm;NOT wrapping/lift/full time.
Latest complete actual event checkpoint:results/autonomous_film_20261118_routed_birth_actual1329/three.checkpoint_122.txt at24.4ms.
DLL:build/routed_birth_20261118_routed_birth_actual1329/libReGripThreeFilmTransfer.so (593fea50b6084e69).
1330 dependency preflight FAIL(path canonicalization),physics NOT RUN;
fixed1332 uses unchanged persistent DLL only after compiled .o.d model
dependency parity.1331 reference/1332 actual longer continuation FAIL
next geometric drift;4 accepted states through25.2ms match EXACT in1333.
Do NOT relabel that failed26ms horizon as PASS.1334 next FaceEdge reference
must be inspected by actual process/result;its inherited24.2..24.4ms label
is stale metadata for supplied25.2ms checkpoint,NOT the physical clock.
Live runner now records source time/dt explicitly.1335 scale1 actual24.4ms
PNG/OBJ generated,contact area/pressure/holding remain NULL.
Next:resolve new supplied25.2ms feature/release event with existing laws;
do not rerun failed long continuation or infer whole-cycle success.
No wrapping,holding,lift,friction,thickness,selfcollision,whole time/energy,
mechanical equalizer or final design superiority is certified.

## Previous actual Hold/Unload and feature-transition checkpoint —2026-11-18

Feature commit before this unit:f2502c2. Actual new-route200us Hold reaches
19.6ms(1300),Unload21.2ms(1307);1303/1311 API q/v/time/force EXACT.
1318 separate explicit100us restart21.2→22.8ms preserves ALL physical
checkpoint tokens except provenance token;1320 API q/v/time/force EXACT
at8 common endpoints of the accepted prefix of FAILED1317. This does NOT
make1317's27.6ms horizon or global time/energy/grasp PASS.
1312 actual/1313 reference longer Unload FAIL endpoint drift;both15 accepted
states exactly match through24.2ms.1317 half-step reference also FAIL.
1319 isolated rejected-step diagnostic:triangle124→117 on all3fingers,
mid gap−1.45847e−9mm,end gap+1.96782e−8mm;rejected state NOT committed.
1322 constraint-defect bisection prototype FAIL:negative stage reaction
requires release/active-set law,not clipping.1323 unit-mass circle FAIL
line-search;separate1324 gram-scale analytic circle PASS,NOT a repair of
1323.1325 existing FaceEdgeTransfer/new-route integration under study;
inspect actual process/result,never infer RUNNING from this historical text.
1309/1315 actual nonlinear force inventory:Skin direct tendon force0,
attachment net force<3e−20N/net moment<1.86e−18Nmm. At19.6ms Skin tip
−.117741mm,rail tip−.198934mm,skin root-tip angle.0142212rad;NOT wrapping.
1314 actual frictionless wrench rank3,body normal Fz5.70371e−6N,
zero centre torque;NOT holding capacity or12-wrench dynamic test.
1316 measured stage-work chain0..21.2ms Wt=.000275939839188Nmm,
signed defect−3.61970e−12Nmm;NOT heat;root workNULL/full energyBLOCKED.
Latest complete200us checkpoint:results/autonomous_film_20261118_routed_unload_begin1307/three.checkpoint_106.txt.
Latest complete100us checkpoint:results/autonomous_film_20261118_routed_refined_actual1318/three.checkpoint_122.txt.
Reuse100us DLL:build/routed_refined_20261118_routed_refined_actual1318/libReGripRoutedRefinedResume.so (e9d31b0aca45895f).
Next:inspect1325,resolve smooth-face/shared-edge/release transition with
EXISTING validated branch laws;do not repeat failed long Unload. Wrapping,
holding,lift,friction,thickness,selfcollision,whole time/energy remain unqualified.

## Previous routed Hold/API/work checkpoint —2026-11-18

Actual quadratic-route3-finger Hold reaches13.2ms (1296), from saved10ms
via1289/1296;1291/1299 strict same-IVP API q/v/time/normal-force EXACT.
This is a maintained T=.0001N/rail INPUT, NOT object holding or lifting.
1295 local10..11.6ms all-pair 200/100/50us reference: all state/force/
stored-energy/tendon/damping metrics <0.1%, but normal-work residual
relative errors FAIL (max cumulative35.015, interval67.546). Overall FAIL
retained;this is NOT fine actual SOFA/full-cycle time certification.
1294 actual stage-work prefix0..11.6ms is connected by EXACT q/v/time;
Wt=.000113108803321Nmm,signed defect−3.28132e-12Nmm,NOT heat/whole energy.
1284/1290 byte-identical journal-row reuse observed34.80%/10.10% runtime
reduction in separate4-step pairs;no universal or combined speed claim.
1287 opt-in cost logging is passive:all9CSVs+4checkpoints byte-identical.
Latest actual:results/autonomous_film_20261118_routed_hold_next1296/
three.checkpoint_66.txt. Reuse routed_resume1278 DLL78ec827b1136f2dc.
Original route44.4ms remains a DIFFERENT model;never splice to this route.
Next:profile-bounded Hold extension to19.6ms,then explicit release-owner
validation;friction/full thickness/self-collision/wrapping/lift/12wrench/
whole energy/mesh/full time/final optimization remain NOT qualified.

## Previous actual routed3-finger milestone — commit267252a (2026-11-18)

NEW quadratic route is now bound to ALL coupled force/event derivatives and
actual fields,not just a loaded OBJ/ForceField.1269/1270/1272 actual first
impact+1.6ms+10ms C2 peak PASS with shared-kernel standalone q/v/time EXACT.
1278 route-bound checkpoint40→44 and1279 actual retransfer44→48 PASS EXACT;
legacy Field sampled-work is NOT restored and must NOT be spliced.
1275:10ms mean tip−.020577mm,centre tip+.000556mm,3D angle.003856rad;
NOT wrapping/holding. Sphere continues downward undergravity0/Fz−.001N,
NOT lift.1277 moving-body stage geometry:612 samples,wire centreline minimum
+.230671mm;triangle buffered gap−5.613e-13mm. Finite wire/guide/physical
thickness/self-contact/friction remain unqualified.1276 actual new-route
stage-work defect−3.280e-12Nmm is NOT heat or whole-energy PASS.
Rejected speed claim:1264 SOFA+5.88%;1266 larger run−1.37%,mixed/no robust
benefit. Default core unchanged. Full quarter tests1255/1267 budget-BLOCKED
at forecasts490.11/483.80s,NOT OS exhaustion.1259 LOCAL3.2ms time PASS only.
Old fixed-route actual44.4ms checkpoint is preserved and is NOT this new model.
Last functional commit267252a. New event/resume DLLs and all reproduction paths
are in [research](REGRIP_TENDON_TRANSMISSION_AND_WRAPPING.md) §8d.
Next:finish route-bound replay to10ms,then SAME-IVP Hold reference/actual
continuation with correct stage-work origin;do not copy old-route gates.
No final grasp/design/Optuna certification;no automatic background restart.

## Latest qualified result — public-clock refinement and routed tendon (1241–1251)

Actual3-finger endpoint remains44.4ms/checkpoint344,NOT wrapping/holding/lift.
Separate NO-OBJECT original-route50ms Hold:all63 exact canonical epochs and
all294/588/1176-step pairs PASS0.1%,maximum0.0271422922% (1241). This does
NOT certify all-time/contact/mesh/whole energy. Old startup/contact FAIL retained.
1238 exposed original wire centerline initial sphere overlap2.607968mm;
old triangle clearance never certified cable/guide clearance.
New separate quadratic route Field/ODE actual math/API/profile PASS (1240–43).
Amplitude0 old-state regression EXACT (1246);plot failure1245 retained.
1244 actual50ms route completed:q/v/time/force-stage/control EXACT vsreference.
1249:mean skin tip-.399593mm vs baseline-.738359mm,root-tip3D angle.031223
vs.063926rad;material75mm still arches AWAY(+.253845mm centre). Thus NO
wrapping improvement certified. Same core/Tmax,NOT same work/hardware mass.
1250 measured route work.0001156624695Nmm,signed defect-2.258e-12Nmm,NOT heat.
1251 VIRTUAL fixed-sphere overlay:wire centerline min+.203039mm;triangles
minbuffer gap-.0218586mm at27.6ms. Obstacle was absent from dynamics,so this
is NOT actual contact-solver failure or wrapping. Finite wire/guide bodies,
friction,self-contact,full thickness,whole energy/lift/Optuna remain BLOCKED.
Latest feature commit:ab02bab. More results must use new tags,not overwrite.
Details and source/binary identities:[research](REGRIP_TENDON_TRANSMISSION_AND_WRAPPING.md).
Reusable route DLL:build/film_routed_20261118_routed_math_api1240/libReGripFilmRoutedTransmission.so.
Next:finish candidate dt comparison and independent static study,then implement
new-route coupled contact without copying old triangle-only qualification.
No automatic post-session restart. Historical RUNNING text below is not process evidence.

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

# Three-finger actual continuation — 2026-11-18

## LATEST verified — C2 unload end,exact-time early recovery,persistent V5

Project remains INCOMPLETE. This is a chain of scoped accepted-state experiments,
not one general automatic contact/impact/release dispatcher or a certified grasp.
Actual1083 reaches29.99999999999993ms from the validated FREE V3 chain.24steps
complete,minimum buffered midsurface gap5.62585363e-5mm,momentum5.38937e-19Ns.
Tension at that accumulated endpoint is3.421782e-46N,not an invented exact0.
New recovery midpoints after30ms use the existing profile's exact unloaded branch.

### Clock/work-duration correction

1089 read-only audit FAIL:1079 has exact stage joins but quadrature duration
exceeds actual clock advance by9.10187724e-17s,above the existing1e-18s
duration-inventory gate.1090/1091 instead integrate each representable interval
`h_i=(clock+nominal_i)-clock`,without resetting the accumulated clock.
1091 actual q/v match independent1090 EXACT.1092 audit PASS:weight sum equals
actual clock advance9.99999999999994e-5s EXACT;nominal-dt difference
-6.09863722e-19s remains below the UNCHANGED1e-18s gate. Original1089 retained.

1096 independent reconstruction of259 ACTUAL1091 stage states:

|Item|Nmm|
|---|---:|
|Tendon mechanical work|-5.45815957350e-8|
|External work|1.20979849041e-7|
|Mass-proportional damping work|6.08952795430e-8|
|Normal work,independent reconstruction|-4.37592621773e-29|
|Stored+kinetic energy change|5.50186003912e-9|
|Signed inventory defect|-1.11372404875e-12|

Positive pull coordinate is minus routed length:power=-T*dL/dt. Negative
tendon work is mechanical energy returned to the prescribed source,not an
electrical-energy measurement. Normal work is reconstructed from actual q/v
and applied multipliers with the same material-edge geometry,not forced0.
No instantaneous velocity jump/impact impulse occurs in this release interval.
Actual field energy discrepancy2.1684e-19Nmm,endpoint control error0N.
Root reaction work NULL. Signed defect is NOT physical heat or whole-energy
certification.1094 missing-iostream compile FAIL remains;1095/1096 fix/reuse
the observer only,no physical simulation data is changed.

### Recovery shape/time scale,not successful recovery

1086 actual30ms geometry uses scale1,rest+u reconstruction7.08114e-15mm.
1093 maps serialized velocities through the exact root map:skin width-mean
tip z=-.322245298mm,vz=-6.705277515mm/s,RMS-displacement-squared rate
+.635853760mm2/s. Rails' corresponding rates are-.519393007/-.541065799:
rails are relaxing while skin still deforms. Zero tension does NOT prove
restored shape. Body vz=-1.232094853mm/s,gravity0;NOT holding/lifting evidence.

1085 independent stress-free FREE-finger spectrum:649 positive modes,
lowest omega1.18611609rad/s,undamped period5.29727686s.1087/1088 CURRENT
deformed finger0 frozen tangent:649 positive modes,lowest1.07376343rad/s,
period5.85155455s;not an equilibrium or nonlinear dominant-response certificate.
Frozen current modal kinetic projection agrees with actual film K to
-2.71050543e-20Nmm;fraction above omega*100us>1 is1.1920716e-9.
The flat-reference quadratic potential grossly differs from nonlinear actual
stored energy;do NOT use1085's combined quadratic metric as actual fast-mode
energy.1087's figure retains an old stress-free title;use corrected1088 image.
1084 worker-import FAIL remains;its complete FEM matrix dump is hash-verified
and reused in1085,no failed physics result is changed into an actual SOFA PASS.

### Exact-time early FREE recovery,0.1% unchanged

1097/1098/1099 independently integrate the SAME actual30ms q/v/mass state
for800us at100/50/25us nominal dt,with a consistent final fractional interval.
1100 all-pair observable subset PASS,base-to-quarter max.0128125483%.
1101/1102/1103 actual SOFA match their OWN accumulated-clock references
EXACT,but endpoints differ by floating clock accumulation.1106 strict
common-time bridge FAIL:max state5.57065505e-12>original1e-12. No waiver.

1107/1108/1109 use a separate public NEXT-dt scheduler,all11 child contexts;
no time reset,q/v correction or StepCount spoof. All reach the identical
absolute target.030799999999999928s,and match exact-target independent states
EXACT.1110 actual all-pair FREE800us observables PASS0.1%,max.0128125483%;
exact-time bridge error0. This LIMITED unloaded/no-contact interval does NOT
replace997/1041 contact/work/full-cycle Time FAIL,mesh/history or energy gates.
1104 legacy1002 regression stays EXACT;1105 confirms original legacy cap/dt
guards still reject31ms/25us. New bounds apply only to the separate owner.

### V5 full numerical-plan persistence and actual extension

1111 V5 stores physical state plus plan start/original counter,nominal dt,total
steps,target,USED dt,EXPECTED NEXT dt and remaining budget.1112 resumes4steps
from checkpoint204:all q/v/time/field/stage/controller records EXACT and
205..208 checkpoints byte-identical.1113 restores checkpoint207's next
dt=.00010000000000000286s (used dt=.0001s) and produces byte-identical208.
1114 corrupted next/used dt,remaining budget/global index all reject before
accepted commit. V4 observation-only snapshots are not silently relabeled V5.

1115 starts an EXPLICIT new800us plan from completed208 without changing
physical payload or counter;C2 absolute time is preserved. Actual end
.03159999999999993s,min gap.0147152625mm,momentum5.10174e-19Ns,EXPERIMENTAL.
1117 resumes its final4steps from212:all state/field/stage/controller records
EXACT,213..216 byte-identical. Private legacy work is not restored;prior
segment evidence stays linked by parent hashes,not an invented cumulative0.

Reusable V5 build:build/three_film_recovery_20261118_three_film_persistent_recovery1111/
DLL SHA2562e5f27eba96c49d2708f90217d898ba35a9ce741d71b9598c359d19e90e9c132.
Actual duration-corrected release1091 DLL SHA256
b85e7ad746fc5649d650cf489e7922ce0c3190e63c9be9fe1e4c513ea7cc4075.
Every campaign retains its runner,source/binary identity,SDK/command,raw and
exit status. Research parameters remain E250MPa,nu0,1g/film,100g sphere,
Tmax.0001N/rail,gravity0,Fz-.001N. No real PET/actuator measurement is implied.

### Remaining bottlenecks and executable checkpoint

Latest complete actual state:1115 checkpoint216 at31.6ms. The next fixed800us
plan would end32.4ms,outside this owner's explicitly validated32ms cap.
This is a MODEL-SCOPE admission condition,not OS exhaustion or proof that
the overall project is complete. Do not delete the guard. Next develop an
independent completed-V5 FREE recovery reference for a longer horizon and
validate time/cost before a separately versioned window extension. In parallel,
the manually selected contact/birth/feature/release owners need one automatic
dispatcher;all-gripper contact time/energy,friction,self-collision,physical
thickness,shared mechanical equalizer,gravity/palm lift and true wrapping
remain unqualified. No Grasp Optuna or final design selection is permitted.

Verified regression after future source changes (NEW tag,not old raw paths):
```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/film_three_film_v5_resume.py --tag UNIQUE --parent 20261118_three_film_v5_next_plan1115 --step 212 --steps 4 --compare
```
Do not rerun unchanged long campaigns to substitute for the missing next code.
No automatic research after session termination is provided or claimed.

## FREE V3 exact resume1082 — actual SOFA

From1081 checkpoint173(27.3ms),a separate Free Owner reproduces two steps
through27.5ms. q/v error0,all force stages exact,actual field error0 with
only declared legacy sampled-work excluded;checkpoints174/175 byte-identical.
Minimum gap6.76473674e-6mm,momentum4.31892292e-19Ns. Original1e-12 gate.
1083 extends checkpoint176(27.6ms) by24steps to30ms;actual measured four-step
runtime22.7082s yields conservative forecast302.498s<480s. Check its result,
not this pre-execution forecast,before asserting completed Unload.

Exact replay with a fresh unique tag:
```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/film_three_film_free_resume.py --tag UNIQUE --parent 20261118_three_film_free_four1081 --checkpoint-step 173 --steps 2 --compare
```

## CURRENT — actual deformed release1079; separated continuation1081

**Actual SOFA1079** integrates the same27ms accepted state of failed1061
through a separately defined acceleration-complementarity release variant.
No stiffness/damping/mass/control change,no force clipping,no velocity reset
or geometric projection.256 actual RK stages all have nonnegative applied
normal forces and whole-stage clearance>=1.42108547e-13mm. Shared momentum
residual3.55121519e-19Ns. At27.1ms active set empty, outgoing normal velocity
>=.00631256147756mm/s. q/v match independent1078 EXACT under original1e-12
API; quaternion and mapped physical state checked exactly at commit.
RK accumulated clock joins free remainder EXACT. This is a LIMITED actual
deformed release,NOT completed Unload/recovery,holding/lift or full physics.

Actual1080 restores FREE V3 and takes one step.1081 continues four steps to
27.6ms. Each uses all960 triangles and existing quadratic midpoint dense
numerical-path CCD; new impact is explicitly rejected,not ignored.1081 minimum
force-stage gap1.99168699e-6mm,momentum4.32180607e-19Ns. No friction/grasp
certificate follows. Legacy work restarts at each process; root work NULL.

1072/1074 are preserved failures: full100us explicit acceleration queries
leave the tangent manifold;1074 first refusal at27.00078125ms has
gap-7.35412e-13mm,vn-1.10922e-9mm/s,lambda+9.72447e-8N. Gate not relaxed.
1075 instead localizes the new integration law to20us,64RK substeps and then
free midpoint;1073 independently tests all8 coupled active subsets,permutation,
zero-reaction and invalid-compliance guards.1077 local64/128 comparison gives
relative full-state q1.93028e-13%,v5.83336e-10%,but both share the same80us
free-remainder bias and there is no base-to-quarter/full-cycle test: NOT
full0.1% time convergence. Tiny gap/residual relative differences are not waived.

1076 old actual release matched its reference but its RK/free clock join
reconstructed from the macro start differs9.02056208e-17s; keep its result
but do NOT use it as exact accumulated internal-clock qualification.1078
independent and1079 actual pass the corrected accumulated endpoint forward.
RK quadrature weights and fractional remainder durations are their actual
floating values; do not force their sum to a nominal value or invent work.

Build:build/three_film_release_20261118_three_film_actual_clock_release1079/
DLL SHA25622add00153af4573a0e852c954af0514f444ca4d23c03a1d9f5136ab05e9cc51.
Raw:results/autonomous_film_20261118_three_film_actual_clock_release1079/,
...three_film_free_profile1080/,...three_film_free_four1081/.
Each contains archived runner/scene,source or parent identity,SDK,binary and
raw hashes,actual command and guarded process exit/runtime. All before/after
physical conditions remain research assumptions,gravity0 andfrictionOFF.

## Release diagnostics1062–1066 (not actual release)

1062 archived independent replay captures the previously rejected100us trial
from actual checkpoint170. Initial reaction+1.0641827e-7N becomes negative
at27.05ms (-4.8875909e-7N) for all three material edges. Nothing is committed.
1063/1065 reintegrated signed bilateral diagnostic locates a reaction root at
27.009042662754602ms, bracket9.31322568e-14s. Outgoing free midpoint remainder
has whole endpoint gap+2.87091638e-7mm and momentum residual3.53960e-19Ns.
1065 importantly measures pre-event collocation reaction minimum
-4.4303170e-16N: this signed diagnostic is NOT an admissible unilateral
trajectory and is NOT directly installed into SOFA. No tiny-force exemption
or clipping is permitted. Next experiment1067 seeks an admissible interval
split satisfying both nonnegative pre-stage reactions and separating free
acceleration, with explicitly refined root uncertainty. Its result must be
checked before actual owner integration; signed-reference PASS alone is not
physical release PASS.

1064 independent regression preserves fourth-order analytic Lobatto behavior
(errors6.33439e-9,3.96261e-10,2.47720e-11), maximum tangent FD1.63276e-16,
and verifies optional rejected-stage observer leaves accepted q/v EXACT while
still rejecting tensile contact and never mutating input state.

1066 read-only actual failed-horizon accepted-prefix geometry at27ms is checked
against the exact serialized q/v before rendering. Reconstruction7.05686e-15mm,
scale1. Skin width-mean tip z deformation-.289499920mm,root-tip tangent angle
1.75203891deg; rail tip angles6.87049/6.85541deg. Body centre z-63.47737494mm,
gravity0. Contact area/pressure/holding load NULL,wrapping NOT ESTABLISHED.
Actual image/OBJ:
`results/autonomous_film_20261118_three_film_unload_shape1066/`.

Functional commit:bea42b197f00e09cc745d8203191c7a9a93f0ef7 qualifies actual
Face->Edge and typed resume;1063–1066 diagnostic sources are archived per run.
No timeout/resource exhaustion caused1061;it stopped at a physical active-set
transition. Existing full time/energy/material/grasp gates remain unmet.

## CURRENT — typed Edge resume qualified; Unload stops at release

1059 actual Face->Edge event PASS;1060 four-step V2 resume EXACT including
byte-identical snapshots.1061 requested30ms FAILS after accepted27ms at
negative stage reaction (127.184s,not timeout).1062 independent signed
diagnostic reproduces +1.06418e-7N at27ms and -4.88759e-7N at27.05ms.
No negative reaction committed.1064 independent passive-observer regression
and query-purity PASS. Next is zero-reaction event and coupled release;
full time/energy/wrapping/lift remain UNQUALIFIED. Detailed1059–1061
evidence and reusable DLL are recorded below; earlier status is historical.


## Actual support migration implemented — through1048

1042 independent isolated new triangle117 birth PASS. Six old/new rows share
the same projected mass;plastic impulse retains new117 rows and releases old124
rows with outgoing normal velocity~+.0201492mm/s,old impulse0. Root time
23.495650505693598ms,bracket9.31322e-14s. Not a full globally earliest CCD.
1043 extracted reusable kernel exactly reproduces this reference;old3-row
J/H match exactly,new6-row directional gap FD7.32e-10mm,H directional relative
8.81327e-9;world momentum balances meet inherited1e-17Ns/1e-16Nmm s gates.

1044 **actual SOFA** ONE100us deformed contact-support transfer PASS:
q/v,event time,impulses,quaternion,actual field control all EXACT to independent
reference under original strict1e-12 API. Whole-stage minimum gap-3.57758e-12mm,
momentum residual3.63071e-19Ns,vn5.46925e-14mm/s. Global linear balance
1.91115e-21Ns,angular1.05097e-24Nmm s. New stage journal separates the two
Lobatto intervals and actual impulse event;weights total100us. Instantaneous
impulse is not a continuous force. Old rows genuinely separate;the object
remains in contact with new rows,so this is NOT object release or successful
Unload. Initial condition is an individually accepted23.4ms prefix of failed
1033,not a claim that1033's requested horizon completed. Parent failure stays.

1048 read-only actual segmented energy inventory consistency PASS:
Wt1.03791839116e-6Nmm,Wexternal1.18270777203e-7,Wdamping7.08645143619e-8,
normal constraint work-1.41849e-22,stable plastic loss4.811702162e-12,
signed residual-2.59885e-15Nmm. Kinetic subtraction differs from stable loss
by-1.84999e-20Nmm;NOT extra physical heat. Callback energy error6.78e-20Nmm,
stage-control error0N. Root work NULL;no whole-energy/time certification.
Actual graph:results/autonomous_film_20261118_three_film_actual_transfer_work1048/actual_transfer_inventory.png.

1045 actual generic-resume regression after embedded-module guard PASS,
q/v/time/used stages exact.1046 runner preflight indentation error:SOFA NOT RUN,
failure.json preserved;import/negative runners corrected and14 new/changed
Python tools py_compile PASS.1047 actual bridge from transferred checkpoint
does NOT finish requested4steps:one23.6ms step accepted,then endpoint drift
rejects. This exposes another contact transition;do not claim persistent
post-transfer/full Unload PASS. No repeated unmodified long run is justified.

Reuse actual transfer DLL:
build/three_film_transfer_20261118_three_film_actual_transfer1044/libReGripThreeFilmTransfer.so
(SHA256940b6cb43e89d00392fcabebb63373a226fab3ef187fdf9d6fc2fdef092741f7).
Reuse generic checkpoint DLL:
build/three_film_resume_20261118_three_film_bridge_regression1045/libReGripThreeFilmResume.so.
Next bottleneck:detect/resolve further inactive-surface births and releases,
not hardcode only124→117. Validate generalized owner independently before SOFA.
Full all-pair time1041 remains FAIL;wrapping/holding/lift remain unverified.

## Newest actual checkpoint through1041 — still INCOMPLETE

Actual1022 completes Hold to19.99999999999999ms in106.8482s;minimum
whole-stage gap-3.49942e-12mm,momentum5.24636e-19Ns,vn1.45484e-14mm/s.
1021 same-DLL opt-in owner profiling retains exact states/used rows versus
continuous1002. Inclusive2-step costs:coupled10.1652s,implicit7.7376s,
selected geometry3.4572s,material force/Hessian1.5498s. These are nested and
MUST NOT be summed. No speed improvement is claimed.

Actual1024 Unload200us FAILS after accepted23ms,before25ms completion:
whole-stage clearance gate. The failed process is NOT a completed trajectory.
Independent1026 cubic numerical-path chain rule on its accepted prefix:
endpoint reconstruction7.11e-15mm,chain-rule error8.09e-15mm;selected
features stay124/6 through that prefix.1028/1030 independent334-bit audit
over ALL960 triangles identifies the discrepancy as stage versus endpoint:
22.9ms midpoint gap-9.69884e-11mm,23ms endpoint+1.81888e-11mm.
AD distance value error<=1.42e-14mm. Thus this specific clearance failure is
real numerical Stage-position drift,not candidate omission or large geometry
roundoff. It is NOT solved by deleting midpoint clearance checks.

1027 actual regression after permitting explicit100/50us checkpoint grids:
q/v/time/stages EXACT versus1002,strict1e-12 unchanged.1029/1034 start from
EXACT SAME complete20ms checkpoint at100/50us and complete20→22ms:
minimum gaps-1.23279e-12/+2.30216e-12mm. No force/material/control changes.
Their clocks accumulate,endpoint discrepancy6.94e-17s is recorded.1041 listed
100→50us pair STILL FAILS:normal constraint-work residual99.99498% relative,
absolute1.67122e-19Nmm. Motion,separate stored/kinetic energies,force and stage
tendon work pass0.1% for this pair only;no base-to-quarter/full-cycle PASS.
Legacy sampled work is NOT continuous across restarts and not substituted.

Actual1033 extended100us Unload FAILS after accepted23.4ms with endpoint
drift. Independent1036 replay captures REJECTED,NOT COMMITTED trial:
mid23.45ms triangle124 gap-8.42e-8mm;end23.5ms selected triangle117 gap
+2.498e-7mm. Initial reaction remains positive~1.266e-5N. It is NOT release.
1036 raw accepted_initial force0 was an unmeasured diagnostic placeholder,
NOT physical zero reaction;use its rejected_initial computed reaction instead.
Future driver writes null for this unmeasured field.1037 frozen-triangle
contrast ran but its initial diagnostic harness did not record the completed
trial;FAIL preserved. Corrected1039 records same fixed124 branch but whole
surface gap-8.79934e-8mm:holding old ownership does NOT fix new contact.
Therefore a new surface/owned-row event must be resolved,not simply more
unchanged time refinement or a relaxed gap tolerance.1040 actual regression
after opt-in pre-rejection observer hook again q/v/time/used rows EXACT;
observer never permits a failed state to commit.

1025 actual10→20ms partial work inventory:Wt2.02742614486e-4Nmm,
Wexternal1.11798136627e-5,Wdamping5.78768015695e-6;
signed residual-1.03539e-12Nmm,NOT heat/full energy.1035/1038 reuse the
immutable read-only material observer with canonical GCC dependency closure;
new PersistentRows diagnostic hook is proven NOT included by that observer.
No included file or binary identity exemption.

1031 visualization failed because installed Matplotlib lacks Axes3D;failure
and OBJ preserved.1032 uses standard orthographic projection of SAME actual
3D coordinates,scale1,not a fabricated pose. Skin width-mean tip z at20ms
-0.167364mm,root-to-tip tangent bend1.18514deg;rails about5.80deg.
These discrete shape metrics do not establish contact coverage or wrapping.
PNG/OBJ:results/autonomous_film_20261118_three_film_hold_shape1032/.
Sphere centrez-63.46909358mm,gravity0,NOT lift. Area/pressure/holding load NULL.

Last feature commit before these diagnostics:be34e4639a770bfc03156333e1760f591cda0717.
New compiled resume DLL1027/1029/1034:
build/three_film_resume_20261118_three_film_resume_grid1027/libReGripThreeFilmResume.so.
Latest regression DLL1040:
build/three_film_resume_20261118_three_film_resume_hook_regression1040/libReGripThreeFilmResume.so.
Next:isolated triangle117 Contact Birth using original124 persistent branch,
shared multi-row impulse,then retained-row/release and whole-surface validation.
This is not a declaration of full production contact completeness or grasp.

Project INCOMPLETE. Measurements below are **actual SOFA** unless explicitly
identified as read-only mathematical postprocessing. No wrapping,lift,holding
load,frictional grasp or design superiority certificate is claimed.

## Persistent transfer implemented

Separate `models/film_three_finger_resume/ThreeFilmResume.cpp` reuses the existing
conservative mechanics and fixed compressive-row Lobatto step. Original owners'
REST checks remain defaults;new owner validates a complete checkpoint instead.
No fake counters,force/velocity projections or relaxed residuals. Public
`Context::setTime` synchronizes exact accumulated clock and dt on11 contexts.
BaseContext has no public setTime:1013 compile failure preserved;1014 uses
public Context API,SDK unchanged.

|Campaign|Actual operation|Result|
|---|---|---|
|1014|1002 step40→44,4 resumed steps|strict1e-12 PASS,q/v/time EXACT|
|1015|1014 serialized step42→44,2 steps|q/v/time and all used stage rows EXACT|
|1016|1014 step44→50,to10ms|q/v/time and all used stage rows EXACT|
|1017|step50→80,10→16ms Hold|COMPLETE,scoped EXPERIMENTAL|
|1018|five corrupt checkpoint actual runs|guards reject;original harness FAIL preserved|
|1019|read-only same1018 reassessment|PASS:zero accepted rows in empty buffered files|
|1020|read-only actual8→10ms energy/work|callback/control consistency PASS,not full energy|

1014 runtime22.4137s,whole-stage minimum gap-7.46070e-14mm,momentum
4.10910e-20Ns,normal velocity1.81327e-15mm/s. All field positions,control,
length,stored/kinetic energy agree exactly;only private legacy work is excluded
explicitly.1017 whole-stage gap-1.32516e-12mm,momentum2.24238e-19Ns,
normal velocity6.63840e-15mm/s. Gates remain -1e-10mm,1e-17Ns,1e-10mm/s.
The actual accumulated time at step80 is0.016000000000000014s,not replaced by
step*dt. Checkpoints save actual xyzw quaternion;historical1002 reconstruction
is allowed ONLY after zero angular velocity/increment checks for all prefix states.

## Energy origin and state ownership

Snapshot includes exact public nodal masses,rigid mass/inertia,root map,
positions/velocities,quaternion,time/dt,step index,active owners and source/binary
provenance. Contact multipliers are recomputed by the SAME stateless one-step
equations,not imported from Native IDs. The three fixed compressive rows are
not a production release active set. Invalid identity,quaternion,mass,mapping
or row ID is rejected before a physical state commit. Invalid init currently
aborts the process;no silent continuation or recovery is claimed.

Private legacy sampled-work history is NOT restored and NOT joined across
chunks.1020 uses full-AD read-only observer946 and actual accepted stage q/v:
8→10ms tendon work4.33297448587305e-5Nmm,external work2.14250610771e-6,
damping6.98284909313e-7,normal constraint work-8.32911e-25;
signed residual-7.00187e-13Nmm. Callback energy error6.09864e-20Nmm,
control mismatch0N. This is a numerical/partial inventory,NOT physical heat.
Root reaction work stays NULL. First200us inventory1011 and post inventory1007
remain separate origins;overlaps must not be counted twice.

## Scope and blockers

Same research geometry/material/control as1002:three100mm films,root radius50mm,
sphereR30mm plus.01mm midsurface buffer,film1g each,sphere100g,Tmax.0001N per
rail,ramp10ms,release20–30ms,Fz-.001N,gravity0. Six equal prescribed tensions
are NOT a physical equalizer. No actual PET/TPU or actuator measurements.
Initial impact fixture is not stationary-object closing. No full-thickness,
self-collision,general friction,full time/mesh/energy certificate.997 overall
time FAIL and999 deformed-release FAIL remain unchanged.16ms is not evidence
of wrapping/holding/lift. Contact area/pressure/holding load remain NOT MEASURED.

## Reproducibility

New source baseline94cdf31 plus per-campaign archived source hashes.
Build:`build/three_film_resume_20261118_three_film_resume1014/`.
DLL SHA256:`32360e2ffabb94749d5e0f6aa8e739d5128734b98f2fc0fbfa9aab04ccd77146`.
SDK `/home/ubuntu/SOFA/v26.06.00`,no mixed Sofa dependencies.
Raw `results/autonomous_film_20261118_three_film_resume1014/` and corresponding
1015/1016/hold1017 directories. Each stores exact scene,command,process result,
q/v,all stages,field geometry,checkpoint files and hashes. Unique names required.

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/film_three_film_resume.py --tag NEW_UNIQUE --step 40 --steps 4
$PY tools/film_three_film_resume_continue.py --tag NEW_CHAIN --parent 20261118_three_film_resume1014 --checkpoint-step 42 --steps 2 --compare1002
```

Next:complete bounded actual Hold/Unload;diagnose genuine lambda=0 release,
never commit tensile contact. Profile and quantify actual curvature before
longer physical time or any grasp claim. No automatic post-session execution.
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
# Latest actual continuation1124–1129

## Frozen-control and actual-recovery energy1135–1138

1135/1136 are independent frozen actual20ms state diagnostics,not new dynamics.
Tendon-force affine residual8.32728e-20N;unit load norm3.92120469 entirely on
Rails,unit Skin force0. Direct normal-acceleration gain0;local zero-velocity
linearized delayed-reaction second derivative norm7.96365944/s². No nonlinear
time scale/actuator requirement inferred.1138 analytic three-mass reference
verifies the delayed-response formula and second-order small-time expansion.
This supports studying transmission through attachment rather than treating
instantaneous gain0 as absent eventual control authority.

1137 independent observer reconstructs192 actual31.6..38ms stages:
stage-duration sum equals actual elapsed0.006400000000000017s EXACT.
Actual stored/kinetic field error2.71050543e-19Nmm. Wt0,Wext8.11563637e-6,
Wdamp6.25963299e-6,delta(stored+K)1.86086141e-6Nmm;
signed defect+4.85802552e-9Nmm,NOT heat. Root Work remainsNULL.
The defect is about0.261% of this interval energy change (diagnostic ratio,
not an invented energy Gate). No full energy/time/contact certification.

## Next completed work1130–1133

Optional value-only clearance (default OFF) preserves original AD primal
operation ordering,including constant multiplication.1130:12000 randomized
point/edge/triangle queries bit-exact and3 degeneracies rejected. Mechanical
Force/Hessian/actual contact Jacobian stay on the original AD2 code path.
Actual1131 matches1124 state/stage and allthree ForceField CSV BYTE-EXACT.
1132 alternating three A/B pairs replay four actual steps:all strict API and
serialized snapshots PASS;median4.175683954s→3.310452311s,20.7207167% reduction.
Only this unloaded FREE recovery scope is qualified;no impact performance claim.

1133 actual20ms Hold-row independent wrench audit:body-normal Jacobian error
1.11e-16,radial moment error1.24345e-14mm;normalized wrench rank3,normal torque0.
Observed upward normal force5.2774468e-6N,NOT holding capacity. 100g Earth-weight
reference.981N is a calculation,NOT a gravity/lift experiment (actualgravity0).
This frictionless spherical-contact geometry cannot certify six-DOF wrench
closure. The actual12-wrench test remains NOT RUN;friction remains unqualified.

Comparing repeated800us plans to one continuous6.4ms numerical plan gives
endpointclock difference1.38778e-17s and velocity difference4.05720e-11mm/s:
the existing1e-12 strict API is NOT waived. Independent1134 uses the identical
accumulated plan schedule to separate clock representation from physical
time-step convergence.1134 completed PASS:all64 actual steps q/v EXACT and
accumulated API times EXACT. Different clock schemes remain different schemes;
this does NOT repair the earlier common-plan strict API comparison by waiver.

Separate Extended Recovery Owner preserves the legacy32ms limit. Independent
1123 all-pair100/50/25us6.4ms subset PASS,max0.02950534%;coarser1121 remains
FAIL0.11718728%. Actual1124 matches the independent800us q/v and clock EXACT.
1126 four-step resume matches API/stages/controller and snapshots BYTE-EXACT.
Seven bounded explicit V5 plans1127 then reach37.999999999999944ms without
reimpact.1128/1129 reconstruct actual state and scale-one geometry.
Skin width-mean tipz=-.34690653mm,velocityz=-3.74943732mm/s;skin squared-RMS
rate remains positive1.07056815mm²/s. No completed recovery or holding/lifting.
Bodyvz=-1.29190161mm/s,gravity0,Fz=-.001N,frictionOFF.
Reusable build/raw/replay commands are at the top of LONG_RUN_RESEARCH_CHECKPOINT.
