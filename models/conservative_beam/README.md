# ConservativeBeam — independent research model

Two-node, three-dimensional midpoint/reduced-integration Simo–Reissner rod.
This is an independently defined discretization, not a replacement edit to SOFA
BeamFEM and not a certified PET-film model. Units are mm, s, and the inherited
project force unit F; energies/torques are F·mm. No physical calibration is implied.

For reference length L, midpoint orientation Rm, and endpoint rotations Ra,Rb:

```
gamma = Rm^T (xb-xa)/L
kappa = Log(Ra^T Rb)/L
E = L/2 [(gamma-gamma0)^T diag(EA,GAy,GAz)(gamma-gamma0)
       + (kappa-kappa0)^T diag(GJ,EIy,EIz)(kappa-kappa0)]
```

Rm is the shortest-geodesic quaternion midpoint. Intrinsic strains come from the
rest state. Global rigid rotations are unrestricted; relative ELEMENT rotation
must remain below 2.8 rad to stay away from the selected logarithm branch.
Material moduli and element lengths must be finite and strictly positive.
Quaternion order is x,y,z,w, with spatial/left increments Exp(dw)Q.

Exact second-order automatic differentiation supplies f=-DE. The energy chart
Hessian is symmetric; the derivative of spatial torques is generally NOT:
`Df=-H-.5*skew(torque)` on each rotational diagonal block. Consequently the
SOFA trials use nonsymmetric EigenSparseLU, not SparseLDL. The correction is a
coordinate connection, not an extra force or torque. All three forcefield APIs
use the same derivative and include SOFA kFactor/Rayleigh conventions.

One-point integration is low order. Its linear cantilever result contains the
discretization term `1-1/(4*m*m)` plus Timoshenko shear compliance. EA/EI/GJ/GA
must be compared separately. Shear correction5/6 is an explicit research choice,
not the exact shear factor of the old circular section. No self-contact,
cross-sectional warping, plasticity, pressure distribution or material damage.

Build with the matched SDK (do not mix installed-SOFA libraries):

```bash
cmake -S models/conservative_beam -B build/beam_local \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH="$PWD/.runtime/closure_sdk"
cmake --build build/beam_local -j2
ctest --test-dir build/beam_local --output-on-failure
```

The equivalence test deliberately obtains its immutable dense reference from
Git commit4d19774. A shallow/source-only archive without that commit is not
sufficient for this test; fetch full local history or preserve that reference
explicitly before porting. Do not silently skip it to claim a clean test PASS.

Research runner examples and actual limitations:
`reports/CONSERVATIVE_BEAM_NEXT_TASKS.md` and `BEAM_02_VARIATIONAL_MODEL.md`.
The full grasp optimization gate remains closed when contact/history convergence
or coupled energy accounting is incomplete, even if individual holds pass.
