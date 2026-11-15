"""Read-only verifier for the conservative-beam evidence; optional raw hashing."""
import argparse,json
from pathlib import Path
from beam_common import ROOT
from beam_publish import digest
def main():
    p=argparse.ArgumentParser();p.add_argument('--raw',action='store_true');a=p.parse_args();m=json.loads((ROOT/'reports/CONSERVATIVE_BEAM_EVIDENCE_MANIFEST.json').read_text());errors=[];count=0
    for group in ('source_sha256','report_sha256','binary_sha256','evidence_sha256'):
        for name,h in m[group].items():
            path=ROOT/name;count+=1
            if not path.is_file() or digest(path)!=h:errors.append(group+':'+name)
    if a.raw:
        for name,x in m['raw_files'].items():
            path=ROOT/name;count+=1
            if not path.is_file() or path.stat().st_size!=x['bytes'] or digest(path)!=x['sha256']:errors.append('raw:'+name)
    print(json.dumps(dict(status='PASS' if not errors else 'FAIL',checked=count,errors=errors,full_grasp_certified=False)));raise SystemExit(bool(errors))
if __name__=='__main__':main()
