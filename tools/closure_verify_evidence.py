"""Read-only closure manifest verifier; raw validation is optional but reproducible."""
import argparse,json
from pathlib import Path
from closure_common import ROOT,sha
def main():
    p=argparse.ArgumentParser();p.add_argument('--raw',action='store_true');a=p.parse_args();m=json.loads((ROOT/'reports/CLOSURE_EVIDENCE_MANIFEST.json').read_text());errors=[];checked=0
    for group in ('source_sha256','binary_sha256','runtime_sha256','report_sha256','evidence_sha256'):
        for name,digest in m[group].items():
            path=Path(name) if Path(name).is_absolute() else ROOT/name;checked+=1
            if not path.is_file() or sha(path)!=digest:errors.append(group+':'+name)
    if a.raw:
        for name,item in m['raw_files'].items():
            path=Path(m['raw_root'])/name;checked+=1
            if not path.is_file() or path.stat().st_size!=item['bytes'] or sha(path)!=item['sha256']:errors.append('raw:'+name)
    print(json.dumps(dict(checked=checked,errors=errors,full_grasp_certified=False),ensure_ascii=False));raise SystemExit(bool(errors))
if __name__=='__main__':main()
