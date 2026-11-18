# Same-core-volume physical rail aspect candidates

Separate75/100/125um rail geometry. Width follows fixed cross-sectional area;
material,E/nu,skin,bond,root map,T profile and routed eccentric offsets are
unchanged.100um returns the original assembly untouched. No stiffness multiplier,
modulus tuning or jamming surrogate.1g/finger remains a research mass assumption,
not measured density. Guide solid volume/mass and fabrication strength unknown.

1649 existing FD/objectivity gates PASS.1654 actual ForceField APIs PASS.
1657/1658 actual SOFA no-object coupon states/Gauss stages/energy match the
same-law reference.10ms75um improves curvature about13% but needs42% more work;
not a selected design or equal-work superiority. Time convergence is separate.

Build through tools/film_rail_aspect_build.py;generated Field is source-bound.
The reused OdeSolver gains only a virtual assembly factory;default behavior
returns the original model. All old source/binary/results remain immutable.
New Field freezes thickness before caching and rejects runtime geometry changes.

Mass-linked static reference geometry is retained for DiagonalMass initialization.
The old100um world mapping is NOT used for modified rails. Deformed coordinates
come from actual Field rest+u,not the static mass geometry. No object/contact,
self-collision,finite wire/guide,wrapping,holding or grasp certification here.
