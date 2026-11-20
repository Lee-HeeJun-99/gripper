# Root wire/pulley contract — 836–839

## Independent product continuation840–842

843 additional actual Native free-in-plane axle diagnostic completed10finite
states in2.77s. Initial reference/J-lambda/linear momentum all equal
(2.5e-9,2.5e-9,0)Ns; angular impulse0. New ideal DOF arrangement,not same bearing
physics as837/838. Repro: `python product_prototype/sofa/root_wire_coupon.py
--tag UNIQUE_FREE_AXLE --balanced --free-axle`. Only initial impulse is certified;
subsequent positions change branch geometry. No reaction/work/sliding claim.

Installed SlidingLagrangianConstraint.{h,inl} also inspected read-only: its
`sliding_point`, `axis_1`, `axis_2` API constrains a point to a straight axis/edge;
it is not an exact circular wrap/arc-length pulley model. This observation is not
a proof that no other SOFA/plugin mechanism could implement sliding. NextNative
work must first specify a matched arc/branch-change contract, not relabel this
straight slider. No custom solver or SDK changes authorized by these results.

First feature commit `468b853`. CAD-root load841 reads all six actual780 route
directions and centres: ideal1.5N/branch gives1.846984426N/axle; angle-reference
error<=4.44e-16N, ideal moment norm<=6.98e-18Nm. No actual load/strength claim.
Physical measurements CSV remains blank/NOT MEASURED; bench protocol is
`ROOT_AXLE_LOAD_MEASUREMENT_PROTOCOL.md`. Candidate geometry was not altered.
840 original calculation retained. Separate integer-fixture software test failed
because in-place division used an integer numpy array; corrected explicit float
conversion and degenerate-direction rejection in841 (no physical-state fudge).
Four standalone reference tests then passed.842 runs the expanded bounded design
regression suite; its actual logs/status are authoritative.

Repro: `python product_prototype/cad/root_load_requirements.py --tag UNIQUE_LOAD`
and `python product_prototype/cad/manufacturing_test_run.py --tag UNIQUE_TEST`.

Source baseline `57b0e97`; SDK `/home/ubuntu/SOFA/v26.06.00` unchanged.
Actual commands (robot_ws Python, repository root):

```
python product_prototype/sofa/root_wire_coupon.py --tag product_root_wire837
python product_prototype/sofa/root_wire_coupon.py --tag product_root_wire838 --balanced
python product_prototype/sofa/root_wire_reference.py --tag product_root_wire_reference839
```

Native runs preserve finite wheel/land collisions and ideal cylindrical bearing.
No FEM, finger, moving wire collision or physical sliding is represented.
Ten steps, dt=250us, assumed cable force 10uN, pitch radius 2mm.
Native force-control value is **T*dt**, not T (prior330/331 calibration).
All actual scenes, producer snapshots, SDK/header/plugin hashes, commands and
journals are in the corresponding unique `product_prototype/results/` folders.

* 836 FAIL: plugin declaration followed the wheel node; CableConstraint factory
  registration unavailable during XML creation. Zero accepted states. Preserved.
* 837 scoped Native anchored-cable PASS: 10 finite states, 3.80s. First angular
  impulse reference, Native J-lambda and angular momentum each 5e-12 Nms.
  Final spin 0.13023024rad/s. This is an attached anchor, NOT a free sliding pulley.
* 838 scoped balanced-anchor PASS: two independent equal prescribed forces;
  zero spin/torque in 10 states, 3.20s. NOT an equalizer or enforced tension sharing.
* 839 independent planar circular tangent/arc reference PASS: length
  23.1415926536mm, endpoint gradient FD error 5.94e-12, rigid planar rotation
  length error <=3.47e-18m; invalid internal endpoint rejected. Assumed equal
  branch forces 1.5N yield resultant(-1.5,-1.5)N and zero spin torque.
  This is mathematics, not another actual SOFA execution.

Installed CableModel.inl `getCableLength` sums straight segments. Its force
Jacobian acts on those guide points. RigidMapping makes an anchor material-fixed
to the wheel; it does not solve tangency or free wire sliding. The balanced anchor
result alone does not establish a circular wrap law. The analytic839 geometry
uses a different explicit smooth branch and is not a matched Native dynamics test.

**BLOCKED for product adoption:** exact circular sliding/arc coupling is not
implemented/qualified by these Native components. Do not attach polygonal points
to a wheel and label that physical sliding. No custom ODE/constraint solver added.
Axle reactions/work, physical friction, wear, wire minimum bend radius, actual
material/retention and full energy are NOT MEASURED. Contact/time/FEM mesh failures,
100g/Lift/STEP Gates remain open. Next independent work: derive CAD root-axle
load vectors and a physical force/deflection/friction measurement interface.
