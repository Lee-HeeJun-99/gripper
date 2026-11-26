# Numerical status — no system pass

Inherited1%mesh,0.1%time and physical force/gap thresholds are unchanged.
No new Native/SOFA or Gmsh FE was run in this integrated session. New analyses
are independent SciPy static/ODE controls and actual OCP geometry checks.

Jam-energy analytic vs numerical checks pass bounded reference tolerances;
they expose transient tension amplification, not a protected load rating.

Finite PET endpoint coupon passes energy refinement but misses finite-wall
interaction. Actual front overlap rejects that system interpretation. AD finite
walls with moving-minimum feature ownership then pass some solver checks but
fail independent force/migration criteria: AD6 16→32 axial migration3.6366%,
versus1% required. Nonnegative physical normal-cone force recovery also fails
at60deg; analytical objective gradients alone did not solve the issue. Do not
call optimizer success a physical equilibrium certificate.

New exact annular-sector envelopes show zero common with actual AD front/back
for the stored32segment AD4 states at15/30/60deg. Earlier ruled-loft overlap
FAIL remains intact; an exact geometry proof, not a relaxed tolerance, resolves
that representation question. It does not resolve force or mesh failure.

Independent owner_contract1 uses the SAME feasible halfspace intersection:
explicit material/contact rows solve the analytical reference, while aggregated
minimum SLSQP reports success at a solution error1.1547. Its numerical Jacobian
lies0.288675 outside the true contact normal cone. This proves a real method
hazard, not that it is the only cause of PET failure. Material-owned exchange
implementation is tested separately; preserve its actual result/limits.

No actual coupled flexible Rail/friction/shell, full drive energy/momentum,
whole-system time/contact convergence or material strength claim follows.
