# Contact history development log

2026-11-15,external-disk workspace. Base5dd3eaf;new branch created without
modifying prior branches or original model/golden/raw/SQLite evidence.

1. Read project instructions and requested prior reports;initial old evidence
   audit2241entries passed before new ignore metadata. Existing blockers retained.
2. Implemented independent MaterialHistoryContact,not a replacement of old FF.
   Reproduced quadrature aliasing and normal reprojection loss mathematically.
   Local commit fda0e80 preserves the first implementation.
3. Fixed value-only commit cost,element-local matrix assembly,material endpoint
   history preservation and detachment-domain integration. Clean v3 build/unit/
   ldd logs preserved. Local commit c4c069e preserves matching core sources.
4. Profiled actual SOFA,then ran bounded homogeneous v3 physical cases. First
   campaign postprocessor lacked `steps`; preserved original FAIL records and
   raw states. Recovered numerics separately with explicit inferred-exit/no-wall
   provenance;new repeated trial directly saved OS result and matched exactly.
5. Normal and cell quadrature tests pass;history/mesh/time diagnostics remain
   failures,not optimized away. Measured profile-based bounded fine exceptions
   retained in campaign. No new grasp Study was started.
6. Added prescribed moving-patch/circle,global objectivity,flat-slider work and
   assembled18DOF FD tests. New contact-birth negative control identifies a
   dropped crossing-step increment;experimental implicit-root kernel is tested,
   but not silently substituted into completed SOFA trials.
7. Independent full-interface structural FEM11..161nodes identifies missing
   between-connector slip extrema. Old candidate remains FAIL,Study unchanged.
8. Recorded partial energy inventory from2401actual saved states;unknown work/
   energy terms remain null. Reused SofaPython3 for real-state headless replay.
9. Fresh golden twice,Python/C++ tests,own-kernel ASan/UBSan and blockedLSan
   evidence retained. Reports,small JSON/CSV/figure and SHA manifest preserve
   what was executed,what failed,and exact resume paths.

This is a bounded development campaign,not completion of all requested research.
The next numerical/model changes require a fresh version and fresh qualification;
neither more local hold tests nor a new optimizer can waive failing prerequisites.
