# BEAM11 — real Optuna, clearly separated scopes

Status: **PASS independent linear structural search execution; candidate
qualification FAIL;100mm grasp optimization BLOCKED.**

Existing Optuna4.6 environment reused via PYTHONPATH=.python-deps/grasp:.:tools.
Old30mm SQLite study unchanged. `beam_structural_optuna.py` creates a NEW100mm
TWO-layer SMALL-PLANAR LINEAR-FEM structural study, not SOFA or grasp trials.
Its3DOF element is independently assembled and its rest stiffness matches the
new3D kernel; actual2layer k0/k100 SOFA equilibrium agrees within.5% reference
gate. This permits an independent stiffness/slip research search only.

Seed2911,TPE,SQLite,3COMPLETE smoke then resume to24COMPLETE,3duplicatePRUNED,
0unintentionalFAIL. k=.001..100,connector count1..10,locations chosen among10
physical grid positions; dt never sampled. Objectives: equilibrium OFF/ON ratio
max and maximum equilibrium interface slip min. No failure gets fabricated values.
New actual contracts also inject1FAIL and1PRUNED with values=None,SQLite integrity,
resume,3objective trials and identical fresh seeded studies all pass.
Manual pre-evaluation pruning is not an unsupported multiobjective intermediate
pruner; resumed TPE state is not claimed bitwise identical to uninterrupted RNG.

Single Pareto candidate trial16:k84.1732992010,all10locations10..100mm,
predicted ratio1.68434718895,slip1.20894798466e-7mm (INDEPENDENT FEM).
Five NEW actual SOFA validations:FREE,ON,repeat,halfdt,21nodes preserving exactly
those connector positions. Actual ratio1.68405837281,ONtip.00925550007117mm,
equilibrium slip1.20955737003e-7mm. All five static residual gates passed.
Repeat and halfdt pass, but21node slip3.55449798290e-7mm fails the unchanged1%
candidate mesh requirement. Candidate remains FAIL, not approved optimal design.

Explore the max slip over all interface nodes: unmatched/new nodes can reveal
localized slip missed by the coarse mesh. Do not replace the objective with
connector-only slip simply to pass. The study is finite exploratory search, not
global optimum,real vacuum/PET calibration or fabrication-ready design.
No100mm contact/grasp objective trials were run past BEAM06/09 failed gates.
