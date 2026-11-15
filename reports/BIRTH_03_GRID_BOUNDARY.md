# Birth validation 03 GRID BOUNDARY

Status: PASS unit scope; history convergence not implied

New campaign: `results/birth_20261115/canonical_v8`; frozen build `build/birth_20261115/v8_clean`. All quantities are research simulation/mathematics, NOT measured PET or hardware data. Earlier v7 results remain separate.

Environment: Ubuntu22.04.5, Linux6.8.0-138-generic, GCC11.4, CMake3.22.1, Python3.10.20. Patched matched SOFA26.06 SDK aliases resolve to the same build, see environment/summary.json.

Birth plugin SHA256 `27b21bb08d0db153c21465b3e3d92e19c62c09b73dc0385fea975f6a895cd0d2`; generated component SHA256 `c23dddd96b5a722427068f7a9a1dfde737de015e38cc3ae5db438053d3fa259b`. Beam SHA256 `52263d3d0a2e8e49a166ec17077c9c58d2d80f46dd51f304b6547681df146b6f`; SDK driver SHA256 `274a9de055d3c3dec07c03ca52866cf66332765500a697715df251ce4a4f875e`.

Collapsed clipped intervals return the mathematically defined zero-capacity contact-boundary limit rather than dividing by u-l or replacing that denominator by epsilon. Exact and adjacent grid boundary cases, inactive state, recontact and finite derivatives are tested.

A second discrete-grid defect was found: nominal 10-mm edges were 9.99999999999999..10.000000000000014 mm. Strict ceil generated 1000 or1001 cells at .01 mm depending on rigid-frame roundoff. The new component canonicalizes a ratio only within32 machine epsilon times its scale of an integer; truly noninteger lengths retain ceil. 100 rigid coordinate transformations and a noninteger counterexample pass. This numerical-ID correction is NOT a relaxation of the1% history gate. New canonical-v8 results remain distinct from v7.
