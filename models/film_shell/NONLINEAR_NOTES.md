# Nonlinear-stage correction, 2026-11-16

This is not a full-grasp qualification. Preserve prior binaries/results.

1. Film cache keys must compare every coordinate scalar exactly. SOFA Vec's
   `operator==` uses an absolute 1e-6 tolerance, inappropriate for memoizing
   forces/Hessians during Newton iteration. Tiny-update regression is included.
2. Force-stage positions can be a solver-owned trial vector, not the main
   MechanicalObject position. Matrix assembly uses the last force-stage vector;
   addDForce reads MechanicalParams::readX. Energy queries do not select a new
   linearization state. The API test deliberately separates main/trial states.
3. ReGripBDFSolver is an independent, LGPL-attributed adaptation of the matching
   SOFA BaseLinearMultiStepMethod. BDF1 is the default; separately labelled
   trapezoidal and fixed-step BDF2 experiments are supported. BDF2 owns distinct
   history buffers and uses BDF1 startup. The installed SDK remains
   unchanged. Only the line-search position increment is multiplied by the same
   alpha as the velocity increment. The full kinematic residual is eliminated:
   dx = alpha*dt*dv - r1. Public SOFA Newton and linear-system APIs are reused.

The matching SDK omits its public NonLinearFunction.h from installation; the
build reads that public header from the matching source checkout. It does not
copy a foreign engine binary or edit installed headers.

Passive matrixProbe traces record actual force calls, trial q/v, decomposed
film/fixture/contact force, prior linear RHS/solution and constraint mask. The
prior system is explicitly not labelled the current force query's system.
The stage matrix check assumes the benchmark's total mass 1e-6, Rayleigh mass
coefficient 2, stiffness damping 0 and BDF1/Euler dt scaling; it is not generic.
Unknown incoming aggregate force is null, not a fabricated external/damping sum.

Mapped scenes require additional care: the SDK addMdx visitor prunes mappings;
the independent solver instead propagates the velocity combination and forms a
cleared, accumulated MBK mass product. Damping and kinematic corrections use
separate cleared product buffers, preventing a second pullback of pre-existing
child forces. Short exact-slope mapped dynamics match independent reduced-mass
FEM within 1.93e-6 relative; the unmapped result changes below 9e-19 mm.
FilmSlopeMapping is an explicit different hard boundary, not a replacement of
failed finite-penalty evidence. It maps force and mass by virtual work, and the
redundant parent row1 z coordinate must be fixed in scene XML.

Pre-fix BDF line-search trials violated q-q_old=dt*v by 0.002992257 mm. With
independent corrected update the defect is at floating-point roundoff. After
exact cache correction, 21-node 200/400-step runs have no Newton-failure warning
and reach static relative force residual below 1e-6. Full transient convergence
still fails at dt .2/.1/.05; final-tip agreement does not certify the trajectory.
See exclusive results/autonomous_film_20261116_* campaigns and source snapshots.
