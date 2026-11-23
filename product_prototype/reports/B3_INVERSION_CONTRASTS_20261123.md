# Native inversion contrasts1107–1111

Starting HEAD1a08872, clean worktree. No original experiments rerun or modified.
Four actual single-finger/no-object Native runs:240steps,dt2.5ms,0.6s,
same SDK/binaries/root/material/mesh;4GiB/120s guards. Exit0/noSOFAERROR and
240 outputs each are execution checks, NOT physical validity.

| Case | Independent change | First saved inversion | Minimum signed ratio | Runtime |
|---|---|---|---|---|
|1105 preserved|reference2.5N/three-point guide|0.520s|−21.95693|2.424s|
|1107|Cable force0 only|none through0.6s|0.999962907|3.619s|
|1108|Native FEM large→polar only|0.510s,element444|−2.15703|3.326s|
|1109|release third FEM attachment node per guide|0.020s,element270|−3.24167e10|3.314s|
|1111|1109 Cable force0 only|0.0375s,element390|−681.589|3.323s|

1109 retains first two rigid attachment nodes, guide mass/inertia, two cables,
hardware and rest route. Twelve released FEM nodes become free DOFs;no
position/velocity correction. This is a different joint kinematic hypothesis,
not an approved mechanism. Its zero-input failure1111 rules out high Cable
force as a necessary condition for THIS candidate's instability. Reject it.
Do not use any post-inversion motion, even though Native execution continues.

1107 establishes only bounded unloaded stability of the original coupled
FEM/guide system. It does not independently certify Skin or bonded Rails.
1108 rejects polar rotation treatment alone as a repair. Installed SDK header
TetrahedronFEMForceField.inl explicitly supports polar;SDK was not edited.

1110 recomputes deformation gradients from actual saved q/rest tetrahedra.
Original1105 first bad Skin tet402 contains rigid-owned nodes172/175 at
material centroid(68.75,−0.15,0.025)mm. Maximum absolute principal Green strain
over the valid saved prefix is2.79362;polar5.03017. These are diagnostic
kinematic values,not a material-valid stress prediction. Two-point first bad
element is Rail,not Skin. Correlation near a joint does NOT uniquely establish
causality. Work/energy and peak-between-output strain remain NOT MEASURED.

## Performance branch decision

Existing1100 already distinguishes100g early load deficit from later Solver
saturation:1–1.2s SkinZ0.706453N<0.981N weight before the post-withdrawal iteration
limit at1.2875s. First2mm slip1.0975s;late persistent negative normalZ1.325s.
Do not repeat this completed analysis or call Skin inversion the sole100g cause.
No mechanically valid improvement emerged from these contrasts,so no renewed
high-force100g Holding/Lift is justified. Old50g functional Lift remains intact;
whole time/mesh/energy/material qualification remains NOT PASS.

## Next experiment

Construct a small Native three-point guide-joint load-transfer coupon and
qualify rest-state force/mass/rotational kinematics before changing B3 joints
again. Compare Skin-only versus bonded-Rail load paths with identical declared
external load, NOT by silently deleting mapped DOFs or reusing a stale checkpoint.
If no interpretable joint candidate is available, proceed with an independent
predeclared stiffness-sensitivity protocol;it is NOT vacuum/layer-jamming evidence.

Reproduce each only with NEW tags and a new hypothesis:
`python product_prototype/sofa/b3_inversion_contrast.py --tag UNIQUE --contrast zero-input`
Other modes:polar,two-point-joint,two-point-zero-input.
Read existing1110 with `python -m json.tool product_prototype/results/b3_inversion_compare1110/summary.json`.
Actual Commands/sourceScene SHA/binarySHA/SDK are in eachpreflight.json;
producer.py and process journals are preserved. No Holding/physical/productPASS.
