# Fixed multiple-row collocation reference

PersistentRows.h extends the existing constrained Lobatto IIIA4 equations to
a prescribed set of independent normal rows. It does NOT replace the validated
single-row actual SOFA owner. Unknowns are two stage velocities and two vectors
of multipliers. q_i=q0+h a_i0 v0+h sum_j a_ij v_j;stage momentum and J_i v_i=0
are solved together using the true nonsymmetric Jacobian including each gap
Hessian. Initial acceleration includes v^T H_r v curvature for every row.

Dependent rows,negative reaction/release,undefined geometry and geometric drift
are explicitly rejected. Impulse nonuniqueness is NOT solved by regularization.
No position/velocity projection,impact atom or active-set insertion occurs.
Momentum1e-17 Ns,normal velocity1e-10 mm/s and gap1e-10 mm gates are unchanged.

827 compile FAIL(duplicate diagnostic local) is archived;828 corrected independent
test PASS:coupled-mass two-row analytic fourth-order errors6.33439e-9,3.96261e-10,
2.47720e-11 mm;changing-normal stage FD1.63e-16;curved gap1.11e-16 mm;
dependent/release negative controls. Follow-up input validation is separate.
These are mathematical tests,NOT three-film SOFA,feature transitions,release,
self-contact,friction or grasp qualification.
