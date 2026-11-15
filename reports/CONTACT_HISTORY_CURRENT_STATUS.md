# Contact history — current status

Branch: `development/regrip-contact-history-convergence`.
Baseline: `5dd3eafbbd459abcdc1c2c3ad9654f00c01545fa`.
Campaign/build/runtime remain on the external disk inside this project.

Overall **FAIL convergence; BLOCKED full coupled energy /100mm grasp Optuna**.

PASS: original-operator aliasing reproduction;transport-before-interpolation
test;new MaterialHistoryContact build and bounded force/Jacobian/objectivity/
dissipation/query tests;normal q8/16/32 and tangent cell2/4 comparisons;repeat;
local+Tz hold and24srelease;two fresh600frame golden regressions;Python/C++
regression;own-kernel ASan/UBSan;measured-state headless replay.

FAIL: history .005→.0025mm and11→21node refinement;time refinement has not met
the original0.1% condition. Exact final finer-case results are in
`history_evidence/convergence.json`,not hidden by the summary.

EXPERIMENTAL: new crossing-aware birth increment,independently tested with
implicit-root derivative,NOT yet used by production SOFA. Partial energy
inventory is NOT full closure. LSan BLOCKED by ptrace restriction.

NOT RUN: new12dynamic-wrench qualification,Cylinder/Box integrated grasp,new
native contact refinement,sustained-contact240000step/hours soak,GUI,real PET/
vacuum measurements. No100mm grasp Optuna trial was run past failing gates.

See CONTACT_HISTORY_FINAL_REPORT and NEXT_TASKS. Original Beam/golden/old studies
are preserved. No push,history rewrite or previous-branch overwrite.
