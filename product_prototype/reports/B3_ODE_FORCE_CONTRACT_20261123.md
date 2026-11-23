# Force-controlled ODE candidate1176–1180

Actually continued after zero-Cable deformed check1175. Same Rail-back mesh,
mass,Guide/root/restshape/routing and original1129 C2 maximum2.5N/Cable.
Only damping distribution/law changes to ODE1/1e-4,fields0;global Guide damping
is new,explicitly NOT an identical original physical model. No object/support.
Bounded0.31s actualNative1176:124outputs,1.407s,minvolume0.978666,finite,
no ERROR/inversion.1179 same input halfdt:248outputs,2.573s,minvolume0.978359.

1177 actual read-only observer at300ms,previous297.5ms,all124q/v/Guide
prefix differences EXACT0.1178 same-state effectiveA error2.19e-16relative.
Previous-state free-motion RHS without added convective term predicts velocity
1.29e-9relative;Cablecorrection A-inverse J-transpose lambda matches1.14e-9.
ActualT1.7064N,lambda0.004266Ns perCable=Tdt EXACT. Added mapped centripetal
hypothesis gives6.12e-7relative velocity error,also below0.1%:cannot uniquely
certify convective inertia from this sample. No force/velocity correction used.

1180 all124 common outputs at clockdifference≤1.33e-15s:
Skin162.801%,Rail164.119%,velocity78.768%,curvature52.046% relative errors.
0.1% Gate FAIL unchanged. Skin max principalGreenstrain≈0.06076/0.06116,
material allowables NULL. No contact/holding/lift test. No full qualification.

Conclusion: ODE damping realizes the intended local discrete velocity law,
but does not fix coarse-step forced-joint time convergence. Do NOT promote
this candidate as an improved100g gripper or run a blind force/dt sweep.
This line has reached its useful diagnostic limit for the session. Next
independent analysis should quantify gravity/C2 modal participation and
time-error sources from saved trajectories before selecting a Native
integration or mechanical redesign. Old constrained higher-order failures
remain;no new custom ODE/SDK patches.

Reproduce with fresh tags:
`python product_prototype/sofa/b3_ode_gravity_candidate.py --tag NEW_FORCE --force`
and `--tag NEW_HALF --force --half`,then generic b3_rail_back_assess.py.
Read-only restart:
`python -m json.tool product_prototype/results/b3_ode_force_pair1180/summary.json`.
Source/binary/SDK/command/limits in each preflight;old Raw never overwritten.
