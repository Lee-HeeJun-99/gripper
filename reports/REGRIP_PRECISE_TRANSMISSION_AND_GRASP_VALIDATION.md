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

# Precise transmission and grasp validation —2026-11-19

## Latest completed actual1ms result (1743–1748)

Actual SOFA40/80/160 public steps, SAME binary
`ef4f9ebe2b1746ea7dee15ef9d969291388ea814e9c933b7ecf9961b7fc26064`:
ALL accepted q/v,384/768/1536 stage q/v/forces,actual accumulated clocks and
applied stage tensions match the independent plan EXACTLY (STRICT1e-12 PASS).
Runtime44.723/91.488/167.411s;maximum RSS254168/254336/254024KiB,actual
`/usr/bin/time -v`,not the4GiB policy limit. No SOFA errors;SDK ldd guard passes.
Reusable build:`build/precise_plan_20261119_plan_actual1743/`.

1747 actual ALL common-clock state/shape test PASS.1%:5280 observables,
worst.020177123476%,same recorded interpolation caveats as1740. This certifies
only the declared1ms free coupon output-clock comparisons, NOT contact/grasp.
1748 links every actual state and stage string EXACTLY to offline1742 inventory,
and checks actual Field energies. Component Work/D/U/K all-time comparisons
PASS.1%;signed partial residual remains FAIL198.7447699%,absolute difference
1.1709654e-29Nmm at.475ms. Whole energy remains BLOCKED,root workNULL.
Actual unscaled plot/CSV:`results/autonomous_film_20261119_plan_actual_inventory1748/`.

1746 precise tendon potential Armijo/residual globalization (same physical
force/tangent,not added stiffness) extends free static continuation to61 accepted
load stages. At51.79474679uN/Rail:force residual4.19669e-13N,Skin mean tip
−22.51065574mm,curvature max.0058608205/mm,root-tip.409717499rad. Next load
stage fails Newton60;100uN remains FAIL. This is a free static shape, NOT actual
object contact/wrapping or dynamic stability. Its whole-surface virtual-object
admissibility and fair rail-aspect comparison are separate follow-up evidence.

Fresh same-build actual reproduction:
`$PY tools/film_precise_plan_sofa.py --tag UNIQUE_ACTUAL --steps 40 --reference 20261119_precise_solver_plan1737 --reuse-build 20261119_plan_actual1743`
Finer actual runs require `--profile 20261119_plan_actual1743` and the same build.

## Scope

### Static contact/structure continuation1754–1771

New independent static equations enforce grad(U)-C lambda=0,g>=0,lambda>=0
and complementarity on ALL320 triangle constraints. Multipliers are N,not Ns.
No inertial/damping term from the reused root map enters these equations.
1754 all8 low loads to1uN PASS;1755 all16 load/unload stages PASS,ending with
zero active force rows and positive gap2.82876209e-5mm. This is NOT a dynamic
release/recovery. Callback regression1760 physical states/rows/wrenches/Newton
journals versus1755 is BYTE EXACT. Fixed-object guards in old SOFA are unchanged.

Rest feature ties make the small-step central gradient FD fail:1751/52/53 remain
FAIL (1753 is an identical diagnostic retry,not new physical evidence). Errors
at h1e-6/1e-5/1e-4 are1.34687e-8/3.97588e-8/4.00430e-7. C1 Richardson
2D(h/2)-D(h),h1e-4,passes the unchanged1e-8 gradient gate with4.26204e-10.
This does not qualify a smooth Hessian/IFT at a feature transition.

1756 original100uN static continuation FAIL,last complete80.3085722uN;1757
smaller load-tail increments freshly validate the q/owned-force seed and reach
90.1542861uN,then FAIL Newton30 with residual~1e-12N. No physical criterion is
relaxed. At90.15uN,Skin mean midspan+1.77606mm,tip−5.21571mm:the arch persists
even in static equilibrium,so short integration time is not its sole cause.

One-factor guide profiling reuses the old1431 geometry (old .5mm dynamic
worse-arch result preserved). Same core439.3397918mm3,T,material,root and object:

|Profile/outboard[mm]|Skin mid z[mm]|Skin tip z[mm]|Shortening[mm]|Wire gap to R30.01[mm]|
|---|---:|---:|---:|---:|
|0/6|+1.554737|−4.738094|3.290686|+.019653|
|.5/6|+1.353947|−4.658590|3.345348|−.066015|
|4.5/6|−.264342|−3.471204|5.178679|−.908896|
|4.5/8|−.171552|−3.581020|5.451211|+.209123|

All values are at the same completed80.3085722uN load,not failed final states.
Profile4.5 changes offsets to[9.5,5,.5,5,9.5]mm;outboard6→8 is a second,
separately isolated factor relative to profile4.5/6.1759/1764/1765 original
force/Hessian/objectivity/balance tests PASS. For changed8mm designs the old
zero-amplitude parity is NOT MEASURED;unvisited raw harness counter0 is not
presented as a physical measurement. Extra guide volume/mass and matched work
are NOT certified. Mean normal offset stays5mm,but cable reference length
changes200→203.2141727mm. No efficiency superiority or final selection.

1766 profile4.5/outboard8 completes all64 static loads through100uN with
force residual8.15572e-13N and gap7.10543e-15mm.1768 freshly validates that static
seed and completes64 unload stages toT0,zero active rows,stored energy~1.6e-27Nmm.
NOT a dynamic checkpoint,actual SOFA or elastic-recovery-time certification.

1767 completed force/guide observer,then Python rendering failed due to a
triangle-index variable shadowing argparse. Original observations are preserved.
1769 recompiles IDENTICAL binary/input,then reuses the completed immutable
observation rather than rerunning physics. Static OBJ/PNG uses stored q at scale1;
labels explicitly say independent STATIC FEM,NOT SOFA/wrapping/holding. All
contact reactions remain one point;area/pressure/continuous coverage NULL.

Crucially,the positive wire gap at80.31uN does NOT extend to all loads.1770 audits
all64 profile4.5/outboard8 states:minimum actual-R30 wire centreline gap
−.111805651mm,so the peak wire path is still inadmissible even at zero radius.
The conservative Skin half-thickness envelope gap is−.01500000008mm,and a
constant-current-facet prism proxy gives the same penetration. This is conditional
on that explicit thickness proxy,NOT a measured physical-film failure. Rails
remain clear in that proxy. The declared .01mm buffer does not qualify .025mm
Skin half-thickness. No force/state is corrected to hide this failure.

1769/1770 therefore do NOT approve the wider route as a final design,despite its
equation-level static PASS. Three rotated copies of the fixed-object reaction
give only a CONDITIONAL vertical scale~2e-5N at80uN versus100g weight.981N;
this is NOT a free3-finger holding capacity or lift experiment. General friction,
finite wire/guide solids,full thickness,self collision and actual C2 validation
of the new profile remain required. Historical archive audit1771 verifies107505
inherited Raw/build/design/absolute-SDK files unchanged. Live edited source is
explicitly excluded;this is NOT physics or old live-root equivalence certification.

Track A numerical convergence and Track B mechanical efficacy remain separate.
No new wrapping, holding, lift, free-object/contact or final design PASS is
claimed. Existing three-film56.4ms checkpoint1644 remains immutable and is NOT
continued with this different precise formulation. SDK and remote Git unchanged.
Each campaign below is under `results/autonomous_film_<suffix>/` and contains
compiled source identities, binary hashes, actual commands, raw journals and
process exits. Development source commit is c0a82b9; archived compiled sources,
not an assumption of a clean pre-build tree, identify each development trial.

## Precise mathematics reused

The displacement/reference-exact bond potential and telescoped constant-T
segment-length potential from1679/1713 are reused, not re-derived or refitted.
No Young modulus, bond stiffness, damping, tendon force or boundary condition
was changed to address numerical failures. All material data remain assumptions.

## Newton failure isolation

1726 `20261119_precise_newton_diagnostic1726` adds an opt-in thread-local
observer of ALREADY evaluated Newton state, residual, tangent, correction and
rejected Trial. It makes no force queries. Same-binary observer ON/OFF startup
and failure state/stage/Newton CSVs are BYTE EXACT. The disabled failure CSVs
also match original1724 BYTE EXACT, preserving its failure and accepted prefix.

At the failed step starting0.84999999999999952ms:

- residual1.0807364412707304e-24Ns; requested criterion1e-24Ns unchanged;
- SparseLU linear residual8.90635e-40Ns, correction norm2.38783e-16mm/s;
- last alpha3.0517578125e-5,2577/2596 unknowns unchanged after rounding;
- full alpha also increases residual; no Armijo trial satisfies acceptance.

1729 `20261119_precise_newton_assess1729` analyzes the saved2596-square,
520144-nonzero actual tangent. One-norm condition ESTIMATE548.642, relative
linear residual1.14622e-15, dominant residual is Rail DOF608 at stage3.
Last predicted residual change3.29815e-29Ns, actual7.97384e-34Ns. This supports
loss of locally resolvable Newton decrease, NOT a badly solved linear system.
It does not uniquely identify constitutive rounding versus stage-coordinate
rounding, and is not authority to waive any physical gate.

Alternative hypotheses were actually tested:

| Campaign | Same1e-24 criterion candidate | Result |
|---|---|---|
|1728|Stage velocity increments rather than absolute velocities|FAIL Newton20 at0.85ms|
|1731|Extended AD/assembly initial private build|Compile FAIL, unused transitive geometry min-type mismatch|
|1732|Extended AD/assembly with explicit private helper conversions|FAIL Line Search at0.90ms|
|1736|Extended AD/assembly plus increment variables|FAIL Newton20 at0.85ms|

All diagnostic ON/OFF physical journals remain BYTE EXACT, including failed
prefixes. No failed candidate is adopted as the production remedy.1734 extended
AD original FD/balance/objectivity gates PASS;1739 default-AD regression passes
and its metrics EXACTLY equal1714. Extended AD requires a separate compile-time
ABI and has NOT been inserted into SOFA or the old three-finger checkpoint.

## Explicit solver plan transition

1737 `20261119_precise_solver_plan1737` uses a separate declared numerical plan:
first200us eight Gauss4 microsteps/public interval with1e-24Ns Newton criterion;
remaining interval to1ms one Gauss4/public interval with1e-22Ns criterion.
This is a NEW plan with a separately assessed late Newton setting, NOT a
resolution of the old24-setting FAIL and NOT a physical tolerance change.
Const plan selection cannot modify q/v/time; accumulated stage clocks and the
same C2 source are used. Gauss is one-step, so there is no BDF history to reset.
The transition-zero columns in the independent plan CSV are invariant
annotations, not a substitute for measured actual API identity.

All40/80/160-step independent processes complete,44.482/88.389/158.095s,
each within4GiB/480s. Immutable reference binary:
`1ebdb0cf0acd9860dfda9136244487ee115c0ce9be52a8e9d08c7c184c0084e1`.

1740 `20261119_plan_alltime1740`: ALL common physical output clocks, all-pair
40→80,80→160,40→160 state/shape comparison PASS existing.1% gate.
5280 observables;worst.020177123476% Skin mid total curvature at12.5us,
absolute8.22129654e-51/mm. No absolute floor. Explicit fine-state interpolation
retains raw clocks/states;largest nearest-clock distance3.46945e-18s.
`interpolation.csv` records bracket, alpha and displacement from nearest saved
state. This displacement is NOT a rigorous interpolation-error bound;continuum
between outputs remains unqualified. Energy/work are assessed separately.

## Actual SOFA and energy (separate evidence)

1741 actual plan build FAIL: frozen reference Owner predates the virtual
physicalParts hook/module embedding guard. No SOFA physics ran from that build.
Corrected actual Owner source selection is explicit in the runner; no force
law or installed SDK is changed. See later checkpoint entries for completed
actual1743+ and offline1742 results; do not infer completion from this section.
Actual runs must compare EVERY accepted q/v and every stage force/input with
STRICT1e-12, same binary across resolutions. Root reaction work remains NULL.
Signed residuals are not heat and no partial inventory certifies whole energy.

## Nonlinear static transmission and structural comparison

1727 precise-law free static16-linear-load-stage tests FAIL for all75/100/125um
equal-core-volume rails: first6.25uN stage uses60 Newton iterations without
equilibrium. This is not a proof that the physical structure cannot bend.
1730 changes only numerical continuation to64 logarithmic stages1e-10→1e-4N.
Baseline reaches43 completed stages;at1uN/Rail residual2.10535e-13N (gate1e-12),
Skin width-mean tip−.415758526mm,curvature max.000104248/mm,root-tip.00743566rad.
Target100uN continuation still FAILS at the next stage. NOT a contact solution.

1735 fresh query of this completed lower-load state confirms the force residual,
but its normalized soft-mode directional FD relative diagnostic8.52272e-5
FAILS its declared1e-5 gate. Tangent eigenvalues6.08562e-9..577.57002N/mm
show a very ill-conditioned STATIC compliance, distinct from the dynamic stage
matrix condition548.6. Direct tendon sensitivity Skin0,Rails9.34648;nonzero
indirect equilibrium Skin bending does not imply instantaneous Skin forcing.
No dynamic stability or exact compliance certification is inferred from this
partial witness;the full witness status remains FAIL.

1733 geometric continuation of thinner/thicker rails also retains full-load
FAILs.1738 compares ONLY their highest common COMPLETED load stage40:
T=.5179474679231214uN/Rail,three-finger core volume439.3397917746mm3.

|Rail thickness|Skin mean tip z[mm]|Skin max curvature[1/mm]|Tendon shortening[mm]|
|---|---:|---:|---:|
|75um|−.271528949|.00006837097|.05719681|
|100um|−.215244916|.00005393197|.04371785|
|125um|−.170036658|.00004240893|.03394043|

Same material,core volume,tension,root mapping and force model;different aspect
ratio is one physical design factor. Wire-guide hardware volume is not certified
and equal tension is NOT equal work. Thinner rails bend more but require more
stroke;no final efficiency/superiority/design selection follows. Figure
`results/autonomous_film_20261119_precise_static_comparison1738/static_common_load.png`
uses saved INDEPENDENT nonlinear static FEM coordinates, explicitly NOT actual
SOFA deformation/contact/wrapping. Contact coverage/area/pressure/holding NULL.

## Remaining gates and reproduction

Full-time energy,contact,mesh convergence,real wrapping,holding,lift,friction,
self collision,thickness clearance,physical equalizer,12-wrench and final
design/Optuna remain unqualified/BLOCKED. No old precise-model checkpoint splice.

Use PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python and unique tags:

```
$PY tools/film_precise_newton_diagnostic.py --tag UNIQUE_NEWTON
$PY tools/film_precise_newton_assess.py --tag UNIQUE_ASSESS --case 20261119_precise_newton_diagnostic1726
$PY tools/film_precise_solver_plan.py --tag UNIQUE_PLAN
$PY tools/film_precise_actual_all_time.py --tag UNIQUE_TIME --plan-case 20261119_precise_solver_plan1737
$PY tools/film_precise_plan_sofa.py --tag UNIQUE_ACTUAL --steps 40 --reference 20261119_precise_solver_plan1737
$PY tools/film_precise_plan_energy.py --tag UNIQUE_ENERGY --plan-case 20261119_precise_solver_plan1737
$PY tools/film_precise_static_comparison.py --tag UNIQUE_STATIC --geometric --thickness 0.1
```

No automatic background restart is promised. Current process exits/result JSON,
not an historical RUNNING label, determine completion.
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
