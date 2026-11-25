# Free-root initial mass contract1784

Start843e7fa. Actual seven Native one-step trials, dt1ms, zero gravity,
root5g/free6DOF, two mapped1g links and one1g coupler; these are coupon
assumptions, not the rejected finite assembly material/mass or real guides.
Forces1e-7N and torques1e-10Nm deliberately probe the small-load tangent.
No prescribed active root/joint motion, no SDK/ODE/solver implementation edits.

Independent7x7 mass = root mass plus sum of body Jv transpose m Jv and
Jw transpose I Jw, including base translation/rotation/joint cross terms.
All7actual Native response columns PASS unchanged absolute velocity gate1e-12.
Maximum generalized velocity error6.776264e-21. This is INITIAL MASS ONLY,
not nonlinear force/gyro/energy/time/contact accuracy or a grasp result.
Each child4GiB/60s, sequential; actual runtimes and SHA/scene stored in1784.
Native outputs are retained as local CSV, indexed in immutable manifests.

Reproduction with new tag:
```
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/open_parallel_free_root.py --tag NEW
```
Next independent fixture: nonzero joint angle and rotated root initial pose,
same physical coupon masses/loads/gate, independent world-space Jacobians.
This does not apply a checkpoint to the FEM or prescribe object/root trajectory.

1786 actual angle.4rad + root Euler20,-15,30deg: all7physical columns FAIL,
maximum velocity error2.040739e-6. Independent factor controls1787angle-only
and1788root-only both FAIL. This is NOT simply a missing translation constraint.
1789read-only analysis of all21actual response columns: a world-FIXED inertia
tensor countermodel explains every response within1.36e-20, while the physical
body-rotated anisotropic tensor does not. Installed UniformMass.inl/addMToMatrix
and AddMToMatrixFunctor header hashes are recorded. This diagnoses this new
articulated configuration; previous general inertia studies are not rerun.

1790 physically transforms the link's declared initial tensor into world basis
ONCE before initialization. Same masses, loads, pose and1e-12gate: all7Native
columns PASS, worst2.371692e-20. This proves only correct initial tensor setup,
NOT continuous body-frame inertia transport or a dynamics fix. No time-history
tensor/state overwrite. Original1786/87/88 FAILs remain unchanged. Do not adopt
1790initial-only correction as a full moving-FEM or grasp qualification.
Feature1784commit37e6ef8. The next geometry task is routed root/carrier load
paths, since the convex connection and pocket cuts are physically rejected.
