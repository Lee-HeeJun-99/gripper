# Three-finger actual continuation — 2026-11-18

Project INCOMPLETE. Measurements below are **actual SOFA** unless explicitly
identified as read-only mathematical postprocessing. No wrapping,lift,holding
load,frictional grasp or design superiority certificate is claimed.

## Persistent transfer implemented

Separate `models/film_three_finger_resume/ThreeFilmResume.cpp` reuses the existing
conservative mechanics and fixed compressive-row Lobatto step. Original owners'
REST checks remain defaults;new owner validates a complete checkpoint instead.
No fake counters,force/velocity projections or relaxed residuals. Public
`Context::setTime` synchronizes exact accumulated clock and dt on11 contexts.
BaseContext has no public setTime:1013 compile failure preserved;1014 uses
public Context API,SDK unchanged.

|Campaign|Actual operation|Result|
|---|---|---|
|1014|1002 step40→44,4 resumed steps|strict1e-12 PASS,q/v/time EXACT|
|1015|1014 serialized step42→44,2 steps|q/v/time and all used stage rows EXACT|
|1016|1014 step44→50,to10ms|q/v/time and all used stage rows EXACT|
|1017|step50→80,10→16ms Hold|COMPLETE,scoped EXPERIMENTAL|
|1018|five corrupt checkpoint actual runs|guards reject;original harness FAIL preserved|
|1019|read-only same1018 reassessment|PASS:zero accepted rows in empty buffered files|
|1020|read-only actual8→10ms energy/work|callback/control consistency PASS,not full energy|

1014 runtime22.4137s,whole-stage minimum gap-7.46070e-14mm,momentum
4.10910e-20Ns,normal velocity1.81327e-15mm/s. All field positions,control,
length,stored/kinetic energy agree exactly;only private legacy work is excluded
explicitly.1017 whole-stage gap-1.32516e-12mm,momentum2.24238e-19Ns,
normal velocity6.63840e-15mm/s. Gates remain -1e-10mm,1e-17Ns,1e-10mm/s.
The actual accumulated time at step80 is0.016000000000000014s,not replaced by
step*dt. Checkpoints save actual xyzw quaternion;historical1002 reconstruction
is allowed ONLY after zero angular velocity/increment checks for all prefix states.

## Energy origin and state ownership

Snapshot includes exact public nodal masses,rigid mass/inertia,root map,
positions/velocities,quaternion,time/dt,step index,active owners and source/binary
provenance. Contact multipliers are recomputed by the SAME stateless one-step
equations,not imported from Native IDs. The three fixed compressive rows are
not a production release active set. Invalid identity,quaternion,mass,mapping
or row ID is rejected before a physical state commit. Invalid init currently
aborts the process;no silent continuation or recovery is claimed.

Private legacy sampled-work history is NOT restored and NOT joined across
chunks.1020 uses full-AD read-only observer946 and actual accepted stage q/v:
8→10ms tendon work4.33297448587305e-5Nmm,external work2.14250610771e-6,
damping6.98284909313e-7,normal constraint work-8.32911e-25;
signed residual-7.00187e-13Nmm. Callback energy error6.09864e-20Nmm,
control mismatch0N. This is a numerical/partial inventory,NOT physical heat.
Root reaction work stays NULL. First200us inventory1011 and post inventory1007
remain separate origins;overlaps must not be counted twice.

## Scope and blockers

Same research geometry/material/control as1002:three100mm films,root radius50mm,
sphereR30mm plus.01mm midsurface buffer,film1g each,sphere100g,Tmax.0001N per
rail,ramp10ms,release20–30ms,Fz-.001N,gravity0. Six equal prescribed tensions
are NOT a physical equalizer. No actual PET/TPU or actuator measurements.
Initial impact fixture is not stationary-object closing. No full-thickness,
self-collision,general friction,full time/mesh/energy certificate.997 overall
time FAIL and999 deformed-release FAIL remain unchanged.16ms is not evidence
of wrapping/holding/lift. Contact area/pressure/holding load remain NOT MEASURED.

## Reproducibility

New source baseline94cdf31 plus per-campaign archived source hashes.
Build:`build/three_film_resume_20261118_three_film_resume1014/`.
DLL SHA256:`32360e2ffabb94749d5e0f6aa8e739d5128734b98f2fc0fbfa9aab04ccd77146`.
SDK `/home/ubuntu/SOFA/v26.06.00`,no mixed Sofa dependencies.
Raw `results/autonomous_film_20261118_three_film_resume1014/` and corresponding
1015/1016/hold1017 directories. Each stores exact scene,command,process result,
q/v,all stages,field geometry,checkpoint files and hashes. Unique names required.

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/film_three_film_resume.py --tag NEW_UNIQUE --step 40 --steps 4
$PY tools/film_three_film_resume_continue.py --tag NEW_CHAIN --parent 20261118_three_film_resume1014 --checkpoint-step 42 --steps 2 --compare1002
```

Next:complete bounded actual Hold/Unload;diagnose genuine lambda=0 release,
never commit tensile contact. Profile and quantify actual curvature before
longer physical time or any grasp claim. No automatic post-session execution.
