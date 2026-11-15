# ReGrip contact/closure campaign — final verification

## Decision

**Overall physical qualification: FAIL /100mm grasp optimization: BLOCKED.**
Meaningful new contact convergence, native sustained contact, wrench analysis and
guided three-finger holding results were obtained. They do not establish a complete
physical6DOF gripper. In particular inherited BeamFEM produces a whole-system moment
defect and nonzero closed deformation work. No physical acceptance condition was relaxed.

Start commit `20249c953a7eef30f5574e4e7d1ce7cb098505f6`.
Branch `development/regrip-contact-closure-optimization`.
Verified code commit `d3a343df197d0cd4cfc4f2164ba0e76ea8e2f00a`.
The final documentation/evidence commit is the commit containing this report;
retrieve its exact SHA with `git log -1 --format=%H`. Self-referential report hashes
are not fabricated. Per-experiment Git/dirty/source/binary identities are preserved.
No push,history rewrite,remote deletion,main overwrite or original/golden edits.

## Environment and provenance

All new raw/build/runtime data live on external disk under
`/media/ubuntu/99419895-2058-45b4-b746-b36ea7112e4e/research/LHJ/ReGrip`.
Ubuntu22.04.5,GCC11.4,CMake3.22.1,Conda Python3.10.20; actual snapshots in
`closure_evidence/environment__summary.json`. Existing Optuna4.6.0 and isolated
CPython3.12.16/SofaPython3 reused, no system Python or installed SOFA replacement.
Native library linkage and actual package versions are recorded, not inferred
from old documentation. Matplotlib2D figures work; optional Axes3D import warns
about pre-existing package overlap, no3D chart or new package reinstall used.

SOFA26.06 source7c18e95 and matched MappingGraph-patched SDK reused. New headers/
exports in `.runtime/closure_sdk` point only to SAME-build libraries; frame-plugin
ldd has no installed-SOFA mixing. Installed engine remains intact. Raw≈4.8GiB is
Git-ignored. Small results,figures,commands and per-file hashes are committed.
Manifest includes failures/timeouts, not just successful experiments.

## New code

- `models/closure/`: active-interval SDF quadrature,fixed material friction-history
  grid,ActiveIntervalContact,spatial6-component external load.
- `models/closure_frame/`: unchanged planar layer law in fixed material frames,
  independently tested wrench/tangent/history transformation; distinct three-finger model.
- `diagnostics/closure/`: actual Beam closed-work loop,live field-by-field wrench,
  matched-engine reload/memory probes.
- `tools/closure_*`: bounded runners,campaigns,reference integration,wrench LP,
  independent convergence/recovery/global-balance/energy/native audits,fail-closed
  optimization eligibility,small evidence publication and read-only hash verifier.
- `scenes/closure_native_*`, `closure_replay.py`: independent native contact and
  actual recorded-state visualization, not fake animations.
- `tests/test_closure*`: FD,objectivity,action-reaction,moment,kFactor/stiffness,
  pure query/history,invalid input,cone/capacity and reference-rotation checks.

Original `plugin/`,old physics models,golden,handover,old raw/build/SQLite unchanged.
README/AGENTS/.gitignore intentionally updated as metadata; strict previous verifier
reports these current metadata deltas. Separate legacy integrity audit verifies
all2286 historical entries while identifying only expected metadata changes.

## Measured results

| Test | Actual result | Decision/scope |
|---|---|---|
|Two-finger sphere+Fx active quadrature|41node Gauss16→32 difference.053853%;mesh11→41.5973045%;halfdt.02602475%;repeat0|PASS11diagnostics,1%space/.1%dt unchanged|
|Independent narrow contact integral|Gauss8/16/32 max error1.69e-11/3.22e-12/3.78e-13|PASS mathematical reference,not trajectory|
|New contact18DOF FD|8.37317628427e-12 max absolute J error|PASS unit scope|
|Two-finger±Tz|angle.0188791644862rad,moment residual.93583841481|FAIL,other ten local wrench checks pass|
|Three-finger+Tz5e-6|angle.000246035599235rad,force residual2.58610e-8,moment8.77998e-9|Local holding PASS only|
|Three-finger12 force/torque cases|all12hold+tail drift+24srelease/recovery pass|Finite-resolution subgate PASS,not full closure|
|Three-finger convergence|n11q8→32translation1.9645%,rotation1.1608%;history halftranslation4.1077%;dttranslation.2016%|FAIL unchanged limits|
|High-resolution three-finger|n41q16,q32 and one independentq32 retry timeout480s;retry≈23000/36000steps|FAIL/unfinished,not equilibrium/performance|
|Whole reaction wrench,+Tz|unbalancedY moment2.26294929813e-5force·mm|FAIL independent global audit|
|Live field isolation13.98s|Beam Ymoment−2.26294389207e-5;layer≈1.94e-12,cables≤6.1e-18,contact≈3.96e-20|Beam defect isolated,not hidden torque cancellation|
|Beam closed work,amplitude.1mm/θspan.002rad|4.36437901e-7force·mm,normalized.0002778851,coarse/fine converges|General potential FAIL even within small-angle range|
|Matched SDK FREE600points×2|deflection.04121379160634628mm,slip.0008228072034270895mm,vz−.014380704053554549mm/s|PASS original1e-10+1e-6×abs(golden),all600sharedmetrics|
|Native cube/plane load.01|reaction.01000000027994 atdt.001;rawλ≈1e-5|PASS calibration:force=Jᵀλ/dt,stick/slip/release/recontact|
|Native sphere gripper positive buffer|.001/.0005mm buffer:displacement1.69534445e-7/1.69546525e-7mm,difference.00712443%|Buffer diagnostic PASS,fullsurface EXPERIMENTAL|
|Native active reaction|≥2positive contacts,maxfriction ratio.28305,zero final active contacts|No24-active-point claim from24candidate rows|
|Matched SDK adaptive240000steps/2cycles|last60000 liveheap+64/−128bytes,RSSplateau,FD7loaded/5unloaded|PASS bounded scope,not hours/allmodels|
|Python/C++/sanitizers|Python73PASS,new3C++ and old5C++ executablesPASS,newkernelASan/UBSan/LSanPASS|Externalengine not sanitizer-instrumented|

All raw metrics and a complete76-trial CSV are in `closure_evidence`; see per-topic
CLOSURE_01..10 reports for commands,thresholds and source scope. Rank6,cone-origin
interior and bounded measured-normal-force feasibility are separately reported.
Actual three-finger patch LP supports all12tested normalized wrenches, but neither
LP nor local dynamics overrides the discovered whole-system balance failure.

Three fingers increase total material/mass/cables50% relative to the two-finger
benchmark. Root radius≈95.15mm is a research layout, not the target50mm body. Finger
planar guides remain explicit; free object has no hidden constraints,pose fixes or
invented restoring torque. Global reaction reconstruction includes fixed and guide
reactions separately, rather than mixing them into free DOF residuals.

## Shapes, controls and jamming

Cylinder/box separately run+Fx,+Tx,+Tz with correct analytic inertia. +Fx/+Tx local
holding pass,+Tz fail; other shape/direction combinations NOT RUN. Sphere is not
reused as all-shape certification. μ0,low μ,wireOFF,overload,bad placement controls
fail. New three-finger μ0/lowμ/wireOFF/overload Fy controls also all fail, including
small displacement but unacceptable force residual cases. Thus position alone
does not produce a false PASS.

Pressure0/.0001/.001/.01 at fixed wire and external load were compared. Low-load
ON/OFF displacement difference≈.0043%,below mesh error≈.6%; no resolved grasp gain.
At1e-5 all fail; positive pressures identical here because sliders already stick.
This is not identification of ultimate load/pressure optimum. Stiffness improvement
and grasp capacity are distinct. Pressure/friction/material are research assumptions,
not measured PET/vacuum fabrication properties.

## Native surface, energy and memory limitations

Original zero-buffer native full gripper had no active hold reaction and fails;
positive numerical skins retain contact. Native calibration confirms impulse/dt
interpretation and repeated contact/release. Fullsphere triangle/dt convergence,
allshapes/12wrenches and native long-run memory remain NOT RUN. Hard contact differs
from soft SDF normal compliance, so tiny native displacement is not a calibrated
performance improvement. Film collision skins do not change underlying beam EA/EI.

Converged Beam circulation and netmoment are independent obstructions. No arbitrary
globalpotential is defined,missing energies are not0. Contact/layer/actuator values
are partial; full Δ(K+U)=external+actuator+parameter work−friction−damping−numerical
dissipation cannot currently be certified. A new energy-derived/objective beam
requires independent implementation and regression, not modification of the golden model.

Memory originalFDclassifier compared open-scene to unloaded counts incorrectly.
Original FAIL retained; phase-aware audit separately verifies exactly two observer
streams close. Liveheap/RSS/PSS/PrivateDirty/FD evidence scopes240000steps only.
ASan virtual-shadow-cap failure and sandbox LSan failure were preserved before an
approved shadow-compatible2GiBRSS/60s run. No claim of full engine ASan coverage.

## Optimization, Python and visualization

Optuna import PASS; old30mm24COMPLETE/3PRUNED study remains separate historical
evidence. New100mm trials0,no objective/Pareto/design optimum because global moment,
energy and improved-geometry convergence gates fail. Hash-verified fail-closed guard
records reasons. No failing values used as favorable objectives; dt not a design variable.

Original PythonV109/V110FREE/V110SHEAR byte-identical copies rerun600steps with
isolated3.12runtime,CSV and XML comparison PASS. These .3s responses are transient,
NOT static equilibrium. V110's proxy slip definition is not conflated with exact
mapped interface slip. Runtime recovery remains PASS,not the earlierhistoricalBLOCKED.

Actual three-finger pilot2401frames replay headless PASS,contacts/cables/object poses
from measured data; GUI NOT RUN. Optional GUI command/environment saved,not a physics gate.

## Completion boundary and next work

Bounded campaign and one independent high-resolution retry are finished; no jobs
left in background. Overall requested physical system is **not completed**. Priority:
new conservative/objective beam →globalmoment/energy →3fingerhistory/spatial/cost
→native triangle/dt/shape/torque qualification →pressurecapacity →100mm Optuna.
No further identical timeout retries or invalid grasp optimization were launched.
Exact verification/reproduction/resume commands are in CLOSURE_NEXT_TASKS.md.

Physical measurements/hardware runs:0. All figures/tables are actual simulations
or explicitly labelled independent mathematical diagnostics. No real gripper
performance certification or global optimum is claimed.
