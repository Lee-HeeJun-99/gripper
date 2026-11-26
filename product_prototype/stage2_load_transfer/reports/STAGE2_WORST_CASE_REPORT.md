# Conditional dimensional corners, not certified all-physics bounds

`validation/worst_case/dimension_corners1`:32actual solutions using released
PET0.28/0.32mm, rail0.19/0.21mm, wire0.48/0.52mm and finished-length±0.25mm.
Effective pull =16.91mm minus length error. WireK1000/10000N/m and material
moduli remain hypothetical model inputs, not procurement intervals.

Tendon force range0.675943..0.968626N; tip rotation43.9042..48.3207deg.
All equilibrium/stroke residuals pass1e-6N/1e-9m. These are no-object closing
model results, not100g Holding requirements or actual full-assembly motion.
Material modulus bounds, clamp slip, contact geometry/friction, motor torque
reduction, fastening preload and dynamic losses prevent system worst-case PASS.

`validation/integrated/stroke1` separately passed potential/KKT comparison,
16/32/64mesh refinement and input-work/stored-energy checks. Initial0.8N-scale
closing is a useful test-envelope candidate, NOT a certified design load.
