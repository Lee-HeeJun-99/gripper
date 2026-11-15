# Birth validation 14 FULL VALIDATION

Status: Mixed PASS/FAIL/BLOCKED; NOT full system certification

New campaign: `results/birth_20261115/canonical_v8`; frozen build `build/birth_20261115/v8_clean`. All quantities are research simulation/mathematics, NOT measured PET or hardware data. Earlier v7 results remain separate.

Environment: Ubuntu22.04.5, Linux6.8.0-138-generic, GCC11.4, CMake3.22.1, Python3.10.20. Patched matched SOFA26.06 SDK aliases resolve to the same build, see environment/summary.json.

Birth plugin SHA256 `27b21bb08d0db153c21465b3e3d92e19c62c09b73dc0385fea975f6a895cd0d2`; generated component SHA256 `c23dddd96b5a722427068f7a9a1dfde737de015e38cc3ae5db438053d3fa259b`. Beam SHA256 `52263d3d0a2e8e49a166ec17077c9c58d2d80f46dd51f304b6547681df146b6f`; SDK driver SHA256 `274a9de055d3c3dec07c03ca52866cf66332765500a697715df251ce4a4f875e`.

Clean new plugin build/unit/API/independent math and intentional source/binary/generated/physical-input mismatch guards are separate from full model convergence. Fresh original FREE golden checks run twice across600 frames at1e-10+1e-6|golden|. A direct Python invocation without the documented verification namespace FAILED (existing output directories and absent default build manifest); its log remains canonical_v8/python_final. Re-execution using the existing isolated validation launcher passed84 Python tests plus3 existing C++ executables; after the physical-input guard was added the final suite passed85 tests, logs canonical_v8/validation_unit_birth_guards_final. No failing test was deleted or relaxed. Old45gate is NOT summed with new birth tests. Existing Beam implementation and old models/golden/raw/Studies are unchanged. See final evidence manifest for exact hashes and individual logs.

Post-physics plotting import initially failed because of a missing space in a Python conditional. analysis_restart.json records the incident; analysis_final contains the corrected actual execution logs. No physics case was rerun or its raw results changed to hide that orchestration failure.
