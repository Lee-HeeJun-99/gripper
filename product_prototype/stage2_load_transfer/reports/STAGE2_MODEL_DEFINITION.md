# Rev AA physical-model boundary

Stage1 assembly has 304 BRep solids. All BOM rows were parsed and STEP hashes
checked. Geometry is in mm; integration outputs SI volume m³, centroid m and
unit-density geometric inertia m⁵. Multiplication by a justified kg/m³ density
is needed for actual kg m² inertia. All 51 physical inspection records are blank.

Independent parallel-axis reconstruction versus assembly STEP:
volume relative error 1.5193233e-11; centroid error 1.1902818e-12 m;
central inertia relative error 1.6825067e-11. PASS only for geometry integration.
Default OCC integration failed the SAME thresholds; adaptive 1e-10 integration
resolved this without changing CAD or tolerances. Old failure remains stored.

Stock solids: rigid structural idealization initially, with critical local
holes/shoulders requiring section/FEA. Motor and bearing solids: purchased
interface envelopes, not homogeneous steel. Fasteners: thread envelopes, not
exact thread mass or notch model. Tendon: tension element requiring supplier
linear mass / axial stiffness and termination ratings, NOT a 0.5-mm solid bar.
PET + two spring rails: deformable unbonded laminate with mechanical root AND
terminal capture. Neither perfect composite bonding nor free end slip is yet
justified; both endpoint conditions must be compared.

Actual physical dynamic assembly mass/inertia remains unqualified. A valid
geometric integral is not a finite-speed dynamics validation.
