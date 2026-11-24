# Historical B3 response-cone reference1294–1296

Read-only immutable response rows of50g485 and100g1059. Select closest actual
stored times to1.1/1.4/1.8s,no interpolation. For nonzero multipliers,
actual generalized object impulse divided by lambda reconstructs its response
column. Require complete normal/tangent triplet,orthonormal translation basis.
Eight-ray inscribed friction cone,assumedmu0.3;LP enforces6 generalized
force/moment equations. No guessed detector normal/contact position.

IMPORTANT:1294 grouping omitted first_row;repeated constraint paths could
overwrite components. It is an invalid analysis,NOT grasp infeasibility.
Original1294producer/summary retained.1295 includes(path,first_row,triplet),
asserts unique globalrow and component.1296 adds exact-circle maximumvertical
force at actual measured normal allocation,ignoring torque (optimisticbound).

50g completeactivegroups3 at each sample:LP feasible,minimum normal sums
0.48857–0.48876N vsmeasured0.48899–0.48947N. Maximumverticalbound≈0.495N
vsweight0.4905N. This is frozen subset equilibrium,not newHoldingPASS.

100g at1.1s:LP minnormal1.01275N vsmeasured0.75040N;measuredgeometry's
optimisticverticalbound0.73321N vsweight0.981N. At1.4s LPmin39.473N,
bound0.02553N. At1.8s subsetLP infeasible andbound−0.05976N. Late geometry
cannot be repaired merely by redistributing existing tangential forces at
these measured normal magnitudes. Omitted zero-multiplier contacts are not
fabricated:failedsubsetLP is NOT a proof about all possible contact sets.
Normal sums are measured response inputs,not actuator capacity or material
limits;39.473N is NOT a motor/tendon requirement or valid recommendation.

Original Native time/mesh/solver-limit failures remain. Basis linearization,
frozen geometry,inscribed polygon and subset coverage limit all conclusions.
The actual object is accelerating/caught by support,not statically held.
No sourceRaw,manifest or historical verdict modified. No new100gPASS.

Design followup:rail-back attachment plane changes load transfer without
raising1.5N/cable. Single-finger1129 previously avoided inverted savedstates,
buttimeFAIL persists. A new independent100g threefinger candidate1297+ is
EXPLORATORY only;ideal hardware connection not fabrication-qualified.

Reproduce read-only analysis with fresh tag:
`python product_prototype/sofa/b3_response_cone_reference.py --tag NEW_TAG`.
Python `/home/ubuntu/miniconda3/envs/robot_ws/bin/python`. Guard4GiB/60s,
1296runtime2.080s. Input hashes and immutableproducer recorded. Synthetic
force/moment cone tests are algebra checks,not actual SOFA grasp results.
