# Ideal interface constraint coupon1238–1240

Independent variable-stiffness LIMIT diagnostic,NOT vacuum jamming. Starts
free1189: same two40x10x.2mm native tetra strips,E2.5GPa,material/mass/mesh/
constant total tip load.1mN,dt200us,root,pressure0,ALL collisions unchanged.
Only added Native BilateralLagrangianConstraint at16 paired interface nodes
(root pairs excluded):XYZ relative translation fixed to original2um rest
vector. Installed component uses x2-x1-rest_vector. No custom physics.
This world-fixed vector is a small-rotation abstract interface limit,not
objective finite-rotation adhesive law or a realizable calibrated joint.

1238 pilot50steps10ms actual.469s;500step forecast~4.7s <120s/4GiB.
1239 actual500steps100ms3.611s,0NativeERROR. Source35fc319,SDK26.06.00,
stock journal hash and commands inpreflight/process. No old source/raw edit.
1240 independent accepted-state audit:

|metric|free1189 reused|tied1239 actual|
|---|---:|---:|
|final width-mean tip displacement|-.118967933um|-.118148052um|
|final max node speed|6.21e-13m/s|5.22e-13m/s|
|last50 tip relative drift|1.85e-9|2.15e-9|
|minimum signed volume ratio|.999999973|.999999957|
|strict centroid overlap witnesses|0|0|
|max interface vector error|1.068nm (free)|.1245nm (tied)|
|iteration limit outputs|0|0|

Actual free/tied displacement ratio1.006939,NOT strong stiffness gain.
Maximum final slope~4.5e-6 supports only small-angle interpretation.
Max solver error1.63e-9 is recorded,not equated with geometry error or a
new relaxed Gate. Existing tolerance remains1e-10 unchanged.

An ideal zero-gap two-layer Euler beam ratio4 is only a theory comparator;
the actual small gap,world-vector tie,coarse highly anisotropic tetrahedra
and3D constraints differ. Result DOES NOT establish mesh-independent EI,
pressure law or jamming benefit. EffectiveEI,rootreaction,energy remainNULL.
No mesh/time convergence or whole static equilibrium certification implied
by settled output. Cause of weak sensitivity remains unresolved;do not
fitE or constraint tolerance to obtain4,do not integrate intoB3.

Next physical prerequisite for any jamming claim: bending-reliable coupon
discretization/interface calibration,not more pressure/friction sweeps.
Independent next executable task: actual primitive component work/impulse
inventory,with BE numerical loss separated from physical friction.

Reproduce(unique output):
`python product_prototype/sofa/layer_interface_limit.py --tag UNIQUE --steps 50`
`python product_prototype/sofa/layer_interface_assess.py --tag UNIQUE`
`python product_prototype/sofa/test_layer_interface.py`
