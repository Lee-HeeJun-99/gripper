"""Validate completed experiment payloads before reusing them in any search."""
import json
from pathlib import Path
from integrated_common import BUILD,sha
from integrated_build import sources

def verify_trial(directory,require_equilibrium=True):
    directory=Path(directory);record=json.loads((directory/'metrics.json').read_text())
    manifest=json.loads((BUILD/'plugin/manifest.json').read_text())
    if manifest['sources']!=sources() or manifest['binary_sha256']!=sha(BUILD/'plugin/libReGripIntegrated.so'):raise ValueError('current build/source mismatch')
    if record.get('binary_sha256')!=manifest['binary_sha256']:raise ValueError('trial/current binary mismatch')
    if not record.get('artifacts'):raise ValueError('missing artifact manifest')
    for name,digest in record['artifacts'].items():
        p=directory/name
        if not p.is_file() or sha(p)!=digest:raise ValueError('corrupt experiment artifact: '+name)
    if require_equilibrium and (record.get('status')!='PASS' or not record.get('equilibrium_validated')):raise ValueError('non-equilibrium result has no performance objective')
    return record
