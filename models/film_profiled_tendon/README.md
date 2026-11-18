# Experimental distributed guide profile

Separate from `film_lateral_tendon`; no change to its qualified geometry.
At material x=0/25/50/75/100mm the normal eccentricities are
5.5/5/4.5/5/5.5mm. The same objective6mm outboard offset is retained.
Changing ONLY this normal profile introduces intermediate guide forces;
the piecewise-linear mean normal offset remains5mm. Neither uniform curvature
nor superior wrapping follows automatically. Guide orientations use the
deformed rail frame,not a fixed world-direction force.

Amplitude0 delegates exactly to the constant5mm/lateral6mm route.
Core volume/material/mass/root/C2 remain unchanged;finite guides/wire,
their mass/friction and fabrication are NOT modelled. Rest cable length
changes200→200.039996mm,so actuator stroke/work are NOT matched by assumption.
The tendon potential T*(length-reference) generates external forces;it is
not stored cable elasticity or motor energy.

1431/1432 independent FD,objectivity and baseline parity PASS;
wire CENTRELINE initial R30 gap+.366772mm is not finite-thickness clearance.
1433 first API harness FAIL:zero-profile mutation used old6mm parameter,
rejected by new0/.5mm domain. Preserved,not a physics-convergence result.
1436 corrected actual addForce/addDForce/matrix/query-purity/Data API PASS.
1437/1438 actual200us and1442/1443 actual3.2ms no-object coupons PASS
strict1e-12 q/v,all stage rows,all context clocks and Field control input.
1444 actual zero-profile versus original lateral6mm over60epochs:
q/v difference0,all stage rows EXACT. This is regression,not time convergence.

Generated providers and binaries are source/hash-bound by
`tools/film_profiled_build.py`;default old routing runners are preserved.
The early generated Field's descriptive Data string inherits old lateral
wording;runtime validator and actual0/.5mm parsing are tested. Do not read
that legacy description as a supported6mm profile amplitude.
No object/contact,wrapping,holding,lift or final-design qualification here.

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/film_routed_run.py --tag UNIQUE --design profiled --amplitude .5 --provider 20261118_profiled_api1436 --duration .05 --profile 20261118_profiled_32_1442
```
