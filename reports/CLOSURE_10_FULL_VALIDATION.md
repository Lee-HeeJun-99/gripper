# Whole validation ledger

All status labels refer to stated scope. PASS requires real logs; EXPERIMENTAL is
not certification; expected failing controls are not successful grasp performances.
Full-model physical qualification remains **FAIL/BLOCKED**.

| Scope | New result | Evidence under results/closure_20261115 |
|---|---|---|
|New active contact clean C++ build|PASS|build/closure_20261115/clean;unit final/active log|
|C++ adaptive FD/query/history/invariants|PASS|validation_unit_final/active,invariants|
|Frame transform force/J/energy/history covariance|PASS|validation_unit_final/frame|
|Python full suite73 tests|PASS|validation_unit_final/python_command/stderr.log|
|Old C++ five module executables rerun|PASS|legacy_units/summary.json|
|New kernel ASan/UBSan/LSan|PASS,not instrumented engine|sanitizers/run_unrestricted|
|Matched SDK V109600points×2|PASS original tolerance|validation_golden/summary.json|
|Original Python FREE/shear and XML transient comparison|PASS600points,not equilibrium|python_recovery;python_xml_compare|
|2finger+Fx11convergence checks|PASS|gate.json|
|2finger full12local wrench tests|FAIL ±Tz|wrenches.json;gate.json|
|3finger12local hold/drift/recovery|PASS finite-resolution subgate|threefinger/gate.json|
|3finger spatial/dt/history convergence|FAIL;three timeout results retained|threefinger/gate.json;retry_result.json|
|2finger+Fx whole reaction balance|PASS|balance_audit.json|
|3finger+Tz whole reaction balance|FAIL Beam Y moment|balance_audit;threefinger/field_balance|
|Measured-patch G/cone/capacity LP|PASS analysis;geometry-specific|wrench/;threefinger/wrench/|
|Native box/plane stick/slip/release/recontact|PASS|native_box_min_confirm;native_box_half|
|Native full sphere surface with positive buffer|EXPERIMENTAL local subchecks;buffer sweep PASS|native_audit.json|
|Native mesh/dt/12wrench all-shape contact|NOT RUN|not certified by box-plane calibration|
|Conservative Beam potential|FAIL actual closed-work/curl|energy_audit.json|
|Whole coupled energy|BLOCKED|energy_audit.json|
|Full adaptive mechanics240000steps/2reloads memory|PASS bounded scope|memory_audit.json|
|3finger/native hours-long memory|NOT RUN|not inferred from2finger result|
|100mm Optuna performance study|BLOCKED,new trials0|optimization_guard.json|
|Measured2401-frame replay|PASS headless,not physics|threefinger/replay/result.json|
|Actual PET/vacuum/hardware|NOT RUN|no measured material data invented|

Historical old45physics gates are reused only after unchanged physics sources,
binaries/config/raw integrity checks; they are NOT counted as new contact/closure
gates. Prior8layer quarter-dt PASS and2/4layer research model retain original
source scope; no claim that new three-finger native contact is thereby validated.

Early execution/configuration failures are retained: invalid preload slug,missing
SDK path,inadequate fixed-frame energy control,native topology/normals/pair/solver
failures,ASan shadow and sandboxLSan failures. Fixes have separate output directories.
The native initial classifier's execution-only EXPERIMENTAL is independently
reclassified FAIL for absent reaction (`native_audit.json`), not overwritten.
FD leak classifier correction compares loaded/unloaded phases explicitly.

Production error policy still rejects nonzero exits,timeout,ERROR logs,undefined
behavior,NaN/Inf,incomplete frames and failed physical tests. Old API tests have
only exact expected fault-injection errors; simulation logs have no such exception.
