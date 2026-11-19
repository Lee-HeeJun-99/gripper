# Finite hardware COM / Native mass validation

## Follow-on actual public acceleration API588–591

Read-only NativeMappingAcceleration observer calls installed Mapping API with real
parent velocity and ZERO parent acceleration into a TEMPORARY output Data object.
No body/child position,velocity,acceleration,force or mass Data are changed.
Expected child composite acceleration is omega cross (omega cross radius).

588 build failure missing MechanicalParams include is archived;589 success only adds
the correct installed header. Build/Native children4GiB/480s guarded. A preliminary
unbounded compiler invocation587 failed with the same include error before the
bounded build runner was added;it is NOT claimed as a guarded experiment.
590 scene failure is XML registration order,not physics failure.591 moves RequiredPlugin
before children;both runs complete. Real q/v/impulse/mapped-point arrays match572
EXACTLY0 before/after observer.96temporary output samples:API0m/s²,expected up to
0.403523684933m/s². This backs the header finding with an actual API capability test.
It does not certify all SOFA compositions or prove an ODE solver replacement is needed.

Probe589 binary SHA3f1c9995cdadbef875ea340a6a814566939bbf19bd636681315e3dc2f397e909;
compiled source SHA9e3e3a8001b1eb9755a32720c3222491d9e5010e9f8fa3d44e3444d66964865d.
Reusable build product_prototype/cad/build_b3_mapping_build589.
Raw build588/589 and Native590/591 under product_prototype/results/.
v26 evidence3933files;prior3785immutable files unchanged. SDK/binaries/source/cache
and scenes/commands/actual outputs frozen. Runtime5910.121/0.137s;RSS NOT MEASURED.

Current composition is BLOCKED for physical off-axis rigid dynamics adoption.
Do not report this as resource exhaustion or product completion. Existing B3 physical
time/mesh Gates remain FAIL and density/joint/wholeassembly data remain missing.
Repeated dt refinement on this branch is stopped because it cannot remove the
identified missing response. Next stock inertial-capability verification or narrowly
scoped inertial-force correction must pass BOTH581/584 references before B3 contact.

## Follow-on cycles581–586 (after feature commit e85534a)

Analytical torque-free reference for an axisymmetric ring:
world angular momentum L is fixed;the symmetry axis n rotates about L with
angular speed |L|/Itransverse. Then
omega=L/Itransverse+(1/Iaxial-1/Itransverse)(L dot n0)n(t).
This is an exact mathematical reference,not prescribed SOFA output.
581 checks reference momentum defect≤2.03e-16,energy≤7.34e-16 and Euler-equation
FD residual≤9.74e-9rad/s². Native measured omega differs by0.122997rad/s after10ms,
same for all3dt;angular momentum defect0.660162%. No timestep cure demonstrated.

582 changes ONLY initial spin direction to the ring principal axis,keeping
spin magnitude,translation,mass,geometry,solver and duration.583 actual mapped
mass inventory relative angular drift3.11e-15;584 Native omega vs exact≤6.47e-15rad/s.
Positive control narrows the failure to non-principal rotational dynamics in this
Native composition. Existing SDK Mapping.h documents dJ*v composite acceleration,
but default implementation is empty and installed RigidMapping.h/inl contains no
computeAccFromMapping override. Headers/executable are hashed in v25 evidence.
Do not infer that every Native rigid/integrator option is unsupported.

585 preserves2 failed independent regression definitions:componentwise relative
comparison at exact-zero off-diagonal inertia components.586 tensor-norm relative
comparison keeps1e-14 threshold without any denominator floor;all5 tests pass
(analytic box,unit scaling,rigid objectivity,principal/stationary spin,invalid inertia).
This changes mathematical-test comparison,NOT physical0.1%/1%/strict API Gates.
Both failed and corrected test source/logs are frozen.

Actual Native plots:results/b3_finite_spin_exact581/actual_native_free_spin.png and
results/b3_finite_spin_principal_exact584/actual_native_free_spin.png. Viewed581.
Experimental vs analytical quantities clearly labelled;no fabricated shape/force.

v25 evidence3787files,prior3672immutable paths unchanged. No long B3 trial run.
Independent material/join calibration cannot be inferred from geometric moments.
No new hardware mass candidate adopted;old Holding and failures unchanged.

NEXT:verify installed stock composite-inertia/gyroscopic path against BOTH
off-axis and principal-axis references before any B3 adoption. No further blind
dt/alarm sweep. No new ODE/contact solver justified. Full B3 time/mesh/interference,
100g Holding,Lift and fabrication remain incomplete. Exact fresh commands in CHECKPOINT.

Research scope only. Original B3 functional Holding/Release and all failed
time/mesh/clearance trials remain immutable. No B3 checkpoint reused.

## Cycle A:independent component moments565

Signed tetrahedral simplex integration independently reproduces trimesh COM and
normalized inertia for box,16/32/64 annuli and36 exported convex supports.
Rigid transformation cross-check max2.35506e-10 in stated mm/mm² diagnostics.
Analytic annulus inertia errors0.0331124,0.00835840,0.00209464mm² decrease with facets.
This is geometric component verification,not selected density or overlapping
eyelet/support union mass. Total physical hardware COM/inertia remains BLOCKED.

## Cycle B:actual Native COM-frame experiment566–574

Two finite rings ONLY,shared original world surface,10mg/ring research mass,
no support/FEM/cable/gravity. COM shifts preserve initial material-point velocity
using vCOM=vframe+omega×offset. Same world shape expressed in two permuted bases.
4steps ×2.5ms. Existing332/512 binaries hash guarded;Native LocalMinDistance,
all finite collision models retained in contact cases. Free reference explicitly
removes contact pipeline,not a hardware-clearance or Holding test.

566 free basis comparison passes.
567 body-frame normalized tensor passed to UniformMass:contact comparison FAIL,
max mapped q0.00120949m,v0.283900m/s. Public initial M returns input rotational
tensor without body-to-world transport while mapped contact J uses world angular
velocity.569 M impulse defect≤4.24e-22Ns/Nms but intended world inertia mismatch
2.68854e-12kgm². This isolates input convention mismatch;not all SOFA rigid models
declared broken.

568 uses initial WORLD tensor:strict basis PASS,q≤1.38e-16m,v≤2.73e-14m/s.
570 public initial inertia mismatch0,M impulse defect≤8.48e-22.
Actual active J point to previous loaded mesh≤1.44e-17m.
World-frozen tensor is a diagnostic approximation,NOT rotating anisotropic inertia.

571 instead uses six equal positive Cartesian masses under Native RigidMapping.
Their volume covariance exactly reproduces ring COM/inertia;no new physics class.
Basis contact PASS,q≤1.27e-16m,v≤2.82e-14m/s.
572 free comparison also passes,but573 actual point-mass angular inventory
FAILS0.1% invariant gate:0.660162% drift after10ms.
574 contact angular impulse defect1.76126e-10Nms.
Neither basis equivalence nor exact initial mass matrix proves physical dynamics.
577/578 keep duration/inputs and refine free dt;579/580 drift remains0.660162%.
This controlled test distinguishes missing rotational dynamics from a timestep cure;
no further blind refinement. Candidate not adopted.

## Cycle C:finite contact discrete event576

575 analysis used isolated3-row block update despite multiple simultaneous blocks.
Its0.51236m/s update mismatch is analysis error;Raw retained.
576 reuses568 untouched states and includes ALL-body row impulses:
row update residual2.22e-16m/s;actual active normal target
vnormal+=-buffered_gap/dt residual2.83e-9m/s.
Normal target is discrete contact stabilization,not restitution or continuous CCD.
No full time convergence PASS or change to contactDistance0.2mm.

## Evidence / runtime / continuation

Native child runtime0.136–0.405s each,4GiB/480s guarded. No long trial justified.
Raw:product_prototype/results/b3_finite_*565 through *580 (explicit names in manifest).
Evidence:evidence_product_com_v24/manifest.json:3674 files,3354 prior immutable
hashes verified,0mismatches. Every experiment includes frozen producer,scene,
Native logs/command/process and actual state journals when run.
Source commit322e73fc1a6c241dedd307247bc67e8842c04879;all per-run hashes in summaries.

Reproduce with new UNIQUE tags,never overwrite:
```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/finite_mass_reference.py --tag UNIQUE_MASS
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/finite_com_native.py --tag UNIQUE_CONTACT --mapped-mass
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/finite_mapped_mass_audit.py --tag UNIQUE_AUDIT --case UNIQUE_CONTACT
```

Next independent torque-free reference;then stock Native inertial/mass composition
verification. Physical material/join calibration remains missing. Do not silently
set density,change old lumped B3 mass,or claim time/mesh/Holding100g/Lift approval.
