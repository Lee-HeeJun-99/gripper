# Reference-exact displacement-frame attachment (experimental)

Independent variant; historical Assembly, SOFA Field and checkpoints remain
unchanged. Flat reference geometry is stress-free by construction. Attachment
gap is computed from material displacement differences and the change of Rail
normal, not subtraction of rounded world positions. This preserves tiny
constitutive force values as well as derivatives. No stiffness, force, velocity,
accepted position or tolerance is patched. Undefined normals are rejected.

Shell elements and lateral routed tendon are reused unchanged. This does NOT
qualify their tiny-signal precision or moving-contact/friction behavior.
`Force.h` preserves the existing projected virtual-work assembly.

1678 legacy tiny-value failure is preserved.1679 analytic tiny-value/rigid
translation PASS;1680 original force/Hessian/objectivity/balance regression
PASS;1685 actual SOFA Force/dForce/matrix/FD/query-purity PASS.
1681–1684 independent four-stage nonlinear200us8/16/32 refinement passes
the0.1% state/shape gate without an absolute floor (worst0.0600822%).
Energy and work are NOT assessed by that refinement. Frozen-linear comparison
still fails and is not an exact nonlinear reference.

Owner.cpp is a separate, bounded eight-step startup coupon, not a replacement
for the contact owner. It emits all four actual stages in `.gauss4.csv`;
the historical two-stage journal is deliberately empty. No object/contact,
wrapping,holding,lift,full recovery or production checkpoint certification.

Reproduce from repository root:

```
/home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/film_precise_startup_sofa.py --tag UNIQUE_STARTUP
```

Use a unique tag. Frozen prior campaign sources and binaries must not be
overwritten. Actual SOFA result status is in the new campaign summary, not
in this model description.
