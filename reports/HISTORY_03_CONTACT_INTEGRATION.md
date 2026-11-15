# HISTORY 03 — separate quadrature and state storage

Status: **PASS prescribed reference and tested quadrature comparisons**;
full spatial/history qualification remains FAIL.

Normal contact uses Gauss order `samples=8/16/32` on each active interval.
Tangential contact independently splits at material-cell and previous active
boundaries, then uses `cellOrder=2` (independently compared with4). Changing
normal q does NOT change tangential order; the two studies are not conflated.
Reference-length weights and the old physical line stiffness/skin are retained.

Piecewise-affine triangular extension: exact force6e-6; new integrated force
6.000000000000002e-6, relative error2.22e-16. The reference is analytically exact
for this flat linear history, not a general high-order curved-contact benchmark.
The assembled smooth-branch18DOF force Jacobian FD maximum is1.3204e-12.
No classical derivative is asserted at contact onset or SDF seams.

Normal q8→16→32 and tangent cell2→4 actual SOFA results are separately listed in
`history_evidence/convergence.json`; strict 1% checks are maintained. Mesh and
history errors remain separate. The normal-quadrature `.patch.csv` contains
normal sample locations/wrenches ONLY, not the entire tangent force distribution;
do not use it alone as a full contact-wrench or force-closure certificate.

The element-local18x18 accumulation and stack point mapping avoid duplicate
triplets/allocations. Force/Jacobian physics is not replaced by a surrogate.
Measured timings and profile predictions remain in each campaign metrics file.
