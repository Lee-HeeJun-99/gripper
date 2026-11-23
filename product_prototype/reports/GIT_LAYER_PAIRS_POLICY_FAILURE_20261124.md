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
