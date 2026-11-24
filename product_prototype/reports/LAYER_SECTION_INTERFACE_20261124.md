# Section-refined ideal interface1290–1293

Existing independent CST with consistent face traction:normal-only displacement
tie ratio≈1 at nx9/nx33;XYZ tie free/tied displacement ratios1.0069643 and
1.1041649. Tangential coupling,not merely preventing normal separation,
changes this reference response. Both ratios remain discretization-dependent.
These are linear fixed-world-gap ideal limits,not pressure/friction laws.

Actual Native1291 pilot50steps0.908s forecasts9.077s;1292 actual500steps100ms
7.297s. Same54node/layer section and112mg/layer UniformMass. AddedXYZ
BilateralLagrangianConstraint;stricter unscaled termination uses unchanged
numeric1e-10,as previously independently validated. Allcollision retained.
Scene/source/binary/plugin/command hashes inpreflight;noSDK modifications.

Actual1293 accepted audit:free/tied endpoint1.00696431945,reference difference
8.24e-10. MaxCq9.43pm,Cv4.04e-8m/s;last50maxspeed1.46e-13m/s;
minimumvolume ratios0.9999999615/0.9999999938;maxiterations14,error9.97e-11.
No effective stiffness or real jamming ratio asserted:explicitNULL.
No time/mesh/product qualification or B3 integration. Actual material,
pressure,friction,seal and fatigue remain NOT MEASURED.

Hypothesis supported in reference scope:tangential load transfer matters,
but shear-stiff coarse solid FEM can hide ideal coupling benefit. Do not fit
Young's modulus or call this vacuumjamming. Next real jamming requires measured
pressure/friction and a bending-reliable/contact-valid coupon first.

Commands with Python `/home/ubuntu/miniconda3/envs/robot_ws/bin/python`:
```
product_prototype/sofa/layer_section_interface.py --tag NEW_REFERENCE
product_prototype/sofa/layer_section_tie_native.py --tag NEW_PILOT
product_prototype/sofa/layer_section_tie_native.py --tag NEW_FULL --steps 500 --pilot NEW_PILOT
```
1293 assessment explicitly refers to1292;do not use unchanged for other runs.
Immutable producers/dependencies andactualstdout/stderr preserved eachcase.
