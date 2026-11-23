# Unpublished oversized Raw blob — requires explicit history-repair authority

During this session bulk `git add -f` of a result directory mistakenly included
`product_prototype/results/layer_mesh_native1260/layer_pairs.csv` in local
commit9a8d4a8. Exactsize128561058bytes,over100000000 policy. This is an agent
error,NOT an acceptable exception. Actual Raw preserved;no push,SDK edit,
history rewrite,LFS substitution or misleading cleanup claimed.

Read-only `git rev-list --objects 168e11b..HEAD` / cat-file audit detects it.
Later delete/untrack commits do NOT remove this blob from prior history.
Thus branch is NOT normal-push-ready under GitHub size policy. Repair needs
explicit permission to rewrite only unpublished affected local history,with
backup first. Existing user instruction prohibits that operation,so repair
BLOCKED pending authority. Do not forcepush,erase sourceRaw or reset worktree.

Added `product_prototype/tools/research_git_guard.py`:read-only staged-file
check rejects detector.csv of anysize and allblobs>=100MB. Optional --since
audits existing local history and returnsFAIL,not a falselyclean result.
No repository hook installed without approval;must explicitly run guard
before later localcommits. Future Raw staging must listfiles excluding
oversizedjournals;their immutable hash/size remain in evidence manifests.

Commands:
`python product_prototype/tools/research_git_guard.py`
`python product_prototype/tools/research_git_guard.py --since 168e11b`
`python product_prototype/tools/test_research_git_guard.py`

## Verified safety backup (not history repair)

External directory:
`/media/ubuntu/99419895-2058-45b4-b746-b36ea7112e4e/research/LHJ/regrip_backups/layer-20261124-SK2mmt/`

`local_commits_7052623.bundle` is an INCREMENTAL bundle168e11b..7052623,
NOT a standalone full repository clone. `git bundle verify` PASS,requires
base168e11bbebae93278de312d6c026c14dd36c7dbd. BundleSHA256
02fcf01aa65be8398c1431dd5bf0cbf3bc9af2b771b86b176fbb0850f39582e5.
Eight rawcopies include oversized1260layer_pairs andall7newdetectorjournals
1265/1266/1269/1270/1271/1272/1273;all8cmp byte-equality checksPASS.
Later checkpoint metadata commits are not included in this earlierbundle;
take another fresh currentHEAD backup before any approved rewrite.

No commits were rewritten,deleted or pushed. NoRaw deleted. Current branch
still contains the oversizedblob and remainsNOTpush-ready. Repair needs
explicit permission;new staged-only guards are not retroactive cleanup.
