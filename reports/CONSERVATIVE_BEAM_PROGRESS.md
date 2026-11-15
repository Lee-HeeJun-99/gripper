# Conservative-beam campaign progress

1. Read latest inherited documents/source; created independent branch from
   b468346. Initial historical2310hash checks passed before intentional metadata
   changes. Original BeamFEM,plugin,golden,old raw/SQLite and branches preserved.
2. Implemented explicit midpoint SO(3) strain energy,exact Taylor AD,spatial
   connection tangent,SOFAForceField registration and API units. Initial C++ alias/
   include errors were corrected; not counted as successful builds.
   Commit4d19774: first mathematical kernel and independent runners.
3. Reproduced actual inherited missing geometric couple to1.563e-17 and full
   old3fingerY defect−2.26294389207e-5. Commit426d58b: live audit/campaign code.
4. Initial3s transient remained FAIL; declared fixed12s/damping2qualification
   reached equilibrium. Initial newBeam observer order ERROR retained and fixed.
   New full3finger+Tz moment balance and24srelease passed. Commitd8e9b8e:
   integration,derived discrete beam energy and diagnostic profiling.
5. Exact AD constant propagation/per-edge cache was independently100state
   bit-identical. Whole profile168.626→150.776s. Frozen binaries/manifests split;
   prototype queued-source snapshot caveat preserved. Commitd24e54b.
6. Completed one profile-justified900s exception at734.780s. Fine21→41mesh
   diagnostic passes,but q/history/dt diagnostics FAIL. No threshold change.
7. Initial8layer standard precision FAIL; translation-only validation preceded
   applying compensated updates exclusively to no-object/no-cable structure.
   Basic,halfdt,21node and18s8layercases now pass equilibrium.
8. New complete scene120000steps/two reloads,memory live plateau and graph lifetime
   passed478.276s.78Python and3+5legacy C++units,clean build,2golden600metric runs
   passed. ASan/LSan initial ptrace failure followed by bounded unrestricted PASS.
9. Independent structural Optuna24COMPLETE/3PRUNED generated candidate;5actual
   SOFA followups show static PASS but fine-mesh slip FAIL. Candidate not approved.
   Actual failed/pruned/SQLite/seed mechanisms separately tested. ae6e8f2 records
   the verified implementation and bounded validation tooling.
10. Native surface sustained contact passes object subchecks,but projected parent
    Jacobian misses constrained guide reactions. First full reaction audit FAIL
    retained. Added direct child-Jacobian physical impulse mapping,detected sparse
    trailing-column padding error,and separated corrective reruns/new directories.
11. Corrected physical child-J native audits both PASS global force/moment and
    free-mapping equivalence;12→24surface diagnostic also passes. Projected-only
    failure and sparse-column padding failures remain separate. Scene templates
    are now source-controlled;pure configuration equivalence to measuredTz_v2
    passes,removing an ignored historical-raw dependency without changing physics.
    Matched8layer compensatedFREE and4layer equal-materialFREE references pass.
12. Recorded-state replay passed in isolatedSofaPython3; no GUI/real hardware.
    New reports/evidence distinguish actualSOFA,independentFEM,mathematics and
    assumed parameters. No real measurements and no100mm grasp optimizer bypass.
13. Publication review separated model-trial CSV from automation fault fixtures.
    Superseded publication draft was moved into ignored raw,not deleted. Final
    source/binary/runtime/report/raw manifest and read-only verifier cover both
    successful and failed records;only the correctly classified final evidence
    is published in reports. No model force or physical tolerance changed.

Remaining work and exact commands are in CONSERVATIVE_BEAM_NEXT_TASKS.md.
Unfinished phases are not reported complete merely because reports exist.
