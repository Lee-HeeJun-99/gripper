# Telescoped displacement-frame tendon (independent experimental variant)

For each routed Rail,constant spatial tension T gives
`Phi=T*sum(|d|-L0)`. Write `d=(L0,0,0)+delta` and telescope
`sum(delta_x)=guide_tip_displacement_x-guide_root_displacement_x` BEFORE
floating-point force assembly. The remaining segment potential is
`T*(d_y^2+d_z^2)/(|d|+d_x)` on the positive-x branch. Nonpositive-x uses
`T*(|d|-d_x)` directly;collapsed segments/normals are rejected,not regularized.
Guide displacement uses material increments of centre,normal and width frame.
All forces and Hessians come from these same AD potentials. No nodal force,
stiffness,accepted state or tolerance is corrected after evaluation.

This assumes the existing frictionless guides and one constant T along each
Rail at each query time;it is NOT capstan friction or a mechanical Equalizer.
The potential is an external prescribed-tension load potential,NOT stored
elastic cable energy. Mechanical tendon work remains `-integral(T*dL)`.

Qualified fixture:100mm,21rows,4quarter-aligned segments,quadratic root,
normal offset5mm,lateral0/6mm. Other meshes/routes are NOT qualified.
Reuses the reference-exact attachment,existing Shell and projected mass.
Historical route,Field,binary,checkpoints and failures remain untouched.

1712 legacy tiny-value test FAIL;1713 new tiny-value test PASS through1e-30mm.
1714 original FD/Hessian/objectivity/force-moment/baseline gates PASS.
1715 Gauss4 nonlinear stage FD and query purity PASS.1716 independent
25us8/16/32-substep comparison PASS0.1% without a floor,worst0.0111928%.
1711 same test with the old tendon FAILED22.3772%. This comparison does NOT
establish the sole cause of every time error or certify actual SOFA/grasp.

Existing actual Attachment-only variants still FAIL all-output-clock shape
time gates1708/1710,despite endpoint-only PASS1691/1706. Do not promote
this new candidate to production contact,checkpoint resume or final design
before separate actual API,dynamic,all-time,work and contact qualification.

Later qualification:1717 actual SOFA API PASS;1718/1719/1720 strict actual
200us8/16/32-public-step dynamics PASS,each public interval subcycled8times.
1721 ALL common public-clock q/v/shape comparisons PASS0.1%,worst0.0201771%.
This is NOT accuracy at every continuous time or contact/long-cycle certification.
1722 actual-force observer reproduces physical forces EXACT;stored/work/kinetic
endpoint comparisons pass,but partial signed energy residual relative FAIL200%
is preserved. Root work remainsNULL and residual is NOT physical heat.
The Field's Legacy Sampled Work still uses rounded historical length sampling;
use separately audited stage work,not this legacy accumulator,for work research.
No old three-finger checkpoint can be treated as an exact resume of this variant.
