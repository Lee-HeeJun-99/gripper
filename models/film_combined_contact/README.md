# Isolated coupled event + persistent-contact prototype

Actual SOFA single Film/Rails/Tendon and FREE isotropic sphere. It reuses
ReintegratedBirth/ReintegratedStep,shared projected mass/normal impulse and
singleRowRadauStep(lobatto=true). Same original C2 control and actual mass/field
Data;no hidden pose/velocity correction. New module,not Native collision.

Initially separated:solve BOTH q/v to the isolated entering event,apply one
shared perfectly-inelastic impulse,then integrate the fractional remainder by
LobattoIIIA. Already touching:use the same persistent Lobatto law. Negative
reaction,release or feature transition still rejects;general active-set contact
and global earliest endpoint-family CCD are NOT implemented by this adapter.

To avoid rewriting the validated event atom,the first separated step also
computes the old midpoint remainder as a baseline validator. Its state/force/
velocity projection is NEVER applied;that real computation is counted. The
accepted result replaces all old regular rows/impulses/projection inventories
with actual Lobatto substates. This redundant computation is a known cost,not
a new force/heat term. Its removal needs an independent equivalence test.

Each actual stage records macro/event clocks,q/v,current geometry,normal force
and weighted time. Regular impulse is force times Lobatto quadrature weight;
the physical impact atom is separately journaled. A stage is a solved substate,
not an independent SOFA commit;only a completed accepted macro establishes it.

## Actual evidence and limits

-765 independent actual PRE-impact C2 state,4/8/16 steps over39.0625us.
-766/771/772 actual same states,773 unchanged0.1% all-pair time PASS.
-775 independent125us,16/32/64 steps;777/779/780 actual,781 time PASS.
  Base-quarter velocity0.0210583%,common-window normal force0.0124939%.
-770 independent actual M/J oracle verifies opposite impulse,momentum,stable
  impact loss5.9542e-8 Nmm and unchanged instantaneous positions.
-782 strict independent reference velocity FAIL8.409e-12mm/s is preserved.
  794 clock-only replay matches all positions/velocities exactly;795 compiler-
  flags-only still FAIL.796 independently generates start+=dt clocks (does NOT
  copy observed times/states) and also matches exactly. Canonical standalone
  reference now uses the same finite-precision clock protocol as SOFA. No
  tolerance relaxation;time0+k*dt differs by2.8866e-15s after64 steps.
-778/783 separately observe skin/rails/attachments/kinetic energy,tendon,
  damping,contact work and stable impact loss. Signed residual is reported,
  NOT called heat or used as a whole-system energy certificate.
- Optional sparseStage Data removes EXACT Jacobian zeros only and uses
  nonsymmetric SparseLU with no diagonal shifts/symmetrization. Default dense
  behavior is preserved790. Same-binary788/789 physical output comparison792
  PASS;7.28245s versus4.92100s (1.48x) in one39us pair,not a statistical or
  long-duration performance claim. Longer sparse time/energy gates still need
  their own actual runs. Defaults remain dense.

Research parameters:zero gravity,no friction,no self-collision,explicit ideal
root mapping,assumed material/actuator values. R8.01 is a declared midsurface
buffer,not certified physical shell thickness clearance. This is a saved-state
impact coupon,not a fresh full C2 closing from0s or a grasp/lift/holding test.
No3finger,12wrench,measured PET/TPU,pressure work or final Optuna certification.
