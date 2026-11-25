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
