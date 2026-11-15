# Birth validation 10 STRUCTURAL OPTIMIZATION

Status: PASS candidate3 structure scope; FAIL candidate23; not grasp

New campaign: `results/birth_20261115/canonical_v8`; frozen build `build/birth_20261115/v8_clean`. All quantities are research simulation/mathematics, NOT measured PET or hardware data. Earlier v7 results remain separate.

Environment: Ubuntu22.04.5, Linux6.8.0-138-generic, GCC11.4, CMake3.22.1, Python3.10.20. Patched matched SOFA26.06 SDK aliases resolve to the same build, see environment/summary.json.

Birth plugin SHA256 `27b21bb08d0db153c21465b3e3d92e19c62c09b73dc0385fea975f6a895cd0d2`; generated component SHA256 `c23dddd96b5a722427068f7a9a1dfde737de015e38cc3ae5db438053d3fa259b`. Beam SHA256 `52263d3d0a2e8e49a166ec17077c9c58d2d80f46dd51f304b6547681df146b6f`; SDK driver SHA256 `274a9de055d3c3dec07c03ca52866cf66332765500a697715df251ce4a4f875e`.

New separate true Optuna study:24 COMPLETE,0failed/pruned,3smoke trials then SQLite reload. Independent100-mm LINEAR FEM objectives are stiffness ratio and maximum across the ENTIRE piecewise-affine interface, refined21/41/81/161 until adjacent tip/slip errors<1%. It does not measure only connectors. Old Studies remain untouched. Separate workflow contracts exercise intentional FAIL/PRUNED with no objective values, seed and SQLite integrity.

Two Pareto candidates were independently run in actual conservative-Beam SOFA: repeat,dt-half,21→41 mesh, physical connector positions held fixed. Candidate3 k=33.20849634084168 at positions10,20,30,40,50,70,80,90mm passes tested structure gates, measured ratio1.6748830397189032. Candidate23 k=17.015359842717366 fails mesh maximum-slip change2.546736848039144%, so is NOT approved. See structure_candidate_decisions.json and all actual raw configurations. This is neither grasp optimization nor a global fabrication optimum.
