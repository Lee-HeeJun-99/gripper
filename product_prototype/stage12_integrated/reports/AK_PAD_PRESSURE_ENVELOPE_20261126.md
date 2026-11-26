# AK separate finite pad pressure envelope

This cycle resolves a specific uncertainty in the existing finite support
candidate: a uniform centroid pressure basis is sufficient but not necessary
for rigid normal equilibrium. This is a new distributed-pressure analysis of
actual CAD, not another placement/interference scan or a support adoption.

All235 AK candidate STEP hashes, existing three pad STEP hashes and upstream
geometry dependencies were checked. On the actual Palm/pad common faces,
two radius1mm uniform patches centered1.5mm in +x from pad0 and pad2 centers
carry0.5N each. Each actual area is pi mm²; pressure0.1591549431N/mm² is an
explicit conditional witness, not an allowable or predicted elastic pressure.
The positive patches balance [0,0,-1,0,14,0] N/Nmm with maximum residual
3.56e-15. The old centroid-only solution [0.52,-0.04,0.52]N rejects this case.
Thus that basis cannot certify all possible eccentric pressure equilibria.

For any nonnegative normal pressure on these actual footprints, the center
of pressure lies in their convex hull. The exact x projection is[-28,15.5]mm.
The old1N/My40Nmm case needs x40mm,24.5mm outside the necessary bound, and
remains impossible even with arbitrary nonuniform pressure. Boundary measures
cannot fix that exclusion. No full two-dimensional envelope is claimed.
All normal contact wrenches still have Fx=Fy=Mz=0 and Fz>=0. Uplift, lateral
and torsional retention and connected ground attachment remain unresolved.

Independent verification uses eight .001/.002mm solid volume/first-moment
slices on both actual Palm and pad sides, cross-product equilibrium, virtual
work, and cylinder volume-derived x extents. A deliberately shifted patch
crossing the pad edge has area0.5498301022mm² instead of pi and is rejected.
Every declared check passed. Initial verifier exit1 from NumPy bool_ JSON
serialization is retained under AK_pad_pressure_verify1 with original producer,
log and explicit failure summary; corrected verifier has a new output tag.
Three bounded children used4GiB/420s and one thread; no SOFA run.

This does not solve elasticity, pressure compatibility under deflection,
preload, material/strength, actual operating loads, full Palm energy or mesh
convergence. CAD/BOM and all historical PASS/FAIL scope remain unchanged.
Read-only release audit remains INTEGRATED_NOT_QUALIFIED. No inference of
system release from this rigid witness is permitted. Further C work requires
positive side/torsion/lift-off retention with a finite connected ground path;
repeat pressure patch scans are not progress. Independent A/B tasks remain.
Supervisor local save is PENDING. No Git add/commit or manager launch occurred.
