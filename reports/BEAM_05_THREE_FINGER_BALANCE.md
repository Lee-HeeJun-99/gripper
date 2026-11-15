# BEAM05 — recovered three-finger global balance

Status: **PASS +Tz bounded equilibrium/release subgate; EXPERIMENTAL whole grasp.**

Actual new-beam run `results/beam_20261115/grasp/Tz_v2`, duration24s,dt.0005,
11nodes per100mm layer,3fingers×2layers,Gauss8,history grid.01mm,
free sphere radius5mm,mass.0001,inertia/mass[10,10,10]mm².
Angles0,±120°,research root radius≈95.15mm, NOT the target50mm body.
Tendon.001,pressure.001,μ.3,normal/tangent stiffness.001 are inherited
research parameters, not measured PET/contact/manufacturing values.
FrameLayer planar guides are explicit; fingers are not unconstrained spatial
3D solids. Object has6DOF and no hidden projective constraints.

After stabilization, external Tz=5e-6F·mm. All root and planar-guide reaction
forces/torques are included about the sphere COM. Free residuals are separate.
Old Beam live Y internal-moment defect−2.26294389207e-5F·mm reproduced first.
New exact energy-derived beam satisfies internal moment identity at kernel
precision, and the complete scene passes normalized global moment3.07426228029e-6
and global force1.94189324993e-5, each below unchanged1e-3. No correction torque
was added; cable/layer/contact laws and physical load were retained.

Measured displacement4.46304267860e-6mm, max orientation.000244127244289rad,
load-induced rotation.000208133804648rad; object force residual3.19275e-8,
moment6.98311e-9,speed3.27342e-11,angular speed1.11919e-11.
At24s active contacts0,finger recovery2.09737731583e-8mm and
2.94701041348e-10rad; recovery velocity gate passes. Local/global/limit/drift/
dissipation subchecks all pass; status deliberately stays EXPERIMENTAL.

Prototype repeat and v2 same-condition actual result are identical; source
mapping caveat is documented in BEAM02/06. Initial observer-before-forcefield
initialization produced an ERROR and FAIL; inserting the new beam before
observers fixes order without changing physical conditions. Original FAIL kept.

New twelve-direction full qualification is NOT RUN because contact/history
convergence and coupled energy gates have not passed. Old12directions are not
reused as certification of this new beam or scene.
