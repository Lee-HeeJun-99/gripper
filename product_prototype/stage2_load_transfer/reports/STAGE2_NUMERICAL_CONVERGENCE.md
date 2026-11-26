# Numerical verification, bounded scope

Actual data: `validation/convergence/torsion1/summary.json`.
Actual Rev AA shaft imported through Gmsh4.15.2/OCC7.8.1 (not OCP's7.9.3 in the
same process), scikit-fem12.0.2, SciPy1.15.3, NumPy2.2.6, pyamg5.4.1.
Binary SHA256 is recorded; installation isolated under `/tmp/regrip_stage2_fem`.

Original P1 cylinder reference error11.23% FAIL. P2/0.8mm2.512% FAIL;
P2/0.5mm1.291% FAIL. P2/0.35mm analytic error0.62466% PASS, final refinement
0.66238% <1%. Fine direct factorization exceeded4GiB; same physics with
AMG-preconditioned CG recovered this reference, without tolerance relaxation.

Actual shaft0.6mm global assembly exceeded4GiB before solving. Element-block
assembly (8000tetra/block), exact degree2 quadrature for affine P2 constant
elasticity, recovered the SAME mesh. On matched0.8mm geometry, compliance
differs from original full assembly by1.31e-14 relative. Actual0.8→0.6mm
shaft compliance difference0.346925% <1%; final compliance0.004767858rad/Nm.
Actual54,198tetra/11,168vertices; retained pin-hole rigid test fixture,
input0.001Nm. This does not validate the real pin pressure or strength.
Reported peak stresses depend on quadrature sample positions; no stress
singularity, bearing-contact, fatigue or full-system convergence approval.

Finite-rotation projected Finger and stroke-control models have their own
independent quadrature/gradient/energy/refinement tests. Actual0.1% time and
1% mesh product gates remain UNQUALIFIED. The two-inertia dynamics coupon
passed its analytic-reference and0.1% step-halving criteria ONLY for that
explicit conditional fixed-axis model.
