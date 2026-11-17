# Three films / one free sphere: separated birth and impact

This is NOT project completion or a grasp certificate.
Source baseline3dbd0fc with immutable per-campaign archived changes.

## Implemented and independently checked

models/film_three_finger_event reuses existing single-film free-midpoint blocks,
ONE shared rigid mass/inertia,existing C2 ControlProfile,ManyRowImpact and
Lobatto persistent rows. No old solver/material/SDK replaced. Plastic normal
impact(restitution0,frictionless) is a NEW explicitly scoped research assumption.
No multistep stencil crosses the discontinuity;this coupon uses midpoint then
Lobatto,NOT a new BDF2 certification.

953 independent free blocks PASS:momentum1.31695e-18Ns,endpoint-family q/v
derivative FD relative errors1.67e-8/6.08e-8. Unmatched mass negative control
rejects. Three physical film blocks and one body,not three body masses.

957 independently isolated bracket birth PASS.958 adds compressive remainder
PASS. Public exact nodal masses used in actual comparison960/964.
Impact time9.99600359471515e-5s,gap-3.55e-15mm,18 rows/rank3.
World linear impulse balance8.875e-21Ns and angular3.849e-23Nmm s in exact-mass
reference. Plastic impulse work9.38172884e-10Nmm,not a force peak or damping.
Duplicate shared-edge rows are retained;their individual multipliers need not
be unique. Velocity and total impulse are the tested physical observables.

962 whole960-triangle relative quadratic numerical-path earliest event PASS:
time9.99600399106119e-5s,18rows,endpoint mismatch3.24e-14mm.
This time differs from the reintegrated partial-interval nonlinear family.
Do NOT claim globally earliest nonlinear endpoint-family CCD. Actual owner
still requires an externally isolated signed bracket[50,200]us.
961 failed because the TEST retained a dangling Eigen expression to a temporary
world point;explicit evaluated Vector3d fixes it without tolerance changes.

## Actual SOFA

960 and964 COMPLETE with actual public mapped masses,three fields and ONE
unconstrained Rigid3. Old persistent component remains separate. New component:
ThreeFilmBracketedEventODE.200us total,initial stationary unstrained films,
sphere z offset+.0001mm,vz=-1mm/s,gravity0,Fz=-.001N. This is NOT C2 closing
from rest. Existing C2 Tmax=.0001N per rail,ramp.01s remains active.
No pose/velocity projection,normal clamp or fictitious balancing force.

Actual event q/v/impulse/time AND final q/v match exact-public-mass reference
exactly.960 runtime17.6778s;964 with row observer16.8428s(one pair,NOT a speedup
claim). Remainder whole-stage gap-1.07e-14mm,momentum8.52437e-20Ns,
normal-velocity residual2.75054e-13mm/s. API mapped q/v and free body writes
are checked against the accepted solve before journalling.

964 owns each actual impact row with finger/triangle/feature/J/normal/point/
pre-post velocity/impulse. Native row IDs are not reused. The old continuous
row journal is empty for this coupon and is NOT claimed as force measurement.
959 invalid final-base inheritance and963 wrong contact member compile failures
are preserved. Neither is a physical run.

Build:build/three_film_event_20261118_three_film_event_rows964/
libReGripThreeFilmEvent.so. Sources,SDK ldd,binary/raw hashes in964 summary.

## Remaining tasks and safe next run

Independent actual row/mapped/end-surface audit965 follows964. Next:short
repeated compressive contact with the SAME free body/C2,then time refinement.
Release/re-impact,generic endpoint-family earliest event,full-thickness
clearance,friction,self-collision,full energy,wrap/lift/hold remain unqualified.
No contact area/pressure/holding force inferred from row count or angle.
Material constants are research assumptions;no measured PET/actuator claim.

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/film_three_film_event_sofa.py --tag NEW_UNIQUE_THREE_FILM_EVENT
```

Runner uses exclusive outputs,archived sources,exact recorded public mass,
bounded reference/build/run and4GiB/480s. Never rerun archived scene paths
directly. No automatic continuation or OS exhaustion is claimed.
