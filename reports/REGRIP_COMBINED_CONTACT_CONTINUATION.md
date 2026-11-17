# Combined event/contact continuation through820 — project incomplete

## Implemented physics,not a plan

New models/film_combined_contact uses the validated coupled reintegrated event
atom,shared perfectly-inelastic impulse and single-row LobattoIIIA remainder.
No position/speed correction is applied. Its old midpoint remainder is still
computed as an unused baseline validator;this redundant real cost is recorded.
Negative reaction,feature transition/release reject;global earliest endpoint-
family CCD and general multirow contact are not certified.

Actual saved C2 PRE-state begins0.97704101562498835s;this is a new local IVP,
not fresh closing from0s. Actual free sphere has six DOFs,isotropic inertia,
R8 physical/R8.01 declared midsurface buffer,mass0.0001 N s²/mm. Sphere normal
rotational Jacobian is physically zero,not an orientation clamp. Single finger
is a rectangular100x24mm research coupon,skin0.05mm,rails0.1mm,E250MPa,nu0,
mass1e-6 N s²/mm,ideal mapped root,Rayleigh mass2,gravity0,Tmax0.001N per rail.
These are research assumptions,not measured PET/TPU or actuator properties.
Buffer0.01mm does not certify clearance of the0.025mm skin half-thickness.

## Measured results

- Actual766/771/772 plus773:39.0625us all-pair0.1% time PASS.
- Actual777/779/780 plus781:125us16/32/64 all-pair PASS.
- Actual policy-instrumented sparse811/812/813 plus817:125us PASS,
  base-quarter velocity0.0210583%,same-window normal force0.0124939%.
  Atom identity is separately checked;regular force is integrated with actual
  Lobatto weights,not obtained by dividing the impact atom by arbitrary dt.
- Actual818 independent state/actual FF/current-J/whole-stage clearance PASS;
  minimum accepted gap -1.2967405e-13mm,minimum whole-stage gap -1.3145041e-13mm.
  Actual819 all accepted triangle kinematics PASS:minimum active normal speed
  -1.2823076e-14mm/s. Neither is a swept CCD proof or contact-area measurement.
- Independent FEM814/815/816:1ms128/256/512 completed in approximately49/99/193s.
  Common physical-time motion820 all-pair PASS;128-to512 velocity0.0359818%.
  Force/work/energy and actual SOFA1ms are NOT certified by this motion test.
- Energy778/783 separately observe skin,rails,attachment,kinetic,tendon,
  damping,normal work and stable impact loss. Signed residual is NOT heat;
  incomplete physical work inventory is NOT a whole-system energy certificate.

## Failed hypothesis and numerical fixes

Strict actual/FEM782 velocity mismatch8.409e-12mm/s FAILED1e-12 criterion.
Clock/compiler factorial tests794/795 and independent accumulated-clock796
identify time0+k*dt versus start+=dt as the cause:2.8866e-15s control-clock
drift. Compiler flags alone do not resolve it. Canonical references now
independently accumulate their own clock;actual observed states are not copied.
782 remains FAIL. Current actual/independent audits meet unchanged thresholds.

Sparse nonsymmetric stage Jacobian factorization removes only EXACT zeros,
without threshold pruning,symmetrization,diagonal shifts or changed equations.
Dense default is preserved. Same-binary802 physical equality PASS:
18.1463s dense versus11.7761s sparse,1.54094x for one125us pair only.
Actual parsed sparseStage0/1 and all nine physical CSVs before/after passive
policy observer810 are byte-exact. Runtime metadata,not just XML,is checked.

## Three-finger independent finding

804/809 implement proper three120degree frames,one shared free body and three
film projected masses,shared impact/momentum/angular/objectivity checks.
R30 sphere/root-centre radius50 geometry is nonintersecting at REST;root skin
extends beyond50mm,so50mm outer palm envelope is NOT established.
R8 negative control of this object-fitted STRAIGHT-mount construction intersects
centre lines at material86.2607mm. This is a genuine design limitation,not a
claim that every R8 ReGrip grasp fails. Actual nonlinear three-finger SOFA,
shared tendon equalizer,self-contact,friction/lift/grasp are NOT implemented.
PNG from804/809 is labelled implemented REST reference,not actual deformation.

## Checkpoint and exact commands

Source baseline5fee2f5 plus this development unit;functional commit is recorded
in Git,each campaign separately archives hashes and dirty-source identities.
Reusable actual runtime-policy build:
build/combined_20261117_combined_policy_dense805/libReGripCombinedContact.so
Both backends share this DLL;do not reuse it after source changes without the
existing runner source/binary guard. Existing installed SDK/libraries unchanged.

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY -m json.tool results/autonomous_film_20261117_combined_sparse_time817/summary.json
$PY -m json.tool results/autonomous_film_20261117_combined_sparse_quarter_audit818/summary.json
$PY -m json.tool results/autonomous_film_20261117_combined_uniform_motion820/summary.json
$PY tools/film_combined_uniform_assess.py --tag UNIQUE_MOTION_AUDIT --cases 20261117_combined_uniform128_814 20261117_combined_uniform256_815 20261117_combined_uniform512_816
```

Next:explicit profiled1ms actual owner scope,then force/energy/common-time
verification. Child forecasts must remain<=480s/4GiB. Do not enlarge integration
iteration caps,remove branch guards or infer full cycle from this local window.
Existing553/657/705/737/782 and Native562 failures/raw remain preserved.
No automatic continuation after the session is promised.
