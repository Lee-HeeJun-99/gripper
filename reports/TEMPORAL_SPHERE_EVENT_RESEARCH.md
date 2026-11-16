# Changing-normal temporal return and sphere event research

Source: independent mathematics and actual matching-SDK SOFA runs, NOT material
measurements or full gripper validation. Existing CurvedContact FAIL remains.

## Active-path isolation

`MovingReturn.h` propagates endpoint derivatives through every normal transport,
capacity and circular return. Substepped backward return is not event-exact.
`MovingSphereBenchmark` uses the same transition for force/tangent and commit.
One material point, fixed externally supported sphere, no Beam/free object.
Actual API F/dF/matrix/query-purity and 20/40/80step dynamics PASS in
`results/vector_history_moving_path_20261116_canonical04`.
Maximum aligned-phase time error:0.00177531%, below0.1% only in that scope.
Independent energy identity residual1.80041e-23 and FD1.03955e-10;
these do not close the entire robot energy balance.

## New birth/death reference and adapter

`SphereEventReturn.h` partitions a straight chord by its two exact sphere
intersection values. Root derivatives use the implicit gap equation.
It includes outside→outside transit with birth AND death in one step.
Grazing nonunique derivatives and center/antipodal normal singularities reject
explicitly. No arbitrary small-denominator or plastic-loss floor.
Capacity varies with actual radial gap at every substep. Normal transport and
endpoint derivatives propagate through event fractions and all returns.
This is a fixed sphere/chord model, NOT arbitrary moving/rotating SDF CCD.
`SphereEventBenchmark` is a NEW independent SOFA component, not an overwrite.
No physical force or hidden coordinate correction is introduced.

Unit:birth fraction0.502475; elastic FD absolute2.54823e-10;
birth identity1.72545e-24; full chord transit identity−7.87476e-21.
Includes common-frame rotation, no-contact and grazing rejection.
The identity separates backward projection inventory from plastic loss.
At death, zero normal capacity returns the elastic state to zero; any remaining
stored inventory is separately named detachment inventory, never guessed heat.
This discrete vector identity excludes radial normal work, parameter work,
inertia, Rayleigh terms and all robot components:global energy stays BLOCKED.

## Failed temporal convergence — do not combine adjacent PASS into approval

Identical prescribed trajectory:p(t)=(.2t,1.021−.2t,.1t),t∈[0,.02],
contact radius1.02,k=.001,μkn=.0003. No Solver in prescribed reference.
Actual dynamic scene uses the same starting position/velocity, point mass.001,
EulerImplicit, EigenSparseLU, zero Rayleigh. These are distinct tests.

| Internal substeps | Prescribed20→40 | Prescribed20→80 | Prescribed40→80 |
|---|---:|---:|---:|
|32|1.53829%|2.32532%|1.53832%|
|128|0.389062%|0.584731%|0.389071%|
|512|0.0975502%|0.146397%|0.0975524%|

All-three-pair temporal Gate remains FAIL at every tested resolution.
Actual SOFA512:0.0975816%,0.146423%,0.0975602% respectively.
Prescribed512 phase absolute maximum difference7.20523e-15 is reported,
but does NOT override relative FAIL. No phases were dropped.
Raw:results/sphere_event_prescribed_20261116_{a01,s128,s512} and
results/vector_history_sphere_event_20261116_{event01,event512}.
Latest finite-input-guard build is separately preserved under
results/vector_history_sphere_event_20261116_event_guarded512.

Interpretation:near-identical no-Solver and dynamic errors strongly isolate
temporal return/loss quadrature in this experiment, not linear Solver error.
Approximately first-order improvement with internal refinement is consistent
with endpoint-capacity backward loss quadrature. This is evidence for the next
derivation, not proof that every old gripper failure has the same cause.
Do not raise512cap indefinitely. Next compare event-aligned integration of
yield/slip/re-stick with an independent evolving-capacity vector reference;
mechanical work and tangent must change consistently with the chosen law.

## Reproduction, fresh paths required

```
g++ -std=c++17 -O2 tests/test_sphere_event_return.cpp -o /tmp/regrip_sphere_event_return
/tmp/regrip_sphere_event_return
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/sphere_event_prescribed.py --tag UNIQUE --substeps 512
$PY tools/sphere_event_run.py --tag UNIQUE --substeps 512
```

Existing active benchmark, birth production versions, raw and SDK are preserved.
Full CurvedOwner commit integration, state compression, original three-finger
mesh/history/dt,12wrenches and qualified grasp Optuna remain NOT RUN/BLOCKED.
