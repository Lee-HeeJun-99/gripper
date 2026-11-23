# Native layer mesh/formulation1260–1262

Continues fe5f9ba. 1260 actual nx33/500steps100ms in62.675s vs pilot-based
63.185s forecast,4GiB/120s. All old material/geometry/load/dt/collision/ODE/
constraint settings retained;only lengthwise mesh changed,totalmass same,
UniformMass nodal distribution necessarily follows new node count.
1261 actual Native methodlarge→small ONLY,originalnx9,500steps100ms2.408s.
Compiledjournal binary hash checked;SDK unchanged. Actual command/source/
scene/binary hashes in independentpreflight and process command files.

1262 bounded reference/accepted-state audit7.086s:

|case|tip magnitude um|relative CST-tip error|reference-force residual relative|
|---|---:|---:|---:|
|reused1189large,nx9|.118967933|5.42e-9|.17425|
|1260large,nx33|1.877677746|2.28e-7|21.5115|
|1261small,nx9|.118967932|4.93e-10|5.58e-5|

Actual Native mesh9→33 tip error93.6641%,FAIL1%Gate. Settled100ms response
is very different despite same geometry/load and zero measured contact
impulses. All accepted elements signedvolume>0;no strict centroid overlap
witnesses,no constraintiterationlimits. Absent centroidwitnesses are not a
complete collision proof. Refined finalmaxspeed1.45e-9m/s andlast50tipdrift
2.15e-6;settled-looking q does NOT prove equilibrium or mesh independence.

Native small formulation agrees linear displacement much more closely,
but residual is still finite. This is independent LINEAR K applied toactual
Native q,NOT queried Native internalforce or nonlinear equilibrium. High
conditioning/nonlinear cancellations remain possible contributors. Do not
call smallmethod a general large-strainB3fix or loosen force thresholds.
Native internalforce,rootreaction,wholeenergy remainNULL in this audit.

Existing alternatives reviewed,NOT rerun: native rectangularBeamAdapter
prior432–455 has loadedprecision/tangent failures;native shell prior415
has derivative limitations;old solid hexa393–399 confirms aspect-dependent
shearstiffening. Installed headers alone do not qualify a replacement.

Next independentP2: exact ideal-interface CST reference across element
aspect ratios,compared toactual1239,then profile a refined-interface Native
contrast ONLY if it can distinguish discretization from interface law.
No more mesh samples just to accumulate tests,no unqualifiedB3integration.

Reproduce(unique tags):
`python product_prototype/sofa/layer_mesh_native.py --tag UNIQUE --nx 33 --steps 500`
`python product_prototype/sofa/layer_linear_native.py --tag UNIQUE`
`python product_prototype/sofa/layer_native_reference_assess.py --tag UNIQUE`
`python product_prototype/sofa/test_layer_native_reference.py`
