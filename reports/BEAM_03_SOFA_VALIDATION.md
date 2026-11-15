# BEAM03 — actual SOFA single-beam verification

Status: **PASS finite small-deformation campaign; general large-load structural
qualification NOT RUN.** Raw root `results/beam_20261115/single`.

`tools/beam_trial.py` creates a100mm independent cantilever with explicit edges,
root6DOF fixed, mass1e-5, zero gravity, EulerImplicit, EigenSparseLU.
Material: E250,ν.32,Iy=Iz=.0426666666667mm4,A=.732232986291mm2,
EA183.058246572754,GAy=GAz57.7835374282682,GJ8.08080808080808,
EIy=EIz10.6666666666667. Effective shear factor5/6 is a declared assumption;
the old rectangular A3.2mm2 is not substituted into the circular golden model.

Initial3s run with mass damping.2 did not reach equilibrium: FAIL retained.
The qualification plan explicitly uses mass damping2,stiffness damping.1 and12s
for ALL compared trials. This is a documented dynamical-condition change, not
a tolerance change or a claim the initial transient converged.
Limits: free force/moment residual<1e-3,speed<1e-5,relative tail drift<1e-4,
global root-reaction residual<1e-3. All10qualification trials passed.

Tip-force Fz=−1e-6 gives z(mm):11nodes−.0311736024449512,
21−.0312321961143061,41−.0312468445551906. This approaches the continuum
`FL³/(3EI)+FL/GA` and the independent discrete prediction with
`1−1/(4m²)` bending correction. Repeat is identical; halfdt result
−.0311736024423335. Actual inherited small-load comparison−.0312499970195894
is consistent with its different shear formulation; no identical-theory claim.

Axial Fx1e-6: x=5.46272801216e-7mm, consistent with FL/EA.
Tip Ty1e-5: z=−.00468749999097mm, angle9.37499999211e-5rad,
consistent with FL²/(2EI) and ML/EI. Pure Tx1e-5, rigid scene rotation2.1rad,
force21/41,repeat and halfdt all passed their actual residual checks.
Detailed per-axis reactions, velocities, parameters, command, raw states and
binary identities are in each metrics/config/command JSON and state/log files.

v2 force run matches prototype and takes9.88s (prototype≈14.65s in that test).
Independent100-state exact equivalence is separate from runtime improvement.
Distributed load, arbitrary combined large loading, nonlinear Newton/line-search
comparison and fully spatial multielement large-deformation mesh validation:
NOT RUN. A low-order objective kernel is not a completed beam-library certification.
