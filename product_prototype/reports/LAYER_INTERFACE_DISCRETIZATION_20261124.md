# Interface sensitivity depends on discretization1263–1266

Independent CST displacement-DOF identification exactly implements the
abstract world-vector tie used in1239. NOT finite-rotation adhesive law,
pressure/friction contact,or calibrated vacuum jamming. SameE/material/
root/geometry and fourtipforces;no force/position writes into SOFA.

1263 exploratory reference assigned exact0 interface error by DOF-equality
construction rather than measuring reconstructed pairs. That field is not
a physical measurement;1264 prospectively fixes it to compute actual paired
displacement differences. Both source/results retained,1264 primary.
1264 independent algebra runs1.009s within4GiB/60s:

|length nodes|free/tied displacement ratio|
|---|---:|
|9|1.006939435|
|17|1.026907368|
|33|1.098733680|
|65|1.301292178|
|129|1.620176227|
|257|1.843531688|

Coarse ratio differs actualNative1239 by1.76e-9;reduced algebra free residual
≤2.38e-13N,computed interface differenceEXACT0. This reproduces weak coarse
coupling without pressure law or Native solver history. It does NOT prove
no physical jamming benefit;the mesh itself changes predicted transmission.
All sections still have one tetra cell through each layer thickness and
two nodes across width;the ideal zero-gap continuum ratio4 is not a target
to fit withE or an asserted reference for this discretization.

New actual Native nx33 tie pilot1265,10steps2ms,2.272s,zeroERROR. Full
500steps100ms forecast113.620s <120s/4GiB;1266 launched separately based
on pilot. Same Native1260 free-layer baseline,ONLY interfaceconstraint added,
all collision models retained. New detector journal filename detector.csv
is NEVER Git-added;Raw remainslocal and hashable. This naming does not
change physics. Actual1266 result and independent comparison follow in
new assessment;do not infer its outcome from predictedratio1.09873.

Git exception/error is explicit: prior9a8d4a8 accidentally included128561058B
layer_pairs.csv. No historyrewrite authorized;seeGIT_LAYER_PAIRS_POLICY_FAILURE.
NoPush;all future stagedfiles checked before commit. Research validity is
separate from unresolved Git history policy failure.

Reproduce(unique outputtags):
`python product_prototype/sofa/layer_interface_reference.py --tag UNIQUE`
`python product_prototype/sofa/layer_refined_interface.py --tag UNIQUE --steps 10`
`python product_prototype/sofa/test_layer_interface_reference.py`

## Actual refined contrast1266/1267

1266 completed500Native steps100ms in107.619s within120s/4GiB (forecast
113.620s),0ERROR,sourcee8ab6ba.1267 accepted-state geometry/referenceaudit
12.735s:finalfree/tied endpoint-displacement ratio1.098749997 vs independent
1.098733680. This is NOT a static stiffness ratio. Actual tied finalTip
−1.70892173um,last50tiprelative drift.0001114,maximum node speed4.87e-5m/s:
static equilibrium NOT QUALIFIED. All500accepted elements remainpositive,
minvolume.999999116;no strict tetra-centroid overlap witnesses. Maximum
interface vector mismatch13.928nm. No complete collision proof claimed.
Contactforce/rootreaction/wholeenergy/pressurelaw remainNULL.

ActualNative PNG/SVG generated and visually checked in1267,with separate
mathreference dottedlines and NOTjamming qualification title. Matplotlib's
Axes3D unavailable warning preserved;2D figure generated correctly.
Next check actual Cq/Cv coupling and accepted-state position increment;
do not infer equilibrium from only width-mean tip convergence.
