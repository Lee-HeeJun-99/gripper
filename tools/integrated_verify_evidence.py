"""Read-only validation of integrated reports and raw artifact identities."""
import argparse
import json
from integrated_common import ROOT,sha

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--raw',action='store_true');args=parser.parse_args()
    manifest=json.loads((ROOT/'reports/INTEGRATED_EVIDENCE_MANIFEST.json').read_text());errors=[];checked=0
    for category in ('source_sha256','evidence_sha256','report_sha256','binary_sha256'):
        for name,digest in manifest.get(category,{}).items():
            p=ROOT/name;checked+=1
            if not p.is_file() or sha(p)!=digest:errors.append(category+': '+name)
    if args.raw:
        from pathlib import Path
        for item in manifest['raw_evidence'].values():
            p=Path(item['raw']);checked+=1
            if not p.is_file() or sha(p)!=item['raw_sha256']:errors.append('raw: '+str(p))
        # Inspect actual trial payloads, excluding deliberate corruption fixtures.
        raw_root=Path(manifest['raw_root'])
        groups=('multilayer','tendon','friction','contact','finite_beam','objective_connector','candidate_validation',
                'warmstart','solver_retry','additional_convergence','hardening_regression',
                'finite_metric_correction_rerun','strict_residual_retry')
        for group in groups:
            for record in (raw_root/group).rglob('metrics.json'):
                data=json.loads(record.read_text())
                for name,digest in data.get('artifacts',{}).items():
                    p=record.parent/name;checked+=1
                    if not p.is_file() or sha(p)!=digest:errors.append('trial artifact: '+str(p))
    print(json.dumps(dict(checked=checked,errors=errors)))
    if errors:raise SystemExit(1)

if __name__=='__main__':main()
