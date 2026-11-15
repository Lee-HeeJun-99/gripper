# HISTORY 04 — actual homogeneous-v3 SOFA convergence

Overall: **FAIL**. Machine-readable measurements, strict limits, both rotation
and translation errors, absolute errors and source paths are in
`history_evidence/convergence.json` and `convergence.csv`. The corresponding
raw experiment is `results/history_20261115/grasp/<name>/`.

Same conservative Beam,100mm three guided fingers/two layers each, free6DOF
sphere, load+Tz5e-6, tension.001,pressure.001,mu.3,kn=kt=.001. EigenSparseLU,
EulerImplicit,Rayleigh mass2/stiffness.1 are unchanged. Research root placement
is about95.15mm, NOT the target50mm body radius. Finger planar .005rad domain
is checked. Normal q, tangential cell order, history h, nodes and dt are distinct
numerical controls. No physical denominator or tolerance was inflated.

Base24s actual hold displacement4.24740979983e-6mm; load-induced rotation
2.09795096325e-4rad; normalized global force2.1340e-5/moment7.0392e-5.
All bounded hold subchecks pass. After release, finger recovery displacement
2.09735e-8mm, rotation2.94695e-10rad,zero contact; repeat state is identical.
This remains EXPERIMENTAL overall, not full grasp certification.

History .01→.005 initially falls below1%, but .005→.0025 exceeds1% again.
11→21nodes fails1%; base→halfdt fails0.1%. Small absolute translations are
reported alongside relative errors, not used to erase FAIL. Full results of
41nodes and quarterdt appear in the machine-readable final table, including
timeout/failure if encountered. No optimization is enabled by a partial pass.

Default process limits4GiB/480s/max4 physics children. One41node profile measured
142.319s for4simseconds (18s prediction640.434s); one quarterdt profile measured
153.794s (prediction692.073s). Each has ONE documented900s/4GiB exception,
`n41_exception.json` / `dt_quarter_exception.json`, not unlimited retries.
18s trials cover the same6..14s hold window but do NOT certify24s full recovery.
41nodes completed775.519s;21→41 translation.782441%,rotation.0436982% PASS.
Quarterdt failed900.005s (timeout,-9,last logged138000/144000steps);no final
performance or convergence value is accepted. The failed attempt is retained.
