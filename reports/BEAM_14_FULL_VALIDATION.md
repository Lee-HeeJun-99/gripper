# BEAM14 — independent validation inventory

The following are separate scopes, not an aggregate certification count.
PASS means actual execution; FAIL is retained; BLOCKED identifies a prerequisite;
NOT RUN is not a substitute for success. EXPERIMENTAL denotes research scope.

|Scope|State|Evidence under results/beam_20261115|
|---|---|---|
|Fresh C++ build/load/linkage|PASS|clean, single,grasp|
|61state potential/force/J/H/API/objectivity/moment|PASS|clean/unit|
|100state prototype-v2 exact E/F/J equivalence|PASS|clean/equivalence|
|40large-rotation kernel +noncommuting closed path|PASS convergence|large_kernel_corrected|
|Cache/material/invalid input/Rayleigh API|PASS|extra_unit|
|ASan/UBSan/LSan, new FF translation unit|PASS bounded rerun; first FAIL|asan_unrestricted;asan preserved|
|Python73legacy+5new tests|PASS78tests|validation_unit_dependency/python_command|
|Three prior closure C++ executables|PASS|validation_unit_dependency|
|Five legacy C++ unit executables|PASS|legacy_units|
|600shared-metric golden regression,2fresh runs|PASS|validation_golden|
|Prior45physical gates|preserved historical PASS,not rerun|original manifest hash audit|
|Single beam force/axial/moment/torsion/rigid rotation/mesh/dt/repeat|PASS10finite cases|single_campaign.json|
|2/4layer FREE/ON equilibrium|PASS|multilayer_campaign.json|
|8layer standard Euler ON|FAIL|multilayer/L8_k100|
|8layer translation-compensated ON,halfdt,21nodes,18s|PASS|precision;multilayer_followup.json|
|Equal-total-material4layer equilibrium|PASS|multilayer/L4_equal_total|
|New3finger+Tz global force/moment/24srelease|PASS bounded subgate|grasp/Tz_v2|
|New full grasp certificate|EXPERIMENTAL/BLOCKED|BEAM06/07/09|
|q/history/dt trajectory convergence|FAIL|contact_convergence_audit.json|
|21→41fine mesh comparison|PASS diagnostic|same audit;fine734.78s|
|Actual patch rank/cone/capped LP|PASS mathematical test only|wrench.json|
|All12dynamic loads,new cylinder/box/negative controls|NOT RUN,prerequisites failed|BEAM07|
|Native sustained contact+object residual|EXPERIMENTAL|native_lat12/24|
|Native full reaction reconstruction|PASS corrected child-J audit;initial projected-only FAIL retained|native_physical12/24/balance.json|
|Native sphere surface12→24|PASS one refinement diagnostic,not full convergence|native_surface_comparison.json|
|Single beam discrete dynamic energy ledger|PASS limited small-load scope|dynamic_energy|
|Coupled actuation/parameter/friction energy ledger|BLOCKED incomplete|BEAM09|
|Independent100mm linearFEM Optuna24COMPLETE|PASS search execution only|structural_optuna|
|Selected candidate SOFA mesh qualification|FAIL|candidate_result.json|
|100mm grasp-objective Optuna|BLOCKED,0newgrasp trials|BEAM11|
|Matched fullscene120000steps/2cycles|PASS bounded scope|memory|
|240000single-run/several hours/persistent-contact memory|NOT RUN|BEAM12|
|Measured-state replay/SofaPython3 batch|PASS replay only|replay|
|GUI|NOT RUN optional|gui_command.json|
|Real PET/vacuum/hardware performance|NOT RUN,0measurements|research assumptions only|

No original/golden/previous raw is replaced. Previous strict manifest intentionally
detects current metadata changes; preservation audit separates those from any
unexpected source/binary/raw mutation. New compiled manifests cover frozen v1/v2
and strict v2 source/binary/transitive-dependency checks. No relaxed physical limits.
