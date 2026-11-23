# Conditional laminated pressure-pocket CAD1198/1200/1201

Independent from failed Native contact coupon and300partB3 assembly. New
parametric8-layer40x10x0.1mm stack,50µm resting gaps,pocket44x12x1.4mm,
0.1mm top/bottom membranes,finite seal bands and explicit polygonal port bore.
15individualSTLs,assemblySCAD,dimensionedSVG,parameters,BOM created. Materials,
forming/sealing process,port joint,friction,fatigue,leakage andpressure UNKNOWN.
No Native deformation or chamber/vacuum law is implied by static CAD.

Independent actualSTL audit1200:minimum layer gap0.04999998mm,membrane
gap0.12500001mm,planar clearance1mm,finitepolygon bore/tube gap0.00914355mm.
Positive gap is NOT an airtight seal;real port joint is required. Individual
STLs are watertight,but concatenatedassemblySTL becomes nonmanifold when
coincident seam interfaces weld. It is VISUALIZATION ONLY,not fabrication
solid.1201 separate-componentGLB preserves15watertight parts without pretending
a boolean/STEP kernel succeeded. STEP/moving interference/assembly strength
remain BLOCKED/NOTMEASURED. Not fabrication ready or integratedB3.

Ideal free-slip EI/E=6.6667e-15m4;zero-gap perfectly bonded EI/E=4.2667e-13m4,
ratio64 for8layers. Mathematical bounds ONLY,not pressure-calibrated stiffness
or actual PET/vacuum/jamming performance. No Young-modulus switch simulation.

Reproduce fresh tags with cad/layer_cartridge_coupon.py,layer_pocket_audit.py,
layer_pocket_scene.py --tag NEW_NAME. No existingCAD/Raw overwritten.
