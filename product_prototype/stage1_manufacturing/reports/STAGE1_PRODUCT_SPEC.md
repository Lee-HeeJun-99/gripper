# Stage1 revH product specification — UNRELEASED

Three replaceable, flat sheet Fingers at120degrees, Root radius50mm.
Free reference length100mm below z0,10mm root allowance; clamp body ends at
z=-7mm. PET0.30mm, two3x0.20mm backing strips on the outside. These are
manufacturing candidates, not measured material properties or B3 geometry.
No adhesive along the span is specified; Root and terminal clamp the stack.
Actual joining/sliding and pad retention are not mechanically qualified.

Three individual tangential winch axes at localX80/Z20mm. Motor shaft couples
to an independently supported Ø5 shaft; two625 bearing boundary envelopes
per shaft. Drum radius8mm, two reserved channels, physical wire diameter0.5mm.
One active path per Finger, not two synchronized tendons. Nominal centreline
winding radius8.25mm gives51.84mm/revolution, NOT measured usable stroke.
Reference1.5N on one path corresponds to0.012375Nm, not a required motor rating.

Fixed idler at localX44/Z25, groove radius4.5mm; centreline4.75mm. Bend
ratio to nominal wire diameter18 at the groove surface. No supplier bend-life,
wire strength, efficiency, friction, usable stroke or fatigue is certified.
Drum channel2 is reserved, not an implemented antagonist/return mechanism.
Current shaft/coupling/drum lack complete torque/axial retention: do not power.

Palm OD270/ID40/thickness5mm, topz=-7. This is larger than the old128mm Palm
because real motor/shaft/Root service envelopes could not be fitted to the
compact radial layout without collisions. This is a NEW minimum prototype
architecture, not adopted300part CAD. No old Native success transfers to it.

SOYO SY42STH38-1684A / Pololu2267 is the motor INTERFACE candidate. Source:
https://www.pololu.com/file/0J714/SY42STH38-1684A.pdf . Exact vendor internals,
lead connector, D-flat and all chamfers are omitted in conservative envelopes.
The modeled2mm pilot projection needs vendor confirmation; don't infer it
from generic NEMA nomenclature. Datasheet holding torque is not continuous
loaded performance. Controller/power supply/limit switches remain unselected.

SKF6255x16x5 boundary source is linked in DESIGN_SELECTION. Bearing pockets
16.05+0.02/-0mm are a proposed machined slip seat, NOT a verified H7 fit or
retained bearing system. Shaft h6 is design intent, not a bearing fit approval.
Fastener head5.5x3 and tool2.5AF reference Bossard ISO4762 table:
https://www.tme.com/Document/807aff253db5b8939e6fd7f5801633d5/BN2.pdf .
Nut circumscribed cylinders are conservative envelopes, not exact hex CAD.
No material strength/preload/fit tolerance is certified by these envelopes.

World units mm; axisZ upward, each module localX radial outward/Y tangential.
Part IDs are assembly positions. Exact solids and holes: producer.py and
part STEP under cad/exports/revH. BOM lists every actual instance and file.
Future jamming chamber interface/space is NOT yet released; no vacuum model.
