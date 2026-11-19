## Product/native SOFA pivot —2026-11-19

User priority now product CAD/native SOFA,not another custom solver. Legacy evidence preserved.
Implemented product_prototype/:parametric SCAD/FreeCAD source,closed Skin/Rail STL,
dimensioned/exploded SVG,BOM,and actual stock-SOFA three-finger free-object scenes.
Functional commit d6c4580. STEP/whole assembly kernel verification NOT GENERATED.
Native actuation/contact observed;whole-time gate FAIL,wrapping NOT PROVEN,
independent holding FAIL044,lift FAIL021,fabrication NOT READY.
Straight cable coupon050 STRICT tracking PASS1.77809e-17m,not finger/grasp approval.
See product_prototype/reports/REGRIP_SOFA_NATIVE_VALIDATION.md and checkpoint.

## Latest continuation1778–1795: thickness-aware geometry —2026-11-19

Functional checkpoint ad3acc5 adds optional per-triangle half-thickness envelope
and passive actual SOFA observer;legacy disabled-envelope1755/1783 journals are
BYTE EXACT. Actual1782 SAME binary ON/OFF and old1743 state/stage/Field outputs
BYTE EXACT,12,800 geometry rows,1ms. This is a FREE coupon with PASSIVE sphere
geometry,NOT dynamic thickness contact or3-finger grasp.

New STATIC model uses explicit+.2mm world-Z sphere-centre placement and
R+.01+half-part-thickness. Both baseline1780 and profile4.5/outboard10,1784
complete64 loads to100uN with original force1e-12/gap1e-10 gates.
1788 profile sampled geometry is clear:Skin envelope+.0100mm,wire centreline
+1.118785mm.1787 baseline wire gap−.0838626mm FAIL. Zero-radius wire only.
Baseline1785 static unload FAIL;profile1789 static64-stage unload PASS toT0,
zero active force rows. NOT dynamic release/recovery,holding or lift.
1794/1795 deformed Lagrangian Hessian FD PASS;old signed-energy FAIL retained.
No final design selected;one contact row is NOT wrapping/contact area/pressure.

Next NEW code:per-triangle radii in a separate dynamic event/contact Owner,
shared by event roots,normal Jacobian,accepted closure and energy/work.
Single-film fixed-sphere verification precedes free-body/3-finger integration.
Do not repeat completed static campaigns unchanged or splice old checkpoint1644.
Baseline unload residual/rounding analysis is independently actionable.

Full results,Raw/build identities,reproduction commands:
[Thickness continuation](REGRIP_THICKNESS_CONTACT_20261119.md).
Reusable actual observer build:build/thickness_audit_20261119_thickness_sofa1782/.
Results/figure:results/autonomous_film_20261119_thickness_assess1790/.
Inherited15,278 immutable v14 artifacts unchanged (1791);new live sources differ.
New byte ledger: FILM_CONTACT_EVIDENCE_20261119_thickness_v15.json.
All owned children completed;no remote push/SDK modification/automatic restart.

## Latest: actual precise1ms ALL-output state/shape PASS, energy still FAIL —2026-11-19

Functional commit8e88fbb. Actual1743/1744/1745 SAME binaryef4f9ebe2b17:
40/80/160 steps,ALL accepted q/v and384/768/1536 physical stages EXACT to
independent plan.1747 ALL5280 common-time state/shape comparisons PASS.1%,
worst.0201771235%,NO floor. Runtime44.723/91.488/167.411s,RSS~248MiB.
1748 actual-linked work/component energies PASS.1%,but signed partial residual
time FAIL198.74477% (absolute1.17097e-29Nmm);root workNULL,whole energyBLOCKED.
Old1724/1708/1710/1722 FAILs remain unchanged. New plan is NOT old24-setting repair.

1746 free static shape at51.79uN reaches−22.51mm Skin tip but1750 virtual
sphere buffer gap−14.503mm:NOT contact/wrapping.1754 separate fixed-sphere
STATIC contact8 load stages to1uN passes force1e-12/gap1e-10;NOT actual SOFA,
free-body grasp or dynamic stability. Further static cycle/full-load trials
have separate result JSONs,not historical RUNNING labels. No precise-law splice
into original1644 three-finger56.4ms checkpoint. Holding/lift/final design blocked.
Full evidence/reproduction:REGRIP_PRECISE_TRANSMISSION_AND_GRASP_VALIDATION.md.

## Historical: new precise-tendon actual200us common-output state/shape PASS —2026-11-19

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

# Autonomous research status — active continuation 2026-11-18

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


## Newest measured state — common C2 three-film/ONE FREE sphere, through903

UPDATE through930:actual same-DLL driven8/16/32 completed.926/928 correct
reference mass INPUT using passive public API917;all macro q/v EXACT. Original
911/912 API FAIL are preserved. Same-binary causal test924 reproduces failure
with default reconstructed mass and removes it with public mass;no tolerance
change. Full listed time930 remains FAIL:endpoint force8→32=.1367496%,old
sampled cable work=.8957352%,despite stage-power work=.0243102%PASS. Full energy,
fullcycle wrapping/lift/grasp still BLOCKED/NOT RUN. Details:THREE_FILM_C2_20261118.

Functional commit6d78a24. Actual8878-step10ms common C2 pilot COMPLETE;
geometry888/input889 PASS,actual/independent v difference3.94e-13mm/s.
Body dz=-.000496664mm,local tip z=.000654073mm:tiny already-touching motion,
NOT wrapping/lifting/grasp. DefaultT0 regression890/891 nine physical CSV EXACT.
Four-step881/882 FAIL preserved:midpoint gap-2.57e-10mm versus-1e-10 gate.
Independent local gap-controlled885 rejects only final coarse interval and
reintegrates halves;PASS without projection. Not yet actual adaptive owner.

Independent C2 8→16 motion/separate energy899 PASS listed0.1% only;not full
time certification.32-step893/898 FAIL due113/334bit distance order disagreement.
Exact rational stored-double fixture900 resolves difference+2.595e-43mm²;
opt-in rational fallback32-step901 COMPLETE,5 fallbacks. Same-binary8/16
902/903 COMPLETE. Common-time triple and actual exact-order refinements are
separate pending qualifications,not inferred PASS. Physical thresholds unchanged.

General friction/self-collision/full shell thickness clearance/full energy,
separated closing/impact/release,shared physical equalizer,wrap/lift/hold,
12wrench/multimaterial/GraspOptuna remain NOT QUALIFIED/BLOCKED.
Cost-cache878 rejected for lack of speedup;passive meters retainedc565ac9.
No OS/session resource exhaustion observed. Older sections below are historical.


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


## Latest measured continuation — persistent collocation through763

Actual coupled single-branch LobattoIIIA is IMPLEMENTED and executed,not a plan.
Independent740 analytic fourth-order/changing-normal FD PASS;actual-state741/751
validates shared projected-M/J/U assembly. Actual742/743/744(1/2/4 steps,9.765625us)
all-pair time747 PASS. Extended actual753/754/755(4/8/16 steps,39.0625us) all-pair
time757 PASS at UNCHANGED0.1%:base-quarter velocity0.0165440%,same-window normal
force0.0509962%,attachment0.00000342806%,tendon-work observable0.000748632%.
These are ALREADY-TOUCHING persistent coupons,not new impact/full C2 certification.

Actual-versus-independent FEM748/756/758 agrees (position exact,velocity<=7.11e-15
mm/s,end reaction exact). Owned stage J/force/impulse/time audits749/759/763 PASS;
whole accepted surface/actual FF audit762 PASS with absent impact quantities NULL.
Each force is integrated with actual Lobatto weights(1/6,2/3,1/6),not hidden pose
or speed correction. Earlier Radau actual737 FAIL0.245223% force remains,as do
705/657 full/longer-window FAILs. Default729/735 five physical CSVs remain exact.

Still NOT QUALIFIED:impact+new collocation in one path,global earliest endpoint-
family event,release/reimpact/multiple-row collocation,full C2/time/mesh/energy,
changing-normal friction,self-contact,3finger/free lift/12wrench/Grasp Optuna.
No measured PET/TPU/actuator or final structure superiority is claimed.
Detailed derivation/build/raw:REGRIP_COUPLED_FREE_BODY_RESEARCH.md and
models/film_coupled_collocation/README.md. No automatic background restart.

## Latest measured continuation — reintegrated event, through721

Project NOT COMPLETE. New isolated coupled C2 solve-to-event kernel/root IFT
695/696/714 PASS;actual SOFA697–704 and guarded715 execute/clearance PASS.
Default-hook706/707 and guard718 preserve five physical CSVs byte-exact.
Independent actual used M/J oracle699 and accepted/FF audit719 PASS.
Actual64/128/256 time705 FAIL:base-quarter film velocity0.171685%,common-window
normal force1.486946%. First impact time/impulse/pre-normal are identical across
these grids;attachment0.00124556% alone passes. Full C2/energy/grasp still blocked.
Same-binary708/709 changes only event policy;partial midpoint defect decreases
from7.3332e-12 to2.3377e-20 N s (710/711/713). NOT global momentum/energy proof.
Frozen shared-contact FEM721 independently reproduces persistent modal error;
higher-order stage integration is under investigation,not actual SOFA PASS.
No globally earliest endpoint-family proof,friction/self-contact/3finger/lift/
12wrench/final Optuna certification. Research materials/zero gravity unchanged.

## Latest measured status — continuation through692,project incomplete

Actual custom single-film/free-sphere dynamics,original C2 closing,explicit
saved-state continuation and independent used-row momentum audits implemented.
Limited1ms/T=0 actual h/h2/h4 time640 PASS remains limited. Actual C2 midpoint
643/648 time653/657 FAIL:attachment2.46263%,velocity6.48059%,1vs2events.
Normal-work bias improves greatly but does NOT solve time convergence.
Actual exact pre-step replay659/672 PASS;isolated actual128/256/512-step
continuation677 FAIL (velocity base-quarter.598185%,common-window force3.11011%).
Full energy/friction/self-contact/3finger/lift/12wrench/multimaterial/Optuna
remain unqualified. No final structure selected or measured PET claimed.

692 localizes an independent adaptive failure to PRE-impact dense velocity:
event time difference5.36e-17s,J difference1.32e-16,same triangle,but velocity
difference3.45e-6mm/s before and after impulse. Next numerical fix must address
actual event subintegration,not replace already validated shared impulse.
Accurate numerical gap solve685 and defect-budget687 experiments still FAIL
adaptive completion;not production PASS. Default actual689/690 remains byte-
exact in five physical CSVs. Detailed failure/resource distinctions and paths:
REGRIP_COUPLED_FREE_BODY_RESEARCH.md,LONG_RUN_RESEARCH_CHECKPOINT.md.

## Latest 2026-11-17 — custom coupled free sphere, through647

Supersedes historical fixed-owner-only statements below. Project NOT COMPLETE.
Actual shared film/Rigid3 custom midpoint/event owner is implemented and tested.
Motion of BOTH bodies,shared projected mass/J,opposite impulse,whole triangle
accepted clearance and actual mapped state commits are checked. Sphere only,
frictionless,isotropic inertia,explicit root fixture,zero gravity;not3finger.

- Actual original C2 closing605/606 (400/800 steps,1s):execute/clearance PASS,
  overall time607 FAIL. Attachment2.456910%,film velocity6.473119%;1 versus2
  impact events. Tighter Newton residual did not solve this.
- Actual bounded adaptive impact620 and optimized opt-in636:382 accepted steps,
  state/force/energy/row CSVs exactly identical.636268.266s versus620259.218s:
  total speed improvement rejected646 despite independent evaluator speedup.
- Genuine physical frozen h/h2/h4 runs628/629/630:382/764/1528 intervals,
  original initial condition re-integrated.640 all-pair0.1% time PASS for
  **1ms zero-tension seeded impact only**;base-quarter attachment0.00378159%.
  Independent actual geometry/mapping/instant momentum audit637 PASS.
-634/639 independent analytic counterexamples distinguish newborn-impact
  velocity defect and persistent normal-work quadrature.635 measured C2 work
  is on already-touching rows,not newborn rows;sole-birth hypothesis rejected.
- Experimental midpoint-force/endpoint-gap path641 consistent tangent FD PASS;
  actual loaded touch644 PASS;default CSV regression647 byte-exact to596.
  C2 midpoint643 actual execution/clearance PASS. Half-grid648 comparison is
  a separate pending experiment;inspect its summary,not this historical text.
- Full-cycle time/mesh/energy,changing-normal friction,self-contact,3finger,
  free-object lift/hold,12wrench,multimaterial and grasp Optuna remain FAIL /
  BLOCKED / NOT RUN. No final structure or measured material performance claim.

Detailed sources/commands/raw:REGRIP_COUPLED_FREE_BODY_RESEARCH.md. Original
Native562 buffered gap failure and all old FAIL/raw/SDK remain unchanged.

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


### Follow-on shared-body reference475 and verified source checkpoint

Last functional/test commit:55eb59b9f9afae0620f63706c0246a51e15beb18
(guard/API evidence commit:e3307b5;initial implementation:1b2b18c).
Independent475 adds point/free-rigid shared mass,inertia and Jacobian with
linear momentum residual8.88e-16 and angular momentum residual6.28e-16.
This is independent mathematics,NOT free-body SOFA integration;the actual
moving-object/additional-mass guards remain enforced. Actual471 archive
matches all30 current model-source files exactly. Current physical gates
remain FAIL/BLOCKED as stated below;project completion is NOT claimed.
All launched jobs have exited. The handoff is an unfinished response-context
checkpoint,not OS/RAM exhaustion,permission denial,480s timeout or proof all
independent research is externally blocked. No unattended restart exists.


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


## 2026-11-17 continuation through319

Actual current-normal sphere307 completes4s; however exact triangle audit312
finds buffered gap -0.000531mm. A new closest-primitive AD contact model is
now implemented and actually SOFA-tested:316 completes20 steps/.1s;317
buffered gap -7.13e-14mm;318 radial moment defect3.18e-15;319 force pullback
defect7.47e-16. These are limited checks,NOT full convergence certification.
See FILM_TEMPORAL_COUPLING_20261117.md for definitions and prior failures.
Whole-cycle292 time convergence remains FAIL;full energy and grasp Optuna
remain BLOCKED. Actual free6DOF/3finger/multimaterial grasp is NOT RUN.
Next executed tasks are wide closest-contact320 and tangent-failure321;
their final result files,not this historical activity note,define status.


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

## 2026-11-17 continuation through224 — supersedes historical checkpoints

Project NOT complete. Code checkpoint b8b9cc3 qualifies profiling/routing;
subsequent native coupling is experimental working-tree development.
Scoped PASS: passive journal identity; reusable-lift derivative/state identity
and4.562% median speed improvement; distributed-guide kernel/API; closed-cylinder
construction; actual20/40-step coupled Sphere BE equation solves. Accepted
nonlinear impulse residual .93498 reduces to <=3.56e-6 in the checked20-step
trajectory. This is NOT full force/moment, time or energy certification.

FAIL retained: inherited gates; native cycle180; object collision mesh201
(fine-pair force1.7359%, kinetic4.2255%); coupled time219. Failed210/211
energy line search is retained;213 uses residual merit, SAME tolerances.
Native LCP nonconvergence222/223 motivates direct active-set reference224.
225/226 are the next actual reproductions: use summary/process result, not
partial CSV, to determine completion.

EXPERIMENTAL: inward no-object bending with slower control and fixed-cylinder
load-bearing location span11.243deg. Sphere broad wrapping NOT approved.
BLOCKED/NOT RUN: whole energy/current-normal angular consistency, self-contact,
friction time/history, free6DOF/three-finger/multimaterial/12-wrench grasp,
final design and grasp Optuna. Properties/actuator/guide hardware remain assumptions.
See the two new20261117 reports.


## Final measured state of this response (through146; project incomplete)

Actual coupled film/rails/tendon and fixed-sphere surface contact implemented.
All launched processes complete. Partial coupon4-observable time PASS remains
strictly scoped. Coupled Trapezoidal AND BDF2 attachment-energy time FAIL;
full BDF2 coarse→fine .7455%, fine-pair .4853%. Pre-1s error also persists after
local refinement. Three BDF2 partial discrete-energy audits PASS but global
grasp energy BLOCKED. Sub-tolerance mapping suppression hypothesis rejected
by source/API unit144. Actual1s geometry arches away, not a qualified wrap.
Free6DOF/12-wrench/Sphere-Cylinder-Box grasp NOT RUN; grasp Optuna BLOCKED.
Response/context budget checkpoint, not OS timeout/final goal completion.
See newest NEXT and FILM_CONTACT_DYNAMICS_20261116.md; no background restart.

## Latest continuation: actual coupled actuation, full grasp still unfinished

Native follow-up110–118 is COMPLETE, not RUNNING: separate installed-ABI
plugins and no-contact control PASS; actual tendon-driven skin contacts fixed
R8 sphere atx95. Native100/200/400-step time FAIL (nonadjacent force25.423%,
tip2.044%). Fixed reaction unobservable after projection: BLOCKED, never zero.
All launched physics processes are complete; no background restart is claimed.

See FILM_CONTACT_DYNAMICS_20261116.md (newest evidence, supersedes historical
status below). Mapped-mass MBK cache defect corrected independently, no SDK
edits. Coupon Trapezoidal3280/6560/13120 windowed time Gate PASS (.1%, all pairs,
physical intervals and endpoints); bitwise repeat PASS. Old coarse/BDF2 FAIL
retained. Fine static21→81 space PASS, old11→41 space FAIL retained.
Actual Film+separate flexible Rails+routed eccentric Tendon implemented and
API/mapping/force/tangent validated. Low-load8s recovery observed; nominal
T=.001 runs to2s with profiled phase refinement without Newton failure.
Coupled low-load1600/3200/6400 time FAIL due attachment-energy .8232% nonadjacent
difference. This is not hidden by passing tip motion. Fixed-sphere Native
integration is experimental; patched SDK lacks collision binaries, so any
installed-SOFA experiment uses separate rebuilt plugins and explicit ABI audit.
No free6DOF grasp, wrapping certification or grasp Optuna. Global energy BLOCKED;
partial no-object discrete energy identity PASS only. Original friction-time
FAIL unchanged. Research NOT completed; no automatic continuation claimed.

## Profiling continuation and rejected optimization

Actual profile28:150steps cost50.859s; force/damping39.406s, gradient/RHS9.862s,
linear solve1.399s, mapped mass product.00724s. Nested residual timing includes
force/mass: do not double-count it. Instrumentation preserved every CSV value.
A runtime gradient-only AD experiment preserved exact state/force/energy, but
cost94.966s (1.867x slower), shifting work into repeated Hessian evaluations.
It is rejected as an optimization; default AD and FilmShell were restored and
cleanly rebuilt/tested in final30. Failed code is retained in Git eebbb45,
campaign29/sources and the archived test under reports/film_newton_experiments/.
No original model/raw/Golden was removed. Full time/grasp Gate remains FAIL.
Next cost research should first count accepted/rejected force evaluations or
test element-local derivative dimensions/compile-time specialization, against
both mathematical equivalence and actual runtime; do not repeat runtime flags.
All launched runs are complete. There is no claimed background continuation.

## Newest completed experiment status

Hard-boundary campaign25 and mapped reference26 are complete, not RUNNING.
Hard mapped short FEM/API/mass consistency PASS; full transient convergence FAIL
despite zero Newton failures. Hard versus penalty waveform differences are far
smaller than time-refinement errors; root penalty is not supported as the main
remaining explanation. Phase27 localizes the largest discrepancy after contact.
No long physics process or automatic restart is claimed at this checkpoint.
Film+Rails/tendon, friction-time qualification, full energy,12-wrench grasp and
grasp Optuna remain unfinished. No OS/session hard-timeout was observed here;
individual runs stayed within480s. Further work is not declared completed.

## Latest verified development checkpoint — nonlinear defects corrected, final goal unfinished

Local feature commit bceda3a records Newton-stage tracing, exact cache keys,
trial-state tangent and independent BDF line-search correction. Subsequent
BDF2 and mapped-boundary work is identified by exclusive source snapshots.
PASS limited: tiny-coordinate API regression; distinct main/trial matrix test;
passive tracing purity; unloaded/no-contact SOFA; 11/21/41 final force balance;
short BDF2 versus independent FEM (relative differences below 2.89e-10).
FAIL: full transient tip/U/contact-area/normal-force convergence; nonadjacent
11→41 energy 1.1486% and area 1.3360%; original friction temporal failures.
Mapped hard-clamp testing is a separate boundary model, not a penalty-model
PASS substitution. Full film/rail/tendon grasp, energy and Optuna stay blocked.
See FILM_SHELL_PHYSICS.md and new raw campaigns; prior entries are historical.

## Latest film implementation checkpoint — final goal NOT complete

Source commits38f3966(film mechanics/contact) andb86e305(equal-volume/competition).
PASS limited:independent membrane/plate/cantilever patch,objectivity,force/Hessian,
actual SOFA API4modes;actual finite-width fixed-plane deformation/contact exists.
Equal-volume skin/rail concept439.33979mm³ and5daytechnical/application drafts
implemented. Baseline/grasp advantage,layer friction and hardware NOT certified.

FAIL:actualfilmEuler dynamic force residuals,BDFnonfinite,base-dtindependentNewton,
coarse→fine contact/energy. Rootfixture continuation achieves21nodestaticendpoint
residual6.35e-6 only. Actual first free M/C/K matrix matches5.58e-17;nonlinear
RHS/correction remains unverified. Independent200/400Newtoncompletes,NOTSOFA.
Temporal exactgreat-circle referencePASS butgeneralendpointtangent NOTimplemented;
originalSphereEvent0.146423%andCurved0.8519%FAILstay. Fullenergy/graspOptunaBLOCKED.
All children finished;no ongoing process or automaticrestart is claimed.

## Latest sphere-event result — further development, not completion

New SphereEventReturn + separate actual SOFA adapter handle fixed-sphere chord
Birth/Death and outside-to-outside transit. Unit FD/objectivity/discrete identity
and actual API PASS. Time FAIL remains:512internal subdivisions give adjacent
0.09758%/0.09756%PASS,but20→80is0.146423%FAIL. Solver-free reference gives
0.146397%,isolating temporal return/loss quadrature in this experiment.
No tolerance changes;oldCurved.8519%FAIL also remains. Manifest
DESIGN_TEMPORAL_EVIDENCE_20261116_v1.json verifies853artifacts,not physics.
Code commit1108fad. All launched physics children finished;no background job.

## Newest physics/design checkpoint

PASS(limited):Changing-normal active one-point path kernel+actual SOFA API and
20/40/80dynamic phase-loss time test(.00177531%max). This NEW fixed-supported
sphere benchmark is not the original curved/freeobject case;old.8519%FAIL stays.
General moving CurvedContact integration/Birth/Death/event-exact law/adaptive
spatial owner/global energy/longduration remain EXPERIMENTAL or BLOCKED.

IMPLEMENTED:baseline source extraction;two tapered-film concept meshes,
50mm body target,3zone circuits,OBJ/XML and SVG/PNG. Actual SOFA geometry
loading+4geometry regression tests PASS;Shell mechanics and grasp comparison
NOT RUN. Material5.74xbaseline is a design risk,not an improvement. Final design
NOT SELECTED;grasp Optuna BLOCKED. No real material measurements or hardware run.

## Newest actual moving3D owner/adapter checkpoint — NOT final completion

Latest completed regression:current03math6/6PASS;06repeat journals identical;
explicit solid-sphere inertia20/40/80contact processes complete,but temporal
phase loss.851917%FAIL. Initial defaultI/m=1was a numerical isolation condition,
not a certified solid sphere. Cases are separate and not pooled. All children
have completion records;no ongoing RUNNING/background restart is implied.

Subsequent work also implemented TemporalYield fixed-plane vector event+IFT
(256states),six-test mathematical regression,and a fresh clean06SDK/API/wrench
build. This is a prerequisite,NOT yet a new changing-normal temporal return law.
No whole3finger simulation/grasp optimum is claimed. No host resource exhaustion
has been evidenced by these bounded experiments;the larger objective remains
unfinished. Full-duration exact replay is algorithmically capped,not a reason
to remove that cap or declare the project complete.

IMPLEMENTED:independent exact-function GeneralVectorCurvedContact,with immutable
material geometry,original Birth/circular return,once-commit tokens and optional
SphereHistoryChart seed. This is128operator bounded replay,NOT a qualified
general adaptive STATE fitter. Adaptive integration is a separate implemented
feature;do not conflate it with adaptive history compression.

PASS in limited scope:2910material states versus explicit point prefix;normal
frame covariance2.1272e-16;actual matching-SDK API/FD;moving sphere global
internal wrench8.61292e-22 and force FD1.18994e-13. Actual free sphere/Hermite
20/40/80step dynamics completed. Adaptive.02/.01/.005mm integration contrasts
PASS1%including aligned phase plastic loss(max~9.41e-9relative). New model's
exact unchanged-configuration identity avoids repeated rounded yield projection;
no positive physical loss threshold or force/torque correction is applied.

FAIL:adaptive time comparison,maximum phase-loss difference.851919%>unchanged
.1%. Final accumulated loss alone.0642703%would pass but does NOT override
phase FAIL. Prescribed identical geometry(no Solver) reproduces.851935%,so
the main measured error is not eliminated by changing the SOFA Solver.
Independent variable-capacity scalar benchmark confirms endpoint-capacity loss
is first order(.10899/.054957/.027594%error at20/40/80),while event-integrated
capacity work matches analytical reference to6.46e-15relative. This scalar
formula is NOT installed as a general3D friction/force/Jacobian replacement.

BLOCKED/NOT RUN:qualified general adaptive history compression,full3finger
11/21/41mesh/history/time,global energy,12wrenches/shapes and grasp Optuna.
No existing full-gripper FAIL has been deleted or reclassified. Old vector and
curved indices still PASS integrity. Current summaries,not old RUNNING entries,
identify finished children. No automatic restart is installed.

## Newest prerequisite — general sphere chart PASS in mathematics ONLY

SphereHistoryChart now supplies nonparabolic normal-force capacity,spatially
varying normals and material first/second jets for prescribed previous Hermite
geometry.129states and event/invalid-input controls PASS in sphere_chart04.
An actual covariance FAIL was corrected by relative-control interpolation;
the1e-16criterion was not relaxed. No SOFA dynamics/Commit approval is claimed
for this chart. The adaptive general-history owner and curved forcefield
integration are still NOT RUN;full gripper/energy/graspOptuna remain unfinished.

All launched children have completion/exit records. This is a finite response
working-context checkpoint,not host exhaustion or project completion. Resume
the first task at the top of NEXT;no background restart exists.

## Authoritative latest checkpoint — vector patch qualification,not gripper completion

All physics/reference children of this vector cohort have actually finished.
No RUNNING process or automatic restart is implied by historical sections.
Same branch development/regrip-autonomous-research. Model/metrics details are
in reports/vector_history/QUALIFICATION_v1.json and immutable raw snapshots.

PASS in FIXED-NORMAL PATCH scope:normalized vector phase/history,strict five
prospective loss references(including1.056e-26Fmm),actual Matching SDK
Force/Jacobian/API/query purity;100/200/400step Newmark time tests;1e-9→1e-10
state-fit contrast;exact repeated journal;50step force reversal;771constant
frame covariance states. Base→quarter movement x.00032505%,y.00103590%,
plastic loss.01805761%PASS unchanged.1%line. Representation loss.00034348%
PASS unchanged1%line. Actual dynamic force residual<=7.08e-14relative.

Outward interval arithmetic is EXACT-RESULT equivalent to the rational
predicate in actual20/100/400/reversal journals(all common values identical).
400step runtime455.897s→6.7775s;100step115.056s→3.5717s. This is bounded
arithmetic acceleration,not changed friction or a whole-gripper speed claim.
Independent material-coordinate first/second derivatives and AD pullback now
PASS;they are not yet connected to the moving curved-contact SOFA component.

EXPERIMENTAL:source-matched fixed-patch discrete energy audit,with signed
linearization,cached-acceleration and representation inventories separate.
BLOCKED/NOT RUN:general moving3Dnormal/capacity/Birth/Death integration,
qualified three-finger Mesh/History/dt/global energy,12wrench shapes and grasp
Optuna. Original Beam/Curved/History/Birth sources and Golden unchanged.
The entire ReGrip objective is NOT marked complete. Remaining work is real
development,not merely documentation or another completed-Hermite rerun.

## Newest scope correction — research NOT complete

Actual fixed-patch projected-cubic100/200/400step runs and repeated200run are
complete. Base→quarter x/y.0049881%,loss.0155430%PASS.1%;this is NOT moving3D
grasp certification. Newmark cached acceleration was checked against actual
SDK cpp;matrix residual<=9.23e-14,discrete energy residual<=5.18e-24Fmm.
Full gripper energy/pressure work and100mm grasp Optuna remain BLOCKED.

Noncollinear projected-cubic100steps:TIMEOUT480s,60commits,not PASS. The
normalized gap/direction alternative passes independent phase/state and five
strict loss references;linear version has an actual8192cell API-budget FAIL.
Cubic version actual API PASS but first dynamics FAILS at step11. New bounded
shape-preserving-gap implementation is being evaluated;no completed dynamic
success should be inferred until its actual summary exists. Older statements
below that snapshots were never deployed are HISTORICAL,not current facts.

All three-finger Mesh/History/dt/full-cycle energy/12wrench/shape/graspOptuna
qualification remains unfinished. No original physical tolerance changed.

## Newest measured vector checkpoint — overall objective remains unfinished

PASS in scope:600circular-return states;normal transport/isometry;12step
noncollinear function history/dense plastic reference;function rigid covariance;
one-sided material derivatives;actual Matching SDK F/dF/matrix/Data/query/API;
actual fixed-patch100/200step dynamics and separate20step current-source smoke.
Directed Newmark fixed-patch dt/2movement.000833938%,loss.00259944%PASS.1%.
Euler fixed-patch time checks FAIL and remain preserved. dt/4 NOT RUN.

Adaptive snapshot EXPERIMENTAL/FAIL,NOT deployed in SOFA:coarse/fine sample
tests alone were insufficient. The independent withheld-state test exposed a
4.6%target overshoot;stricter internal estimation corrects the withheld error
without relaxing its budget. Strict loss integration still exhausts500000
TOTAL evaluations;latest diagnostic identifies unresolved upper-bound
accumulation,not a measured negative energy or physical engine crash.
50digit point comparison FAILS4of72branch/loss cases near yield;absolute loss
density error1.8261e-29F. No tiny-loss cutoff or fake PASS applied.

No running child/automatic restart should be inferred from historical text.
Current actual processes must be checked. All three-finger/full-shape/global
energy/grasp optimization gates remain BLOCKED/NOT RUN;this fixed-patch model
has no moving boundary,normal compliance,Birth/Death,rigid rotations or6DOF
object. It cannot certify the gripper. New source/binary snapshots are in
results/vector_history_*;old manifests/physical models remain unchanged.

## Newest actual continuation — vector reference,not SOFA approval

Same branch resumed fb6a698,old indices PASS4945/149and34/3. No prior physical
child remained. Independent circular vector-return600states and stateful
function-history tests actually PASS in validation01. Preserved new failures
include unresolved quadrature and a tiny loss17.17%error,corrected only after
analytic virgin yield-front splitting (tolerance tightening alone did not work).
This is fixed-normal/fixed-patch mathematical scope,NOT3D/SOFA/grasp PASS.
Current work is objective transport/general stateful front accuracy and bounded
cost,not a repeat of completed Hermite/mesh runs. All earlier physical FAILs,
global-energy BLOCKED and100mm grasp Optuna BLOCKED remain unchanged.

## Authoritative checkpoint — incomplete objective,not a completion declaration

All physical runs/replay described in the latest PROGRESS/NEXT are completed;
no pending physics child or automatic restart remains. Old "running" entries
below are retained chronology. Prior premature stopping was the agent's own
choice,not evidenced host exhaustion. Actual current trial/policy limits are
documented separately and must not be described as a server/session failure.

PASS in scope:actual Hermite SOFA integration/API/invariants,fine21→41spatial
contrast,original1000nm24s hold/recovery,immutable local-prefix motion/normal
force contrasts,point/recording query purity,source/raw integrity and exact
sealed4s replay. Base index4945artifacts/149blobs;replay34artifacts/3blobs.
FAIL:coarse11→21,small-phase time/history losses,including0vs4.365e-19Fmm
newly resolved prefix loss. Old v1ignored-XML profile PASSs are INVALIDATED.
BLOCKED:qualified total physical energy and100mm grasp Optuna. NOT RUN:new
12wrench/shape/full-recovery qualification of the refined model and3D SOFA
integration of the new stateful scalar history reference. Overall EXPERIMENTAL.

Last validated physics/reference source:a5703beff2839d0feea9f8174e862e645948871f.
Replay source:a543bc4c84896028e06e9896c1b4c05e1c14fcf4. Packaging commit is
`git log -1`;source indices deliberately avoid self-referencing SHA claims.
First unfinished development:objective vector yield-front/material-history
function,not another rewrite of ConservativeBeam or the completed Hermite map.

LATEST IMPLEMENTATION:independent PatchRefinedContact v2,actual registered
SOFA Data/API/FD PASS,empty-vector4s parent X/V/Rexact. V1local profiles are
INVALIDATED (Unused Attribute);their original raw remains. V2actual grids
528000/624000states confirmed;local4s profiles are running before bounded
prefix contrasts. Original1000nm full24s also running. See TOP of NEXT for
the current processes/paths rather than old "running" chronology below.
Global goal is NOT complete;physical thresholds/old failures remain intact.

NEWEST:actual Hermite implementation and11/21/41dynamics are completed.
New phase-grid21→41spacePASS;full-cycle time loss.0682459%PASS.1%,history
loss.06299997%PASS1%,repeatX/V/R0. Additional small-phase time/history FAILs
remain;full grasp/energy qualification and100mm graspOptuna remain BLOCKED.
Actual read-only24s point traces both PASS,showing narrowly localized yielding;
at7.2s only8/813coarse and12/1623fine active points carry plastic loss.
v15observer8s160.047s PASS,physicalX/V/R0. Latest live-work/restart details
are at TOP of NEXT;historical running statements below are retained chronology.

The prior stop was an agent-selected campaign checkpoint, NOT an observed
session timeout or exhausted system resource. It did not complete the user's
research objective. Development has resumed; the historical checkpoint below
is retained as history, not the current curved-contact status.

- Actual new `CurvedMaterialContact` SOFA integration: implemented, clean-built,
  dense-map/API/FD/objectivity/action-reaction tested; ConservativeBeam unchanged.
- Actual 11/21/41-node dynamics completed. Inherited all-node connectors/cable
  routing changed physical hardware with mesh; separate controls expose this.
- Fixed hardware plus derived uniform-density tributary masses: 11→21 motion
  1.597823% FAIL;21→41 .423918% PASS against unchanged1% criterion.
- Strict-FP native compilation of unchanged kernels: actual path equivalence
  PASS. One runtime pair at21nodes: history .0025→.00125 motion/loss PASS1%;
  repeat/recovery PASS. Half-dt motion PASS .1%,plastic loss .160535% FAIL .1%.
- Quarter-dt full18s: ACTUALLY COMPLETED1101.416s under the one recorded1320s
  exception(4GiB retained). FAIL:global moment relative residual .001031812
  exceeds .001. Half→quarter motion/loss differences pass,but the underlying
  physical failure forbids qualification. Base→quarter loss .196644% also FAILS.
- Checkpoint v2/v3: FAIL trajectory equivalence despite exactly restored force
  and Jacobian. Public first-step MBK/RHS/solution errors1.735e-18/0/1.098e-25
  support assembly roundoff amplification. Not used for physics qualification.
- Actual synchronized8s journal:48000stage rows,X/V/R exactly unchanged;
  kinetic algorithmic residual ≤1.4751e-20. NOT global stored-energy closure.
- New discrete radial-return energy identity:2000independent states PASS;
  actual16000step pre-Commit identity residual2.63344e-26,X/V/R exactly unchanged.
- Independent structural-only compensated summation contrast is now running:
  actual5000step scope test PASS(object,all rotations,roots,velocities exactly
  untouched). Actual18s hold at base/half/quarter dt PASS;global moment relative
  1.99483e-5/3.22488e-5/6.21926e-5 versus1e-3. Actual24s repeat/recovery PASS.
  Base-dt loss still FAILS time convergence;half→quarter motion/loss PASS.
  This is a21node half-dt candidate,not full-grasp certification.
- Its own same-half-dt11/21/41and fine-history revalidation is active.
- Energy observer has been moved AFTER live structural summation and BEFORE
  history Commit using public scene APIs. Actual1s/8s X/V/R differences0.
  Same-run Beam/normal/layer projections,algorithmic cable work and contact
  return accounting reduce8s derived residual to4.51719e-13;remaining after
  explicit potential remainders -6.22707e-14. Not yet global qualification.
  New Frame pressure-return audit passes actual1s;full24s journal is RUNNING.
- Full12wrench certification,global energy,100mm grasp Optuna remain BLOCKED.

Current raw: `results/autonomous_20261116_curve_a01`,
`results/autonomous_20261116_full_native_a01`,
`results/autonomous_20261116_checkpoint_a01` (plus explicit native/scalar controls).
Last committed source checkpoint: `0c6cb77`;additional energy/integrator work is active.

## Latest actual checkpoint (supersedes RUNNING lines above)

- Same-half-dt fine21→41mesh and fine history PASS1%;coarse11→21FAIL1%.
- Full24s synchronized journal completed;X/V/R unchanged,remaining signed
  residual-1.45037e-13;global energy still BLOCKED,not a success certificate.
- Whole contact-cycle loss time convergence FAIL even when hold loss passes.
- Integer-index clock implemented/tested. Actual base24/half24/quarter18
  completed;all original hold gates PASS,base/half recoveryPASS. Fixed clock
  does NOT resolve full-cycle loss(half→quarter.441979% FAIL.1%).
- Actual public solved-MBK probe4s PASS query purity,initial sampled damping
  minima positive.17.1srelease probe RUNNING;coupled negative-damping hypothesis
  not established. No physical damping modification.
- Event-aligned release-only time refinement is a NEW integration-grid
  experiment. Unit/clean buildPASS;4sactual prefix testRUNNING. No inherited
  full time certification. Native3D/12wrench/energy/grasp Optuna remain blocked.
- Actual raw:results/autonomous_20261116_fixed_clock_a01 and
  results/autonomous_20261116_event_clock_a01,in addition to prior campaigns.
- No automatic restart is installed or assumed. Check actual results before
  resuming;existing output names are deliberately refused.

## Latest measured results (supersedes earlier active-process statements)

- New nonuniform grid actual24s coarse/fine,41nodes,finer material sampling,
  repeat all completed and pass original physical hold/recovery. Full-cycle
  time loss.0682459% PASS.1%;fine space comparisons/repeat PASS.
- Additional phase-resolved time/history loss still FAILS;all flags and tiny
  absolute errors are retained. No global grasp/optimization approval.
- Initial variant comparator used different dt;old FAILs preserved. Actual
  SAME-grid .5s controls show exact X/V/R equality;v2physical reanalysis of
  existing full raw passes without rerunning or loosening limits.
- Actual new-grid coarse24s energy journal840.463s,X/V/Rexact,remaining
  -1.55243e-19 after separately derived signed terms. NOT full physical energy
  certification. Fine24s BLOCKED by1986.658s profile forecast versus1320s policy,
  attempts0;this is not a server-forced failure. Unknown pressure fields NULL.
- Research continues:read-only per-point24s SOFA traces and exact cable-query
  reuse. Frozen100state API plus1s actual path tests pass;8s test RUNNING.
- Mathematical slip-band reference shows why small force error need not imply
  small loss error;it is NOT a completed 3D adaptive history implementation.
- No object-pose correction was introduced;plasticity bins show a decaying
  transient rather than a proved permanent roundoff-creep floor.
- Final goal remains incomplete;12wrench certification and100mm grasp Optuna
  stay BLOCKED/NOT RUN rather than inferred from this single +Tz research case.

## Historical checkpoint 2026-11-15 (not current model certification)

Branch `development/regrip-autonomous-research`; baseline63970172ad196e0add3ad42a67ccaee4c7a8975e.
Raw campaign `results/autonomous_20261115_a01`,compiled physical component
`build/autonomous_20261115_a01/v3/libReGripMaterialPointContact.so`.
See FINAL_REPORT and manifest for final source checkpoint and exact hashes.
Validated source checkpoint:456d83f2f36fb0e64deabac91341c636681af36d.
New campaign integrity:PASS894SHA256artifacts. Raw1173017042bytes,external only.

| Scope | Result |
|---|---|
| Historical source/raw/binary integrity | PASS1845entries,old physics preserved |
| New immutable material-point component clean build/API/FD | PASS |
| Actual plastic Commit versus observed plastic | PASS,exact equality |
| Same-hold loss history convergence | PASS .129703/.279753/.049621% vs1% |
| History motion .01→.005→.0025 | FAIL4.61737/1.01697% |
| History motion .0025→.00125 | PASS .0300247% |
| Mesh11→21→41 motion | FAIL4.95984/2.80102% |
| Fine dt-half motion/loss | PASS .0977366/.0999735%,borderline.1% |
| Half→quarter-dt motion/loss | PASS .015950/.074528%,679.15s actual run |
| Base→quarter-dt motion/loss | FAIL .113702/.174427% vs.1%;time qualification incomplete |
| Hold force/moment relative residuals | PASS local1e-3 |
| Repeat | PASS,hold motion/loss exactly reproduced |
| 24s recovery | PASS base/fine-repeat;not fully tested by18s cases |
| Independent curved-contact pullback | PASS60states,NOT SOFA-integrated |
| Global energy closure | BLOCKED |
| New12wrench/full-shape certification | BLOCKED by convergence/energy |
| New100mm grasp Optuna | BLOCKED;0new trials,no fabricated Pareto |
| Native surface/new GUI | NOT RUN;prior independent research unchanged |
| Continuous-contact long-soak/no-leak certification | NOT RUN;bounded samples EXPERIMENTAL |

Largest remaining measured blocker is Beam/contact spatial convergence.
Plastic-state consistency improved;it does not repair spatial kinematics or
complete the synchronized global energy/work journal. No real material
measurements or actual gripper performance are certified. Research fingers
still have explicit planar guides and the~95.15mm base-radius assumption.
## 2026-11-18 — passive owner profiling through880

Actual same-DLL profile875: nine physical CSVs EXACT, nested owner geometry
1.35145s/step and material force/Hessian0.550743s. Query-local precision-value
reuse877/878 retained physical CSVs879 and audit880, but actual wall time
4.89190s versus4.22901s: NOT adopted; original selector restored. Evidence and
compile failure876 preserved. Functional commit c565ac9. See
THREE_FILM_COST_20261118.md. No new wrapping/lift/full-energy PASS.
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
## Checkpoint 2026-11-19 — precise 1ms and mechanical limitations

Actual SOFA1743/1744/1745 completed40/80/160 steps with SAME binary and
STRICT1e-12 state/stage agreement. All-common-output state/shape1747 PASS:
maximum0.0201771235% against0.1%. Offline same-law force/Hessian replay1777
also PASS800 comparisons:worst0.00122270019%,absolute5.62252e-13N.
This is single-film NO-object1ms evidence,NOT3-finger contact/grasp qualification.
Partial signed energy residual1748 remains FAIL198.74477%;root workNULL.
Old Newton1e-24 failure remains preserved;explicit numerical plan is not its cure.

Independent static constrained designs retain identical core volume/material/
tension. Guide profile4.5mm,outboard8mm reaches100uN and statically unloads,
but whole sampled-load wire clearance FAILS:actual-sphere gap−0.111806mm.
Outboard10mm only completes through80.3086uN;full100uN solve FAIL.
Its sampled-prefix wire gap is+1.41313mm,NOT a full-load qualification.
Both fail skin half-thickness clearance by about0.015mm. One contact row is
NOT continuous coverage/contact area/wrapping. Pressure/holding loadNULL.
No final design selected;NO lifting,friction,self-collision or Optuna PASS.

New diagnostics1776 reconstruct the failed-stage mechanical Hessian from the
saved Newton matrix:reconstruction relative2.15448e-16,mechanical condition
estimate~9.33e10. This differs from dynamic Newton matrix condition~548.6;
diagnostic symmetrization was never fed back into physics.

Latest detailed results and exact reproduction commands:
[precise validation](REGRIP_PRECISE_TRANSMISSION_AND_GRASP_VALIDATION.md).
Actual reuse build:build/precise_plan_20261119_plan_actual1743/.
Raw:results/autonomous_film_20261119_precise_actual_force_time1777/,
results/autonomous_film_20261119_precise_static_thickness1770/,
results/autonomous_film_20261119_precise_static_wide10_compare1775/.
Next development:thickness-aware contact plus consistent initial mounting,
then profile precision/time qualification BEFORE new3-finger integration.
Do not splice precise model into legacy56.4ms checkpoint1644.
No SDK changes,remote push or automatic post-session execution.
