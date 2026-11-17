# Three-film/shared FREE sphere — actual narrow contact,through851

Project NOT COMPLETE. No OS/session exhaustion occurred in these experiments.
Actual contact IVP is implemented,not yet an actuated three-finger grasp.

## Actual and mathematical results

- Independent math833:fixed two-row Lobatto,true stage Jacobian FD,curved normals,
  analytic fourth-order errors6.33439e-9/3.96261e-10/2.47720e-11,rank/release guards.
- Independent nonlinear842:three100mm rectangular Film/Rails coupons,proper
  120degree frames,root-centres50mm,ONE free R30 sphere,1953DOFs,T0,external
  Fz=-.001N,100us,gravity0. Assumed E250MPa/nu0,skin.05mm,rail.1mm;not measured.
  Three contact reactions≈2.21e-8N. One Newton update;momentum residual
  1.70799e-23Ns,normal velocity residual2.28536e-18mm/s;minimum gap-7.10543e-15mm.
  Body displacement z=-4.99957e-8mm. This small motion is NOT visible wrapping.
- Actual SOFA843/844/846/848 executes this shared solve using actual public
  mass/inertia and actual mapped field parameters.848 versus independent842
  maxq2.82594e-20mm,maxv3.47297e-19mm/s. One100us step,not a time certificate.
- Actual stage/field/whole-surface audit851 PASS:world map1.38778e-17mm,
  unit-row action/reaction1.24127e-16,unit-row moment5.08551e-15mm,
  contact point1.67581e-14mm,whole-stage minimum buffer gap-1.42109e-14mm.
  These are kinematic/virtual-work checks,NOT independent full Hessian FD or
  whole-system momentum/energy/work certification.
- Nine actual physical CSVs across the added read-only body-commit guard850
  are byte-exact. Actual846/848 stage vectors are journaled,not end-only.
-844 explicitly registers/checks fixed radius30.01 Data.843 inherited unused
  default8.01 although the hard R30.01 geometry was used;this API inconsistency
  was corrected,not treated as an R8 experiment.847 unsupported8.01 is a
  preserved FAIL. Runtime rejects initialization before any accepted commit;
  guarded-process generic 'nonlinear_failure' label is CONFIGURATION rejection,
  NOT Newton nonconvergence,OS memory depletion or an authorized physics change.

## Failure-driven geometry work

834 +z force releases contact correctly. Different -z1e-6N/1us835 completes
with zero Newton iterations/sub-ULP body motion;not meaningful dynamic success.
Stronger -z.001N/100us836 fails fixed feature ownership. Rescan838/observer839
fail when face115 and edge116 both report double gap0 but their generalized
gradients differ4.25097e-9. Compile827/832 and CLI837 failures are preserved.

The hypothesis 'these MUST be physical independent simultaneous contacts' was
not justified. Observer840 uses EXACT same stored double geometry and independent
Decimal80/120 arithmetic. Gaps resolve to-4.23660179583e-18 and+9.74511387323e-19mm;
precision disagreement<8e-79mm. The ordering,not a fake contact force,is missing.
PreciseDistanceOrder.h compares squared distances at113/334bits,requires the
same ordering,checks all triangle candidates,and rejects unresolved independent
ties.841 checks840 fixture,exact90degree rotation,face/degenerate cases. The
selector changes NO existing double gap,normal,AD force/Hessian or tolerances.
New opt-in842 succeeds. This is numerical-precision evidence,not a formal
arbitrary-geometry interval/CCD proof. True independent ties/more than one
active patch per finger/release still need a production active-set extension.

## Actual implementation and restrictions

SharedFilmSystem.h assembles three material-coordinate film energies and exact
root-map masses,one common body mass,affine world/shared Jacobians/Hessians.
PersistentRows.h extends the existing nonsymmetric Lobatto equations to fixed
independent compressive rows;no regularization,diagonal shift,component clipping
or post-step velocity/position correction. ThreeFilmPersistentODE reads actual
three fields/four masses,checks free body and sole ODE,integrates then commits
all mapped film/body states exactly once. It is an independent component;older
Native/Event owners and installed SDK are unchanged. SDK ldd logs are archived.

This actual owner explicitly supports ONE REST/T0/100us/R30.01 trial only.
No whole-surface event/birth in this three-finger owner,full C2 closing,shared
tendon equalizer,self-collision,friction,lift/hold/release,12wrench or Optuna.
Sphere rotational Jacobian is physically zero;rotation has not been excited or
generically certified,not fixed by a hidden rigid constraint. Radial normals
alone are not six-dimensional force closure. Pressure/contact area unmeasured.
R30.01 is a midsurface buffer,not certified skin.05mm/rail.1mm thickness clearance.
Root-centre50mm extends beyond50mm in physical skin/hardware envelope. Rectangular
coupons are not the tapered equal_volume_v2 manufacturing design.

## Checkpoint/reproduction

Preceding functional commit5a7879e. New functionality is saved by the following
local feature commit;use git log to resolve it,not a fabricated self hash.
Reuse build/three_film_20261117_three_film_commit848/libReGripThreeFilmContact.so
with its immutable source snapshot. Reuse build/combined_20261117_combined_sparse_1ms821/
libReGripCombinedContact.so for the separate combined-event1ms specimen. Current
live source guards may reject reuse after new development;do not bypass them.

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY -m json.tool results/autonomous_film_20261117_combined_1ms_time829/summary.json
$PY -m json.tool results/autonomous_film_20261117_three_film_commit848/summary.json
$PY -m json.tool results/autonomous_film_20261117_three_film_commit_audit851/summary.json
$PY tools/film_three_film_audit.py --tag UNIQUE_ACTUAL_AUDIT --case 20261117_three_film_commit848
$PY tools/film_three_film_persistent.py --tag UNIQUE_INDEPENDENT --precise-ties
$PY tools/film_three_film_sofa.py --tag UNIQUE_ACTUAL --reference UNIQUE_INDEPENDENT
```

Actual scale1 PNG/OBJ:results/autonomous_film_20261117_three_film_commit_audit851/.
They use stored SOFA coordinates and explicit compiled frame transforms. Film
deflection below visualization resolution is clearly labelled,NOT magnified
or called wrapping. Matplotlib3D unavailable;three orthographic views are used.

## Next development,not a completion claim

1. Independent three-film repeated steps at same physical inputs,whole stage
   clearance,common-time force/energy metrics,unchanged0.1% time gate. Profile
   using measured8423.215s/step before increasing duration/count.
2. Only after independent proof,extend actual owner beyond its guarded ONE
   step;common C2 actuation and actual event integration still required.
3. General patch/row activation,release/reimpact and thickness-aware geometry.
4. Friction/self-contact,actual closing/wrapping/lift/hold/release and comparison.
   No final material/actuator measurement/design superiority is claimed.
5. Preserve old failures and generate a NEW byte-evidence manifest after this
   development unit. Old v8 snapshots are not rewritten/live-current certified.

Resource policy remains4GiB/480s/max4 long physics children. No background
automatic restart is promised;reports/checkpoints are for explicit resumption.
