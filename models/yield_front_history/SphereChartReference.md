# General sphere/Hermite material-history chart — independent prerequisite

SphereHistoryChart uses immutable previous Hermite endpoint poses and reference
length. In material coordinate x,t=(x+1)/2,the Bezier controls are
a.p,a.p+(L/3)Ra ex,b.p-(L/3)Rb ex,b.p. Subtract the sphere center from each
control BEFORE interpolation;interpolating large world coordinates and only
then subtracting center caused an actual strict covariance failure.

Let r(x) be the relative centerline,n=r/|r|,gap=R+skin-|r|. On an active
smooth branch capacity is mu*kn*gap,not C(1-x²). A prescribed gap-history
polynomial δ and vector-direction polynomial p define
e=(capacity/kt)(1-δ) Pt p/|Pt p|,Pt=I-n n^T. First and second material
derivatives are computed with the existing unchanged Beam Taylor algebra.
This reconstructs an admissible history CHART;it does not evolve history,
solve frictional return or provide a complete mechanical contact Jacobian.

The chart rejects exact contact events,cell boundaries,undefined direction,
nonfinite inputs and unresolved tangent-direction conditioning. It does not
choose an arbitrary tangent axis. Inactive/zero-friction controls are tested.
One must still derive/generalize the adaptive state fitter,spatial transport,
Birth/Death,return/Commit and virtual-work pullback before using it in SOFA.

Actual independent campaigns:

- sphere_chart01 FAIL:the assumed active fixture was inactive after Hermite
  director sag. This was a manufactured-fixture error,not a gripper Gate.
- sphere_chart02 FAIL:common rigid transform covariance1.66533e-16 exceeded
  its1e-16line. No threshold relaxation.
- sphere_chart03 PASS after center-relative interpolation,with covariance
  7.71952e-17;first derivative FD9.29132e-12,second FD1.87758e-11.
- sphere_chart04 PASS with NaN,undefined tangent and exact-event rejection.

All use independent prescribed histories and assumed numeric properties;none
is an actual moving-contact SOFA simulation or a measurement. The new chart
must not inherit the fixed-patch SOFA qualification as a whole-gripper PASS.
