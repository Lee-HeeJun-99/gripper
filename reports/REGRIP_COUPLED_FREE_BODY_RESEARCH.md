# Coupled custom film/free-sphere research — 2026-11-17

## Actual higher-order persistent contact — through763

See models/film_coupled_collocation/README.md for complete stage equations and
true nonsymmetric Newton tangent. RadauIIA3 and LobattoIIIA4 are separate schemes
using exactly the same shared mass/material/C2/damping/current geometry. Initial
Lobatto force is acceleration-compatible;unknown stages constrain relative normal
velocity. Stage forces are nonnegative,endpoint positions are never projected.
Release,feature change,singular stage tangent or whole endpoint gap violation
reject. This is ONE persistent branch,not a general active-set/impact law.

Independent740:linear Radau errors(4/8/16 steps)1.15208e-7,1.40084e-8,1.72595e-9;
Lobatto2.47840e-9,1.55008e-10,9.68972e-12. These are independent analytic test
errors,not actual SOFA deflections. Changing-normal full-stage FD also passes.
741/751 actual-state nonlinear FEM separately checks explicit-coordinate versus
shared-System adapter without changing physical mass or force. Default Radau
regression752 reproduces726/727 numerical results after adding Lobatto.

Actual742/743/744 uses1/2/4 steps over9.765625us;all-pair0.1% time747 PASS.
Actual753/754/755 extends SAME initial post-impact state to39.0625us over4/8/16
steps.757 all-pair0.1% PASS:base-quarter velocity0.016544006%,common-window normal
force0.050996245%,attachment0.000003428059%,endpoint-trapezoid tendon work
0.000748632%. This is not whole energy closure. It contains no new birth or
release;705/657 earlier/full-window time FAILs remain unchanged.

Actual/independent748/756/758:position exact,velocity<=7.11e-15mm/s,end force
exact. Actual owned stage pullback/force/impulse/time749/759/763 PASS;48 rows in
the16-step case. Whole accepted triangle/FF audit762 PASS,min buffered gap about
-3.38e-14mm. Audit762 records absent impact momentum values NULL,not invented0.
No stage impulses are divided by an arbitrary dt and claimed as atomic force.
Default stage-clock interface729/735 preserves five physical CSVs to596 exactly.

Actual geometry/observable PNG and OBJ:.../coupled_lobatto_long_audit762/ under
results/autonomous_film_20261117_ (join prefix);scale1,no pose manipulation.
Actual short-coupon time comparison plot:.../coupled_collocation_plot761/
actual_collocation_time.png and.svg. Concept and nonlinear actual-state labels
remain explicit. All experiment identities include compiled sources/binaries/
Installed SDK/actual XML/process records;old Raw and SDK stay unchanged.

Reusable NEW long-window module:
build/coupled_restart_20261117_coupled_lobatto_long753/libReGripCoupledRadau.so.
Radau728 and Lobatto742 are older immutable builds;source guards must reject
reusing them with changed live owner headers. Long753 uses an explicit qualified
maximumDuration,default10us remains for the standalone component.

Next actual integration must combine ReintegratedBirth with Lobatto persistent
stages,including fractional remainder and stage journals. Current isolated owner
does NOT execute Closing from rest or own Contact Release/Re-impact. Then extend
time/geometry tests before3finger/free grasp. No valid reason exists to call the
whole project complete from747/757. No OS exhaustion/automatic restart claim.

## Latest implementation — reintegrated impact and persistent collocation

Functional event implementation committed0d36cbe. All historical failures/raw
remain. Project NOT COMPLETE;no full grasp,energy or material certification.

### Coupled solve-to-event (independent mathematics + actual SOFA)

ReintegratedBirth.h solves the SAME coupled implicit midpoint equations to each
trial event time,using original C2 control including its time derivative. Root
and state IFT are defined only for the isolated smooth unique-row branch.
Ambiguous branches,transient endpoint-clear events,feature mismatch and physical
nonapproaching velocity reject explicitly. No denominator regularization or
artificial speed/pose correction. Dense surface CCD supplies a candidate only:
globally earliest root of the nonlinear endpoint family is NOT certified.

Independent695/696/714 PASS (root IFT error9.76e-11,velocity IFT3.48e-7 in the
specified FD experiment;parent-bracket velocity spread2.28e-10mm/s). Actual
SOFA697–704/715 bounded execution and whole-endpoint clearance PASS. Actual715
uses the latest approaching-velocity guard;718 preserves five physical CSVs
exactly to697;default706/707 remains exact. Independent actual M/J impulse699
and whole accepted surface/FF/mapping audit719 PASS their limited scopes.

Actual64/128/256 grids702/703/704 span the SAME625us C2 initial-value window.
705 all-pair time FAIL:base-quarter film velocity0.171685%,same-window regular
force1.486946%. Attachment0.00124556% alone passes. First impact time,impulse,
loss and pre-normal velocity are identical across grids. No full-cycle claim.

Controlled708/709 uses the SAME binary,physical parameters and initial state,
changing only event evaluation policy. Independent actual-substate diagnostic
710/711/713 measures partial midpoint momentum-equation residual:
7.333215587e-12 versus2.337695976e-20 N s (force-equivalent1.33628e-5 versus
4.25983e-14N). This confirms consistency of the NEW partial-step method;the old
dense extension was not designed to solve that partial endpoint equation. It
does NOT invalidate the old instantaneous impulse balance or certify global
energy. New method26.897s versus21.284s is slower,not a runtime optimization.
717 recompiles actual archived headers and reproduces711 despite live changes.

### Persistent modal hypothesis (independent FEM,not nonlinear SOFA)

716/720/721 freeze the actual post-impact geometry,force,tangent and one normal
row. Elimination gives M_eff=M_f+m_body*j_f^T*j_f,not the old free-film mass.
All649 film modes are retained. Five free rigid tangential/spin coordinates
are uncoupled from the frozen normal row,not artificially constrained. Full
shared KKT acceleration agrees3.23e-15 relative;modal reconstruction6.09e-15.
Largest angular frequency634807.29/s. Constant tangent/force/normal,bilateral
branch is an explicit limitation;it is NOT continuous nonlinear contact.

Against independent modal matrix exponentials over625us at64 steps,normal
reaction errors:midpoint1.15444%,Gauss2 0.0302485%,Radau2 0.223265%. At128
steps Radau2 is0.0369651%. These support stage integration research,not direct
transfer of a PASS to actual SOFA. Figure:results/autonomous_film_20261117_
coupled_contact_kkt721/frozen_methods.png (join the wrapped path).

### Nonlinear persistent collocation (new experimental work)

SingleRowRadau.h implements the two coupled stage equations with actual M,
U gradient/Hessian,current J/H_g,damping and common C2 control. Stage normal
velocity is constrained,endpoint position is NOT projected. Negative stage
reaction,initial release,feature transition or whole endpoint gap violation
reject. All stage force/time/impulse ownership is explicit. This is one
persistent branch,NOT production active-set contact/impact/release.

722–724 unit-mass curved test FAIL at2.889e-17 N s residual floor;threshold
1e-17 is NOT relaxed. Separate1e-6 N s²/mm research-mass problem725 passes
curved-normal tangent FD and linear analytic third-order refinement. These
different physical test scales are NOT the same failed trial relabeled PASS.
726/727 independently integrate actual post-impact state on1/2/4substeps over
9.765625us and verify the shared adapter against explicit coordinate assembly.

Actual SOFA728/730/731 implements that SAME Radau adapter and original free
Rigid3 mass/initial state.732/738 compares q/v/end reaction to independent727:
position exact,velocity at most3.55e-15mm/s,end force exact.733/739 independently
checks stage impulse/time/J/linear-angular pullback;736 checks actual FF and
whole endpoint gap. Default729/735 preserves five original physical CSVs.

737 all-pair time still FAILS:base-quarter same-window force0.245223%;velocity
0.00848108%,attachment0.0000117105% pass in THIS9.765625us window only. No
impact occurs inside this already-touching coupon. This is not a replacement
for625us705 or full C2 failure. Fourth-order stiffly-accurate LobattoIIIA is
being tested as a separate integration method,not a physical stiffness change.

### Units,scope and evidence

CLI --force-residual is historical naming:the underlying Newton gradient G
has N s units,with force equivalent2*norm(G)/h in N. Initial research mass,
modulus,frictionless sphere,zero gravity,root fixture and1mN-per-rail C2 remain
unchanged. R8.01 is a midsurface buffer,not certified physical shell clearance.
No measured PET/TPU,actuator,lift,holding force or3finger performance is claimed.
694 preserves Eigen test lazy-expression failure;712 parser failure and734
operator wrong-input-path failure are preserved separately from physics FAIL.

Reproduction:each immutable case stores runner.py,source archive,scene,input,
process logs,binary hashes and summary. Reusable actual persistent library:
build/coupled_restart_20261117_coupled_radau_sofa728/libReGripCoupledRadau.so;
reuse ONLY with archived source identities,not changed live collocation headers.
Remaining:global earliest endpoint-family event,multicontact/release collocation,
full C2/time/energy/mesh,friction/self-contact,3finger/free grasp/12wrench/Optuna.

## Latest continuation — measured through692 (earlier sections retained)

### Precise remaining blocker;do not certify adaptive C2

679 pinpoints strict Newton rejection in a FREE stage (owned=0):h.00015625,
residual2.302681e-18 versus threshold1.921390e-18. An explicitly experimental
absolute residual1e-17 (still100x tighter than original1e-15) avoids that
particular rejection but680/683 still fail the adaptive depth12 criterion.
It is not a solution of the dominant event defect. No physical Gate relaxed.

683 shows the limiting event-bearing interval had zero regular rows and
buffered gap-1.10134e-13mm. Reusing1e-10 validation tolerance as internal row
activation/stopping threshold hides this tiny reaction and defers it to a
velocity projection. New independent `AccurateDual.h` and opt-in numerical
solve gap1e-14 distinguish solve accuracy from unchanged1e-10 validation.
686 scalar LCP/geometry/FD tests PASS.685 produces one true regular row and
zero projection loss at that interval,but velocity error remains unchanged:
this is NOT the sole adaptive/time failure. Original Native dual and custom
default are preserved.689/690 actual default regression:five physical CSVs
byte-identical to596.691 default adaptive mathematical regression PASS.

687 experimental event/smooth defect allocation retains TOTAL1e-4 local
budget,half distributed over smooth time and half over at most16 discrete
event intervals.688 proves the bookkeeping inequality,not nonlinear stability.
This gets beyond the first event but FAILS later:tiny numerical projection
inventory (about1e-23) drives the unchanged criterion past depth12. No term is
set to zero or relabeled as heat;no global time PASS follows. This option is
independent experimental research,NOT wired as a qualified production owner.
683's `projection_velocity_jumps` diagnostic was mistakenly after-minus-after
and is NOT evidence of zero velocity change;later traces record actual impulse
sums instead. Owned rows/gaps and all physical states in683 remain valid.

692 isolates the event-state defect at h1.52587890625e-7s:

- Coarse/fine event-time difference -5.36300366e-17s.
- Same first triangle124;shared first-J difference1.32031241e-16.
- Pre-impact velocity-vector difference3.45326779e-6mm/s.
- Post-impact difference3.45326776e-6mm/s,essentially unchanged by impact.

Thus this particular limiting velocity defect is already present BEFORE
impact,not created by mass/J/impulse or endpoint contact projection. The
quadratic dense path has internally linear velocity based on the FULL-step
midpoint force. Endpoint midpoint accuracy does not certify that interior
velocity. Next:reintegrate the coupled midpoint equations to a bracketed
event time,with the SAME C2 schedule;reuse the approach of BracketedFilmBirth
but do not mislabel its fixed-body BE formula as coupled C2 midpoint or global
earliest-event proof. Endpoint-family root/IFT and all feature/clearance tests
are required before an actual new owner can be qualified.

No actual adaptive C2 run is approved by failed forecasts671/673/678/680/685/
687/692. Explicit saved-state actual replay659/672 is qualified for its exact
one-step scope only. Whole-cycle time/energy and3finger/free grasp remain
unfinished. There was no OS RAM exhaustion or engine permission failure;
671 was the runner's120s cap,others were numerical/algorithmic rejections.

### Actual C2 and post-impact isolation: no overall time PASS

648 completes the800-step C2 midpoint-J run in246.946s.653/657 overall
time FAIL:attachment2.46262769%,film velocity6.48059361%,event count1vs2.
Contact work654 is -5.36279e-15/-2.51319e-15,so removing endpoint normal-work
bias did NOT solve the dominant time failure. Midpoint-J is not adopted as
the final contact method.651/655 independently reconstruct every used row's
closest barycentric point,normal,root-map gradient and opposite body impulse:
max unit angular error1.47e-14;not a whole-step global energy certificate.

657 isolates first-impact time9.64436e-7 relative,impulse1.82233e-5,
impact loss3.30907e-5:all within0.1%. Preimpact390 common samples PASS.
Persistent response/recontact,not just first-event accuracy,requires work.

New explicit stateless `CoupledRestartODE` preserves actual initial q/v,body
pose/velocities and physical C2 clock via public Context.659 restores the
original preimpact step and reproduces ALL ten state/energy fields exactly.
672 repeats exact reproduction from the finer663 trace.658 event-remainder
bitwise comparison FAIL remains:velocity error4.33431e-12 after reconstructing
fractional h by subtracting stored absolute times. Do NOT use658 as an exact
resume certificate;the qualified pre-step route avoids that lost-bit h.

661/662/663 re-integrate SAME659 pre-step initial state for2.5ms with128/256/
512 steps (29.47/57.20/113.13s).665/677 time FAIL despite energy improvement:
base-quarter attachment0.01997735%,film velocity0.59818474%,common-window
regular body force3.11010999%,tendon quadrature work0.02482305%.
Half-quarter velocity0.35800324% remains FAIL. This is an isolated declared
initial-value experiment,not a new full1s trajectory or a warm-start shortcut
to certify original400-step physics.

The newly added step-average force diagnostic initially compared coarse
impulse/dt with only the LAST fine impulse/dt:unequal averaging windows.
677 corrects this observation bug by summing fine impulses over identical
coarse physical windows. The previous mismatched-window error is retained
as NOT COMPARABLE diagnostic;the0.1% Gate is unchanged and overall still FAIL.
No instantaneous impact force is invented from impulse/dt.

666/667 reuse the old frozen FEM modal diagnostic with ACTUAL coupled event
state and the existing C2 function. No negative modes;max omega634807.294/s.
Free-film spectrum is NOT a constrained film/body spectrum. Signed modal
amplitudes and full-nodal Gram allow the same velocity norm as actual traces.
669 oscillator local-order/energy/ballistic tests PASS;668 import failure is
preserved.675 independent exact frozen modal response at9.765625e-6s has
velocity error2.08502%(midpoint),0.03301%(Gauss2),0.39983%(Radau2). This
supports higher-order phase-resolution research,NOT an actual SOFA higher-
order contact implementation or convergence PASS. Numerical Radau damping
is not reclassified as heat.670 earlier source-hash list omitted the Gram;
675 includes its exact bytes;old670 is not edited.

671 adaptive four-macro C2 pilot timed out at its own120s cap,not OS resource
exhaustion.673/676 single collision-macro diagnosis fails fixed depth12:
controller1.35372906e-4>1e-4 at h1.52587891e-7s.676 component trace identifies
VELOCITY error as dominant;body-center difference is0 there. World-position
cancellation hypothesis is therefore rejected for this failure;no compensated
pose or ignored energy was introduced.678 tighter Newton experiment fails
line search,not memory/trial exhaustion.679 adds passive rejection diagnostics
to resolve the solver precision floor before further changes. There is NO
actual adaptive C2 PASS from these failed independent forecasts.

Actual result visualization664 contains saved C2 states without amplification;
not concept geometry. Full energy/friction/self-contact/3finger/lift/12wrench/
multimaterial/Optuna and final fabrication performance remain unqualified.

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
