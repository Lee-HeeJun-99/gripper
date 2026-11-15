# BEAM07 — free6DOF grasp qualification

Status: **EXPERIMENTAL +Tz hold/release; full12-wrench certification BLOCKED.**

BEAM05 records the actual full24s sphere sequence and new global balance.
The sphere is not fixed; root/planar finger guides are explicitly logged.
At the actual13.98s new-beam patch, `tools/beam_wrench.py` finds normalized
wrench matrix rank6, strict origin-interior of the inscribed8-ray friction cone,
and capped LP feasibility for ±Fx/±Fy/±Fz/±Tx/±Ty/±Tz. Limits use actual measured
normal forces and μ.3; force scale1e-6,torque scale5e-6F·mm,length scale5mm.
Singular values,left nullspace,actual positions/normals/caps and LP residuals
are preserved in `results/beam_20261115/wrench.json`.

This is a static polyhedral-cone feasibility calculation, not proof the compliant
actuator can realize all those loads dynamically or an ultimate load bound.
Rank6 alone is not force closure. The actual twelve-direction dynamic campaign,
new-beam sphere overload/μ0/wireOFF/misplacement controls and cylinder/box
sequences are NOT RUN in this campaign: prerequisite BEAM06 failed and BEAM09
whole coupled ledger is incomplete. Historical old-beam control successes or
failures are not reused as new-beam certification.

No100mm grasp objective is evaluated or optimized behind these failed gates.
Existing research radius≈95.15mm is not passed off as50mm construction geometry.
