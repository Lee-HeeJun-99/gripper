# Loaded native Rail derivative validation — 2026-11-19

Feature commits:1c20109,b19f839. No SDK/physical solver changes.
Previous authority:NATIVE_FINE_RAIL_PRECISION_20261119.md remains preserved.

## Problem and implementation

The next task was loaded-state native tangent verification,not repeating the
initial-reference matrix tests432/439.455 already contained mixed-direction FD
outputs,but excluded only2root nodes. Actual41/81 roots are3/5nodes.

458 adds explicit root-start and FD-step inputs to the read-only observer.
459 runs actual installed SOFA at the frozen PRIVATE failed poses with all root
nodes excluded. Left quaternion increments are used;translation direction scale
is0.1m,rotation1rad. No PRIVATE pose is assigned to MechanicalObject.
460 regression uses the old defaults:FD output bytes exactly equal455 for both
meshes. Actual unloaded center positions remain exactly unchanged in all runs;
observer also asserts full actual Rigid3 q/v equality before/after queries.

461/462 attempted an explicit bending direction but Data registration was wrong.
SOFA reported Unused Attribute privateDirection;runner rejected exit0 output.
462 original source/binary/process/output are preserved,NOT bending evidence.
463 fixes Data initialization through the constructor initializer;464 executes
the intended direction. It is failed-frame displacement and quaternion logarithm,
normalized to max1rad rotation,with fixed roots zero.465 extends FD steps because
464's best force result was at the boundary. This is a derivative diagnostic,
not changing material,load,geometry or any actual state.

## Actual results

459 mixed-direction best force relative differences:
41:1.2956867758255458e-9;81:7.401189073487264e-10 at h=3e-7.
These do not certify a complete Jacobian or strict equilibrium.

465 bending-direction best force relative differences at h=3e-5:
41:0.00016542196880390671;81:0.00020447101483086222.
Corresponding derivative error norms2.6372458379887884e-7 and
3.2484757148376617e-7N per dimensionless direction parameter.
These are NOT physical force residuals. Derivative norms are about0.00159N,
versus9256/48942N for the mixed directions. Mixed directions mask soft behavior.

Torque derivative norms near this step are2.78310e-11/7.91466e-11Nm;
relative differences about0.960 remain UNRESOLVED. No absolute floor is introduced.
Small-step force differences deteriorate;large steps add truncation effects.
These observations do not isolate cancellation from native tangent approximation.
No physical heat,mesh convergence,or static solve remedy is inferred.

All completed runs have2actual unloaded frames and center-position error0.
Single process runtime approximately0.2seconds;exact times and commands are in
each process directory. Each child uses existing4GiB/480second guarded runner.
No OS exhaustion is claimed. Actual loaded/static41/81 equilibrium still FAIL.
B3 functional50g Holding and release evidence is unchanged and remains unqualified
for full mesh/time/energy/interference/fabrication.100g/Lift remain NOT RUN here.

## Decision and next independent hypothesis

Stop FD-step sweeps:the best measured derivative agreement does not solve the
coordinate-sensitive axial equilibrium residual. Do not implement a new solver,
alter the SDK,or relax gates. Next inspect the native axial strain/length formula
and compare represented segment-length differences with native per-element axial
forces at the preserved PRIVATE states. First establish the actual force path;
a generic chord length is not automatically BeamAdapter's internal length.
Quantify subtraction/representation sensitivity without installing corrected q.
Any alternative stock component requires its own small-load benchmark before B3.

## Reproduction and identity

```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/native_beam_loaded_fd.py --tag UNIQUE_ROOT_FD
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/native_beam_loaded_fd.py --tag UNIQUE_REGRESSION --legacy-regression
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/native_beam_mode_fd.py --tag UNIQUE_MODE --fd-steps 0.001 0.0003 0.0001 0.00003 0.00001 0.000003 0.000001
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/native_beam_fd_assess466/summary.json
```

Build458 binary7637bd0b7928f7fc95e93fd60b0be586935da3765c3b575c2e882f33addcf61b;
compiled C++6b941c36b76713ea107d10dd7d3dbceea651784f3695d456dd1543c64282479a.
Build463 binarye1ca5da4442eabed8b0cef2c3bf96b681fa0d593665aaa3c875e13a3449c12f5;
compiled C++13e497228eb290fcae75a701113dd2be5d8af7f894e7179aa633d1734a31e483.
Frozen guards in observer_identity.py;no live-source relabelling.
SDK:/home/ubuntu/SOFA/v26.06.00. Sources,scenes,materials and exact commands
are preserved in native_beam_loaded_fd459,loaded_regression460,mode_fd462,
mode_fd464,mode_ladder465 and fd_assess466 under product_prototype/results.
466/PRIVATE_loaded_FD.png is a query-diagnostic plot,NOT a physical trajectory.
Evidence:evidence_native_loaded_fd_v17/manifest.json.
Prior immutable audit1119files,0mismatches. New manifest1261files.
No physics process intentionally left running;no automatic continuation promise.

