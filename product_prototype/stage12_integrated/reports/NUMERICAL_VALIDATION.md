# Numerical status — no system pass

Latest completed follow-up: owner64_working1 uses static constraint generation,
220near-active of3752original rows, and full nonlinear post-checks. Actual
archived-code QP control working_controls1 verifies insertion of an initially
inactive violated constraint; disabling insertion is rejected by full guard.
Its actual optimizer reached300iterations (FAIL), not silently promoted.
However independent final-state force certificate1.34548e-9N and relative
complementarity9.72769e-9 meet unchanged thresholds; exact actual geometry also
passes. owner_states2 pins original states and certificate identities, records
original FAIL status separately, and certifies local KKT only. Finest32/64
axial migration refinement0.02093% PASS;16/64 remains3.99215% FAIL. Do not
hide this coarse-to-fine failure behind the adjacent pair or call it full
Finger convergence. Next is a separate elastic-Rail/PET model, not blind mesh
scanning. Friction, shell, material strength and system gates remain absent.

Latest actual material-owner follow-up supersedes only the unresolved method
status, not the historical failures below. owner_analytic_reaction2 independently
certifies unchanged16/32 saved states below1e-8N force-equivalent residual;
exact actual-channel envelope audits pass. Relevant migration refinement~4%
still FAILS1%. Interrupted64 guess is NOT an equilibrium: force residual
1.001656e-6N and complementarity2.16556e-7 fail unchanged thresholds even
though its exact geometric envelope passes and migration is near the32 result.

owner_rank1 measures actual active Jacobian row dependence. owner64_cone1
shows that replacing196 active rows by15 signed QR rows changes the normal
cone (nonnegative reconstruction residual0.0816634). owner64_cone2 enriches
to170 actual rows; all original local row directions have nonnegative
reconstruction residual<=7.41822e-9. This local algebraic certificate is not
a nonlinear feasible-set proof, new equilibrium, pressure uniqueness, or
permission to discard physical contacts. Future reduced working sets must
still check EVERY original nonlinear inequality and independent force balance.

Software validation:17 actual negative release controls; empty/failed states
cannot pass all([]) or close-output comparisons. audit3 resolves88 result and
failure records with immutable source archives, no protected Stage1/2 change.
This provenance PASS does not promote any physical result. All old failures
remain preserved. Offline manager guards do not start external Codex sessions.

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
