# Bounded1ms early/late numerical plan

Separate `FilmPreciseSolverPlanODE`, not a change to the qualified200us Owner.
Same precise tendon/attachment potential, actual public mass, root mapping,
zero initial state, C2 input and four-stage Gauss collocation.

- First200us: eight private microsteps per public interval, Newton1e-24Ns.
- Later interval through1ms: one Gauss step, Newton1e-22Ns.
-40/80/160 public steps. Accumulated clock and actual stage input are retained.
- No state, velocity or clock correction and no multistep history at transition.
- This is an explicit numerical candidate; it does NOT repair or relabel the
  old1e-24 failures, and it does NOT relax the1e-12 API/.1% time physical gates.

1737 completes the independent three-resolution run;1740 checks5280 state/shape
observables at ALL common public times and passes.1%,worst.0201771235%.
This is NOT between-output continuum accuracy, energy, contact or grasp PASS.
See the research report for actual SOFA and energy evidence, including failures.

The independent plan CSV's transition-zero columns are invariant annotations
(the const selector cannot access state), NOT a measured resume/API comparison.
Actual SOFA-vs-independent ALL-state comparisons are performed separately.
