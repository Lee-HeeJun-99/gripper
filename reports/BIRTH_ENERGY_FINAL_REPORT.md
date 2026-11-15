# Contact birth and energy — measured development report

Baseline `651a02ed24a11a9fce00fe3b437f188ded27266e`; branch `development/regrip-contact-birth-energy-validation`.
Publication-parent commit `96d0b648392cb3efbcc53029bf7e29aa5933d701`; the documentation commit is obtained with `git log -1` (no self-referential hash). No push performed.

New campaign: `results/birth_20261115/canonical_v8`; frozen build `build/birth_20261115/v8_clean`. All quantities are research simulation/mathematics, NOT measured PET or hardware data. Earlier v7 results remain separate.

Environment: Ubuntu22.04.5, Linux6.8.0-138-generic, GCC11.4, CMake3.22.1, Python3.10.20. Patched matched SOFA26.06 SDK aliases resolve to the same build, see environment/summary.json.

Birth plugin SHA256 `27b21bb08d0db153c21465b3e3d92e19c62c09b73dc0385fea975f6a895cd0d2`; generated component SHA256 `c23dddd96b5a722427068f7a9a1dfde737de015e38cc3ae5db438053d3fa259b`. Beam SHA256 `52263d3d0a2e8e49a166ec17077c9c58d2d80f46dd51f304b6547681df146b6f`; SDK driver SHA256 `274a9de055d3c3dec07c03ca52866cf66332765500a697715df251ce4a4f875e`.


## Outcome

Independent birth/IFT/Jacobian and actual SOFA API integration PASS in tested scopes. Missing post-birth extension is restored. Exact-grid degeneracy and rigid-frame-dependent cell counts are handled without denominator regularization. Existing kernels/golden/Studies are preserved. Full history/space/time/energy approval is NOT inferred from kernel tests.

## Changed implementation

- Independent `models/contact_birth/`: birth law/root/commit/grid/journal/CMake/plugin (old prototype BirthIncrement.h preserved).
- `tests/test_birth.cpp`, event math and source/binary/physics guard tests.
- `tools/birth_*`: isolated build/trial/finite campaign, diagnostics, replay and evidence verification.
- `models/structural_interface/refined.py` and structure Study/candidate tools: entire-interface objective, separate from grasp.
- New BIRTH reports/small JSON/CSV/figures; append-only guidance in README/AGENTS/PROGRESS/VALIDATION.

Full repository path inventory: `reports/birth_evidence/changed_files.json`. No old physics/golden/raw/SQLite was replaced; build/raw/env remain ignored.

The following statuses concern the historical **motion** diagnostic only; they do NOT certify convergence of dissipated energy or the full history field. Additional same-stage force/energy/loss comparisons are in convergence.json.

| Diagnostic | Status | Translation relative | Rotation relative | Limit |
|---|---|---:|---:|---:|
| history_half | FAIL | 0.044867291263203386 | 0.00029208941669281067 | 0.01 |
| history_quarter | PASS | 0.005620263674684299 | 2.0156294037670122e-05 | 0.01 |
| mesh11_21 | FAIL | 0.0451804556338499 | 0.0006299587911428888 | 0.01 |
| mesh21_41 | FAIL | 0.030431999790751008 | 0.00031555686127082103 | 0.01 |
| normal8_16 | PASS | 9.1857516413475e-09 | 1.1624745523376298e-12 | 0.01 |
| normal16_32 | PASS | 1.6739813609831256e-08 | 1.585685523299437e-12 | 0.01 |
| tangent2_4 | PASS | 1.8420866679520817e-08 | 1.8333117107039296e-13 | 0.01 |
| time_half | PASS | 0.000995319356396089 | 7.019311872066688e-05 | 0.001 |
| time_quarter | PASS | 0.0004963598535400475 | 3.5171097994397806e-05 | 0.001 |
| repeat | PASS | 0.0 | 0.0 | 1e-06 |
| history_eighth | PASS | 0.00032477184901438165 | 9.820094429377025e-06 | 0.01 |

| History friction-loss comparison | Status | Relative difference | Limit |
|---|---|---:|---:|
| history_half | FAIL | 0.7451331600926177 | 0.01 |
| history_quarter | FAIL | 0.26305867031822355 | 0.01 |
| history_eighth | FAIL | 0.08716021296353499 | 0.01 |


Full coupled energy, qualified12-wrench grasp and100-mm grasp Optuna remain BLOCKED. Native/other-shape full grasp and GUI are NOT RUN in this campaign. See BIRTH01..14 for measured scopes and limitations. Earlier failed prototypes and v7 diagnostics are retained, not replaced by v8 results.

## Independent optimization

New24-COMPLETE independent linear-structure Optuna study has two Pareto candidates. Actual SOFA approves only candidate3 in its tested structural scope (ratio1.6748830397189032); candidate23 FAILS mesh maximum slip. This is not actual grasp optimization or hardware performance.

## Reproduction

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/birth_assess.py
$PY tools/birth_verify.py --raw
mkdir -p results/birth_recheck_01
REGRIP_CLOSURE_OUT=results/birth_recheck_01 $PY tools/closure_validation_suite.py unit --suffix _isolated
REGRIP_CLOSURE_OUT=results/birth_recheck_01 $PY tools/closure_validation_suite.py golden --suffix _isolated
```

Choose a fresh recheck name on repeated invocations; the launcher refuses overwrite. Do NOT run the historical Python suite without its isolated environment. New experiments require NEW OUT/build paths; see NEXT_TASKS. Per-case command/config/identity/stdout/stderr/state/metrics/resource samples are under campaign/grasp. Compiled source/binary/generated hashes are in build_manifest and this manifest. Reports distinguish actual SOFA, independent FEM, independent math and assumptions; there are no new material measurements.
