# Experimental single-branch constrained collocation

This is a separate research integrator,not a replacement for impact/event or
production active-set contact. It uses the existing coupled film/sphere mass,
force/Hessian,root map,current normal and spherical gap derivatives. No SDK
edits,material changes,mode truncation,pose correction or added damping.

## Equations

For each stage,`Q_i=q0+h sum_j A_ij V_j` and
`M(V_i-v0)=h sum_j A_ij F_j`,where
`F_j=-grad U(Q_j,T(t_j))-c M V_j+J(Q_j)^T lambda_j+F_external`.
The persistent branch imposes `J(Q_i)V_i=0` with nonnegative stage reaction.
`lambda` is FORCE in N,not impulse. Observed row impulse is `h*b_j*lambda_j`
in N s,at the actual stage geometry/time. The same original C2 control is used.

- RadauIIA order3:`c=(1/3,1)`,A=((5/12,-1/12),(3/4,1/4)),b=(3/4,1/4).
- LobattoIIIA order4 includes known initial stage and unknown middle/end:
  `c=(0,1/2,1)`,A=((0,0,0),(5/24,1/3,-1/24),(1/6,2/3,1/6)),
  b=(1/6,2/3,1/6). Initial reaction solves acceleration compatibility
  `J M^-1(F_free+J^T lambda0)+v0^T H_gap v0=0`.

Both are stiffly accurate:endpoint q/v are the last stage. No normal-velocity
projection is applied afterward. Geometric drift is checked against the
original1e-10mm endpoint gate,not hidden by changing positions.

For unknown-stage k,the true mechanical Newton block is
`delta_ik M + c*h*A_ik M + h² sum_j A_ij A_jk (H_Uj-lambda_j H_gapj)`.
Reaction block is `-h*A_ik J_k^T`;constraint block is
`delta_ik J_i+h*A_ik V_i^T H_gapi`. A nonsymmetric pivoted LU is used;
the tangent is never symmetrized or regularized. Opt-in central FD checks
the complete stage Jacobian on the nonlinear changing-normal unit problem.

## Restrictions and evidence

Strictly one already-touching,tangent,feature-preserving row. Initial release,
negative reaction,feature transition,undefined geometry,singular stage system,
or whole endpoint surface violation rejects. This does not search for new
interior-time impacts or own release/reimpact. Actual SOFA owner defaults to10us;
longer windows require explicit independent qualification<=625us and steps<=10us.
The runner currently qualifies39.0625us,NOT625us. Every used stage is recorded.
This is NOT full C2/grasp/energy
qualification. Rigid sphere rotational normal Jacobian is physically zero;
orientation remains free and isotropic angular damping is integrated.

Independent722–724 unit-mass curved problem fails a2.889e-17 N s arithmetic
floor against unchanged1e-17 threshold. Separate research-mass725 passes;
740 checks Radau third-order and Lobatto fourth-order analytic refinement and
changing-normal FD. Do not relabel the unit-mass FAIL as PASS. Actual-state
FEM726/727 and741 compare explicit-coordinate and shared-System assembly.
Actual Radau728/730/731 matches independent FEM but all-pair time737 FAILS
regular force0.245223% in the9.765625us window. Actual Lobatto experiments use
the explicit `lobatto` Data flag;inspect their completed summaries,not this
README,for current status. Prior models/binaries/raw remain immutable.

Stage CSVs are solved substates written before the enclosing owner's global
commit;only a completed successful macro state establishes actual acceptance.
The existing tendon-work CSV still uses endpoint trapezoidal work and is not
a stage-consistent full energy certificate. Impact dissipation,normal work,
numerical projection inventory and unmeasured damping/global work are distinct.
