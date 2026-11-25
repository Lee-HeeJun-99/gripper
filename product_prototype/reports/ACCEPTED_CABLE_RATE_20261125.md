# Accepted cable geometric rate observer

1818 reconstructs all six1741 routes using actual Scene RigidMapping ownership,
initial local coordinates and saved accepted rigid q/v. World point velocity
is v_center + omega cross rotated_local. Analytic length rate agrees with
independent world-angular directional finite difference to2.695e-11m/s.
Hold rate range spans approximately -31.328 to31.512mm/s across cables.
This is a kinematic contract, not time convergence or a selected feedback law.

New NativeCableRate is a read-only BaseObject observer, NOT a ForceField,
custom ODE, contact law or state corrector. AnimateEnd reads q/v and writes
only its exclusive CSV. Actual origin is stationary in this1741 test.
1820 actual SOFA v26.06.00:4steps/.01s,1.307456s runtime, normal exit;
q/v/object-impulse prefix difference EXACT0, independent sensor error
1.388e-17, all saved Skin volume ratios positive. This is only prefix purity.
1821 extends the unchanged observer to240steps/.6s: normal exit,87.100060s,
exact0 prefix q/v/impulse difference, sensor error2.776e-17, minimum saved
Skin volume ratio0.990449515. Never infer full Holding from this prefix.

Existing finger CSV does contain command_N, command_Ns and cable_force_raw;
thus actual input impulse is not globally absent. What remains unverified is
the force/Jacobian/free-motion time phase needed for discrete work/passive
feedback certification. Accepted force times accepted geometric velocity alone
is NOT proven to be the solver's actual discrete work. No gain chosen, no
controller actuation or new Holding success claimed.

Actual build (new local plugin only; installed SDK unchanged):
```
prlimit --as=4294967296 --cpu=120 -- cmake -S product_prototype/sofa/native_cable_rate -B product_prototype/cad/build_cable_rate1819 -DCMAKE_PREFIX_PATH=/home/ubuntu/SOFA/v26.06.00
prlimit --as=4294967296 --cpu=120 -- cmake --build product_prototype/cad/build_cable_rate1819 -j 1
```
Actual analysis/Native commands, NEW tags required for rerun:
```
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/accepted_cable_rate.py --tag accepted_cable1818
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/native_cable_rate_pilot.py --tag cable_rate_native1820
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/native_cable_rate_pilot.py --tag cable_rate_deformed1821 --duration .6
```
1820 and1821 freeze their own producer/Observer source, actual Scene, command,
preflight/source/plugin SHA256 and full local Raw.1820 wrapper snapshot predates
the .6 option; actual observer binary unchanged. No old binary was rebuilt.

Next: actual applied cable-J/free/accepted phase contract on a bounded coupon
before claiming passivity or choosing an active law. Such a controller could
not by itself certify removal of Guide–Guide bracing. Other open-link inertial,
wire routing/contact and real assembly/material prerequisites remain.
