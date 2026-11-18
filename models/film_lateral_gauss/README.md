# Separated post-unload Gauss block — independent candidate

Reuses existing two-stage order4 Gauss-Legendre film integration and exact
public projected mass/root mapping. Existing free rigid midpoint is retained.
Zero external force,tension0,zero angular state only. Not an impact/contact
solver or an installed SOFA component. No geometry/strength/damping change.
Passive final-stage force capture is checked against returned Gauss stages.
Every new trial needs independent momentum,energy,time and clearance checks;
do not infer whole trajectory qualification from a local coupon.
