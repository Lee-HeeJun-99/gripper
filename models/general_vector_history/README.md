# Independent general moving material history

`Owner` stores a function of reference material coordinate, not quadrature IDs.
Each immutable operator captures previous/current geometry and object poses by
VALUE. The verified circular return, objective normal transport and chord/IFT
Birth law are reused. Pure trial queries and owner/epoch tokens prevent repeated
or foreign commits. SphereHistoryChart can seed immutable prescribed history.

This is an EXACT FINITE-PREFIX REFERENCE, not a qualified adaptive history fit.
At128operators the next transaction is rejected, never silently truncated.
Full-duration gripper runs require a separately qualified general state fitter.
No representation heat is invented; detachment inventory is separate from heat.
The inherited chord approximation is not exact finite-rotation CCD.

New SOFA class `GeneralVectorCurvedContact` reuses Hermite virtual-work pullback.
Its material abscissae are fixed reference coordinates, not moving state IDs.
Original Beam/Curved/Birth/vector models are unchanged. Build modes:

- default: inherited midpoint quadrature with function-owned history;
- `GENERAL_HISTORY_GAUSS=ON`: identical composite Gauss rule for force/energy/commit;
- `GENERAL_HISTORY_ADAPTIVE=ON`: experimental8/16embedded integration with global
  measure-scaled budgets for force,moment,U,prospective plastic loss and detach.

The adaptive estimator has NO absolute heat floor. It is NOT a continuous error
certificate: a completely unsampled isolated patch/front may be missed. Independent
dense/front references remain required. Changing adaptive partitions also does
not prove an exact discrete mechanical Jacobian;actual FD tests are required.
Sphere normal torque is analytically zero in the ERROR ESTIMATOR ONLY;assembled
forces,torques and Jacobian are never corrected to cancel an imbalance.

Evidence:results/vector_history_owner_*,moving_*,compare_*,material_rule_*,
rule_geometry_*,frames_*. A process/smoke PASS is not gripper qualification.
Full3finger,11/21/41mesh,energy,12wrenches and grasp Optuna remain unqualified.

Fresh commands (new tags required):

```
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/curve_general_owner.py --tag UNIQUE --adaptive
$PY tools/curve_general_dynamic.py --tag UNIQUE --build build/vector_history_owner_UNIQUE --speed .2
```

Default per-child4GiB,compile/API180s,dynamics480s via bounded launcher.
No system SDK overwrite,remote push or automatic restart is performed.
