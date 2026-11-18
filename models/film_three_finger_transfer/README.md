# One isolated deformed contact-support transfer — EXPERIMENTAL

`ThreeFilmContactTransferODE` reuses validated persistent checkpoint restore,
public masses,existing Lobatto/C2 and ManyRowImpact. It handles ONE externally
identified124→117 birth in a100us interval from an actual accepted23.4ms state.
It is not a global earliest-event or arbitrary active-set production solver.

The constrained pre-impact endpoint family is reintegrated during the signed
root solve. Six old/new rows share ONE mass matrix and ONE free Rigid3. The
plastic LCP yields zero impulse and positive separation velocity at old rows;
new rows remain tangent. No reaction/velocity clamping or pose projection.
Only a final three-independent-row branch may enter existing V1 checkpoint;
other outcomes reject rather than silently discard contact constraints.

All11 contexts retain accumulated absolute time/dt. Accepted physical roots,
mapped local states,public Rigid3 centre/velocity/quaternion are verified exactly.
Segmented pre/post stages have explicit actual time and quadrature weight.
Instantaneous impulse is never divided bydt and called continuous force.
`.rows.csv` inherited old header is intentionally unused:read
`.transfer.stages.csv` and `.transfer.impulses.csv` instead.
Weights repeat per owner;sum once per stage,not three times.

1042 independent isolated transition PASS;1043 factored kernel q/v/time EXACT
and directional6-row derivatives checked.1044 actual SOFA q/v/impulse/time
EXACT,strict1e-12 API;whole-stage gap-3.57758e-12mm,world linear impulse
balance1.91115e-21Ns,angular1.05097e-24Nmm s. Root impulse is explicitly
recovered from unreduced nodal momentum,not fitted. Root work remains NULL.
1048 actual-stage energy inventory consistency PASS,NOT whole-energy certificate.

This is CONTACT SUPPORT MIGRATION,not object ungrasp:the sphere remains in
contact with the new rows. Gravity0,no friction,self-contact or physical equalizer.
1047 subsequent ordinary persistent continuation fails at another event after
one accepted23.6ms step. Do not claim complete Unload/release/wrapping/grasp.

Full provenance,Raw/build and failed campaigns are recorded in
reports/REGRIP_THREE_FINGER_GRASP_CONTINUATION.md.
