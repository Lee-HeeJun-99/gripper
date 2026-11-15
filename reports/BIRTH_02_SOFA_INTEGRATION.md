# Birth validation 02 SOFA INTEGRATION

Status: PASS API scope; EXPERIMENTAL full model

New campaign: `results/birth_20261115/canonical_v8`; frozen build `build/birth_20261115/v8_clean`. All quantities are research simulation/mathematics, NOT measured PET or hardware data. Earlier v7 results remain separate.

Environment: Ubuntu22.04.5, Linux6.8.0-138-generic, GCC11.4, CMake3.22.1, Python3.10.20. Patched matched SOFA26.06 SDK aliases resolve to the same build, see environment/summary.json.

Birth plugin SHA256 `27b21bb08d0db153c21465b3e3d92e19c62c09b73dc0385fea975f6a895cd0d2`; generated component SHA256 `c23dddd96b5a722427068f7a9a1dfde737de015e38cc3ae5db438053d3fa259b`. Beam SHA256 `52263d3d0a2e8e49a166ec17077c9c58d2d80f46dd51f304b6547681df146b6f`; SDK driver SHA256 `274a9de055d3c3dec07c03ca52866cf66332765500a697715df251ce4a4f875e`.

Independent `BirthAwareContact` is generated at configure time from the preserved production contact source plus new `BirthLaw.h`, `Crossing.h`, `HistoryCommit.inc`, `Journal.inc`. Old MaterialHistoryContact/Beam/golden/binaries are not replaced. Generated code and all transitive source hashes are checked before every run. Earlier failed v1..v4 prototypes preserve raw/binary/generated-code/hash manifests, but not every historical header snapshot was versioned before subsequent fixes; full clean source reconstruction of each failed prototype is a limitation. Approved current v8_clean sources and successful v7 core are versioned separately.

Actual addForce/addDForce/buildStiffnessMatrix accumulator tests include kFactor 0,2.5,-.25, finite differences, action/reaction and torque. Scalar Commit and AD next-state agree to 2.01e-17; scalar observer wrench versus AD agrees to 5.64e-18. Duplicate AnimateEnd at one time cannot Commit twice. Force/Jacobian/energy/record queries are pure. Pre-step implicit force evaluation still precedes end-state birth Commit: endpoint correction does NOT itself split the ODE event.
