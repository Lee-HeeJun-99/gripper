# Native layer-pressure/friction coupon — exploratory research

New independent track,NOT a Young-modulus change or calibrated layer jamming.
Two separate40x10x0.2mm strips,Native large-tetra FEM,2µm initial interface
gap,actual Triangle/Line/Point interlayer friction contact. Opposite outer-face
nodal pressure loads approximate pressure differential;no vacuum chamber,
membrane/seal model or measured pressure/friction data. Assumed E2.5GPa,
density1400kg/m³,nu0.3,mu0/.3,p0/1000Pa are RESEARCH INPUTS,not confirmed PET.
Both roots fixed;total bending load0.1mN,constant for this transient coupon.
Native global ODE Rayleigh1/1e-4,dt200µs;not measured damping or convergence.

1188 pilot50steps/10ms actualNative5.085s,0ERROR;both layers finite,
min volume ratios0.999922/0.999937. Native detector and multiplier journals
record actual contact;solver residual not automatically qualified byexit0.
Forecast500steps~50.85s each within4GiB/120s guards,atmost3physicschildren.
Next matched trials:zero pressure/friction;pressure withmu0;pressure withmu.3.
Same E/mass/mesh/root/bending force/time. Compare transient tip displacement,
interlayer slip,gap andsolver status. No static stiffness ratio unless equilibrium
confirmed,NO vacuum-jamming/holding/product PASS. Work/heat/pressure map NULL.

Actualcommands/source/binaryhashes/SDK in each preflight. No detector.csv used.
Reproduce fresh tag:python product_prototype/sofa/layer_pressure_coupon.py
--tag NEW_LAYER --pressure 1000 --mu .3 --steps 500.
