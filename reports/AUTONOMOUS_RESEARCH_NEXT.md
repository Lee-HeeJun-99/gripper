# Next research checkpoint

## Active continuation 2026-11-16 — implementation is no longer pending

The tested Hermite map is now integrated in `models/curved_contact`,with actual
11/21/41-node SOFA runs and original spatial limits. Do NOT repeat the old
"implement Hermite" task below. Current priority is full time/loss qualification
of the fixed-hardware,tributary-mass21node candidate,then synchronized energy.
11→21 still FAILS;21→41PASSES. Do not relabel the coarse model as qualified.

Current commands (external-drive project root):

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
export REGRIP_BEAM_PLUGIN=build/autonomous_20261116_full_native_a01/beam/libReGripConservativeBeam.so
export REGRIP_CURVE_BUILD=build/autonomous_20261116_curve_native_a01/v1
export REGRIP_CURVE_OUT=results/autonomous_20261116_full_native_a01
$PY tools/curve_qualification.py
```

Completed,do not duplicate or overwrite:
`curve_quarter_exception.py`→grasp/quarterdt_exception (1101.416s,global moment
FAIL.001031812);`curve_return_journal.py`→return_journal_v4(PASSlocalidentity);
`curve_checkpoint_solver_probe.py`→checkpoint_a01/solver_probe_v4(EXPERIMENTAL).
Completed continuation:transaction_journal_8s_v6 and the independent
`curve_compensation_campaign.py` under results/autonomous_20261116_beam_compensation_a01.
Current bounded children:`curve_compensation_refine.py`(same-half-dt mesh/history)
and `curve_compensation_energy.py --steps 48000`(full24s synchronized journal,v9).
These are real active processes,NOT an automatic future-session restart.
Check actual process/results before any resumption;tools refuse existing names.
The original900s blocked decision and failed checkpoint equivalence remain.
Actual quarter assessment is separate:quarterdt_actual_assessment.json. Half
versus quarter motion/loss pass but physical moment failure remains. Original
canonical_completed's900sblocked decision is not overwritten.

Next meaningful alternatives if loss still fails: separate endpoint-return
integration error from transport/global virtual work using the new actual
pre-Commit audit;compare public assembled solver systems before blaming missing
physical history. No arbitrary damping or friction changes to force PASS.
Keep grasp optimization blocked pending required convergence/energy gates.

The new observed fine-dt moment floor selected a more immediate test:use the
preserved Compensated.h arithmetic ONLY on structural free X/Z translations,
never object/quaternion/root. New component rejects non-roundoff discrepancies
or >2ULP adjustments. Actual scope test and profile are prerequisites;higher
resolution full contrasts launch only after base hold and their own profiles.
Its base/half/quarter hold tests and24srecovery have now actually passed.
Half→quarter time motion/loss PASS;base time loss FAIL is preserved.
Do not reuse standard-Euler spatial/history qualification as certification of
this new integration-arithmetic contrast. Its same-half-dt mesh/history cases
are running. Use `curve_compensation_assess.py --checkpoint UNIQUE_NAME` after
actual completion;existing qualification_v1.json is an immutable partial view.

After the full24s journal finishes,inspect all phases and the independently
derived Frame-return projection. Its first1sactual API/query-purity test PASS.
Cap-dependent RETURN energy is not fixed-state stored energy:the independent
pressure test shows released energy must include plastic and projection terms.
Do not infer vacuum-source work from finite differences of a clipped trial
potential. Physical vacuum work remains outside this prescribed-cap model.

## Historical plan (retained; Hermite implementation tasks now performed)

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
