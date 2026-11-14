"""Read-only source/build/report/raw integrity check, including failed trials."""
import argparse
import json
from pathlib import Path
from stabilization_common import ROOT,sha

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--raw',action='store_true');args=parser.parse_args()
    manifest=json.loads((ROOT/'reports/STABILIZATION_EVIDENCE_MANIFEST.json').read_text());errors=[];checked=0
    def check(path,digest,label):
        nonlocal checked
        checked+=1
        if not path.is_file() or sha(path)!=digest:errors.append(label+': '+str(path))
    for category in ('source_sha256','binary_sha256','report_sha256','evidence_sha256'):
        for name,digest in manifest[category].items():check(ROOT/name,digest,category)
    if args.raw:
        for item in manifest['raw_evidence'].values():check(Path(item['raw']),item['sha256'],'raw evidence')
        for record in Path(manifest['raw_root']).rglob('metrics.json'):
            data=json.loads(record.read_text())
            for name,digest in data.get('artifacts',{}).items():check(record.parent/name,digest,'trial artifact')
    print(json.dumps(dict(checked=checked,errors=errors)))
    if errors:raise SystemExit(1)

if __name__=='__main__':main()
