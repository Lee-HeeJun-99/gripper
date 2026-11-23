# Critical Guide footprint1152–1155

After one-step impulse isolation, implemented a single joint-design contrast:
Guide3/9 third Rail-bottom anchor moves75→80mm, other two anchors at70mm.
Three non-collinear points,36 disjoint mapped nodes, full rest FEM/material/
mass/routing/C2 force/root/Guide frames retained. No object or support.
This idealized attachment is NOT a fabricated Support; extended hardware
geometry/mass/joint allowables remain NOT MEASURED.

Actual Native SOFA v26.06.00,4GiB/120s guard,1s physical interval:

|Case|Input|dt|Runtime|Minimum volume ratio|
|---|---|---|---|---|
|1152|zero Cable|2.5ms|5.223s|0.9999684|
|1153|2.5N/Cable C2|2.5ms|5.325s|0.5838634|
|1154|same|1.25ms|10.254s|0.7878690|

No saved inversion, all outputs finite, no SOFA ERROR. Baseline1129/1130
ratios0.7764471/0.8752293 were better. Candidate maximum Skin principal Green
strain0.242150/0.211967; material allowable strain NULL.
1155 compares400 actual common outputs, clock mismatch≤5.50e-15s:
Skin139.786%,Rail139.208%,velocity172.487%,curvature56.483% relative errors.
Existing0.1% Gate FAIL. No floors/interpolation; energy NULL. Not a full
three-resolution study. No Holding or Lift performed. REJECT AS NUMERICAL
REPAIR; no CAD adoption or physical qualification. Enlarging the footprint
alone does not resolve early transient sensitivity and worsens volume quality.

Source/binary hashes, command, geometry and snapshots are in each preflight;
new producer and actual Native logs/states are saved separately. Old Raw
unchanged. Reproduction uses fresh unique tags:

```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/b3_joint_footprint.py --tag NEW_FORCE
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/b3_joint_footprint.py --tag NEW_HALF --half
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/b3_rail_back_assess.py --tag NEW_ASSESS --base NEW_FORCE --half NEW_HALF --short none
```

Next: read-only early transient localization using saved baseline/common
clocks, with absolute differences alongside unfloored relative errors.
Do not repeat full100g/high-force runs or parameter sweeps.
