# Tendon and actual loaded seating

[Carl Stahl current6x7-WSC table](https://www.carlstahl-technocables.com/gb/en/products/wire-ropes-and-strands/stainless-steel-wire-rope/)
listsAISI3160.45mm/SE000005151N/0.8g/m and0.54mm/SE000006235N/1.2g/m.
The inspected table does NOT list the current nominal0.50mm. Custom supply
is possible but unconfirmed. Do not interpolate a certified rating or replace
it with1x19. Finished NI000032 pullout, EA and fatigue are unresolved.

`validation/tendon/seated1` intersects exact torus/cylinder wire envelopes
against the actual Rev AA drum, cap, pin and plugs. Nominal floorR10.930 plus
wire radius gives11.170/11.180/11.190mm centres. All30 exact-common checks0.
The full torus conservatively contains any wrap arc. The fixed nipple outlet
atR11.25 connects through a taut tangent initially5.920..6.837deg from its
old nominal direction. This is a zero-bending-stiffness geometry limit, NOT
finite-wire contact dynamics, actual curvature transition or fatigue approval.

Stroke-control sensitivity usesK_wire1000/10000N/m and the inextensible limit,
explicit ASSUMPTIONS, not solid rod E*A. Actual measured EA/length/preload
must replace them. Finite grip fixtures and strict empty-log rejection are
implemented under hardware_test; no physical data were entered.
