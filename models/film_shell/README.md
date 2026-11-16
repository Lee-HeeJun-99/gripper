# Independent structured film research ROM v1

Not ConservativeBeam with increased width. Every grid point has xyz DOFs;
membrane stretch,curvature in both material directions and mixed twist are
represented. Flat rectangular reference only;not a general production shell.
Units:mm,s,model force F. E=250 F/mm² is an assumption,not measured PET.

Membrane:linear triangles,Green strain,plane stress
`ψm=t[λ/2 tr(ε)²+μ tr(ε²)]`,λ=Eν/(1−ν²),μ=E/[2(1+ν)].
Bending:nodal material second differences projected onto current unit normal,
`ψb=D/2[bxx²+byy²+2νbxxbyy+2(1−ν)bxy²]`,D=Et³/[12(1−ν²)].
Trapezoid reference-area quadrature and one-sided boundary stencils.
Curvature formula is a small-in-plane-strain flat-reference Koiter-like ROM;
not a validated arbitrary curved-rest/isotropic discrete-shell element.
The existing [Discrete Shells research](https://multires.caltech.edu/pubs/DS-CDROM/)
was reviewed;this structured stencil is NOT an implementation of that paper.

Force=−gradient(U);tangent=−Hessian(U),exact AD2 over9-point patches27DOFs.
`addForce/addDForce/buildStiffnessMatrix/getPotentialEnergy` share the energy.
The optional world-z root-slope fixture is explicit external boundary energy,
not internal moment compensation. Keep its physical stiffness and root fixed
row constant during mesh refinement. Old two-fixed-row experiments change
effective clamped length and cannot define a clean continuum mesh test.

Optional fixed frictionless plane:exact clipping of each linear triangle in
REFERENCE barycentric coordinates,then exact quadratic penalty integration.
Recorded area is reference contact area and F/area is nominal traction,NOT
deformed area/Cauchy pressure. No free object,friction,grasp,layer sliding,
wire routing or pressure-to-jamming calibration is implemented here.

`displacementDofs=1` means solver coordinates are u,actual geometry=rest+u.
It preserves physical mass/velocity and force/tangent,while retaining tiny
increments and using ε=Sym(grad u)+.5(grad u)^T grad u without squared-length
cancellation. Actual geometry is exported to the journal. Native collision
MUST NOT use the u MechanicalObject directly;it requires x=rest+u mapping with
correct virtual-work pullback. The internal plane is already reference-aware.

Tests:analytical membrane,force/Hessian FD,rigid-motion objectivity,net force/
moment,quadratic plate+twist energy,cantilever mesh and actual SOFA API.
These do not certify contact-cycle energy,nonlinear dynamics or multilayers.
Actual Euler/BDF dynamics still FAIL independent equilibrium/completeness
criteria;see reports/FILM_SHELL_PHYSICS.md. Do not approve grasp Optuna.
