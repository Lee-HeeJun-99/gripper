# Bounded contact-admissibility reintegration

`EndpointControlledRows.h` is separate from the unchanged `persistentRows`
law. It discards an entire uncommitted step and integrates two smaller
intervals if whole-surface penetration exceeds1e-10mm or an active stage's
absolute gap exceeds1e-10mm. The latter also rejects an artificial positive
gap while a compressive multiplier is retained. Endpoint drift is caught
ONLY when the existing endpoint observer identified that exact rejection.
Unilateral release,ambiguous supports,singular geometry,Newton/line-search
failure and other exceptions propagate unchanged. No q/v projection,
negative physical reaction,force correction or tolerance change is used.

The maximum63attempts/depth5 is an algorithm budget,not an OS resource limit.
The second subinterval ends at the original accumulated endpoint;durations
and stage times are retained. Failed recursive calls do not commit to SOFA.
This is NOT an error-controlled temporal integrator or a general active-set
contact solver. A new impact/release requires a separate physical transition.
Momentum/normal-velocity gates remain1e-17Ns/1e-10mm/s.

1466 circular point-contact test:analytic trajectory error3.58e-12mm;
15attempts,7stage rejections.1477 also covers a nonquadratic sine curve:
3endpoint/4stage rejections,max gap8.33e-11mm,numerical RK4-reference
position error1.96e-11mm. That reference is NOT an analytic solution;
10k/20k RK4 refinement differs5.25e-15. Release and budget guards tested.
1463 line-search fixture FAIL,1464 incorrect endpoint-count assertion FAIL,
1475/1476 positive active-stage gap test FAIL are preserved.1477 fixes the
positive-gap acceptance omission with a STRONGER check,not a relaxed test.

Actual lateral3film/free Rigid3:1469 reaches23.2ms and1472 reaches23.4ms,
all q/v,internal stage force/state/time EXACT to standalone reference.
Those binaries predate the additional positive-active-stage guard;their
actual stage gaps are small,not evidence that all future stages satisfy it.
1480 separately source-bound stronger-guard actual replay PASS,all internal
stage q/v/force/time EXACT to standalone reference.
1470/1473 longer reference FAIL because124→117 contact birth occurs.
1473 observes old124reaction positive at23.5ms and new117negative endpoint
trial reaction:do NOT interpret that rejected trial as physical release.
Independent isolated6-row transfer1478 passes at23.503224464179916ms.
1481 ACTUAL transfer PASS:same event/state/impulses EXACT.1483/1486 actual
post-transfer to24.4ms PASS narrow gates,not a global CCD/time/grasp proof.

The original time/energy FAILs remain. Numerical normal-work defects are
not Coulomb heat. Root reaction work/full energy/friction/grasp remain blocked.
