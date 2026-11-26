# Rigid coupling alignment: new load-risk evidence

`validation/coupling/alignment1` is an implementation failure (undefined result
variable) and remains preserved. Corrected `alignment2` uses actual shaft BRep
sections at33quadrature stations and nominal manufacturer D-shaft geometry.
Rigid coupling links contact centroidsY−26/−15.25; bearing centres−6/+11.5.
Independent uniform-beam element formula and force/energy checks passed.

Motor shaft modulus193/200/210GPa are ASSUMED sensitivity inputs, not a known
motor alloy range. Output303193GPa is typical. The conditional frame stiffness
is1.028..1.100MN/m. Elastic extrapolation at0.25mm offset gives257..275N,
far above the manufacturer's21N radial reference. Such extrapolation may
already violate actual elastic/material/support limits; it is NOT a prediction
of measured load. Stage1's generous pilot/bolt clearance is therefore NOT an
axis-alignment allowance. Existing dial-indicator instruction needs a quantified
load budget, not automatic acceptance at the clearance extreme.

Using half the21N radial reference alone gives conditional offset limits
9.54..10.21um; this does NOT validate a combined force/moment motor envelope.
A provisional5um combined translation+angular-error setup budget was selected
below this range, reserving room for normal loads. It is NOT a certified safety
limit until actual motor material, bearings, plate compliance and contact are
validated. No CAD or Stage1 approval has been changed on an assumed result.

`scripts/alignment_records.py` reduces two four-azimuth rim measurements at
stations bracketingY−26mm, propagates bounded probe uncertainty, includes the
10.75mm contact-centroid separation and rejects incomplete/excess-budget data.
The new physical record CSV is blank. Even a valid synthetic log cannot produce
hardware PASS or power authorization. Actual gauge mounting, runout separation,
calibration and combined motor reaction remain follow-up verification tasks.
