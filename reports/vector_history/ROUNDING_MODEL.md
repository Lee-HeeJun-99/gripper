# Restricted cubic snapshot sign/rounding model — experimental

This is an independently derived numerical-reference argument,not certification
of the complete SOFA gripper,arbitrary contact geometry or a general floating
point library. Its forward-error expansion is manually reviewed code,not a
machine-checked proof. Independent precision comparisons remain mandatory.

## Ideal function and exact sign

Four finite binary nodal vectors define a cubic in the local coordinate u.
Convert every binary long-double datum exactly to a rational using its integer
mantissa and power-of-two exponent. Do not round expanded coefficients before
constructing the rational polynomial. On an interval transform the power
coefficients to Bernstein coefficients using exact rational arithmetic. Their
common nonnegative/nonpositive sign proves the same weak sign throughout that
interval because the Bernstein basis is nonnegative and partitions unity.
Mixed coefficients mean UNKNOWN,not a guessed sign.

With p the cubic,c=C(1-x²),the old state is projection onto |k e|<=c.
Old projection regime is decided by k²|p|²-c² (degree6). For a constant vector
increment d at unchanged C,the new yield is k²|p+d|²-c² in an unprojected
cell. In a projected cell its sign is that of
2*c*(p.d)/|p|+k|d|². If p.d<0,squaring gives degree10 polynomial
4*c²*(p.d)²-k²|d|⁴|p|² with the REVERSED sign for the yield test. Keep the
unsquared direction condition. Whole-polynomial equality is explicitly
nonclassical yield,not a unique Jacobian. No arbitrary axis or epsilon divisor
is introduced. Capacity-zero endpoints are excluded from this certificate.

Actual hard interval [.963612886301514045,.963612886595943825] is certified
StickOrBoundary for the IDEAL function. This is stronger than its overly large
generic Lipschitz uncertainty,but does not imply the implemented evaluator has
identically zero roundoff loss.

## Implemented-evaluation error inventory

The implementation keeps a nonzero rounding-density bound instead of deleting
the unresolved inventory. Assumptions:round-to-nearest,IEC559 long double,
strict operations/no fastmath or contraction,normal-scale inputs. The guard
restricts magnitudes to [1e-100,1e100],positive capacity/stiffness and material
cell widths >=1e-100;unsupported regimes return UNKNOWN. Exact zeros are allowed.
These are numerical-domain guards,not changes of a physical material value.

Let epsilon be the type spacing at1 (conservative versus unit roundoff),
gamma_n=n*epsilon/(1-n*epsilon),M=max nodal vector norm,r=C/k and delta=|d|.
Local-coordinate formation uses exact binary inputs and at most three rounded
operations. For u in[0,1],each cubic factor has magnitude<=3. Expanding the
three-factor weight error bounds it by gamma1024;four vector products/sums
and the Euclidean norm are covered by gamma16384*M. Nonexpansiveness of ball
projection,capacity/radius evaluation,norm/division/scaling,increment addition
and final plastic subtraction are conservatively covered by

delta_p <= gamma65536*(M+delta+r).

The capacity error is bounded by delta_c=gamma64*C. On an IDEAL sticking
interval,implemented return-loss density is therefore bounded by
(C+delta_c)*delta_p. This is an ERROR INVENTORY,not heat or physical plastic
loss. Multiply by the actual reference length and add it to the existing
unresolved-loss budget. The requested absolute+relative integral tolerance is
UNCHANGED. Unknown cells retain ordinary refinement;no false zero override.
Outside this restricted evaluator the estimate must be rederived,not copied.

The50decimal diagnostic finds4/72near-yield point disagreements,max density
error1.82610e-29F. Their local1%FAIL remains recorded. The bound is deliberately
conservative and is not calibrated to that measured number. The interval
certificate alone is insufficient without the implemented-rounding inventory.

## Actual reference result

The previous dense131072point reference reported zero for one future probe.
The front-aware adaptive reference resolves1.05625928e-26Fmm;the compressed
candidate gives1.05627284e-26Fmm (relative.00128393%). All five current probes
pass1%,including this newly resolved tiny loss. Earlier500000-evaluation
failures and coarse2.668%/58.14%loss failures are preserved. These are NOT
contact birth/death,pressure work,3D curved contact or free-grasp certificates.

An actual compressed SOFA API attempt then exposed another issue:recomputing
yield metadata with a floating norm generated a fragmented near-circle tangent
field and exhausted50000samples. `IdealYieldState` now carries the exact
rational polynomial projection decision separately from rounded force values.
It is a bounded,immutable-snapshot memo,not an update of physical history on a
query. This fixes the actual API test in the fixed-patch benchmark. It does
not establish active-set preservation for arbitrary moving3Dcontact.
