# Native contact policy:geometry,velocity and event time are distinct

660 reuses649–651 actual states/owned response rows,not another simulation.
All8active contacts have positive PREVIOUS buffered gap. First active intervals:

|dt(ms)|start(ms)|accepted(ms)|previous gap(mm)|normal impulse(Ns)|
|---:|---:|---:|---:|---:|
|2.5|0|2.5|2.973245|2.344283e-6|
|1.25|1.25|2.5|0.887662|4.344664e-6|
|0.625|1.25|1.875|0.887663|1.091818e-6|

Actual contact lever points lie on PREVIOUS mapped finite surface≤1.56e-17m.
Owned Point/Line/Triangle pairs change with time and resolution. Active accepted
normal velocity follows-gap/dt,not an explicitly localized impact law. Frozen
linear gap crossing fractions in Raw are NOT actual ODE event/CCD times.

## Minimum Native sphere/plane661–662

No FEM,cable,guide,gyro or custom solver.1g sphere,R1mm,buffer0.2mm,initial
buffered gap1.5mm,speed-1m/s,gravity0,friction0. Same geometry/mass/input across
2.5/1.25/.625ms. Explicit independent reference:e=0 instantaneous collision at
BUFFERED plane,time1.5ms. This is a specified reference assumption,not a claim
that the Native method implements it or actual material restitution was measured.

Six actual Native runs:position-first vs solveVelocityConstraintFirst. Runtime
0.137–0.172s each,bounded4GiB/480s;RSS NOT MEASURED. Native position/reference
error≤6.51e-19m,momentum residual≤5.43e-20Ns. Nevertheless maximum post-birth
normal velocity error0.6/.2/.4m/s,not monotonic with dt. At common2.5ms actual
velocities are-.6/-.2/~0m/s. Native impulse splits across successive steps.
Exact Decimal recurrence v_next=max(v_old,-gap/dt),gap_next=gap+dt*v_next
matches actual Native state at1e-12. Both animation-loop options differ≤1.12e-16.

Installed BaseContactLagrangianConstraint.inl getVelocityViolation explicitly
uses relative free velocity PLUS gap/dt. Therefore the velocity-first option
does NOT replace this response by a pure instantaneous impact law. Stop that
configuration direction;do not reintroduce the failed Cable velocity-first path.

662 actual all-common/all3pairs0.1%Gate FAIL (velocity relative100%,absolute.6m/s).
Final kinetic decrease0.0005J agrees with e=0 reference total loss,but this is NOT
time-resolved energy agreement,physical heat calibration or coupled energy PASS.
No tolerance floor,output correction or historical FAIL deletion.

Source:sofa/inertia_contact_phase.py,native_plane_policy.py,native_plane_assess.py.
Raw:results/b3_native_contact_phase660,b3_native_plane_policy661,
b3_native_plane_reference662. Evidence:evidence_product_contact_policy_v33.
```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/native_plane_policy.py --tag UNIQUE_PLANE
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/inertia_contact_phase.py --tag UNIQUE_PHASE
```
Next independent hypothesis:Native finite-compliance response vs its own elastic
reference,not the e=0 model. Requires a separately declared stiffness and cannot
retroactively repair661/652 or qualify B3. Physical contact stiffness remains
unmeasured;no product promotion or new custom solver is authorized by these data.
