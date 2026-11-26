# Endpoint compatibility — verified reduced model, not strength approval

Actual Rev AA skin occupies X50..50.3 mm; rails X50.3..50.5 mm.
Root and terminal mechanically capture the unbonded laminate. Interior slip
alone does not imply axial freedom at the terminal. Two boundary hypotheses
were implemented, rather than silently selecting a free-slip EI.

Projected 88-mm Euler–Bernoulli beam, tapered PET width, two 3-mm rails;
small 0.001-N transverse tip load. Assumed candidate Mylar A typical modulus
507 kpsi is from [manufacturer data](https://mylar.com/wp-content/uploads/2025/08/mylar_a-1.pdf).
It is NOT a material procurement limit; manufacturer explicitly cautions against
using typical data alone as design specification. Rail 193 GPa is annealed
typical; actual full-hard modulus remains unverified. No actual material PASS.

Axial compliance per layer is integrated; minimizing common end extension
leaves an endpoint rotational stiffness sum(k_i(d_i-dbar)^2). This is an
endpoint coupling, NOT a fully bonded laminate along the span.

Executed `scripts/finger_structure.py --tag endpoint1`:

- Nominal free terminal slip tip deflection: 0.24344050 mm.
- Both clamps axially locked: 0.14629835 mm (60.096% compliance).
- Endpoint rotational stiffness: 0.01197966 Nm/rad.
- Independent compliance quadrature versus assembled 8/16/32/64-element FEM
  met 1% reference/refinement and 1e-8 relative energy thresholds.
- Released thickness limits were also evaluated with the same criteria.

No large-bend, buckling, contact, fatigue, clamp pullout or hardware claim.
Small-load response must not be extrapolated linearly to 60-degree closure.
The next necessary calculation is geometrically nonlinear tendon-driven
equilibrium with endpoint compatibility, followed by stress/retention review.
