# Distributed manufactured curvature1187 — REJECT INITIAL GEOMETRY

100g baseline1100 shows early1–1.2s Skin support0.70645N<0.981N before late
solver saturation. Hypothesis: spread same40deg distal angle over60–100mm
instead of70–100mm,improve inward reach without increasing tension/friction.
Implemented separate parametric config,actual Skin/Rail/STLs,3-finger routes,
SCAD reference and dimensioned orthographic drawing. All other config equal.
Tip reference moves3.060mm inward,1.580mm upward. Not observed actuation.

Actual initial triangle/sphere gap becomes−1.675mm (baseline+1.399mm).
Conservative Guide envelope gap−0.045mm (baseline+5.511mm). Wire clearance
still+1.508mm. Signed tetra volumes positive,but initial object penetration
rejects this candidate BEFORE Native dynamics. No object repositioning,
collision disable,Guide shrinking or tolerance relaxation used to pass.
Tet-discretized volume410.1026 vs410.0524mm³;analytical material dimensions
same but numerical volume differs,so not exactly equal-volume FEM certification.
No adoption,no Holding/Lift/assembly/STEP PASS. Original B3 kept unchanged.

Source config/producer/STL hashes in results/b3_arc_start_candidate1187.
Reproduce fresh tag:python product_prototype/sofa/b3_arc_start_candidate.py
--tag NEW_ARC. Do not force this penetrating shape into grasp simulation.
Next independent layer pressure/friction coupon;actual PET properties unknown.
