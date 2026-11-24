# Native section control1286–1289

Only thickness node count2→3 changed from1282 at nx9,ny2. Same geometry,
50µN/layer uniform end-face traction,small Native FEM,E/nu,collision,dt and
ODE. Total UniformMass112mg retained;discrete section inertia changes with
nodal distribution,explicitly recorded rather than hidden as mass convergence.
Preflight stores actual scene,command,binary/plugin hashes,sourcecommit/hash.

1286 producer FAIL before Native: numpy int64 triangle JSON serialization.
Partial scene retained,explicit failure summary;fixed integer conversion uses
fresh1287,not overwrite.1287pilot50steps0.643s→500step forecast6.433s.
1288 actual500steps100ms4.831s,all saved signedvolumes positive,min ratio
0.9999999793. No ERROR/unused attribute;500outputs/layer.
1289 independent endpoint q error3.18e-17m;mean tip−0.11937825µm vs1282
−0.11896792µm.Thickness pair relative0.343722% passes this1%PAIR ONLY.
Reference shear energy fraction99.6683% vs99.3377%:this is not a bending
accuracy fix. Native/reference agreement can coexist with stiff discretization.
No time/contact/wholemesh/jamming/B3/100g/physicalqualification.

Reproduce with Python `/home/ubuntu/miniconda3/envs/robot_ws/bin/python`:
```
product_prototype/sofa/layer_section_native.py --tag NEW_PILOT --nz 3
product_prototype/sofa/layer_section_native.py --tag NEW_FULL --nz 3 --steps 500 --pilot NEW_PILOT
product_prototype/sofa/layer_section_assess.py --tag NEW_ASSESS --source NEW_FULL
```
Read-only mathematical reference on same geometry,not a custom Native solver.
Native root reaction,wholeenergy and hardware data remain NOT MEASURED.
Next:decouple ideal-interface sensitivity from bending reliability;do not
expand thickness mesh blindly or transfer this pairPASS into B3.
