# Cable phase and geometric work continuation

Starta8f4f44 clean. New read-only BaseObject observer, no ForceField/SDK/state
changes. Installed CableModel.inl629build uses supplied positions;793violation
and811storeLambda differ in phase. The installed source warns displacement is
one step behind. Source locations are interpretation, not actual measurement.

1824 failed before physical test: GenericConstraintSolver XML factory removed
in installed26.06; actual logs prescribe BlockGaussSeidelConstraintSolver.
Original failed XML/logs retained; initial runner source snapshot/hash was NOT
MEASURED, explicitly NULL.1825 fixes only that registered factory name into a
new result directory. No previous result overwritten or converted to PASS.

1825 actual control and observed5steps each,dt.01s,3independent10g points,
nonzero initial velocities, fixed origin, constant cable0.05N/0.0005Ns, no
gravity/contact/FEM/mapping. Normal exit0, noERROR,~.14s each. q/v difference0.
Observed J exactly matches previous accepted geometry in all5steps. Free and
accepted geometric directions differ substantially in this deliberately finite
motion coupon. Actual impulse response error<=1.627e-19Ns. Accepted position
and midpoint kinetic increment match independent formulas within1e-12.
At first solve_end cable force Data remains0, whereas actual solver f=.0005Ns;
at accepted_end it is updated. A raw Data query without phase can be stale.

1826 independent read-only work decomposition on those actual trajectories:
Wrow=lambda Jprev vnew, Wgeom=-T*(Lnew-Lprev), Euler kinetic loss=.5dv'Mdv.
DeltaK-Wgeom=(Wrow-Wgeom)-loss. Maximum identity residual3.727e-20J.
3of5steps have positive Delta(K+T L), maximum4.190891e-5J. This is a failure of
energy monotonicity for this constant-tension geometric reference, NOT global
B3 energy or a proof of the sole cause of1741 speed/bracing failure. No
dt/tension/damping sweep or force correction was applied to obtain this result.

Next actual task: B3 mapped cable phase prefix with unchanged physical inputs.
No gain or passive feedback controller selected. A current-geometry length
rate is not interchangeable with the actual frozen-row generalized power.
Parent mapping/free state adds requirements beyond the unmapped coupon.

Build:
```
prlimit --as=4294967296 --cpu=120 -- cmake -S product_prototype/sofa/native_cable_phase -B product_prototype/cad/build_cable_phase1824 -DCMAKE_PREFIX_PATH=/home/ubuntu/SOFA/v26.06.00
prlimit --as=4294967296 --cpu=120 -- cmake --build product_prototype/cad/build_cable_phase1824 -j 1
```
Actual commands (never rerun existing tags):
```
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/cable_phase_coupon.py --tag cable_phase1825
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/cable_geometric_work.py --tag cable_work1826
```
Actual scenes/commands/binary hashes/runtime/producer/observer snapshots are
preserved per case. SDK26.06.00 unchanged; no new grasp PASS or lift claim.
