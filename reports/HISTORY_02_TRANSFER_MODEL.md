# HISTORY 02 — material-node research model

Status: **PASS bounded kernel/API checks; EXPERIMENTAL complete history model**.
Original `StickSlip`, `AdaptiveContact`, Beam and golden data are untouched.
New component: `MaterialHistoryContact`, `models/contact_history/`.

History is stored at fixed reference-material nodes per beam edge, separately
from force integration points. Runtime topology/physics changes are rejected.
All history vectors are in the object's material frame. With shortest normal
transport T, query interpolation is

`e(s) = (1-alpha) T(n_left,n_s)e_left + alpha T(n_right,n_s)e_right`.

Each neighbor is transported BEFORE interpolation. Antipodal normals are guarded;
no arbitrary rotation axis is used. Active-domain boundaries have zero extension
anchors; inactive material does not inherit stale state. Lost-domain stored
energy is integrated as detachment dissipation, an explicit model assumption.

For one time increment, `delta = local_new-local_old`, the trial extension is

`e_trial = T e_old + [T P_old delta + P_new delta]/2`.

Return mapping uses `C=mu*kn*(skin-distance)`, `|kt*e|<=C`, with equal static and
kinetic coefficients. Plastic dissipation is `C*|e_trial-e_returned|`.
This is elastic penalty stick, NOT an exact zero-slip constraint. The symmetric
chord approximation is not an exact curved finite-rotation trajectory.

60 random smooth states: value-only/AD agreement 1.735e-18, Jacobian FD maximum
5.593e-9, action-reaction moment maximum 1.735e-18. Global observer rotation
error 6.592e-17; prescribed circular path extension error decreases by ~4 per
step halving. Queries are pure; only AnimateEnd commits history, once per engine
step. Force, derivative and energy queries do not commit. Endpoint, detach,
recontact reset and runtime-cache guards are tested.

Limits: this is NOT a general conservative remapping theorem. Changing the
history grid requires a fresh trial. Newborn material still resets at the end
of the crossing step. No full energy closure, arbitrary patch merge/split
certificate, surface-area contact or calibrated PET friction is claimed.
