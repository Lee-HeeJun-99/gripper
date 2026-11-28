"""Read-only worker preflight; unchanged Supervisor remains the final authority.

Always use the MANAGER checkpoint_beforeN.json, never a worker-created inventory.
Reports/seals belong under ignored runtime so generating them cannot change delta.
No Git writes, auto-list repairs, baseline changes, exclusions or cleanup.
"""
import argparse
import hashlib
import json
from pathlib import Path
from supervised_save import changed, untracked, safe_path, validate, git, digest
from goal_manager_policy import engineering_record


def inspect(repo, request, checkpoint, pins=None):
    repo = Path(repo)
    old = set(checkpoint['preexisting_untracked'])
    actual = changed(repo) | (untracked(repo) - old)
    records = request.get('files', [])
    names = [r['path'] for r in records]
    listed = set(names)
    errors = []
    invalid = []
    stale = []
    for record in records:
        try:
            path = safe_path(repo, record['path'])
            if digest(path) != record.get('SHA256'):
                stale.append(record['path'])
        except (ValueError, OSError) as exc:
            invalid.append(dict(path=record['path'], error=str(exc)))
    pin_errors = [p for p, h in (pins or {}).items()
                  if not (repo / p).is_file() or digest(repo / p) != h]
    trusted_listed = sorted(listed & set(pins or {}))
    if pin_errors or trusted_listed:
        errors.append('Trusted source mismatch or trusted source in worker manifest')
    record = None
    try:
        validate(repo, request, checkpoint['HEAD'], old)
        record = engineering_record(request, repo)
    except (ValueError, KeyError, OSError) as exc:
        errors.append(type(exc).__name__ + ': ' + str(exc))
    return dict(status='SAVE_PREFLIGHT_PASS' if not errors else 'SAVE_PREFLIGHT_FAIL',
                expected_HEAD=checkpoint['HEAD'], actual_HEAD=git(repo, 'rev-parse', 'HEAD'),
                original_preexisting_count=len(old), actual_change_count=len(actual),
                listed_count=len(names), missing=sorted(actual-listed), extra=sorted(listed-actual),
                duplicate_paths=sorted({n for n in names if names.count(n)>1}),
                preexisting_user_paths_listed=sorted(listed & old), stale_hashes=stale,
                invalid_paths=invalid, trusted_source_errors=pin_errors,
                trusted_sources_listed=trusted_listed, errors=errors, engineering=record,
                scope='Read-only exact manifest preflight, not physical approval or save')


def seal(repo, request_path, checkpoint_path, pins):
    """Bind exact request, manager baseline, scope and contents for a final recheck."""
    request = json.loads(request_path.read_text())
    checkpoint = json.loads(checkpoint_path.read_text())
    report = inspect(repo, request, checkpoint, pins)
    if report['status'] != 'SAVE_PREFLIGHT_PASS':
        raise ValueError(json.dumps(report))
    return dict(request_SHA256=digest(request_path), checkpoint_SHA256=digest(checkpoint_path),
                changed_hashes={r['path']:r['SHA256'] for r in request['files']},
                HEAD=checkpoint['HEAD'], source_pins=pins, report=report)


def verify(repo, request_path, checkpoint_path, pins, sealed):
    current = seal(repo, request_path, checkpoint_path, pins)
    if current != sealed:
        raise ValueError('Files/request/checkpoint/pins changed after preflight seal')
    return current['report']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument('--checkpoint', type=Path, required=True)
    parser.add_argument('--request', type=Path, required=True)
    parser.add_argument('--ledger', type=Path, required=True)
    parser.add_argument('--seal', type=Path)
    parser.add_argument('--verify-seal', type=Path)
    args = parser.parse_args()
    pins = json.loads(args.ledger.read_text())['source_pins']
    # Require an ignored runtime output, never write research files during preflight.
    if args.seal:
        target = args.seal.resolve()
        runtime = (args.repo/'product_prototype/stage12_integrated/runtime').resolve()
        if runtime not in target.parents or target.exists():
            raise ValueError('Seal must be NEW ignored runtime file')
        relative = str(target.relative_to(args.repo.resolve()))
        if not git(args.repo, 'check-ignore', '--', relative):
            raise ValueError('Seal output must be ignored')
    try:
        if args.verify_seal:
            report = verify(args.repo, args.request, args.checkpoint, pins,
                            json.loads(args.verify_seal.read_text()))
        else:
            report = inspect(args.repo, json.loads(args.request.read_text()),
                             json.loads(args.checkpoint.read_text()), pins)
        if args.seal and report['status']=='SAVE_PREFLIGHT_PASS':
            args.seal.write_text(json.dumps(seal(args.repo,args.request,args.checkpoint,pins),indent=2)+'\n')
    except (ValueError, KeyError, OSError) as exc:
        report = dict(status='SAVE_PREFLIGHT_FAIL', error=str(exc))
    print(json.dumps(report, indent=2))
    return 0 if report['status']=='SAVE_PREFLIGHT_PASS' else 2


if __name__=='__main__':
    raise SystemExit(main())
