# Three-film shared C2 continuation — 2026-11-18

## Latest actual qualification through930 — FULL LISTED TIME GATE FAIL

Original16/32-step actual911/912 COMPLETE but API comparison FAIL against
reconstructed default masses:v1.84386e-12/2.62190e-12mm/s,gate1e-12 unchanged.
Actual public mass journal917 and same-DLL passive9CSV919 PASS. All693 nodal
mass doubles differ from reconstructed model by at most2.886e-16 relative.
Same-binary one-factor924 proves the cause for16steps:public-mass reference921
q/v EXACT actual911;default-model reference922 reproduces original discrepancy.
Public-mass8/32 references920/923 also q/v EXACT corresponding actual states.
Reassessments925/926/928 preserve original FAIL/Raw;they correct REFERENCE
INPUT,not actual dynamics,state,tolerance or physical force. No new actual
16/32 run is claimed by these reassessments.

Actual same-DLL8/16/32 time930 remains **FAIL**,including both endpoint force
and legacy sampled cable work. Base8→quarter32:

|observable|relative error|gate|
|---|---:|---|
|film velocity|0.06924025%|PASS0.1%|
|attachment energy|0.06749809%|PASS0.1%|
|endpoint normal force|0.13674960%|FAIL0.1%|
|common-window contact force|0.07798805%|PASS0.1%|
|stage-consistent tendon work|0.02431016%|PASS0.1%|
|old field-sampled tendon work|0.89573518%|FAIL0.1%|

16→32 endpoint force PASS0.00773146%,but old sampled work FAIL0.18348498%.
No adjacent/base-quarter FAIL is removed. Independent subset910 PASS does NOT
replace this actual force/work assessment.

Actual-state energy/power observers913/927/929 reuse routed cable derivatives:
positive tendon work=-integral T*dL,existing C2 stage T,physical rail endpoint
AND guide force gradients. T*length is NOT stored cable energy. Signed energy
defects-5.60e-9/-3.57e-10/-2.30e-11Nmm are numerical diagnostics,NOT heat or full
energy certification. Legacy FF work is endpoint trapezoidal Stieltjes sampling;
the new Lobatto stage-power integral is separately named,not silently substituted.
Actual16/32 wall times63.14/122.23s;not OS/session exhaustion.

Exact order900–903:recorded113/334bit disagreement at898 resolved using rational
arithmetic on EXACT stored binary doubles (positive2.595e-43mm² difference).
Opt-in fallback only on unresolved floating comparison;zero rational tie still
uses original independent-support rejection. No altered gap,normal,force/Hessian.
Actual exact-order8-step904 PASS.907 and895 directories with observer reuse
identity rejection are diagnostic setup failures,not physics results.

Next:remove proven duplicate readonly journal geometry work,validate exact
CSV/force/time and wall cost;then finer force/work qualification within measured
runtime policy. Actual wrapping/impact/release/friction/lift remains NOT RUN.

Research assumptions: same rectangular three-film/ONE free sphere geometry,
root-centre50mm,R30 sphere,constant externalFz=-.001N,Rayleigh mass2,
frictionless and no self-collision. Existing ControlProfile is reused, not
duplicated. NEW prescribed input: maximum tension.0001N PER RAIL,
ramp.01s,release begins.02s,ends.03s,C2. The10ms already-touching REST pilot
is NOT original4s closing, initial separation/impact, wrapping or grasp.
No actuator capability or measured PET/TPU claims.

## Independent nonlinear FEM

- 881 four-step10ms FAIL at fourth interval. Completed three rows are not a
  full trajectory PASS.882 diagnostic archives preserve rejected stage q/v.
- Recorded midpoint t=.00875 whole gap-2.56736854e-10mm;owned gap agrees.
  Endpoint gap+9.27578014e-11mm. Original minimum gap gate-1e-10mm unchanged.
  This fixture indicates integrated stage-position drift, NOT missing candidate
  geometry alone. It does not establish the cause of all historical failures.
- 883 uniform8-step PASS,27.2027s. No time-convergence certification from this.
- 884 compile FAIL (duplicate function fragment), preserved and corrected.
- 885 gap-controlled4macro-step PASS,24.5272s. First three intervals unchanged;
  only final coarse uncommitted interval is rejected and reintegrated as halves.
  Five accepted leaf steps,one rejected attempt;final interval min gap
  -3.48663320e-11mm. No position/velocity projection, force correction or relaxed
  tolerance. Other geometry/solver exceptions still propagate. Depth4/attempt32
  are algorithm policies, NOT OS memory/session exhaustion.
- test_gap_controlled_rows PASS: plane unchanged,no-split;explicit MOCK predicate
  tests reject/reintegrate transaction,budget and nonfinite rejection. Mock is
  not presented as a physical contact Reference.

## SOFA integration scope

ThreeFilmDrivenODE reuses ThreeFilmPersistentODE's actual public masses,
state mapping,shared1953-DOF system,current-normal geometry,strict Lobatto and
once-only commit. Separate component checks exact8-step10ms C2 pilot parameters
on ALL three FilmRailTendon fields. The original T0 owner keeps its guards.
Applied tension at every implicit stage comes from the SAME existing
ControlProfile with those actual field Data.886 registration FAIL: different
component names incorrectly shared one registration object;fixed via separate
public factory registrations.887 actual PASS,32.8157074s;q error6.93889e-17mm,
v error3.94351e-13mm/s versus independent883.888 used-row/whole-stage audit
PASS,min gap-3.25926e-11mm,unit-row moment1.55407e-14mm.889 actual accepted
field tensions exactly equal independent existing ControlProfile values.
Final body dz=-.000496664mm,local tip z=.000654073mm. These are tiny motions,
NOT wrapping/lifting. Field-sampled tendon work9.70714360e-5Nmm is an inventory,
NOT independently quadrature-qualified work/energy certification.
Actual scale1 PNG/OBJ:results/autonomous_film_20261118_three_film_c2_audit888;
control plot:results/autonomous_film_20261118_three_film_c2_control889.
890 defaultT0 owner also actual PASS with new sameDLL. Reusable build:
build/three_film_20261118_three_film_actual_c2_887/libReGripThreeFilmContact.so.

Remaining:actual stage/FF/control equality,driven time/mesh refinement,work,
changing active sets,event/release/self-contact/friction/full thickness clearance,
physical common equalizer,wrapping/lift/hold/free-object grasp,12wrench/Optuna.
