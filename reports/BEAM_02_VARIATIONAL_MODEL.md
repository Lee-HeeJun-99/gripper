# BEAM02 — conservative/objective beam definition

Status: **PASS kernel and actual SOFA API tests; EXPERIMENTAL beam theory scope.**

Chosen model: objective two-node midpoint Simo–Reissner/Cosserat-type rod with
axial/shear/bending/torsional energy, independent rigid6DOF nodes and SO(3)
rotation increments. Euler–Bernoulli alone omits shear; a full higher-order
geometrically exact element has greater implementation/conditioning cost.
The selected low-order reduced-integration energy is explicit and testable;
it is not asserted to be an exact reproduction of a named published element.

See `models/conservative_beam/README.md` for the complete discrete energy,
intrinsic strain, branch and coordinate definitions. Under x→Sx+t,R→SR,
gamma and kappa are invariant, so E is objective and f/torque rotate with S.
Spatial virtual work is `δE=−Σ(f·δx+τ·δw)` for Q'=Exp(δw)Q.
Exact second-order AD obtains the negative gradient and symmetric chart H.
Spatial force Jacobian is `−H−.5 skew(τ)` per rotational diagonal block;
symmetric energy Hessian and nonsymmetric spatial Jacobian are NOT confused.
Nonsymmetric EigenSparseLU is used in actual scenes.

Fresh clean-unit log: `results/beam_20261115/clean/unit/stdout.log`:
61states, max absolute energy FD error1.36518618632e-8, force-Jacobian FD
5.46999650020e-8, moment5.68434188608e-14, covariance1.91846538655e-13.
Closed rectangular path work64→256 intervals:
3.14275756893e-10→1.96422941627e-11 F·mm, converging to zero.
Rest, axial, shear, midpoint bending, torsion, objectivity, action/reaction,
stiffness matrix assembly and kFactor are individually asserted.

Additional40 large relative-rotation states:
`large_kernel_corrected/unit/stdout.log`, energy FD4.02278431011e-7,
Jacobian FD5.90219196184e-7,moment2.27373675443e-13.
Noncommuting SO(3) closed path32→128 work
−3.70616002193e-4→−2.31637992050e-5 F·mm (~16× reduction);
this is convergence evidence, not a claim finite-resolution work is exactly0.

`extra_unit` tests cache invalidation by positions/materials, unused object,
Rayleigh/kFactor, invalid quaternion/topology, and transactional cache safety.
ASan/UBSan/LSan: first ptrace-constrained execution FAIL; identical bounded
`asan_unrestricted` execution PASS. Only the new forcefield translation unit is
instrumented, not the full SOFA engine. Compiler warnings: no `warning:` in
the fresh clean build logs; this is not a proof all external code is warning-free.

Exact constant propagation/per-element cache replaces the prototype's dense AD
without changing E/F/J:100random comparisons all bit-identical. Frozen prototype
and v2 binaries/source manifests remain distinct. Some queued prototype trials
captured later working-tree snapshots: the git4d19774 anchored prototype build
manifest, not that snapshot, identifies their compiled source. They remain
diagnostics; they are not silently mixed into a v2 optimization study.

Context: [SO(3) geometrically exact beam example](https://fenics-arclength.readthedocs.io/en/stable/examples/force_control/beam/README.html).
The formula here is independently specified; no unverified literature identity
or whole-structure validity is inferred from a kernel test.
