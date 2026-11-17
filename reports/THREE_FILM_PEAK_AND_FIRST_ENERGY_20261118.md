# Actual first C2 peak and first-impact interval inventory

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


This checkpoint is NOT a final grasp or full physical-energy certificate.
Every measured value below is classified by its origin.

## Actual SOFA to10ms

1002 actually completes50x200us in193.40398s,forecast404.9591s below480s.
Three actual FilmRailTendon states/masses,ONE free Rigid3,proper fixed mounts.
Research assumptions:film100mm,root-centre radius50mm,sphereR30mm plus.01mm
midsurface buffer,film1g each,sphere100g,gravity0,Fz=-.001N.
C2 Tmax=.0001N PER RAIL,ramp10ms,release20–30ms. Common input is not a
physical tendon equalizer. Initial sphere z offset+.0001mm,vz=-1mm/s;not
closing a stationary object from rest. No friction/self-contact/layer jamming.

Minimum whole-stage buffered gap-1.10134e-13mm,momentum max8.52437e-20Ns,
normal-velocity residual2.75054e-13mm/s. Geometric/force residual gates retained.
1004 independent mapped/end-surface/used-impulse audit PASS.
Actual scale1 images/OBJ in1004,actual width profiles1003:
skin centre-node tip+.000662151mm but width-mean tip-.02496388mm;
rail width-mean tips about-.101045mm. NOT wrapping/lift/holding evidence.
Contact area,pressure and holding load remain null/NOT MEASURED.

## Absolute API gate error discovered and corrected

Original inherited absolute state API gate is STRICT <1e-12.
Three new runners mistakenly used1e-11;source predicates are restored.
1006 independently re-audits all completed continuations WITHOUT changing Raw:
966 and978/979/980/986/993/994 still pass1e-12;1002 versus original reference
1000 FAILS(v3.82804899e-12,q1.11e-16). Its original loose-runner PASS is
preserved but MUST NOT be used as qualification.

Independent nonlinear FEM1008 uses ONE compiled binary to isolate ONLY the
floating input clock:accumulated t+=dt versus multiplied step*dt. No SOFA state,
force or velocity is injected into reference integration. All other inputs,
exact public masses,algorithm and C2 law unchanged. Both complete50 steps.
Accumulated clock:q/v EXACT to actual1002;multiplied clock reproduces exactly
the original3.82804899e-12 velocity difference. Clock discrepancy only
6.07153e-18s but relevant to strict bit-level stiff-dynamics comparison.
Runtimes145.45/147.59s(each bounded480s/4GiB).

1009 hash-bound same-actual reassessment checks archived kernel headers,
plugins,physical XML,masses/control proof and all Raw;STRICT1e-12 PASS with
q/v/time differences0. No tolerance/actual force/state changes.
This is NOT a new SOFA execution and does NOT erase1006 or full-time997 FAIL.
Future independent-to-SOFA comparisons default to accumulated input clock;
multiplied mode remains an explicit counterfactual.

## Source-corrected force generator observation

1005 initial extra generator audit FAIL assumed T*L. Existing Kernel.h actually
uses T*(L_current-2*100mm). This is a force generator,not stored elastic energy.
1007 corrects only the observer definition;old1005 remains FAIL. Stored/kinetic
inventory,mechanical -integral T*dL and signed residual are unchanged.
Actual endpoint control mismatch0N,stored/film kinetic callback error6.10e-20Nmm.
Interval200us..10ms:stage tendon work9.80103177e-5Nmm,
signed residual-3.87613e-12Nmm. First interval was not included in this ledger.
Residual is not heat;full physical energy remains BLOCKED.

## Actual first free/impact/remainder journal

1010 implements opt-in firstIntervalJournal,default OFF. Same DLL OFF/ON actual
trials both COMPLETE16.57/17.06s. All ELEVEN physical CSVs byte-identical
to each other AND prior964,including forces/impulses/states/displacements.
Added journal contains7 actual accepted-stage records:
initial,free midpoint,pre-impact,post-impact,remainder initial/midpoint/end.
Weights sum exactly200us. No new force/velocity/position correction.

1011 independent full-AD inventory of those ACTUAL recorded stages:

| Term | Nmm |
|---|---:|
| Stored+kinetic change |1.59156280008e-7|
| Tendon mechanical work |5.74839650396e-16|
| External work |2.00158100406e-7|
| Rayleigh damping work |4.00636480748e-8|
| Normal constraint work |-4.59748335431e-25|
| Stable plastic impact loss |9.38172883664e-10|
| Signed residual |-1.38829341120e-17|

Actual-field stored/film kinetic error1.07e-27Nmm,stage and endpoint control
errors0N. Kinetic subtraction minus stable impulse loss=-1.14432e-20Nmm is
a numerical inventory,not additional heat. Root reaction work remains null:
ideal fixed/mapped-root virtual-work assumption is not an independently
measured reaction journal. This is a first200us coupon ledger,NOT FrameLayer,
pressure,friction,fullcycle or total-gripper energy qualification.

## Independent timescale evidence,not a mode or real material measurement

1001 nonlinear FEM Hessian at stress-free T0 uses an admissible quadratic
film trial and shared body translation satisfying all3 contact-tangent rows.
Rayleigh quotient omega=.0602317rad/s,conditional lowest undamped bilateral
period lower bound104.317s. This is NOT an eigensolve,dominant forced mode,
actual wrapping duration or damped response prediction. Film kinetic fraction
of this trial=.001629;100g sphere dominates. It shows why a10ms diagnostic
cannot by itself establish slow full-gripper adaptation or a failed route.

## Still unqualified

997 overall post-time FAIL(legacy work.7214%,normal-work residual relative
FAIL);event/impulse time refinement,nonlinear earliest-event completeness,
mesh/history,physical-thickness clearance,general friction,self-contact,
deformed release/re-impact,wire-driven wrapping,holding/lift,12wrench,
multimaterial and Grasp Optuna.999 weak pull-away release hypothesis FAIL:
the deformed state still needs positive normal reaction. No fictitious
ungrasp operation was applied.

## Exact safe commands

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/film_three_film_clock_qualify.py --tag NEW_QUAL --proof 20261118_three_film_clock_reference1008
$PY tools/film_three_film_first_inventory.py --tag NEW_INV --case 20261118_three_film_first_journal1010
# Actual reproduction only if needed;both exclusive NEW output paths:
$PY tools/film_three_film_horizon.py --tag NEW_REF --clock accumulated
$PY tools/film_three_film_peak_sofa.py --tag NEW_ACT --reference NEW_REF
```

Reuse actual peak DLL:build/three_film_peak_20261118_three_film_first_peak_actual1002/
libReGripThreeFilmEvent.so. Current first-journal DLL:
build/three_film_first_journal_20261118_three_film_first_journal1010/
libReGripThreeFilmEvent.so. Source/binary/SDK and generated scenes in campaigns.
Do not rerun archived scenes into existing outputs. No automatic continuation
or OS/RAM exhaustion is claimed.
