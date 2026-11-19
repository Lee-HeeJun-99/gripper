# Finite hardware COM / Native mass validation

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

