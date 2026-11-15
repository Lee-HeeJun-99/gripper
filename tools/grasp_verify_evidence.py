"""Non-mutating verifier for current sources and immutable new/old raw evidence."""
import json,argparse
from pathlib import Path
from grasp_common import ROOT
from grasp_publish import digest
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--raw',action='store_true');args=parser.parse_args();m=json.loads((ROOT/'reports/GRASP_EVIDENCE_MANIFEST.json').read_text());errors=[];checked=0
    for group in ('source_sha256','binary_sha256','report_sha256','evidence_sha256'):
        for path,h in m[group].items():
            checked+=1;p=ROOT/path
            if not p.is_file() or digest(p)!=h:errors.append(path)
    for path,h in m.get('external_runtime_sha256',{}).items():
        checked+=1;p=Path(path)
        if not p.is_file() or digest(p)!=h:errors.append('runtime:'+path)
    if args.raw:
        for path,item in m['raw_files'].items():
            checked+=1;p=Path(m['raw_root'])/path
            if not p.is_file() or p.stat().st_size!=item['bytes'] or digest(p)!=item['sha256']:errors.append('raw:'+path)
    print(json.dumps(dict(checked=checked,errors=errors,full_grasp_certified=m['full_grasp_certified'])))
    if errors:raise SystemExit(1)
if __name__=='__main__':main()
