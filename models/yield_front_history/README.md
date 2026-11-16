# Stateful scalar yield-front reference — EXPERIMENTAL

This is an independent mathematical reference,not a SOFA ForceField or a3D
contact replacement. Domain/normal are fixed. No contact birth/death,moving
contact boundary,SO(3)history transport,object torque or coupled dynamics is
implemented. Existing Beam/contact components are untouched.

Let x=s/a in[-1,1],capacity c(x)=C(1-x²),increment d(x)=d0+d1*x+d2*x².
Coefficients d are mm,a is mm,k is F/mm²,C is F/mm. Each material state is a
piecewise quadratic elastic-displacement FUNCTION e(x),not point samples.
Return: e_trial=e_old+d,e_new=clip(e_trial,-c/k,c/k),p=e_trial-e_new.
Split each existing interval at real roots of k*e_trial±c. On each resulting
branch the stored function is quadratic. Identical adjacent polynomials merge
without projection or interpolation. Maximum8192pieces;failed trials do not
mutate the field. Commit is epoch-checked and validates the partition.

With ds=a*dx:

- U=integral(k*e²/2 ds),D=integral(c*abs(p) ds).
- W_endpoint=integral(k*e_new*d ds).
- P_endpoint=integral(k*(e_new-e_old)²/2 ds).
- U_new-U_old=W_endpoint-D-P_endpoint.

P is a derived endpoint algorithmic term,NOT heat or a fitted closure error.
In particular,C=0has zero force and zero classical tangent,including at rest.
Its instantaneous reset can remove stored U through P;this is not a model of
fluid/vacuum work or physical contact detachment. Those remain unimplemented.

At fixed old history and C,the incremental potential U_new+D has generalized
tractions F_i=integral(k*e_new*phi_i ds),phi=[1,x,x²]. In smooth integrated
regimes K_ij=integral_stick(k*phi_i*phi_j ds),a symmetric PSD MATERIAL Hessian.
It is NOT a SO(3)spatial force Jacobian. Moving yield-boundary terms cancel
because traction is continuous at the boundary. Gauss3 integrates each
degree<=4branch exactly in exact arithmetic.

Whole intervals exactly on a positive yield limit have different loading and
unloading derivatives. `tangentIsUnique=false`;`classicalTangent()` explicitly
rejects that event. The stored matrix then only describes the selected elastic
one-sided branch and must not be used as a unique classical Jacobian. C=0is
handled separately as an identically-zero operator,not by epsilon capacity.
Near-degenerate roots still require conditioning analysis before3D deployment.

Validation:virgin closed-integral reference,120step stateful reversal/capacity
history,energy identity,potential-gradient/3x3tangent FD,Coulomb bound,pure
queries,stale/invalid Commit,zero capacity and directional yield events.
An independent dense plastic-slider implementation provides convergence
comparison. All values are mathematical/assumed research values,not SOFA or
real-film measurements. A3D adaptation requires a separately derived state
representation,objective vector transport,event handling and API validation.
