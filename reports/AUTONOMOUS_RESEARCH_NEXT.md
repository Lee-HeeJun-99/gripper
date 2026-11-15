# Next research checkpoint

Read FINAL_REPORT,STATUS,assessment.json and manifest first. Do not rerun the
immutable a01campaign in-place. Work inside external-drive ReGrip directory.

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
git status --short
git log -4 --oneline
$PY tools/research_evidence.py --verify
$PY tools/birth_verify.py --raw
$PY tools/research_assess.py
```

1. Prioritize remaining4.96%/2.80% Beam-mesh translation differences.
   Contact-history loss already passes1% in this new model;do not rewrite the
   ConservativeBeam or tune its parameters to mask spatial error.
   Adjacent dt comparisons pass,but base→quarter motion.113702% and loss
   .174427% fail.1%;do not classify base-dt time qualification as complete.
2. `models/contact_kinematics/HermiteMap.h` is a tested independent candidate.
   Implement a NEW component using virtual-work pullback,not just a point
   replacement. Validate curved-contact detection,reference integration,
   normal/tangent consistency,multiple active intervals and query/Commit.
   Straight-segment active bounds without a proven conservative envelope can
   silently omit curved contact. Director length/axial strain is an assumption.
3. Compare against dense AD2 before optimizing assembly. Sparse equivalence is
   tested,but no production speedup or curved-contact dynamics result exists.
4. Run prescribed geometry/reference before3finger dynamics. Then profile4s
   and use independent11/21/41mesh and fine-history tests with original1%line.
   Normal Gauss order differs from immutable midpoint tangent integration.
5. Finish transaction-level work/energy accounting:matched-state Beam/FrameLayer/
   cable/contact/parameter/external work and Rayleigh loss. Scalar identity is
   not a global energy model;detachment inventory is not automatically heat.
6. Only after space/history/time/energy qualification:12wrench trials,shapes,
   pressure-capacity contrasts and new100mm grasp Optuna Study. Maintain
   failure controls and50mm target versus95.15mm research-layout distinction.

New namespace/clean build example(existing names are refused):

```bash
export REGRIP_RESEARCH_OUT="$PWD/results/autonomous_next_a02"
export REGRIP_RESEARCH_BUILD="$PWD/build/autonomous_next_a02/v1"
$PY tools/research_build.py
$PY tools/autonomous_trial.py profile_next --history .0025 --profile
$PY tools/autonomous_trial.py reference_next --history .0025 --duration 24
```

These reproduce CURRENT linear-centerline material points,not future curved
contact. Sources are snapshotted before compilation and identities guarded.
Default4GiB/480s,max4long children.900s only after recorded profile decision.
No background automatic restart installed. Source checkpoint is in manifest;
final documentation commit is visible in Git log.
Last validated source checkpoint:456d83f2f36fb0e64deabac91341c636681af36d.
New raw/source/build verifier passes894entries. All physics children in this
campaign have completed;there is no pending quarter-step process to resume.
