# Matched actual1586/1741 impulse inventory

1813 actual saved per-Finger Skin response rows, same Hold1.6–2s:

| Actual source | Mean Fz per Finger (N) | Peak velocity (mm/s) |
|---|---|---|
|1586|0.324911 /0.327558 /0.328535|[-4.149169,0.070412,-0.008245]|
|1741|0.362190 /0.263109 /0.357852|[-7.171895,16.006477,27.868021]|

Different hardware/mass configurations prohibit attributing the difference to
one variable. Cached-row normal torques are measured, not proof of radial
physical normals. Original all-time Skin partition difference0.006715Ns
includes earlier non-Skin support: it is NOT a Hold partition failure or a
reason to subtract/overwrite Raw.1815 independently groups every actual object
row, including other contacts, and checks the complete velocity trajectory.

1815 PASS_ACTUAL_IMPULSE_VELOCITY_BOOKKEEPING only:
whole trajectory reconstruction error <=3.092e-13m/s; both actual100g cases.
From1.6s to peak,1586 delta-v[-4.318468,0.343878,0.027420]mm/s;
1741 delta-v[-5.881271,15.387576,29.018647]mm/s. Other-contact contribution
is exactly zero over these intervals.1741 Skin upward accumulated impulse
exceeds gravity by0.002901865Ns, producing the measured vertical speed rise.
Thus a near-weight mean reaction is insufficient to pass the instantaneous
speed criterion; momentum bookkeeping agrees with actual response impulses.
This does NOT show the contact law is physically accurate or which mechanism
caused those impulses. Cannot remove internal guides by subtracting their
forces from a saved trajectory, nor infer a counterfactual controlled run.

No new Native trial, motor feedback, gain scan or mass/material change.
Motor-port observation/control remains a prerequisite, NOT a demonstrated fix.
Full1741 Holding and UNBRACED FAIL remain unchanged;1586 object-only PASS
remains braced. Time/mesh/contact/hardware qualification not improved.

Reproduce read-only into NEW tags:
```
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/matched_finger_impulse.py --tag NEW_MATCHED_TAG
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/hold_velocity_budget.py --tag NEW_BUDGET_TAG
```

Scripts and result producer snapshots/hash records preserve actual commands'
inputs. These are Python analyses: Binary/SDK execution version NOT APPLICABLE
(no Native child); actual scene inputs are existing immutable Native evidence.
Future independent directions require a concrete supported composite inertial
contract, qualified curved finite tendon routing/attachment, or phase-correct
input-power observation. No new fullgrasp is justified by these inventories.
