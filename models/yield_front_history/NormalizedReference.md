# Normalized gap/direction contrast (experimental fixed-normal patch)

This is NOT the curved three-finger contact component. It has prescribed
capacity c(x)=C(1-x²),fixed normal z,and material coordinate x in[-1,1].
The old components and their output remain unchanged.

## Representation

Store gap δ=1-k|e|/c separately from direction n. The elastic state is
e=(c/k)(1-δ)p/|p|. δ and p use cubic Bezier controls on each material cell.
An entire yielded cell has exactly zero gap controls:phase is not inferred
from a floating norm of an already projected elastic vector. Circular Coulomb
return is unchanged;no componentwise clipping is used.

Gap controls must belong to[0,1]. If the interpolating cubic overshoots,this
implementation uses the linear interpolant of endpoint GAP only,then applies
the same state/loss error tests and refinement. It does NOT clip a physical
force or elastic state to make a diagnostic pass. All direction controls have
projection>=.5 on the left unit direction,so convex interpolation has |p|>=.5.
Undefined interior zero-direction events are rejected,not assigned an axis.
Zero state is an explicit exact chart. Capacity-zero endpoints use the
one-sided direction of the final nonzero return increment;this is a restricted
model assumption,not a general Birth/Death rule.

Builder tests13withheld-in-cell values,elastic state error,and five future
vector-return loss densities. This estimator is NOT a uniform proof of error.
Independent131072point state/phase checks and strict adaptive prospective-loss
references are therefore required. Finite dense sampling alone can miss a
genuine1e-26Fmm loss event;no tiny-loss cutoff is permitted.

## Integration and derivative

The function-valued history is independent of force quadrature points.
For a seeded rest state the positive-yield generalized derivative is explicitly
velocity-sided. Loading classification is sign(p·v);a fast conservative sign
test falls back to exact binary-rational evaluation. Cubic sign changes are
isolated by exact Bernstein subdivision,with outward root brackets of width
<=1e-12 in material coordinate. This is a selected nonsmooth derivative,not
a unique classical Hessian at yield.

For nonzero uniform increment d,the ideal stick inequality is
A sqrt(p·p)+B<=0,where
A=c²((1-δ)²-1)+k²(d·d),B=2kc(1-δ)(p·d).
Bernstein signs and sign-guarded squaring provide a sufficient ideal-function
stick certificate. It supplies a NONZERO forward-rounding loss-density bound
to the unchanged integration error budget. It never overrides a computed
return loss with zero. The restricted manual rounding model is described in
reports/vector_history/ROUNDING_MODEL.md;it is not a machine-checked proof.
Exact-query memoization only reuses identical(interval,increment)results;
257independent cached/uncached checks accompany range-lookup equivalence.

## Energy and scope limits

Representation changes are measured as paired integrals of .5k(|e_new|²-
|e_old|²) with8/16point contrasts. They are numerical inventory,NOT heat,
actuator work,or pressure-source work. End-of-step material return satisfies
ΔU=ke_new·d-D_plastic-.5k|e_new-e_old|². The final term is endpoint projection,
not automatically physical friction heat. SOFA Newmark's actual cached
acceleration recurrence has a separate independently checked work term.

The actual benchmark's external load exceeds its total Coulomb capacity;it
accelerates/slips and is NOT a static hold or force-closure demonstration.
Moving normal fields,3D material transport,variable capacity,Birth/Death,
coupled beam/rigid Jacobians,and global gripper pressure work are NOT approved
by these tests. Existing gripper Mesh/History/dt/energy gates must still pass
before12wrench approval or100mm grasp Optuna may begin.

## Optional arithmetic prefilter and material pullback

OutwardPolynomial expands every nearest-rounded finite binary primitive by
one representable neighbour. It is disabled on non-IEC559/nonbinary or
non-nearest platforms and under fast-math. No physical capacity/force floor
is introduced. Polynomial Bernstein coefficients use these enclosures;only
conclusive signs may bypass rational work. All inconclusive intervals use the
unchanged exact-rational predicate. The returned NONZERO floating loss-bound
formula is unchanged. This is arithmetic acceleration,not a new friction law.

Actual independent tests enclose384exact rational Bernstein coefficients
through degree26.257material-interval comparisons agree exactly with the
rational predicate;245are resolved by the prefilter. Constant-frame covariance
tests771states through3rad(rotation only,not moving-normal transport). Future
compiler/platform changes require rerunning enclosure tests.

MaterialDerivative supplies first/second spatial derivatives of the immutable
normalized history INSIDE an explicitly selected material cell. If a force
abscissa depends on mechanical q,e(s(q)) requires these chain terms. Partition
boundaries deliberately reject an undeclared classical derivative. This is a
prerequisite for a moving curved-contact pullback,NOT its implementation or
SOFA qualification. The reference uses the original unchanged Beam Taylor
algebra as an independent differentiation oracle;no Beam source is modified.
