# Autonomous research status — checkpoint 2026-11-15

Branch `development/regrip-autonomous-research`; baseline63970172ad196e0add3ad42a67ccaee4c7a8975e.
Raw campaign `results/autonomous_20261115_a01`,compiled physical component
`build/autonomous_20261115_a01/v3/libReGripMaterialPointContact.so`.
See FINAL_REPORT and manifest for final source checkpoint and exact hashes.
Validated source checkpoint:456d83f2f36fb0e64deabac91341c636681af36d.
New campaign integrity:PASS894SHA256artifacts. Raw1173017042bytes,external only.

| Scope | Result |
|---|---|
| Historical source/raw/binary integrity | PASS1845entries,old physics preserved |
| New immutable material-point component clean build/API/FD | PASS |
| Actual plastic Commit versus observed plastic | PASS,exact equality |
| Same-hold loss history convergence | PASS .129703/.279753/.049621% vs1% |
| History motion .01→.005→.0025 | FAIL4.61737/1.01697% |
| History motion .0025→.00125 | PASS .0300247% |
| Mesh11→21→41 motion | FAIL4.95984/2.80102% |
| Fine dt-half motion/loss | PASS .0977366/.0999735%,borderline.1% |
| Half→quarter-dt motion/loss | PASS .015950/.074528%,679.15s actual run |
| Base→quarter-dt motion/loss | FAIL .113702/.174427% vs.1%;time qualification incomplete |
| Hold force/moment relative residuals | PASS local1e-3 |
| Repeat | PASS,hold motion/loss exactly reproduced |
| 24s recovery | PASS base/fine-repeat;not fully tested by18s cases |
| Independent curved-contact pullback | PASS60states,NOT SOFA-integrated |
| Global energy closure | BLOCKED |
| New12wrench/full-shape certification | BLOCKED by convergence/energy |
| New100mm grasp Optuna | BLOCKED;0new trials,no fabricated Pareto |
| Native surface/new GUI | NOT RUN;prior independent research unchanged |
| Continuous-contact long-soak/no-leak certification | NOT RUN;bounded samples EXPERIMENTAL |

Largest remaining measured blocker is Beam/contact spatial convergence.
Plastic-state consistency improved;it does not repair spatial kinematics or
complete the synchronized global energy/work journal. No real material
measurements or actual gripper performance are certified. Research fingers
still have explicit planar guides and the~95.15mm base-radius assumption.
