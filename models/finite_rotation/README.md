# Experimental finite-rotation shear, version 0.1

This component is separate from the certified `TangentialRigidForceField`. It is not vacuum friction.
Coordinate units are model F, mm, s. Quaternion convention is SOFA xyzw and spatial left increments.

For lower/upper centroid poses (p_l,R_l), (p_u,R_u), define material attachments
`a_l=(0,0,h/2)`, `a_u=(0,0,-h/2)`, lower material tangent `t=R_l e_x`, and

```
d = p_u + R_u a_u - p_l - R_l a_l
s = t · d
E = k s² / 2
```

Both `t` and `d` rotate under a superposed rigid motion; their dot product is invariant.
The lower convected tangent is a constitutive modelling choice (not a symmetric layer average).
It has no antiparallel-average singularity and deliberately penalizes only one tangential direction.
There is no normal contact, out-of-plane shear, film incompressibility, pressure, seal or damage law.
Reversing the labelled layers is not claimed to give an identical nonlinear constitutive law.

At the undeformed planar state, `s=Delta u - h/2*(theta_l+theta_u)+higher-order terms`,
because `R_y(theta)e_x=(cos(theta),0,-sin(theta))`. Euler–Bernoulli phi=dw/dx≈-theta_y.
The legacy expression is linear in this planar angle and conservative within that coordinate model,
but not an objective finite-3D connector.

The kernel uses 12-variable second-order automatic differentiation in the local retraction
`p'=p+u`, `R'=Exp(w)R`. Exp's quadratic Taylor expansion gives **exact derivatives at w=0**;
it is not used to advance finite orientations (SOFA advances quaternions).
`g=dE/d(delta)`, spatial force/torque `f=-g`. The local variational Hessian H is symmetric.
However the **spatial derivative of the torque is not simply -H**:

```
Df = -H - 1/2 skew(torque)  [on each diagonal rotational block]
```

This is the SO(3) left-Jacobian connection term. Symmetry of the chart Hessian must not be
confused with symmetry of the raw spatial force Jacobian under prestress. The implemented
Jacobian is checked against finite differences of actual spatial forces after exact Exp increments.
Use a nonsymmetric solver (`EigenSparseLU`), not SparseLDL, for the experimental component.
The geometric stiffness can be indefinite away from equilibrium; PSD is not claimed at all states.

Actual C++ unit tests cover 60 random finite orientations, all 12 force/derivative axes,
H symmetry, energy gradient, force covariance, rigid-motion energy invariance, total force/moment,
small-angle limit, invalid quaternion and real SOFA addForce/addDForce/kFactor/matrix indexing.
Separate component ASan/UBSan disables LSan explicitly. The distributed engine is not instrumented.
SOFA integration/convergence and full-scene covariance evidence are reported separately.

Build (fresh log output):
```
/usr/bin/python3 tools/next_build.py --out results/new_finite_build
```

The emitted manifest binds the component/test sources to the loaded library. Numerical success
does not validate a real large-rotation film laminate or any 100 mm hardware.
