# Layer coupon reference1257–1259

Started168e11b clean. Independent small-strain constant-strain tetra algebra
reference,not a new SOFA solver/ForceField. Actual1189 mesh,root,material,
four tip nodal forces reused,all old Raw/verdicts preserved. Guard4GiB/60s.
1257 actual reference .507s;source/input hashes and command in results.

Independent tip−.1189679323um,actual settled Native large-FEM−.1189679329um:
relative5.415e-9,maximum displacement difference2.234e-13m. BUT Native state
inserted into linear-reference K has free residual1.239e-6N,relative17.43%.
Tiny displacement agreement is NOT force balance or actual nonlinear Native
internal-force validation. Reference own rootreaction+50uN,free residual
1.14e-14N;reference mass/volume matches actual8e-8m³. WholeenergyNULL.

Exact nodal pure-bending displacement (kinematic interpolation test ONLY,
not dynamic actuation) has zero continuum shear. On actual9-node length
CST mesh its interpolant energy is538.714x exact3D epsilon_xx-only energy;
99.443% is shear. Reference tip-load solution shear energy99.338%. This
establishes excessive bending/shear interpolation stiffness for THIS mesh,
not a universal Native bug or sole B3 instability cause. Euler beam tip64um
is approximate,NOT exact3D;poisson/boundary differences remain.

1258 ONE-axis independent reference9/17/33/65/129/257 preserves volume,
geometry,E,nu,root,SAME4tipforces. Tip[um]=.11897,.49555,1.87768,5.80164,
12.0011,16.3541. All adjacent pairsFAIL1%;129→25726.617%. Pure-bending
energy ratios538.714→136.929→36.482→11.371→5.093→3.523. Section resolution
still fixed2x2 and unqualified. Do not infer converged EI or vacuum stiffness.

1259 NEW actualNative nx33 pilot50steps10ms,6.318s,0ERROR,no inversion:
tip≈−2.33045um at10ms(transient,NOT settled stiffness). Compared oldnx9
but not endpoint matched:independent reference static is−1.87768um.
Native500steps100ms forecast63.185s within120s/4GiB;launch separately1260.
All collision/ODE/constraint/material/load settings kept;only length cells
changed. No pressure/friction sweep,old B3 full run or static372 replay.

Reproduce(unique tags):
`python product_prototype/sofa/layer_bending_reference.py --tag UNIQUE`
`python product_prototype/sofa/layer_mesh_reference.py --tag UNIQUE`
`python product_prototype/sofa/layer_mesh_native.py --tag UNIQUE --nx 33 --steps 50`
`python product_prototype/sofa/test_layer_reference.py`

Next actual100ms meshcontrast and independent settled/overlap/reference
assessment;then small-vs-large Native constitutive/arithmetic contrast if
needed. No product or jamming qualification.
