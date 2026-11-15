# BEAM01 — inherited global-moment diagnosis

Status: **PASS reproduction/root-cause evidence; inherited finite-deformation
moment consistency FAIL.** Original BeamFEM and historical data were not edited.

Fresh execution: `tools/beam_inherited_audit.py`,
`diagnostics/conservative_beam/InheritedAudit.cpp`; raw
`results/beam_20261115/inherited_audit/{command.json,stdout.log,summary.json}`.
Actual Beam `addForce` on two prescribed cantilevers was evaluated at amplitudes
.001/.1/.4 and global rigid rotations0/1.7rad. Net force was zero, while Y moments
at rotation0 were −2.4163689869e-12,−2.41633870839e-6,−1.54616737190e-4 F·mm.
The missing-geometric-couple prediction matched all six cases to1.563e-17 F·mm.

The inherited local linear element balances torque using its rest lever.
When its local force is rotated back with the first node frame but evaluated
about CURRENT positions, the remaining term is
`Σ Ra (u_local × f_b_local)`. This term predicts the measured defect; rotating the
entire scene rotates the defect covariantly. This is not a quaternion-order,
reference-origin, root-reaction or world/local observer conversion explanation.
It does not establish a general potential for that inherited force law.

Fresh full old-model replay: `tools/beam_inherited_live.py`,27960actual steps,
`inherited_live/summary.json`. Beam Y moment reproduced
−2.2629438920710246e-5 F·mm, with FrameLayer≈1.94e-12 and cable/contact terms
orders smaller. The inherited diagnostic binary and original scene-template
hashes are retained. Recorder removal changes I/O, not physical force laws.

Separate root/guide reactions in new trials use `support=-unprojected_force`
only on constrained DOFs; free residuals are not mixed with those reactions.
All moments use the object COM as the same origin and include r×F.
The full eight-item scene-isolation matrix requested by the user was NOT RUN
as eight separate campaigns: prescribed-beam, single fixed-root and full live
field decomposition are the actual evidence. No broader claim is made.

New-model comparison and resolution: BEAM05. Prior closed-work result remains
historical evidence in CLOSURE06, not a newly rerun old-work integral.
