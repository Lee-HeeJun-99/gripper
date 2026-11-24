# Unpublished layer_pairs.csv history cleanup — 2026-11-24

User explicitly authorized this targeted repair. No SOFA/research execution,
Raw deletion, force push, remote push or published-history modification.

## Scope and result

- Branch: `development/regrip-autonomous-research`.
- GitHub live remote HEAD, checked twice: `9d954a848e71b2def357b49ed9ff7fc13cdec45f`.
- Initial clean local HEAD: `6611a8eabc62d300832a6adf46754928a1d2d38a`.
- 30 unpublished commits audited; 21 unchanged, 9 rewritten. No commit dropped.
- Repaired history tip before this documentation commit:
  `00e9713c1b52c3aeda215219f1274903e53ba3ad`.
- Only removed tracked path:
  `product_prototype/results/layer_mesh_native1260/layer_pairs.csv`.
- Blob: `5ab9fca074a337bb5b869aaa0a4a1db75a924c67`, 128561058 bytes
  (122.61 MiB). It was the ONLY >=100000000-byte blob in the push range.
- CSV SHA256, identical original and external backup:
  `ad90ceea5e3856329c6efbbb8ebe6baa3c02155cc73af99d74034ca168782539`.
- All 30 before/after commit snapshots compared by mode/type/blob/path,
  excluding ONLY this CSV. Author/committer/message and mapped parent links
  identical. Published base object identical; every unrelated ref identical.
- Repaired range has zero >=100000000-byte blobs. Remote base is ancestor:
  ordinary branch-specific fast-forward push is possible while remote unchanged.
- Existing Raw, source snapshots, manifests and historical PASS/FAIL records
  remain byte-identical. Old Source Commit fields intentionally retain original
  provenance; map below and backup ref preserve access to those identities.

## Independent external backups

Directory (outside repository):
`/media/ubuntu/99419895-2058-45b4-b746-b36ea7112e4e/research/LHJ/regrip_backups/git-layer-repair-20261124-4QWM41/`

- `git-directory.tar`: complete `.git`, including refs/reflogs/unreachable
  objects. Extracted to `archive-check/`; `git fsck --full --no-reflogs` exit0,
  only dangling objects reported (not corruption).
  SHA256 `9952efd7c8710a43541ae0c1749e8a70559941a83f1f8244284be4399ec7a897`.
- `all-refs.bundle`: complete reachable history, no prerequisite commits;
  `git bundle verify` PASS. SHA256
  `e843657a0a0484026887df3115e8fcc7b5b73a623aa49226a0cf4d0499338a2d`.
- `layer_pairs.csv`: original exact bytes; `cmp` PASS.
- `before.json`, `after.json`, `audit.py`: object/range inventory and complete
  30-commit comparisons. `rewrite.git/`: independently copied temporary bare
  repository where filtering and all checks ran BEFORE applying to source.

New local recovery ref:
`refs/backup/regrip-before-layer-cleanup-20261124` → original `6611a8e`.
Existing detector recovery ref and all older external backups untouched:
`refs/backup/regrip-before-detector-cleanup-20261123` → `0f5e603`.
Old large blobs intentionally remain reachable through recovery refs/bundles;
do NOT push `--mirror`, `--all`, or backup refs. Push-range scanning is the
relevant GitHub check, not deletion of recovery evidence from local objects.

## Commit mapping (changed only)

```
9a8d4a89a408380715f0d8c41415d71b34f72124 46abd11ba5cec5c62a5f133a8eb4393364c5dcf2
981e03567ffcb0ea36fbd486e8845be3a60462aa d016357c8ef8e7d7bb8f97b0fa0380ccac663eae
e8ab6bab144d2f49e56686aef6481785081dae70 fd1881da98058c00e04da9104ab45ceaf6eea871
7cc66712289875fa2df939cde5c4230d89d06e2b f830c40d82b6ca8262da82bb66ecdbb1121caeb1
70526235cebaabdab12774deb83407b3a9308506 11f7d2d291236838524d6fa7e530d5ec86669e6c
4372ac100f699cb9588eb3d985cb7ba505ae8150 b69bdc7ded4fde7aa80767d6fb4dfab4d46e845f
c3d2e9e65fe95d01f0323d7a41eec998f7a481c8 49e5337e285e3b8e5cda6ef47d0c1d90ddc2a630
26459719039dfe2d886352204bba238a194767fd 5cb69f12098c3156a342ca7c9d2a2655c8021c69
6611a8eabc62d300832a6adf46754928a1d2d38a 00e9713c1b52c3aeda215219f1274903e53ba3ad
```

## Method and recovery

Temporary mirror cloned from the verified external `.git` archive copy,
with `--no-hardlinks`. Only explicit unpublished range was filtered:

```
git filter-repo --force --partial --prune-empty never --prune-degenerate never --path product_prototype/results/layer_mesh_native1260/layer_pairs.csv --invert-paths --refs 9d954a848e71b2def357b49ed9ff7fc13cdec45f..refs/heads/development/regrip-autonomous-research
```

Source imported only repaired branch objects, created recovery ref, then used
`git read-tree` WITHOUT `-u` and compare-and-swap `git update-ref`. No checkout,
hard reset, original CSV removal, other-ref rewrite or automatic push.
Separate additive maintenance commit changes only ignore rule, this report,
checkpoint and NEXT notice; it is not part of research-history filtering.

For non-destructive recovery inspection, clone the external bundle to a NEW
directory (`git clone --mirror <backup>/all-refs.bundle <new-recovery.git>`),
or inspect `git show refs/backup/regrip-before-layer-cleanup-20261124:<path>`.
Do not reset the working repository or overwrite current work to recover.

Manual future publication, only if explicitly desired and remote still ancestor:
`git push origin HEAD:refs/heads/development/regrip-autonomous-research`.
No push executed by this repair. Research resume remains the section-refined
Native pilot described in the checkpoint; no research result was regenerated.
