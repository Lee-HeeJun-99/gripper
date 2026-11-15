# ReGrip autonomous research — measured checkpoint

## 1. Outcome and provenance

**Overall: EXPERIMENTAL, not a qualified100mm grasp design.** An independent
material-point contact model removes the observed force/Commit state mismatch
and brings the measured friction-return loss history differences below1%.
Beam/contact spatial motion convergence still FAILS. Global energy and100mm
grasp optimization remain BLOCKED. No failure threshold was relaxed.

Baseline: `63970172ad196e0add3ad42a67ccaee4c7a8975e`.
Branch: `development/regrip-autonomous-research`.
Implementation checkpoints: `621266c` and `18ce7d4`,followed by the temporal
cross-check commit recorded in the manifest.
Final validated source checkpoint: `456d83f2f36fb0e64deabac91341c636681af36d`.
The evidence manifest records the final source checkpoint;the subsequent docs
commit is identified by `git log -1` to avoid a self-referencing commit hash.
All new raw is in `results/autonomous_20261115_a01`;no remote push performed.

Actual environment:Ubuntu22.04.5,kernel6.8.0-138,GCC11.4,CMake3.22.1,
Conda Python3.10.20. Reused the matched MappingGraph-patched SOFA26.06 SDK
`build/grasp_20261115/sofa_patched`,not the system installation. The immutable
physics library is `build/autonomous_20261115_a01/v3/libReGripMaterialPointContact.so`.
A separate clean-final rebuild/API test also passes;it is not pooled into the
v3dynamics identity. Exact transitive source/generated/binary hashes are in
`autonomous_evidence/compiled_identity.json` and the evidence manifest.

Before work the tree was clean and1845entries of inherited birth raw/source/
binary evidence passed verification. Those are prior results,not new-model
certification. Old ConservativeBeam,contact versions,golden and Studies remain
unchanged. No actual PET/vacuum/hardware measurements were made.

## 2. Research questions selected from evidence

1. **Is interpolated return-map loss the loss of the actually committed state?**
   Old force integration returns at moving/interpolated quadrature locations,
   whereas Commit returns and stores fixed grid nodes. They are different
   spatial discretizations. This is a testable mechanism,not proof that all
   convergence failures have the same cause.
2. **Can same-material-point force/return/Commit improve loss convergence?**
   Selected fixed reference midpoints,not parameter tuning. This avoids history
   interpolation,zero-boundary anchors and changing quadrature identity.
3. **Does removing that mismatch solve Beam-space convergence?**
   Actual11/21/41node trials show it does not. Priority therefore changes to
   contact centerline interpolation and the Beam nodal deformation field.
4. **Can objective curved interpolation be differentiated consistently?**
   Developed and independently tested a virtual-work pullback kernel. It is
   not yet a production SOFA contact model or a claimed spatial-error cure.

## 3. Implemented model and mathematical meaning

New `models/material_point_contact` generates a separate SOFA component from a
new local generated copy of the inherited Birth-aware implementation. No old
source/library is overwritten. For reference edge length L with Npoints:

`s_i=(i+1/2)/N`, `w_i=L/N`.

Each immutable reference material point owns an object-material-frame history.
The original chord birth crossing,implicit root derivative,normal transport,
Coulomb cap and return-map kernels are reused. Force,AD Jacobian,value-only
observation and Commit evaluate the same `s_i`;there is no remapping. Normal
contact retains the original active-interval Gauss8rule. Tangential quadrature
is now fixed midpoint,NOT the legacy moving Gauss/cellOrder rule. Thus this is
an independent numerical model to converge,not an exactly equivalent speedup.

For each point,the return measure is `D_i=c_i||u_trial-u_return||`,
`c_i=mu*Fn_i`;reported plastic-return loss is `sum(w_i D_i)`.
The actual Commit sum and the observation sum are separately accumulated and
compared. Query/energy/Jacobian calls do not advance history. Detachment removes
stored tangent energy into a separately reported inventory loss;it is NOT
automatically relabeled as frictional heat. Through-chord and grazing guards
are inherited;this remains endpoint-chord detection,not full curved-surface CCD
or an ODE event-subdivision integrator. Initial friction remains elastic penalty
stick,not an exact no-slip constraint. Actual midpoint coordinates satisfy an
ULP-scale identity check;physical tolerances are unchanged.

Relevant changes:the new component/test,`diagnostics/autonomous/Prescribed.cpp`,
`tools/autonomous_trial.py`,research build/campaign/refine/quarter/assess/event/
prescribed/geometry/energy/evidence tools,`models/contact_kinematics/HermiteMap.h`,
Hermite and artifact-guard tests. New sources and commands are hashed/archived.

## 4. Independent and API verification

| Actual new verification | Result and numeric evidence |
|---|---|
| Clean build,plugin linkage and actual SOFA API | PASS,v3 and separate clean_final |
| Uniform plane slip | PASS,D=.000050999999999999912 vs analytic.000051 |
| Actual assembled force Jacobian FD | PASS,max6.83755e-10 |
| addForce/addDForce/buildStiffnessMatrix | PASS,kFactors0,2.5,-.25 |
| Query purity/Commit consistency | PASS in unit and completed dynamics |
| Prescribed common rigid transformation | PASS,new relative D covariance8.42e-16 |
| Actual birth/no-contact SOFA scenes | PASS,logs under events/ |
| Through-chord scene | PASS expected rejection;invalid scene is not physical PASS |
| Frozen ConservativeBeam61states/API | PASS,spatialJ error5.47e-8,moment5.68e-14 |
| ConservativeBeam dense100equivalence | PASS,E/F/J difference0 |
| Python suite | PASS89tests;includes4new identity/preservation guards |
| Existing contact/invariant/frame C++ suites | PASS3suites |
|600step FREE golden repeated twice | PASS9metrics,both actual patched-SDK runs |

Logs: `build_v3/`, `build_clean_final/`, `prescribed_clean/`, `events/`,
`final_regression/`, `validation_unit_autonomous/`, `validation_golden_autonomous/`
inside the campaign. Golden tolerance remains `1e-10+1e-6*abs(reference)`.
The original45gate suite was not re-executed or counted as new contact gates.

The prescribed moving Sphere geometry deliberately excludes Beam/ODE dynamics.
Across its cases the old maximum absolute accumulated pre/post Commit energy
jump is1.01687e-6;new8.70326e-20. At h=.005/200steps old signed jump is
−1.27181e-7. It grows with step count in this path. New observed/committed
plastic loss agree exactly. Both models' loss spatial differences already
pass1% on this simpler path:the evidence supports a representation mismatch,
not a unique explanation of every old dynamic error. Endpoint work residual
is nonzero and decreases with dt;it is not fitted away.

## 5. Actual SOFA three-finger convergence

All rows below are **new actual SOFA** with one v3 compiled contact identity,
original ConservativeBeam,three100mm/two-layer fingers and explicit planar
guides. Object is a free6DOF sphere(R5mm,mass.0001,per-mass inertia10I).
EA183.0582466,GAy=GAz57.7835374,GJ8.0808081,EIy=EIz10.6666667 in inherited
simulation units. Equal-mu.3,kn=kt.001,wire tension.001,pressure.001,
Rayleigh mass2,EigenSparseLU,base dt.0005s and +Tz5e-6F·mm remain unchanged.
These are research assumptions,not measured PET/pressure values. Pressure
switches at3/15s,wire at.5/16s,disturbance at6/14s;the exact scene contains the
piecewise schedule. Object has no hidden projective constraints.

Diagnostic window is unchanged13.9<=t<14s. Loss is the mean **cumulative**
plastic-return loss in that window,not the increment within that window.
Errors are `abs(coarse-fine)/abs(fine)`;absolute errors remain in assessment.

| Comparison | Translation difference | Rotation difference | Loss difference | Original limit | Joint result |
|---|---:|---:|---:|---:|---|
| h.01→.005mm |4.617372%|.014337%|.129703%|1%|FAIL |
| h.005→.0025mm |1.016972%|.015406%|.279753%|1%|FAIL |
| h.0025→.00125mm |.030025%|.002407%|.049621%|1%|PASS |
|11→21nodes,h.0025 |4.959838%|.061953%|.377502%|1%|FAIL |
|21→41nodes,h.0025 |2.801024%|.034681%|.124697%|1%|FAIL |
| dt.0005→.00025s,h.0025 |.097737%|.005720%|.0999735%|.1%|PASS,borderline |
| dt.00025→.000125s,h.0025 |.015950%|.004351%|.074528%|.1%|PASS |
| dt.0005→.000125s,h.0025 |.113702%|.010070%|.174427%|.1%|FAIL |
| Same-condition repetition |0%|0%|0%|.0001%|PASS |

Quarter-dt completed144000steps in679.151wall seconds. Its actual hold
displacement is4.368852201e-6mm and relative moment residual4.97024e-4.
Nonadjacent base→quarter differences fail despite both adjacent pairs passing;
therefore base-dt time qualification is NOT complete. Normal Gauss8→16→32 was
not rerun for this independent component;
old normal integration success is inherited scope,not full new qualification.

Measured hold displacement at h.0025:11nodes4.373819678e-6mm,
21nodes4.602075143e-6mm,41nodes4.734695093e-6mm. Corresponding global relative
moment residuals7.79794e-5,2.52567e-4,4.84342e-4 all pass the local1e-3line.
Force residuals also pass. Small absolute mesh-motion errors do NOT erase
their relative FAIL. All completed bounded-hold cases are EXPERIMENTAL as full
grasp models.24s base and fine-repeat complete recovery/release;18s runs only
support the hold comparison,not the full24s recovery gate.

See `autonomous_evidence/comparisons.csv`, `assessment.json`, `convergence.png`,
and per-trial scene/config/identity/command/state/contact/layer/process files.

## 6. Remaining spatial error and a separate candidate

Independent prescribed cubic cantilever with a narrow Sphere contact gives
linear-centerline normal-integral errors4.83418%,1.46780%,.10491% at11/21/41
nodes. SciPy reference integral.0014915586869258936 has estimated absolute
quadrature error3.07e-14. A scalar cubic Hermite curve reproduces this prescribed
cubic;this is not a solved Beam convergence test.

Offline actual-state reconstruction at13.99s gives linear versus director-
Hermite normal-integral differences3.08517%,.100805%,.048647% at11/21/41nodes.
It cannot predict the equilibrium after changing the map,and does not remove
nodal FEM discretization error. It is evidence to select the next experiment.

New candidate centerline uses reference-length directors and Hermite weights.
Force pullback is virtual-work consistent and includes nodal moments. The
spatial Jacobian includes the geometric force-position Hessian and the
left-SO(3)connection,not just a symmetric energy Hessian.60independent smooth
states give FD1.56e-9,normal-energy gradient3.47e-10,objectivity6.11e-16,
force/moment1.73e-17. Sparse analytic pullback matches denseAD2 within2.78e-17.
**Not SOFA-integrated**:curved active bounds,multiple contact intervals,axial
strain/director interpolation and profiling must be verified first. Simply
changing the point location in the old linear assembler would be incorrect.

## 7. Energy,grasp,optimization and resource boundaries

Global energy remains BLOCKED. A scalar seeded10000step spring-slider derives
`W_endpoint-ΔU-F1Δp=.5k(Δe)^2`,max unexplained residual1.02e-17. That derived
projection term is not a fitted global numerical dissipation. Scalar capacity
variation is not vacuum-volume work. Full synchronized FrameLayer,cable,
pressure-control,normal/tangent contact,Rayleigh and external-work accounting
is still missing. Detachment inventory relative differences remain large even
when absolute energies are tiny;no release-energy convergence is certified.

New12wrench/Sphere-Cylinder-Box/full-force-closure certification and100mm grasp
Optuna remain BLOCKED by mesh/energy qualification.0new grasp trials,no new
qualified Pareto candidates. Prior24COMPLETE structural trials/Candidate3 are
inherited independent structural evidence only;not repeated or relabeled.
No new pressure-capacity improvement,50mm-base compliance,native surface
qualification or GUI demonstration is claimed. Research base radius~95.15mm
still violates the50mm target. Rank6alone would not establish force closure.

Four first-stage history jobs used4GiB/480s each.41node profile justified one
900s exception;full run completed635.76wall seconds. A separate quarter-dt
profile justified one900s bound. Exact decisions and process outcomes remain
raw,including failed builds/tests. At most4long physics children were used.
Per-process/proc RSS/PSS/Private_Dirty/FD and native MEM/live-heap samples are
preserved. Resource summaries describe bounded runs,not240000step continuous-
contact,reload/unload or hours-scale leak certification. No installed SDK was
overwritten and no ABI-mixed header substitution was used.

Sampled full-run peaks are RSS111040KiB/PSS107127KiB in the fine-history run;
FD is10in every sampled process.41node RSS peaks99516KiB and quarter-dt92948KiB.
See resources.json for exact slopes/sample counts and raw sampling limitations.
The new artifact verifier passes894SHA256entries;raw archive is1173017042bytes
at this checkpoint,external-drive only and excluded from Git. The2D plot used
a writable/tmp Matplotlib cache fallback;the unavailable optional Axes3D warning
is not a physical validation result and no3D GUI was claimed.

## 8. Failures,preservation and reproduction

Initial unit build failed(unqualified pose),then a query-purity test mistakenly
compared separately accumulated AD/scalar floating sums exactly. Corrected to
the actual before/after purity contract,not relaxed physics. Failed logs remain;
the first failing test-source snapshots were not captured before correction.
Subsequent builds automatically archive sources before compile. A prescribed
warning was corrected in a new clean diagnostic namespace. A refinement-script
syntax error was fixed before child launch. Initial Hermite test warning was
corrected in the separately archived sparse test. None is hidden as PASS.

A temporary tool-name collision overwrote the historical research_trial.py.
Restored exact baseline content;the new runner is autonomous_trial.py. The
collision/restoration remains in local history. Early raw command references
to research_trial.py mean the new runner at621266c;use autonomous_trial.py now.
Hash guard checks the restored historical file. Old physics/raw/golden were
not modified. Reports/raw/compiled identity distinguish code snapshots.

Read-only/current-evidence commands:

```bash
cd /media/ubuntu/99419895-2058-45b4-b746-b36ea7112e4e/research/LHJ/ReGrip
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/research_evidence.py --verify
$PY tools/birth_verify.py --raw
$PY tools/research_assess.py
$PY tools/research_prescribed_assess.py
```

Fresh namespace reproduction(do not overwrite a01):

```bash
export REGRIP_RESEARCH_OUT="$PWD/results/autonomous_reproduce_a02"
export REGRIP_RESEARCH_BUILD="$PWD/build/autonomous_reproduce_a02/v1"
$PY tools/research_build.py
$PY tools/autonomous_trial.py profile --history .0025 --profile
$PY tools/research_campaign.py
$PY tools/research_refine.py
$PY tools/research_quarter.py
$PY tools/research_prescribed.py --suffix _clean
$PY tools/research_events.py
$PY tools/research_slider_energy.py
$PY tools/research_geometry.py
$PY tools/research_assess.py
```

Campaign/refine/quarter perform profiles and enforce bounded attempts. For a
single24s reference use `tools/autonomous_trial.py NAME --history .0025 --duration 24`.
Each raw command.json is the exact native-driver command;config.json and
scene.scn record physical parameters. Auxiliary Hermite tool has its own
exclusive output/binary suffix,not a physical campaign component.

## 9. Checkpoint and next research decision

This finite campaign resolves a measured state/loss inconsistency,not the
ultimate system objective. Avoid spending more bounded runs on an unchanged
known-failing linear map or launching unqualified optimization. The next
meaningful phase is a new curved-contact component with correct virtual-work
assembly,independent reference and conservative curved-contact detection,then
profile and11/21/41mesh qualification. The tested candidate kernel is saved;
that substantial SOFA integration is NOT RUN at this session checkpoint.
See NEXT for exact entry points;no unattended restart is promised.

Actual fabrication still requires measured layer thickness/width,anisotropic
moduli,pressure distribution,friction curves,wire routing/offset/friction,
sealing and attachment compliance. Numerical research success is not hardware
performance validation. All present numbers are actual SOFA,independent
prescribed/math calculations or explicitly research assumptions;none is a
real-material measurement.
