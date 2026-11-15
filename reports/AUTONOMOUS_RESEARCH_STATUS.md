# Autonomous research status — active continuation 2026-11-16

The prior stop was an agent-selected campaign checkpoint, NOT an observed
session timeout or exhausted system resource. It did not complete the user's
research objective. Development has resumed; the historical checkpoint below
is retained as history, not the current curved-contact status.

- Actual new `CurvedMaterialContact` SOFA integration: implemented, clean-built,
  dense-map/API/FD/objectivity/action-reaction tested; ConservativeBeam unchanged.
- Actual 11/21/41-node dynamics completed. Inherited all-node connectors/cable
  routing changed physical hardware with mesh; separate controls expose this.
- Fixed hardware plus derived uniform-density tributary masses: 11→21 motion
  1.597823% FAIL;21→41 .423918% PASS against unchanged1% criterion.
- Strict-FP native compilation of unchanged kernels: actual path equivalence
  PASS. One runtime pair at21nodes: history .0025→.00125 motion/loss PASS1%;
  repeat/recovery PASS. Half-dt motion PASS .1%,plastic loss .160535% FAIL .1%.
- Quarter-dt full18s: ACTUALLY COMPLETED1101.416s under the one recorded1320s
  exception(4GiB retained). FAIL:global moment relative residual .001031812
  exceeds .001. Half→quarter motion/loss differences pass,but the underlying
  physical failure forbids qualification. Base→quarter loss .196644% also FAILS.
- Checkpoint v2/v3: FAIL trajectory equivalence despite exactly restored force
  and Jacobian. Public first-step MBK/RHS/solution errors1.735e-18/0/1.098e-25
  support assembly roundoff amplification. Not used for physics qualification.
- Actual synchronized8s journal:48000stage rows,X/V/R exactly unchanged;
  kinetic algorithmic residual ≤1.4751e-20. NOT global stored-energy closure.
- New discrete radial-return energy identity:2000independent states PASS;
  actual16000step pre-Commit identity residual2.63344e-26,X/V/R exactly unchanged.
- Independent structural-only compensated summation contrast is now running:
  actual5000step scope test PASS(object,all rotations,roots,velocities exactly
  untouched). Actual18s hold at base/half/quarter dt PASS;global moment relative
  1.99483e-5/3.22488e-5/6.21926e-5 versus1e-3. Actual24s repeat/recovery PASS.
  Base-dt loss still FAILS time convergence;half→quarter motion/loss PASS.
  This is a21node half-dt candidate,not full-grasp certification.
- Its own same-half-dt11/21/41and fine-history revalidation is active.
- Energy observer has been moved AFTER live structural summation and BEFORE
  history Commit using public scene APIs. Actual1s/8s X/V/R differences0.
  Same-run Beam/normal/layer projections,algorithmic cable work and contact
  return accounting reduce8s derived residual to4.51719e-13;remaining after
  explicit potential remainders -6.22707e-14. Not yet global qualification.
  New Frame pressure-return audit passes actual1s;full24s journal is RUNNING.
- Full12wrench certification,global energy,100mm grasp Optuna remain BLOCKED.

Current raw: `results/autonomous_20261116_curve_a01`,
`results/autonomous_20261116_full_native_a01`,
`results/autonomous_20261116_checkpoint_a01` (plus explicit native/scalar controls).
Last committed source checkpoint: `0c6cb77`;additional energy/integrator work is active.

## Historical checkpoint 2026-11-15 (not current model certification)

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
