# ReGrip contact-history verification report

Baseline `5dd3eafbbd459abcdc1c2c3ad9654f00c01545fa`;branch
`development/regrip-contact-history-convergence`. Core source milestone c4c069e
follows fda0e80;final source/report commit and hashes are recorded by Git and
CONTACT_HISTORY_EVIDENCE_MANIFEST.json (a final documentation commit may follow
the manifest's code commit;no self-referential SHA claim).

## Outcome

**Full qualification is NOT complete.** Independent mechanisms were reproduced,
a separate SOFA history component was implemented and actually executed,and
normal/tangential quadrature sensitivity improved. History and temporal
convergence still fail strict criteria;full coupled energy and100mm grasp
optimization remain BLOCKED. No failed trial is assigned successful objectives.

|Scope|Decision|
|---|---|
|Original quadrature aliasing / normal projection-loss reproduction|PASS|
|New kernel force/Jacobian/objectivity/local dissipation|PASS bounded tests|
|New MaterialHistoryContact actual SOFA loading/integration|PASS execution|
|Normal q8/16/32 and tangent cell2/4 diagnostics|PASS|
|Material h=.005→.0025 convergence|FAIL|
|11→21node convergence|FAIL|
|Time refinement to original0.1% requirement|FAIL/incomplete;see final table|
|Local+Tz hold and24srelease/recovery/repetition|PASS subgates,overall EXPERIMENTAL|
|Crossing-aware birth increment|EXPERIMENTAL independent-only|
|Partial energy inventory / full coupled closure|PASS inventory / BLOCKED closure|
|New12direction/shape-general grasp approval|BLOCKED/NOT RUN|
|New100mm grasp Optuna|BLOCKED,0 trials|
|Independent structural objective diagnosis|PASS;old candidate remains FAIL|
|Fresh600frame golden regressions|PASS twice|
|Own-kernel ASan/UBSan /LSan|PASS /BLOCKED ptrace|
|Actual-state headless replay /GUI|PASS /NOT RUN|

Final numerical finer-case decisions,including41nodes andquarterdt,are in
`history_evidence/convergence.json` and CSV. They are not overridden by prose.
The41node run completed775.519s;21→41 translation difference.782441% and
rotation difference.0436982% pass the1% diagnostic,without erasing11→21 FAIL.

## Implementation and evidence

New code: `models/contact_history/`,experimental `models/contact_birth/`,
`diagnostics/contact_history/`,`tests/test_contact_history.cpp`,
`tests/contact_history_extra/`,`tests/test_history_assess.py`,and`tools/history_*`.
Original Beam,old contact/StickSlip,original45gate,golden data and Studies were
not modified. All raw files/builds/environments stay under the external drive.

See HISTORY01..14 for derivation,assumptions,commands,failures and limitations.
New history uses material nodes,transport BEFORE interpolation,cell-split tangent
integration and a symmetric transported chord increment. This is NOT general
conservative remapping or an exact zero-slip contact constraint.

Actual repeated24s+Tz SOFA:hold displacement4.24740979983e-6mm,rotation increment
2.09795096325e-4rad,relative global force2.1340e-5,moment7.0392e-5. Recovery
translation2.09735e-8mm,rotation2.94695e-10rad,zero remaining contacts.
All bounded local checks pass;none establishes full force closure or convergence.

Independent triangular-history exact force6e-6:old q8 error26.0019%,new cell-split
error2.22e-16. Prescribed normal-transport squared-norm loss3.94695%→0 for the
specific reference.60smooth-state kernel Jacobian error5.593e-9;assembled18DOF
FD error1.3204e-12. These are mathematical/C++ tests,not hardware measurements.

The production newborn rule drops the partial displacement between contact
crossing and step end. Independent flat-reference expected.01,actual0. New
experimental crossing kernel gives.01,implicit-root FD error2.746e-10,with a
grazing-derivative guard. It is NOT used in completed v3 simulations.

The first campaign's Python NameError is preserved,not relabeled engine failure
or concealed. Separate recovered metrics explicitly infer exit0 from the
short-circuit exception;wall time is unknown. Repeated run records the real OS
exit0,281.877s,and exactly matches saved state. Source/build identities are checked
separately;different numerical model versions are not pooled into a Study.
Normal-quadrature geometric wrench analysis gives rank6/cone interior atq8/q32;
its capped LP andmu0 control are independent discretized feasibility tests,not
a substitute for actual12dynamic force/torque trials or force-closure approval.

## Independent structure and energy

Same linear100mm candidate k84.1733:full-interface maximum is1.20895e-7mm at
11nodes but3.55269544e-7mm at21..161nodes. The coarse mesh omitted inter-connector
maxima. Connector-only slip is NOT substituted. No new optimum is approved.

2401actual state records yield an explicit partial energy journal. Beam/kinetic
energies are computed using the frozen strain kernel and configured isotropic
mass. Unknown controller work,normal/layer energy and damping terms remain null.
Contact pre-commit energy and end-event state require a synchronized per-step
journal before a full energy claim. Unexplained residual is not named numerical
dissipation merely to close a balance.

## Environment and reproducibility

Ubuntu22.04,observed kernel6.8.0-138;Python3.10.20,NumPy2.2.6,SciPy1.15.3,
Optuna4.6.0 already available. Separate patched matched SDK is reused for physics;
installed SofaPython3/isolated3.12 is used only for optional recorded-state replay.
No system Python replacement or ABI symlink workaround. Default4GiB/480s/max4
physics children;two single900s exceptions have measured profile evidence.

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/history_verify.py --raw
$PY tools/history_assess.py
$PY tools/history_plot.py
```

For a NEW campaign/build and actual reruns,use CONTACT_HISTORY_NEXT_TASKS.md.
Existing output names refuse overwrite. Raw logs/config/state/metrics and full
streaming SHA inventory accompany small tracked evidence. Historical manifest
metadata deltas are listed,not erased by refreshing old manifests.

## Remaining work and limits

First integrate birth-time/transfer correction WITH consistent Jacobian and
commit,then rerun separate h/q/node/dt gates. Test exact active-boundary/grid-node
degeneracy. Implement the full force-stage energy journal. Only after qualification
run12wrenches,controls,other shapes,pressure-capacity sweeps and new grasp Study.

Native surface contact/new sustained-contact FD/PSS/240000step tests remain
separate unfinished work. Current fingers are guided-planar and object6free,
with~95.15mm research placement rather than50mm target radius. No real PET,
vacuum/friction/material properties,wire routing or fabrication-ready grasp
performance has been measured or certified. No remote push was executed.
