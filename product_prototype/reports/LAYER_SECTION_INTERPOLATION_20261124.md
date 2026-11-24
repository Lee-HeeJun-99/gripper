# Section interpolation diagnostic — 1279

Independent exact-field diagnostic, not Native execution or grasp qualification.
Command: `/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/layer_section_reference.py --tag layer_section_reference1279`.
Raw summary and immutable producer: `product_prototype/results/layer_section_reference1279/`.
Source commit/hash recorded in summary. SDK/binary: NOT USED.

Same 40×10×0.2mm volume and assumed isotropic material. The prescribed
polynomial displacement is only an interpolation probe, not actuation.
At nx33, width nodes2→5 leave total energy ratio36.482142857 unchanged.
Thickness nodes2→3→5 reduce normal energy ratio3→1.5→1.125 but leave
parasitic shear ratio33.482142857 unchanged. Length nx33→65→129 reduces
shear ratio33.4821→8.37054→2.09263 (factor4 per doubling intervals).
Thus section thickness refinement alone cannot remove longitudinal
interpolation shear for this field. Width independence applies ONLY to this
y-independent polynomial, not general load response or Poisson relaxation.

Analytic normal ratio is 1+2/nz_intervals²: tetrahedral constant normal
strain samples section endpoint z values, rather than integrating the exact
quadratic strain energy. Positive tetrahedra and volume are independently
checked. This is not proof of the unique B3 failure cause.

PASS: exact-field diagnostic. Native time/mesh/contact, loaded section,
jamming, Holding and product qualification remain NOT QUALIFIED.
Next: consistent face traction integration before any Native section variant.
