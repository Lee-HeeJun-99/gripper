# Alternative transmission after1838

Startfa709ff clean. New mechanisms, not another control/dt/guide-dimension scan.
1839 single central tendon/six transverse-carrier necessary initial routing
gate REJECTED: nine centreline segments enter actual R30sphere; minimum finite
wire capsule gap -4.110722mm. WireØ0.5mm retained. No Carrier assembly or Native
trial justified. Centralization changes the load path; rejection does not
prove all rerouted or dorsal drives impossible. Visual SI wire cylinder caps
are not a qualified solid; analytic centreline witness alone proves rejection.

1840 initial SI cylinder creation omitted caps (strict closed-volume test
rejects it before Native). Failure kept.1841 constructs the SAME physical
dimensions in CAD millimetres, preserves closed indexed topology, scales the
finished shapes to SI; no tolerance/SDK change or cap repair by deletion.

1841 actual fixed-root bellcrank rotor24x2x1mm, central boreR.3mm/pinR.25mm;
assumedrho1000kg/m3, actual rotor volume47.71907mm3,mass47.71907mg,Iz2.319987e-9.
COM/pivot principal z, five DOFs projectively fixed, only rz free. Initial
omega=-.2rad/s. Root+single fixed axis has constant scalar inertia, unlike the
moving-COM/multijoint1806failure; this does NOT repair1806. Cable at+10mm arm
pulls downward, opposite -10mm output moves upward against a downward dead
load. Output is a force port, NOT an installed pushrod or Finger mechanism.

Three actual Native10step/.01s cases: unloaded free spin, loaded control,
loaded observer. T=.0001N,output deadload=.00005N,dt1ms,zero gravity/contact.
All normal exits/noERROR, each~.10–.14s; angular impulse/inertia response
matches independent previous-state torques within unchanged1e-12 gates.
Observed/control q/v difference EXACT0. Actual per-step figures/source/Scene/
binary hashes and commands retained in bellcrank_port1841.

Ideal PartialFixed pivot, pin contact/retention/base reaction NOT MEASURED.
Finite wire sliding, full output joints, nonlinear Finger/FEM and strength
not implemented. No UNBRACED/grasp/time/mesh/hardware PASS inferred.
Next actual task: finite connecting-rod/slider output mechanism geometry and
kinematic force transmission, then small Native joint/mass contract if clear.

Actual commands (NEW tags required for rerun):
```
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/central_carrier_route_screen.py --tag central_carrier1839
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/bellcrank_port_coupon.py --tag bellcrank_port1841
```
No source solver, ForceField, ODE or SDK modification; existing compiled
observers reused with identity guard. Existing1741and1586verdicts preserved.
