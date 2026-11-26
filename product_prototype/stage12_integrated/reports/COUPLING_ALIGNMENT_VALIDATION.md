# Alignment alternative — not selected

Existing rigid-coupling conditional reaction risk remains unchanged. A new
[Huco238.19 disc](https://www.huco.com/shop/couplings/oldham-couplings/oldham-disc/238-19)
screen and ideal Oldham reference are stored in validation/alignment/oldham1.
Manufacturer disc-only data:19.1mm OD, nominal1.15g, radial0.2mm, angular0.5deg,
axial+/-0.10mm, peak0.43Nm, static break2Nm, torsional stiffness115Nm/rad.
These are not a full coupling/hub specification or a guaranteed release torque.
No stock/price claim or purchase was made.

Independent two-line loop solve matches the closed-form disc centre
`e/2*(1+cos(2theta),sin(2theta))`. Finite-difference velocity/acceleration and
translation energy agree within1.34e-6relative at prescribed300rpm/e0.2mm.
Translation inertia increment is `m*e^2`; corresponding nominal disc inertia
force0.000454N is NOT total shaft reaction. Friction, actual hub preload and
torque-contact forces, rotor inertia and bearing loads are still required.

This mechanism removes the ideal rigid offset constraint in its mathematical
reference; it does not prove the actual motor's21N reference is respected.
Current4.4mm shaft interface and fine-nut service passage need real hub/shaft
redesign. Do not model a19mm disc as an entire19.5mm-long coupling or use its
static break torque as overload protection. Coupling Stage2 gate remains open.
