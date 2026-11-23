# Native detector / response provenance — 1220–1224

Started clean 9d3d064. New observer reads public detection vectors and actual
Vec3 child position/J at BuildConstraintSystemEnd. No getConstraintInfo,
protected-memory casts, force queries, SDK edits or state writes.

1220 compile FAIL: getMechModel returns BaseMechanicalState, not typed state.
Original failed source/logs preserved. Explicit checked Vec3 cast fixed in
fresh build1221 (3.313s); old1211 build untouched. Binary SHA
4d0c75478e5b3cc1785d549b63fd7bc509cdef627b190886faafa43a2c0a80b6.
Source SHA 2c9402711032617d5f1d1ead2b89d747d2b28421bc18e914d399900a296ee33a.
SDK /home/ubuntu/SOFA/v26.06.00; guarded 4GiB/120s build,60s run.

1222 actual Native10 steps,2ms,0.136s: q/v/contact impulse EXACT0 difference
versus1212. PASS read-only purity ONLY. Actual scene/preflight/ldd/command
and hashes are in results/contact_provenance_run1222.

1223 first analysis rejected shared-state rows with missing opposite owner
side; analysis exception, no physical verdict. Corrected1224 requires both
owner sides and unique detector coordinate/normal matches (1e-12 identity
matching,not relaxed contact or time Gate). Native mu=.3 three-row order is
explicitly sourced to installed BaseContactLagrangianConstraint.inl.
Shared child states include other owners' rows; those cannot be attributed
to the current owner merely because they appear in its mechanical state.

35/35 actual normal rows uniquely match detector model/element/index/points
and +/-normal at five previous accepted times0,.2,.4,.6,.8ms. At .4ms all7
horizontal +X normals originate in the detector itself: 4 support Triangle–
layer Point,3 layer Line–support Line. It is not merely a downstream parent
mapping rotation. Point distances0–3.57e-17m at this event. Earlier normals
vertical; later reverse. This is scoped evidence,not a universal SDK defect.

Next independent contrast: primitive finite-radius sphere over the same
support/load/fixture/dt. Its center-to-surface distance remains finite at
surface contact,unlike coincident zero-thickness feature coordinates.
Different contact geometry/inertia;NOT a repaired layer or grasp candidate.
Require mu0 sliding and mu.3 friction control,actual geometry,impulse balance.

Reproduce (unique output names required):
`python product_prototype/sofa/contact_provenance.py --tag UNIQUE --build-tag contact_provenance_build1221`
`python product_prototype/sofa/contact_provenance_assess.py --tag UNIQUE`
`python product_prototype/sofa/test_contact_provenance.py`

All B3 time/mesh/100g Gates unchanged. No new Holding/Lift or jamming PASS.
