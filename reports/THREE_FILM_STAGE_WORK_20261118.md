# Actual three-film stage work and limited time refinement

Source baseline62b76c5 plus archived working sources in each campaign. This is
actual SOFA, three films and ONE free sphere,10ms already-touching C2 coupon.
It is NOT closing from separation,grasp,lift,release or full energy certification.

## Actual execution and input preservation

941/947/948 use the SAME core DLL at
build/three_film_20261118_three_film_actual64_941/libReGripThreeFilmContact.so.
16/32/64 steps completed in58.3642/112.3663/210.9186s. The64-step forecast was
436.7542s,below480s,transferred only across two reviewed grid-cap guards.
No equation,tolerance,Newton budget,SDK or memory/runtime policy was changed.
Old T0/nonexact control guards remain. Independent exact-public-mass references
944/945/939 match actual q/v exactly. Whole-stage gap minimum64:
-2.1316282e-14mm,against unchanged-1e-10mm gate.

952 full listed time assessment remains FAIL.16→64 legacy field sampled
tendon work differs0.22975515%;endpoint force0.00824165%,film velocity
0.01077927%,attachment energy0.00426753%,stage work0.00196181%.
Earlier8→32 failures930 and all historical failures remain unchanged.

## Read-only actual stage-power observer

RoutedCablePower reuses actual guide geometry and measures -dL/dt. Standalone940
agrees with original unit-tendon AD power,objectivity and directional FD.
ThreeFilmStagePowerObserver reads accepted public stage journals and existing
ControlProfile;it writes -integral T*dL using the same Lobatto stage weights.
It never writes physical states,forces,mass or legacy work fields.
It is not tendon stored energy,friction heat or an actuator measurement.

943 initial8-step test and949/954/955 actual64/16/32 runs retain all NINE
physical CSVs byte-exact. Same observer DLL:
build/stage_power_20261118_three_film_runtime_work943/libReGripStagePower.so.
Full-AD versus runtime maximum cumulative work difference64:
2.7105054e-20Nmm;rate difference3.126388e-13mm/s.
Final64-step tendon work9.800940034755767e-5Nmm.
942 compile failure preserved;not a physical run.

956 stage-consistent component time gate PASS at0.1%,all adjacent and
base-to-quarter pairs,using actual observer data and unchanged other physics
metrics. Top-level EXPERIMENTAL;legacy-inclusive time gate STILL FAIL.
This is a corrected numerical quadrature of the SAME mechanical work,not a
changed force law or an exemption for a small error. No old column overwritten.
Signed residual64=-1.4449602e-12Nmm is a diagnostic,NOT unexplained heat.

## Remaining barriers

Generic birth/release,full physical thickness clearance,mesh/friction,
self-collision,equalizer,full energy and sustained actual wrapping/lift/holding
remain unqualified. Buffer30.01mm is midsurface research geometry,not full
.05mm skin/.1mm rail clearance. Gravity0,Fz=-.001N,Tmax=.0001N per rail,
C2 ramp.01s;material properties are research assumptions,not measured.

Actual width visualization936 shows centre-node tip+.00065335mm but
width-mean skin tip-.02496706mm and rail mean tips about-.10104mm.
Do not interpret a single centre-node trace as whole-finger wrapping.
Contact area/pressure remain NOT MEASURED here.

## Safe reproduction (new exclusive output tag)

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/film_three_film_runtime_work.py --tag NEW_UNIQUE_STAGE_WORK \
 --case 20261118_three_film_actual64_941 \
 --reference-work 20261118_three_film_actual_work946 \
 --reuse 20261118_three_film_runtime_work943
```

The runner verifies immutable plugin/source identity,clones output paths,and
keeps4GiB/480s. Do NOT directly rerun archived scenes into old output paths.
