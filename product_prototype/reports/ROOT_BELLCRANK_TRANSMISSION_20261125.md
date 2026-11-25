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

## Actual finite output linkage1843–1845

1843 implements NEW three-bore rotor,32mm rod with30mm pin spacing,4x4x1mm
slider, three load pins plus fixed pivot;7connected separate solids. Body planes
z0/2/4mm. Exact slider-crank kinematics sets4mm output at0.412801rad.21samples:
solid-pair intersections0, finite wire intersections0 outside declared last
.7mm unqualified termination domain; closure<=7.106e-15mm. This is sampled
geometry, not swept clearance or a manufactured wire anchor. Pins unretained,
housing/bearing unavailable.50um radial gap still incompatible with200um
Nativecontact budget if real bearing surfaces are used; no contact fix claimed.

1844 NEW Native ideal point-joint tests:1step rest and10steps initialomega-.2.
Three actual rotor/rod/slider masses from1843solids at assumedrho1000. Pin
dynamic masses omitted as an explicit *ideal massless joint* model; this is
NOT the complete7part assembly dynamic mass. All normal exit/noERROR,~.105s.
Both original1e-12 gates FAIL: first angular error7.425e-9rad/s, first closure
2.566e-11m(rest) or3.689e-10m(finite speed), latter reaches4.199e-9m in10steps.
No q/v correction, tighter solve, smaller dt or physical-gate relaxation.

1845 independently assembles initial8DOF mass and6point-joint rows. Actual
Native multipliers reconstruct actual velocities to5.552e-17; exact initial
Schur reference differs7.425e-9, so this initial response discrepancy is
explained by iterative termination, NOT a proven new mass-law fault. Actual
input rod compression8.37827e-5N and rod-to-slider force6.12609e-5N measured
from joint rows; these are coupon forces, not motor requirements. The initial
closure gap equals r*(1-cos(delta_theta)) within7.729e-19m: frozen tangent
constraint and exact rigid rotation differ. This diagnoses a separate geometric
error even if linear solve were exact.1844 remainsFAIL; no Finger expansion.
Full nonlinear joint/integration qualification still requires a supported
different contract, not another tolerance/dt scan or state projection.

1847 independent prerequisite: matching actual REST route's paired nominal
1.5N cable moment0.009Nm through3mm dorsal offset requires3N compression
reference. This is NOT the measured minimum100g motor load. A pair of loose,
isolated100mm x2mm x.5mm rails at existing assumedE250MPa has optimistic
pinned Euler capacity0.0051404N EACH versus1.5N EACH reference, ratio291.8.
At that reference load maximum pinned support spacing is5.854mm. This rejects
only the **unsupported loose straight-rail** path. Existing bonded Skin/Rail,
curved geometry, actual joint/end conditions differ; no actual composite
buckling/strength conclusion or fitted material change is made. A supported
compression spine and qualified output joint are prerequisites to Finger use.
Root bellcrank success at small coupon loads cannot be scaled to3N hardware
qualification without real material, pin/termination and lateral support data.

Actual commands (NEW tags only for future runs):
```
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/bellcrank_link_geometry.py --tag bellcrank_link1843
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/bellcrank_output_joint_coupon.py --tag bellcrank_joint1844
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/bellcrank_kkt_audit.py --tag bellcrank_kkt1845
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/test_bellcrank_contract.py
```
Additional actual command: `python product_prototype/sofa/dorsal_compression_screen.py --tag dorsal_compression1847`
This changes a physical transmission topology but not the old B3 model. No
full100g test, UNBRACED, numerical convergence, physical joint or hardware PASS.
