# Native section backward error and stock bending alternatives

2026-11-19. Feature commits `3593421`,`c487517`,`127119b`,`e0d5750`.
This is **not B3/grasp qualification**.
Historical B3 functional holding344/351, release375, mesh/time failures and
hardware clearance failure are unchanged. No 100g, Lift or new product CAD run.

## Problem and controls

The prior checkpoint required loaded Skin/one-Rail/two-Rail tests, not more
initial spectra.407 uses exactly the same eight Skin tip load locations and
1e-6N inward resultant for all three components. All stock Newton absolute and
relative stopping settings remain1e-12; physical time.1%,mesh1%,stateAPI1e-12m
gates are not relaxed. No own FEM, contact, integration or force-law solver was
introduced. New C++ components are read-only BaseObjects observing native forces
and matrices. Installed SDK is untouched, matching v26.06.00 only.

## 407 — force residual and coordinate representation

Let `u=K_free^-1 F_free` be an independent matrix reference and
`u_repr=fl(q0+u)-q0`. These PRIVATE positions are passed to native addForce in a
separate buffer, NEVER installed in MechanicalObject. They are not accepted
SOFA states or static-equilibrium results. Root DOFs are projected consistently.

| Component | norm(Ku-F),N | norm(Ku_repr-F),N | Native force residual,N |
|---|---:|---:|---:|
| Skin |4.35349e-14|3.87329e-9|3.87323e-9|
| Skin+one Rail |2.13889e-14|4.00599e-9|4.00594e-9|
| Skin+two Rails |2.53782e-14|4.60307e-9|4.60324e-9|

Maximum coordinate rounding is6.88–6.93e-18m. Native-force versus represented-K
defects are1.17–3.64e-11N, much smaller than the represented residual. Thus this
case is dominated by stiffness-amplified coordinate representation error; it is
not explained by the private linear solve residual alone. This is not a theorem
that no representable equilibrium can exist. All six actual loaded native trials
FAIL strict log/solver qualification. All three zero-load observed states remain
exactly at rest. Do not derive certified loaded stiffness ratios from the PRIVATE
reference displacements, or turn process exit0 into a PASS.

425 moves the **whole** Skin reference by(-.04995,0,.05)m, without changing
dimensions, material, loads or constraint indices. Native initial K changes by
only3.22837e-15 relative. Represented residual decreases to5.82736e-10N;
native force residual is6.98822e-10N, still above1e-12N. Zero-load actual state
error remains0; both loaded trials FAIL. Translation supports the arithmetic
diagnosis, but does not solve the required equilibrium gate. No state correction
or origin substitution is applied to B3.

## 408–421 — installed native membrane/bending alternative

Separate flat rectangular coupon:L100mm,W20mm,h.1mm,E250MPa,nu0,root5mm,
no guide/cable/contact. Native TriangleFEMForceField plus
FastTriangularBendingSprings uses unfitted `D=E*h^3/(12*(1-nu^2))`.
It is deliberately NOT a same-geometry B3 comparison or a replacement.

Direct assembled static solves408 fail. Source inspection found the native
FastTriangularBendingSprings modern buildStiffnessMatrix iterates3 local spring
indices, whereas legacy addK/addDForce includes all4.415 measures the actual
modern assembled matrix against the native legacy matrix: relative Frobenius
difference **0.347062388183**. Legacy force FD error is1.33e-11 at epsilon1e-7m.
No SDK patch or ReGrip derivative ForceField was written.

GraphScattered CG409 solves only the coarse coupon. Fine411/412 fail;413/414
show the2000-iteration inner cap is reached. Changing only the inner CG criterion
did not solve the outer gate and was not adopted. Stock native matrix-free PCG
with native Jacobi preconditioner416/417 solves the same stored force model,
without rebuilding the force law or relaxing the outer gate.

Actual tip displacement with width3nodes is3.506517/3.938997/4.080353mm for
length21/41/81nodes. ALL-PAIR mesh errors are10.9794%,3.46431%,14.0634%:
**FAIL1% mesh**. Width5nodes21→81 differs30.5570%.418 half-load all-node/two
static-output linearity errors1.13e-14/2.72e-14m pass ONLY that linearity check.
420 observer-on/off CSVs match417 exactly for81×3 and81×5 (same hashes).

421 evaluates quadratic curvature REFERENCE FIELDS on native K, not prescribed
or simulated deformation. The inferred tensor has substantial mesh-dependent
bending/twist coupling, unlike the target isotropic nu0 plate tensor. Example
81×3 normalized diagonal(.329167,.166667,43.074479),off-diagonal C13=2.633333,
versus target diagonal(1,1,2). One scalar fitted to tip displacement would conceal
this issue and was NOT fitted.

419 uses a manufactured distal40deg reference, not a rendered deformation.
Native initial bending force norm7.69693e-4N and subsequent solve failure mean
this spring construction is NOT automatically a stress-free precurved B3 skin.
No initial prestress is hidden. Native PCG is a numerical workaround, not a
qualified continuum shell or a product advancement.

## 422–424 — installed rectangular BeamAdapter Rail

Stock BeamInterpolation rectangular2mm×.5mm,E250MPa,nu.3; native
AdaptiveBeamForceFieldAndMass with computeMass=false for STATIC tests. The
rectangular implementation disables shear terms and uses polar J for torsion;
torsion/dynamics remain unqualified. The Euler bending reference is only an
approximate independent comparison, not SOFA evidence.

422 loaded direct Newton21/41/81 fails;424 coarse GraphScattered CG also fails.
423 `straight=false`, manufactured40deg reference, zero load: all three meshes
complete with EXACT0 rest-position error and repeat difference. This validates
only zero-load reference retention, not loaded bending, angular state accuracy,
stress-free internal force to1e-12N, Skin/Rail attachment or B3 use. Repeated
loaded Newton failures are retained; no blind iteration/tolerance sweep follows.

## Reproducibility, builds and resources

Actual scenes, process commands, limits, logs, producer snapshots and source/
binary hashes are in `product_prototype/results/<case>/`. Every new run is a
unique path. Enforced per-child4GiB/480s. These short native runs do not justify
predicting full-grasp runtime. Null energy/work/contact values were not filled
with zeros: these coupons do NOT measure whole grasp energy, reactions or area.

-406 `cad/build_elastic_probe406/libReGripElasticObserver.so`
 SHA256 e143096e607ab25c0740254b8bd66a7983a3bd6b1ba6a1ec447925b52e514f53.
-410 `cad/build_assembled_observer410/libReGripElasticObserver.so`
 SHA256 51b004b5b0022db006d92762f2f10175060eefe32db9ce8f0907130a6d5c29b3.
-428 `cad/build_rigid_observer428/libReGripElasticObserver.so`
 SHA256 0cf7421083eec9f01d8c175b1dfaab4dd4396f06a7467e9fa0e5e50a3be916f0.
-332 calibrated journal/controller is unchanged. Frozen source400/406/410 and
 binary identity guards prevent edited live C++ being labelled as an old build.
-v8 publication verifies764 prior-v7 immutable files without mismatches. v9
 verifies395 prior-v8 immutable files,v10 verifies429 prior-v9 files;v11 records
 the final audit and all21 summaries. Every manifest retains exact snapshots.
 Figure `evidence_native_alternatives_v11/native_diagnostics.png` separates
 PRIVATE reference residuals from actual native accepted shell tip outputs.

Read-only restart, from repository root:

```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/native_section_translation425/summary.json
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/native_shell_assess421/summary.json
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/native_bending_matrix_paths415/summary.json
```

Example reproduction commands (MUST choose fresh tags; these do not overwrite):

```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/native_loaded_section.py --tag NEW_translation --components skin_only --origin-shift -0.04995 0 0.05
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/native_shell_coupon.py --tag NEW_shell --nx 41 --ny 3 --solver native-pcg
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/native_beamadapter_coupon.py --tag NEW_rest --load 0 --precurve
```

## 427/429 — continued Rigid3 tangent diagnosis

The proposed next independent test was actually implemented in this session.
NativeRigidTangentObserver is another read-only BaseObject, not a ForceField.
Translations are perturbed by epsilon×.1m; orientations use LEFT quaternion
exponentials with epsilon×1rad angular scale. The first two root nodes have zero
perturbation. Force[N] and torque[Nm] errors are reported separately,not combined
into an arbitrarily scaled norm. Actual q/v are checked unchanged after queries.

427 initially called the scalar convenience addKToMatrix API, which BeamAdapter
does not override; that path returns no useful tangent. Its apparent100% FD
difference is **observer/API failure,not evidence of a native derivative bug**.
All427 source/binary/Raw remains preserved and excluded from physical conclusions.
429 fixes the diagnostic to call the actually implemented native addDForce path.
The curved reference at amplitudes0 and1e-7 has stable relative force errors
~3.12e-5 and torque errors~8.90e-4 across epsilon1e-6/1e-7/1e-8. These are measured
directional discrepancies,not an all-column derivative or time-convergence PASS.
The curved observed/unobserved actual rest positions match exactly. The straight
reference has strict Newton failure even WITHOUT the observer;do not attribute
that failure to observer mutation or present its partial state as a PASS.

430 tests the specific iteration-cap hypothesis from422's still-decreasing
residual:Newton maximum30→120, all tolerances/load/model unchanged. It fails
actual Line Search at iteration58 (later62/65 also logged),runtime.211s.
This is a numerical iteration-budget change,not an OS exhaustion or a physical
parameter change. Increasing iteration count alone is NOT adopted as a cure.

## Next hypotheses / stop conditions

Do not rerun372 or expand unqualified B3 to100g/Lift. Next useful physics work is
a native rectangular BeamAdapter reference-length/initial-force inventory,
comparing exact geometric segment rest transforms with the straight-reference
assumption, then actual modern assembled matrix versus addDForce at that SAME
state.429 directional FD is DONE; do not repeat it unchanged. Reuse read-only
observers,not a new force law. Any new inner plan requires evidence from this
distinction,not another blind iteration/tolerance sweep. Coordinate-local native
configuration remains a candidate,not a force-gate waiver.

First read-only command for the next session:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/native_rigid_tangent429/summary.json`.
The implemented reproduction command is
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/native_rigid_tangent.py --tag NEW_rigid_probe`;
use only for a justified regression,not as new research. It validates frozen428
source/binary identities before querying the native model.

Stock alternatives have not passed required continuum/loaded gates. Repeated
failure directions above are stopped and checkpointed, not promoted. Existing
B3 moving-solid clearance/CAD STEP kernel and material/actuator measurements
remain separate unfinished tasks. No claim of final fabrication readiness,
wrapping,100g,Lift,whole energy or automatic background continuation is made.
