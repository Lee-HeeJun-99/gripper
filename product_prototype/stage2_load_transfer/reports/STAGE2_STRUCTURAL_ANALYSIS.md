# Structural verification progress

No actual part strength or fatigue release yet.

## Finite rotation Finger control

`validation/finger/elastica1` stores 40 actual quasi-static equilibria, two
endpoint conditions and 8/16/32/64 cells, under 0.05/0.25/0.5/1/1.5 N.
Analytic potential gradient matches independent finite differences within
3.65e-9 relative. Equilibrium force-equivalent residual <1e-6 N and final
mesh displacement differences <1% passed. Positive tangent eigenvalues
identify local minima of THIS model, not unique global equilibria.

With both endpoints locked, fine-grid rotations are 1.436/8.215/20.248/70.578/
135.426 degrees. The last two EXCEED Stage1's prescribed 0..60-degree
geometry evidence. No hardware or integrated dynamic PASS follows.
Free-terminal-slip control gives3.193/21.358/66.996/167.371/191.435deg.
Larger rotations are preserved diagnostics OUTSIDE the assembly validation
domain; they are not usable mechanisms or qualified motion predictions.

The assumed rail/PET moduli and projected rail geometry are explicit.
Unknown clamp slip/retention is influential; it cannot be hidden by choosing
the more favorable stiffness. New full-load actuation must remain gated.

## Actual shaft sections

`validation/shaft/sections1`: exact shaft BRep intersected with0.02/0.01/0.005mm
slices at six mechanical stations. Net cross-pin section38.33619mm² versus
clear8mm shoulder50.26548mm²; root4.30mm sections14.52201mm². All section
refinements <1% passed. Polar area moment is NOT Saint-Venant torsion constant
for flat/perforated sections. Neither nominal round-shaft stress formula nor
net-area integration certifies the hole-edge stress concentration.

Next: actual STEP linear-elastic local torsion control with defined fixtures,
independent circular-cylinder reference and bounded mesh-refinement tests.
This will not substitute for actual pin bearing/contact or material allowables.
