# Unpublished detector CSV cleanup — 2026-11-23

This is Git publication maintenance only. No simulation evidence was modified,
regenerated or reclassified. No actual remote push or force push is performed.

## Before / verified remote / backup

- Branch: `development/regrip-autonomous-research`; initial working tree clean.
- Original HEAD: `0f5e603756a203b236a967339abf34b88cac11fe`.
- Successfully fetched remote base: `67906a68b3231a77efbde6efc8b57613246e7ec2`.
- Remote behind/ahead comparison:0 remote-only /43 local-only commits,no merges.
- Backup directory OUTSIDE the repo:
  `/media/ubuntu/99419895-2058-45b4-b746-b36ea7112e4e/research/LHJ/ReGrip_git_backups/detector-cleanup-20261123-2nd77m/`.
- `pre-cleanup-all-refs.bundle`:complete24-ref history,`git bundle verify` PASS.
  SHA256 `8ab9061f92364c48b24ed008355d5dced9cf187a71e13514202847133c1e9574`.
- `pre-cleanup.git`:independent non-hardlinked bare copy,full`git fsck` PASS.
- `raw/`:independent full copies of the five CSVs,not links or truncated samples.
  Original/copy SHA256 values agree;see `backup_manifest.json` in backupdir.
- Local recovery ref: `refs/backup/regrip-before-detector-cleanup-20261123`
  retains the original HEAD. This is deliberately NOT a branch to publish.

## Exact removal scope

Only these five paths were excluded from unpublished commit trees:

| Path below `product_prototype/results/` | Git blob bytes |
|---|---:|
| `product_root_bearing832/detector.csv` | 141175634 |
| `product_root_intersection817/detector.csv` | 153024553 |
| `product_root_intersection819/detector.csv` | 153784595 |
| `product_root_wire_section845/detector.csv` | 117178305 |
| `product_root_wire_section846/detector.csv` | 117169625 |

All five original files still exist at their ORIGINAL working-tree paths with
unchanged SHA256. They are now local ignored Raw,not Git-tracked artifacts.
The other11previously tracked detector files remain tracked and unchanged.
No entire results directory was removed. Existing code,CAD,reports,manifests,
binary/source snapshots,other Raw and PASS/FAIL evidence remain byte-identical.

## Method / exhaustive audit

`git filter-repo` was executed ONLY in the separate `rewrite.git` bare clone,
using five exact `--path` arguments, `--invert-paths`, and
`--refs 67906a6..refs/heads/development/regrip-autonomous-research`.
`--preserve-commit-hashes` preserves literal historical hashes in messages;
`--prune-empty never --prune-degenerate never` preserves all43commit positions.
Its local `--force` safety override is NOT `git push --force`.

`git_cleanup_20261123/history-audit.json` verifies EACH of43old/new commit pairs:

- No changed tree path outside the five exact CSV paths.
- Commit author/committer/encoding/message headers match exactly.
- Parent relationship matches the old→new mapping;no commits removed.
- Remote base remains an ancestor and itself is not rewritten.
- Tip-to-tip diff is EXACTLY the five CSV removals.

16early commit IDs remain identical;27IDs changed because of tree/parent hashes.
The full mapping is `git_cleanup_20261123/commit-map.txt` (SHA256
`cc834d363c1931ae97cddfbfdf2b2055c5a5d016cae96a9001a6a786ff80b28f`).
Cleaned research HEAD before this maintenance commit:
`012c31637b0d151808e9366114be39abd7cb9607`.

The original repository imported only the rewritten branch objects,created the
local recovery ref,and used compare-and-swap `git update-ref` plus **mixed**
index reset. No checkout,hard reset,working-tree CSV deletion or GC/prune was
used. Existing other branches/tags/origin configuration were not rewritten.

Full cleaned-branch reachable history AND unpublished range were scanned,not
only current files: **zero blobs ≥100000000bytes**,stricter than100MiB.
Largest blob37982185bytes:
`product_prototype/meshes/b3_rail_edge_clamp_v45/full_assembly_recipe.json`.
Original large blobs intentionally remain reachable from the LOCAL recovery
ref/bundle,not from the cleaned publication branch.

## Ignore / normal push / recovery

Root`.gitignore` now explicitly contains:
```
/product_prototype/results/**/detector.csv
```
The existing nested `product_prototype/.gitignore` also ignores `/results/`.
Already tracked smaller files are not untracked by adding this rule. Do not
use `git add -f` on detector journals. Summaries and hashes still refer to the
unchanged local originals;this cleanup does not make local Raw downloadable.

Normal explicit-branch push,when the user elects to publish:
```
git push origin HEAD:refs/heads/development/regrip-autonomous-research
```
No force push is required while remote tip remains the verified ancestor.
Do NOT push backup refs or use `--mirror`. If remote advances,fetch/recheck
ancestry first;do not force-overwrite another contributor's changes.
An actual push is NOT authorized/performed by this cleanup task.

Non-destructive recovery:clone the complete bundle into a NEW directory:
```
git clone -b development/regrip-autonomous-research /ABS/BACKUP/pre-cleanup-all-refs.bundle recovered-regrip
```
Use the exact backup directory above in place of `/ABS/BACKUP`. `raw/` contains
the independent CSV copies. Do not reset/overwrite the active cleaned tree to
restore history merely for inspection.

## Research continuation

Research scope is unchanged:exact service proofs and finite0.30mmpressure shoe
are CAD/reference results,not full Native joint/grasp qualification.125software
tests previously passed;no physics rerun was needed for a Git-only change.
Physical material/preload/slip/indentation data,thread/retention interface,
time/mesh/100g/Lift/STEP remain open. Continue from
`RAIL_SEPARATION_AND_PRESSURE_SHOE_20261123.md` and actual existing Raw.
Historical source SHA values in evidence are deliberately unchanged and remain
resolvable through the recovery ref/bundle;use the mapping rather than editing
old manifests or pretending binaries were built from rewritten commits.

Key old→new research commits:

- `18dea00` → `3ca56702ba8c7830f370bd78bcd11c80b1f78e2f`.
- `5c1a99b` → `f28a16aa5b653af8dd809b579ba36574ea6a469f`.
- `0f5e603` → `012c31637b0d151808e9366114be39abd7cb9607`.
