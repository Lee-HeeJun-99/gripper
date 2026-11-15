# Birth validation 04 FULL CONVERGENCE

Status: FAIL / incomplete (see measured table)

New campaign: `results/birth_20261115/canonical_v8`; frozen build `build/birth_20261115/v8_clean`. All quantities are research simulation/mathematics, NOT measured PET or hardware data. Earlier v7 results remain separate.

Environment: Ubuntu22.04.5, Linux6.8.0-138-generic, GCC11.4, CMake3.22.1, Python3.10.20. Patched matched SOFA26.06 SDK aliases resolve to the same build, see environment/summary.json.

Birth plugin SHA256 `27b21bb08d0db153c21465b3e3d92e19c62c09b73dc0385fea975f6a895cd0d2`; generated component SHA256 `c23dddd96b5a722427068f7a9a1dfde737de015e38cc3ae5db438053d3fa259b`. Beam SHA256 `52263d3d0a2e8e49a166ec17077c9c58d2d80f46dd51f304b6547681df146b6f`; SDK driver SHA256 `274a9de055d3c3dec07c03ca52866cf66332765500a697715df251ce4a4f875e`.

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


Individual bounded-hold passes do not approve full grasp. Relative denominators and original limits are unchanged; absolute differences also appear in convergence.json. Every compared pair must have identical compiled identity, unchanged physical inputs and pass its underlying physics checks. A24-s base covers recovery, while18-s refinement runs do not cover final recovery. Same13.9<=t<14 measurements show history.005→.0025 friction-loss difference about26.3%, despite motion passing. A frozen planar analytic field diagnostic independently demonstrates return-map/interpolation noncommutation and energy representation error decreasing with refinement; it does NOT uniquely establish the full dynamic root cause. No artificial compensating dissipation is added.
