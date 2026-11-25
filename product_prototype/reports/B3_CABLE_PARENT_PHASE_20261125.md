# B3 phase continuation and honest failure recovery

Feature phase/work commit d611804 after starta8f4f44. No physical input change,
state correction, SDK edit, contact removal or tolerance relaxation.

Actual1828 read-only4step B3 control-prefix match: q/v/impulse difference0,
Jchild exactly previous geometry.1829 actual240step/.6s87.527916s, normal exit,
min Skin volume ratio0.990449515, same exact trajectory and child-J match.
Its original phase assessment is FAIL: string force Data differs from actual
solver impulse by up to4.928e-9Ns, exceeding the preregistered1e-12 gate.
Do NOT convert1829to PASS.1830initial parent analysis refused this failed
input; its BLOCKED summary is retained. The Native execution itself was valid.

1833 reads actual solver f and original full-precision Native cable force from
all240saved rows: EXACT agreement0; all string differences equal rounding to
six significant digits, EXACT residual0. This diagnoses observation formatting,
not a force transmission failure. New typed-double observer compiled separately
as build_cable_phase1831 (old binaries1824/1828 untouched).1831 actual100steps/
.25s43.162044s, normal exit, q/v/impulse difference0; command/actual/typed force
and previous-J gates PASS unchanged1e-12. Minimum Skin volume0.995626739.

1832 independently analyzes trustworthy q/v/J in both1828and1829 while retaining
their original statuses. Actual parent row matches previous lever arms to
5.204e-18. Accepted mapped point velocities instead match accepted lever arms
to1.388e-17; child/parent accepted frozen-row products can therefore differ:
maximum row-rate mismatch1.49715e-5m/s, corresponding observed product difference
up to1.97632e-5W. This is a measured mixed-geometry linearization contract,
NOT an unexplained missing force, global energy defect magnitude or sole cause
of1741grasp failure. Use an actual conjugate row/velocity pair for any input
power accounting, not current geometric dL/dt substituted without proof.

1834 tests a necessary sign condition for a proposed *infinitesimal* law
deltaT=b*min(previous_rate,0), b>0, with no chosen gain or control execution.
Actual baseline240samples contain7positive incremental-power coefficients.
Thus an unconditional extra-damping argument is REJECTED. This is not proof
of absolute active motor power, nor a controlled/counterfactual trajectory.
No gain/force/dt sweep, controller activation or new full Holding is justified.

Remaining GOAL A:1741full100g still speed32.928255mm/s and30internalHoldrows FAIL.
Guide geometry, finite wire, nonlinear joint inertia and real material gates
remain unchanged. GOAL B observation progressed, not actual actuation accuracy.
No UNBRACED/Numerical/Hardware/Lift PASS added. Coupled actuator work/passivity
needs a specifically supported discrete contract before active-law promotion.

Actual commands (existing outputs must never be rerun):
```
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/b3_cable_phase_pilot.py --tag b3_cable_deformed1829 --duration .6
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/b3_cable_phase_pilot.py --tag b3_cable_typed1831 --duration .25
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/cable_parent_phase_contract.py --tag cable_parent_phase1832 --cases b3_cable_phase1828 b3_cable_deformed1829
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/cable_force_precision_audit.py --tag cable_force_precision1833
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/delayed_port_passivity.py --tag delayed_port1834
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/test_cable_work_contract.py
```
Four deterministic algebra regressions PASS; these are NOT Native performance
tests. Actual run snapshots contain the producer version at execution, observer
source, scene, SHA256 and process command/runtime; use those for historical
reconstruction. Current runner defaults typed1831binary with compiled-source
identity guard. Its source is NOT the old1828/1829producer. Old calls above
document actual history, not permission to overwrite or imply identical binary.

Build1831 used same two prlimit/cmake commands as phase report, with build
directory build_cable_phase1831. Rebuild frozen sources only into NEW build
folders; don't overwrite old compiled plugin evidence. No hardware quantities
measured; physical motor law, material, finite-wire and joint data NOT MEASURED.
