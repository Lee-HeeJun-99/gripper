# BEAM06 — contact/history convergence and bounded performance

Status: **FAIL full convergence.** No tolerance or denominator inflation.
`contact_convergence_audit.json` uses |coarse−fine|/|fine| separately for
translation and load-induced rotation. Space/history limits1%,dt.1%,repeat1e-6.

|Comparison|Translation difference|Rotation difference|Decision|
|---|---:|---:|---|
|q8→16,11nodes|2.56045%|1.02534%|FAIL|
|q16→32,11nodes|2.54613%|.164326%|FAIL|
|11→21nodes,q32|3.76773%|.129958%|FAIL|
|21→41nodes,q32|.0506788%|.0390639%|PASS diagnostic|
|dt half|.449947%|.00495885%|FAIL translation|
|history grid half|2.75738%|.0204306%|FAIL translation|
|same-condition repeat|0|0|PASS|

Fine41node Gauss32 trial completed734.780s instead of timing out.
Measured new-beam8000step41node profile150.776s predicted678.494s for36000steps.
One explicit900s/4GiB exception was planned on that evidence, per user policy;
all other physics children retain480s,maximum4 concurrent. No repeated timeout
was relabeled PASS or rerun indefinitely. Actual fine displacement
4.41195685244e-6mm,global moment residual.000525316185<1e-3.

Exact AD constant propagation and per-ELEMENT cache reduce one-node invalidation
from~7249µs to~74µs. Whole8000step run improves168.626→150.776s (~10.6%),
not100×whole-engine acceleration. v1/v2 E/F/J100states are bit-identical.
Profile old cable/contact costs remain; no approximate force/Jacobian shortcut.

Independent axes show the fine Beam mesh is approaching agreement, but contact
quadrature/material-history and temporal trajectory sensitivity remain larger
than limits. This does not uniquely attribute all error to a single interpolation
operation. Existing history law is preserved; no unsupported new friction law
was substituted simply to improve these numbers.

Most convergence cases are frozen prototype diagnostics; some queued record
working-tree hashes changed while its binary did not. Prototype git4d19774
build manifest plus equivalence checks identify the actual math. The strict v2
fine trial is not silently pooled into a v1/v2 optimization study. A homogeneous
v2 rerun is still required after a justified history/contact improvement.
Moving-patch conservative history projection is the next research task, not
claimed implemented. Full grasp and100mm grasp-objective optimization BLOCKED.
