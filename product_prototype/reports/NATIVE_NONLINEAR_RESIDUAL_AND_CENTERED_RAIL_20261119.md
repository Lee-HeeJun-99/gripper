# Native nonlinear residual and centered Rail442–453

2026-11-19. Feature commits2dc6afc,fcc7ba5. Started at51011ca,clean worktree.
Completed the specified next PRIVATE force diagnosis and continued to actual
native small-load tests. No SDK/ForceField/ODE/contact solver development or push.

## PRIVATE query,not accepted geometry

NativeRigidTangentObserver accepts optional PRIVATE Rigid3 coordinates,queries
stock native addForce in local buffers,restores actual-force cache,and checks
actual full q/v unchanged. Native zero-load scenes are run with those queries;
they are NOT loaded trajectories. All actual mapped-center outputs match the
zero-load control exactly. Root DOFs0/1 remain projected. Quaternion construction
uses world-left rotation exponentials and validates finite,unit poses.

442 measures native forces at the existing440 linear matrix reference,without
installing its positions. Scale1/.5/.1/.01 changes PRIVATE deformation and
reference load,NOT dt. Native free axial residuals are9.66162e-5,2.41541e-5,
9.66162e-7,9.66196e-9N;fitted amplitude exponent1.9999924. Transverse exponent
2.9999906. Represented linear residuals~1e-17N are far smaller. This separates
geometric axial/transverse nonlinearity from coordinate rounding for this query;
it is not proof of a unique cause for all B3 failures.

444 evaluates a separate PRIVATE second-order geometric reference:
`u_axial=-1/2 integral(w'(s)^2 ds)`,using the Euler slope with free length95mm.
It is a kinematic hypothesis,NOT a solved equilibrium or simulation correction.
At scale1 axial residual decreases to2.18439e-8N (4423-fold),transverse2.80420e-10N.
At scale.01 axial2.43220e-12N;the force effect of representing coordinates is
1.61249e-12N. This measured representation error is NOT a universal lower bound
and is not grounds to relax the1e-12N criterion. Finite PRIVATE tangent FD data
remain diagnostics,not general derivative/time/energy certification.

443 tests native line-search iteration budget0 with all force thresholds unchanged.
It actually accepts a residual-growing full Newton direction while emitting
Line Search failure. First norm9.66162e-5 agrees with442's predicted nonlinear
increment (printed log has limited precision),then approaches2.26355e-12 and
fails. This plan is NOT adopted or relabelled successful.445 at1e-8N with ordinary
line search also FAILs near1.33116e-12. Old failures stay immutable.

447 independently enables installed native reinforceLength,which CHANGES the
axial force approximation,not merely solver precision. At the same corrected
PRIVATE scale1 axial residual8.74989e-10N,but at scale.01 it worsens to3.96657e-12N.
No actual loaded equilibrium or equivalence gate passed;this candidate is NOT
integrated into B3. No stiffness,friction,damping or tolerance fitting occurred.

## Actual centered native Rail evidence

Since zero-load/no-contact physics is translation-invariant,448 moves the complete
reference and fixed root from x=[0,.1]m to[-.05,.05]m. Dimensions,clamped5mm,
E250MPa,nu.3,rectangular2mm×.5mm,native geometric rest,force1e-8N and strict
solver settings remain unchanged from445. These material values are assumptions,
not measured PET/TPU data. ComputeMass=false;no mass/gravity/dynamic qualification.

448 completes both native static outputs with no solver failures.450 at half
force5e-9N also completes.449 at41/81nodes FAILs:there is NO all-pair mesh PASS.
Do not transfer a coarse success to refined meshes or to a Skin/attachment model.

452 adds a separate read-only actual end-event Rigid3/force observer to frozen
448/450 scenes. It checks q/v are not mutated by native force queries. Both
mapped-center q/v outputs exactly match unobserved controls;actual Rigid3 poses
and unprojected elastic force/torque are journalled. Angular velocities are not
exported;do not claim post-step quaternion/velocity identity against an unavailable
unobserved full-Rigid journal. Quaternion norms are checked separately.

| Actual native static test | Tip,m | Max free force residual,N | Result scope |
|---|---:|---:|---|
|21nodes,1e-8N|5.487199999812008e-7|6.17377612336839e-13|small-load state/force only PASS|
|21nodes,5e-9N|2.7435999999765015e-7|2.304298664923817e-13|small-load state/force only PASS|

Both actual free torque residuals meet1e-12Nm. Root balancing reactions are
computed from the unprojected native internal forces at fixed nodes,not guessed
from a zero projected Jacobian. Root force and global force/moment balances are
recorded in452. No impulse/force unit conversion is involved in these static tests.

453 compares actual states with approximate Euler/second-order references:
all-node transverse errors1.87993e-17/2.34988e-18m;rotation errors2.38013e-16/
2.97512e-17rad;axial second-order errors1.13104e-15/2.84495e-16m. These references
are NOT exact nonlinear solutions or prescribed physical states. Full-versus-twice-
half displacement error9.50233e-13m passes the existing absolute1e-12m load-scaling
check only. Transverse relative scaling error2.56953e-11 uses no artificial floor.
Static context indices1/2 are NOT transient physical-time convergence evidence.

## Evidence and reproducibility

Unique Raw paths under product_prototype/results:
native_beam_private_force442,native_rectangular_ls_zero443,
native_beam_second_order444,native_rectangular_small_load445,
native_beam_private_assess446,native_beam_reinforce447,
native_rectangular_centered448,native_rectangular_centered_refine449,
native_rectangular_centered_half450,native_beam_accepted452,
native_beam_centered_assess453. Sources/scenes/commands/logs/configuration and
binary/source/SDK SHA are retained in each producer record. All child limits
4GiB/480s unchanged. Peak RSS is NOT MEASURED,not fabricated as0.

Reusable builds:

- cad/build_private_rigid441/libReGripElasticObserver.so
 SHA ceadd757a6d134be84f5f59aa29219f57955af1ebf704ec4ed04ec52e3797d42.
- cad/build_accepted_observer451/libReGripElasticObserver.so
 SHA9674de6b5c85051c52b1b055e09e8725393e71319d6e639fbcb6a42cb1aaa9ef.
Compiled-source guards in sofa/observer_identity.py prohibit substituting edited
live C++ for these binaries. No old build is overwritten.

Evidence:reports/evidence_native_centered_v15/manifest.json (relative to
product_prototype). v14 verifies726 prior immutable files without mismatch;
v15 preserves the later native results and prior-v14 audit. Actual accepted
profile plot:actual_native_static_profiles.png,with mm/micrometre axis units
explicitly NOT aspect-preserving. PRIVATE_reference_force_scaling.png is clearly
marked a PRIVATE query,not actual loaded deformation.

Read-only restart from repository root:
```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/native_beam_accepted452/summary.json
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/native_beam_centered_assess453/summary.json
```
Reproduction only if justified,use fresh tags:
```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/native_beamadapter_coupon.py --tag NEW_centered --nx 21 --geometric-rest --load 1e-8 --origin-x -0.05
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/native_beam_accepted.py --tag NEW_accepted_force
```

## Next work and unresolved product gates

Do not repeat442/444 or coarse successful cases as new research. Stop unsupported
full-step/force/routing sweeps. Next:diagnose41/81 centered failures449 with native
per-node force/torque versus coordinate representation,using full Rigid3 snapshots
clearly labelled FAILED diagnostic states;do not treat failed output as accepted
equilibrium. Compare physical-unit/frame-invariant residuals before adopting any
native scaling/local-frame configuration. Keep.1% time and1% mesh gates unchanged.

B3 functional50g holding/release stays preserved,not newly rerun. Full wrapping,
Skin/Rail/Guide attachment,whole energy,mesh/time,hardware clearance,100g,Lift,
STEP/fabrication remain open. No new physical material,actuator or CAD claim.
These coupon passes are not a final ReGrip design PASS. No physics child is left
intentionally running;no automatic continuation after the session is promised.
