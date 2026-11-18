# Typed stationary separated Gauss continuation

Separate experimental numerical owner. Existing midpoint model,old FREE50ms
guard,material,damping,root mapping,force kernels and failures are preserved.
Original exact50ms/200us checkpoint is restored BEFORE explicit50us transition.
New checkpoints use REGRIP_STATIONARY_GAUSS_FREE_V1 with exact physical clock,
public mass/root/quaternion and original release/impact provenance.
New typed footer bounds the independent qualified window at56.4ms. Old parser
still rejects after50ms;no header/time/step manipulation is allowed.

Three immutable numerical workers,serial observers/SOFA commits,existing Gauss4
with1e-18 Newton and1e-17Ns momentum gates. Only temporal position/residual sums
use extended accumulation;AD2 forces/Hessians/materials unchanged. No contact,
loads,tension or spin permitted. Whole-triangle numerical path separation is
bounded each step;new contact rejects without commit.

1637 actual4 vs2+2 checkpoint/stage/state EXACT.1639 actual51.8ms continuation
q/v/stages EXACT.1634 independent cumulative50/25/12.5us core comparisons to
56.4ms PASS .1%,but signed partial-defect relative error FAIL remains.
No full energy/time,recovery,wrapping or grasp certification. Legacy sampled
work internal state is NOT restored;stage work origin must be tracked separately.
