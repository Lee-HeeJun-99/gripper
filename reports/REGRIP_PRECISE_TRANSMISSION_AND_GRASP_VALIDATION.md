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
