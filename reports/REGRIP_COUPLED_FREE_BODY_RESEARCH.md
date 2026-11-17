# Coupled custom film/free-sphere research — 2026-11-17

## Latest continuation — measured through647 (earlier sections retained)

Actual SOFA628/629/630 re-integrated the SAME initial film/free sphere on
382/764/1528 accepted physical intervals. These are genuine h/h2/h4 grids,
not output thinning or replay.640 compares all pairs at common physical times:
PASS existing0.1% gate for the **1ms,zero-tension,seeded-impact coupon only**.
Base-to-quarter relative attachment error3.78158675e-5 (=0.00378158675%),
film velocity8.15922674e-6,impulse1.30809762e-7,event time4.43993934e-7.
637 independently checks actual SOFA quarter-grid geometry/mapping/instant
momentum. Actual runtime151.387s half/262.564s quarter,within480s/4GiB.
Old full C2 time607 remains FAIL;no full-cycle/time/energy/grasp certification.

New value-only energy evaluator reuses original formulas in a separate generated
namespace/static TU,without changing AD2 forces or Hessians.624:48 states
bit-exact energies;625:controller/accepted-state equivalence.627 independent
actual21 controller139.379s versus619207.918s. However actual SOFA636 took
268.266s versus620259.218s.646:all five physical CSVs EXACT but observed
runtime ratio0.9663;**actual speed improvement REJECTED**. It remains opt-in
experimental,not the production default. Do not use the scalar-energy-only
342.7x ratio as total physics speedup.

634 independent shared-mass counterexample proves that an endpoint constrained
midpoint step can have exact positions and momentum but wrong newborn-impact
velocity depending on event phase.635 falsifies this as the sole explanation
of measured C2 normal work:all nonzero signed work was from already-touching
rows,not initially separated rows.605/606 measured discrete normal work is
-5.1982121e-9/-2.6668368e-9 force*mm;not friction heat or a full energy residual.

639 independent prescribed rotating/sliding segment uses actual ClosestPrimitive:
gap stays within4.44e-16mm but endpoint-J work is -0.0159988/-0.00799985/
-0.00399998/-0.001999998 for20/40/80/160 intervals. Midtime-J work is below
7.2e-17. This isolates a persistent-contact quadrature bias;it is NOT a free
dynamics solution.638 missing archived transitive header failed compilation
and is preserved;639 includes it and passes.

An explicitly opt-in `midpointContact` experiment now keeps endpoint gap
closure but evaluates regular contact-force gradients at arithmetic midpoint
positions of BOTH film and sphere. Its true mechanical tangent uses h/2 Hmid,
while endpoint constraint derivative remains h Jend. The Schur system is
generally nonsymmetric;no fake symmetrization/regularization is applied.
641 independent chain-rule FD2.02406e-12,regular force residual4.73275e-20.
642 actual precontact profile and644 loaded-touch execution pass their limited
scope.647 confirms the DEFAULT endpoint implementation still produces all
five physical CSVs byte-identically to596.643 C2 actual comparison was launched;
inspect its completion record before claiming results. No default replacement
or energy certificate follows from these preliminary experiments.

Units are mm,s and assumed N:mass1e-6 corresponds1g and body.0001 to100g.
These are research assumptions,not measurements. The8.01mm midsurface buffer
is not a certified shell-thickness clearance model. The rectangular single
coupon is not the final tapered cartridge or50mm-palm three-finger assembly.

Project incomplete. This is actual implementation/evidence,not a final grasp
or energy certificate. Starting HEAD69bdc1e;functional commitsc5a42d7,
9c17c56,48c5b14. The original fixed-body owner,Native law,SDK,Golden,Raw,
SQLite and old FAIL results are preserved. No remote push.

## Model and shared state

New `models/film_coupled_contact/` uses actual root Vec3 displacement,
actual FilmRailTendon and actual free Rigid3 mass through public SDK APIs.
The actual film quarter-root map B and all nodal masses are retained.

```
y = [film reduced velocity,body linear velocity,body angular velocity]
M = diag(B^T Mfilm B,m I3,Ibody I3)
g = distance(closest triangle point,body center) - buffered sphere radius
J = [film gap gradient B,-normal^T,-(r cross normal)^T]
```

For the implemented frictionless SPHERE,r is radial and r cross normal=0
exactly. This is not a frozen rotational DOF or a generic Box/Cylinder
Jacobian. The actual isotropic body's quaternion and angular velocity are
integrated;anisotropic inertia/general torque/other shapes are unsupported.
There is no tangential friction law in this component. Research values:
100mm rectangular skin/two flexible rails,explicit quarter-root fixture,
radius8mm plus.01mm midsurface buffer,body mass.0001 and inertia/mass25.6,
mass damping2,gravity0. These are NOT measured PET/TPU or actuator data.
The existing research coupon is not the fully qualified final50mm-palm
three-finger assembly or exact tapered cartridge geometry.

## Time integration and events

The sole `CoupledSphereODE` calls existing film mechanics,common C2 profile,
whole-surface numerical-path birth search and many-row plastic impulse.
Moving sphere centers and film positions use the SAME quadratic midpoint
numerical path in relative coordinates. It is not an exact continuous FEM
trajectory or merely interpolation of saved frames. All triangles and all
closest vertex/edge/face features are searched by the reused bounded kernel.

At a root,the shared mass/J computes both velocities at the same time.
Positions/quaternion do not jump. Impact work is stable impulse work;
momentum-energy defect and subtraction residual remain separate,not heat.
On a smooth unique entering branch,the coupled incoming-velocity event IFT
is checked by FD;594 error2.20643e-10. Indistinguishable independent-feature
branches do not acquire a fabricated unique derivative. This is not yet a
complete endpoint impulse/solver sensitivity qualification.

Sustained contact uses y_mid,q1=q0+h*y_mid,v1=2*y_mid-v0,physical impulse2λ.
Both bodies enter the same nonlinear endpoint gap and Hessian. The true
tangent includes the center/film cross blocks;negative tangents are rejected,
not regularized. All triangles are checked after each accepted solve and
missing rows trigger a new solve. The existing1e-10 gap gate is unchanged.
A separate shared mass-metric velocity projection has an explicitly
numerical inventory;it is not physical Coulomb heat. Release under outward
velocity is unconstrained. Re-impact was actually observed in606.
Initial inward contact inside the event tolerance still requires explicit
zero-time treatment and is rejected rather than silently clamped.

This is one-step midpoint/event integration,NOT BDF2 smooth resumption.
Whole endpoint clearance does not prove continuously nonpenetrating
sustained paths between endpoints. Full sustained swept certification,
moving-normal friction,self-collision and full-cycle time remain open.

## Actual experiments and failures

|Campaign|Source of numbers|Measured result and scope|
|---|---|---|
|567/568|independent math|FAIL coverage:loaded fixture's displacement stayed below1e-10 gap threshold;also separate stage momentum from subsequent projection|
|569/578|independent math|moving sphere/return/release,relative geometry FD gradient1.035e-10,Hessian1.810e-11;loaded stage momentum5.878e-20|
|570/571|actual SOFA|20steps/1ms,first event.000333908496748s,all accepted triangle gaps positive|
|573|independent check of actual SOFA|state/FF/triangle gap audit PASS;instant momentum3.309e-24,angular balance9.359e-23|
|574|prelaunch policy|BLOCKED,not OS exhaustion:400step forecast555.85s exceeds480s;no physics launched|
|577/583|actual SOFA/byte audit|whole-triangle checks avoid unnecessary global Hessian construction;5physical CSVs exact;14.133->6.259s,one measured2.258x contrast|
|579|actual SOFA time comparison|10/20/40steps FAIL:base-quarter attachment1.240267%;motion alone is not time qualification|
|581/582|actual SOFA|unloaded touching and physical outward release execute with whole-surface gap gate|
|584/589|actual SOFA/independent audit|original C2,400steps/1s,first impact.977041433916s;min gap-1.02123e-11;body motion.000127618mm;runtime140.106s|
|585/590|actual SOFA/independent audit|external body force+.01,20steps/1ms sustained contact;min gap≈-8.88e-15|
|586–588/592|actual SOFA|1000x stricter Newton residual contrast does not fix attachment error:base-quarter1.240267%;hypothesis rejected for this coupon|
|594|independent math|shared event IFT FD2.20643e-10;exact accepted cache,5versus8stage evaluations|
|595|independent actual-state body balance|regular momentum1.360e-18,kinematic1.635e-15,body-only work identity1.088e-22;NOT whole energy|
|596/599/603/604|actual SOFA/independent impulse oracle|heavy/light sphere actual shared impulse;body postvz-.000232975/-.403074599;oracle velocity errors5.42e-20/1.11e-16|
|600/601/602|actual SOFA,same binary,serial|exact5physical CSVs;C2 cost5.378->4.612s,1.166x measured contrast,not statistical benchmark|
|605/606/607|actual SOFA|same-binary C2 400/800steps both finish with gap gate;time FAIL and events1versus2|
|608|independent actual-state audit|800step min gap-5.12710e-11;actual FF/owner geometry,energy and C2 end tension agree|
|611|selected regression|10groups PASS;not a whole-system/grasp certificate|

The shared impulse603/604 has3duplicate rows but rank1;individual row impulses
are nonunique. The independent small active-subset oracle is test-only,not
the production solver. Sustained actual C2 rows at steps391onward include
two independent rows(rank2),not merely duplicate row counts. Event rows,
regular step impulses and projection impulses have separate owner/stage IDs.

Native562 remains FAIL at-2.18154673259e-5mm. It is a separate BE/Native law,
not overwritten or relabeled by the custom midpoint/event result. The same
original C2 inputs are used,but different numerical/contact laws must not be
described as an identical-physics performance superiority comparison.

### Full original C2 time607 — FAIL

At common physical times400->800:film displacement.0402208%,velocity6.47312%,
body velocity4.20029%,body displacement.408592%,shell.232335%,attachment
2.45691%,film kinetic.121959%,body translational kinetic7.14873%.
One impact versus two means the event sequence is not converged.
0.1% gate unchanged. Base-quarter and full16s cycle are NOT RUN for this
component. No400/800 adjacent-only approval is issued.

## Energy inventory,not global certification

Measured:film shell and attachment storage,film/body kinetic,stable event
loss,momentum defect,projection inventory,tendon end-state tension and legacy
FF work,body-only smooth work identity. Missing synchronized film damping,
full nodal fixture work,consistent internal-substep tendon work and nonlinear
whole-step angular energy identities remain unmeasured/BLOCKED. Missing terms
are not assigned0;unexplained residuals are not added as heat. Pressure/vacuum
work,friction,3finger lift/hold and grasp Optuna are not qualified.

## Adaptive investigation — separate EXPERIMENTAL branch

`models/film_coupled_adaptive/` is not the qualified SOFA owner.609/610
instantaneous relative-energy step doubling FAILS its explicit depth12
budget,not OS limits. At t0,attachment energy decreases≈h^6 but its local
relative discrepancy approaches43.75%. Analytic independent jerk example:
q'''=j gives midpoint q_full=j*h^3/4 and two-half q_fine=3*j*h^3/16.
Thus U_fine/U_full=9/16 even as h->0. Merely shrinking h cannot satisfy
that local relative criterion at the shrinking observation time.
No small-energy threshold or relaxed physical gate is introduced.

An explicit opt-in fixed macro-horizon error budget is under test;raw
instantaneous relative errors remain recorded,not marked PASS.612 is a
preserved const-pointer initializer compile failure;613 tests its correction.
This controller is NOT global.1% qualification and is NOT yet actual SOFA.

## Reusable builds,actual images and restart

Main latest shared owner binary:
`build/coupled_sofa_20261117_coupled_cache_actual596/libReGripCoupledSphere.so`.
Exact archived sources and binary guards are mandatory on reuse. Earlier
577/584 are preserved versions. Source changes require fresh build paths.

Actual raw lives under`results/autonomous_film_<campaign name>/`.
Original C2 base/half:20261117_coupled_c2_base605 and
20261117_coupled_c2_half606. Actual scale1 PNG/OBJ:coupled_c2_audit589 and
coupled_c2_half_audit608. Sphere centers are saved at the same time as film
states;silhouettes are not computed contact area/pressure maps.

```
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
git status --short
$PY -m json.tool results/autonomous_film_20261117_coupled_c2_time607/summary.json
$PY -m json.tool results/autonomous_film_20261117_coupled_adaptive_trace610/summary.json
# After model changes:choose a NEW tag,do not overwrite earlier evidence.
$PY tools/film_coupled_sphere_reference.py --tag NEW_COUPLED_MATH
$PY tools/film_coupled_adaptive_reference.py --tag NEW_ADAPTIVE --horizon --trace
$PY tools/film_coupled_sofa.py --tag NEW_COUPLED_API
```

The historical`tools/film_coupled_reference.py` was initially overwritten
by an unfortunately reused tool name in c5a42d7.9c17c56 restores it byte-for-
byte and gives the new reference the unique name above. All actual archived
567–594 runners retain their exact launch bytes;Git history is not rewritten.

Next:finish/falsify adaptive horizon experiment,then actual bounded SOFA
integration if independently valid. Do not skip zero-time/recontact/gap
uncertainty analysis.3finger/shared equalizer,Box/Cylinder,friction,self-contact,
12wrench and final design comparison remain NOT RUN/BLOCKED,not successful.
