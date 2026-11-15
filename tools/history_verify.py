"""Read-only verification; does not refresh a failing manifest."""
import argparse,json
from history_publish import ROOT,digest
def main():
    p=argparse.ArgumentParser();p.add_argument('--raw',action='store_true');args=p.parse_args();m=json.loads((ROOT/'reports/CONTACT_HISTORY_EVIDENCE_MANIFEST.json').read_text());errors=[];count=0
    for group in ('source_sha256','report_sha256','binary_sha256','evidence_sha256'):
        for name,want in m[group].items():
            count+=1;path=ROOT/name
            if not path.is_file() or digest(path)!=want:errors.append(group+':'+name)
    if args.raw:
        for name,r in m['raw_files'].items():
            count+=1;path=ROOT/name
            if not path.is_file() or path.stat().st_size!=r['bytes'] or digest(path)!=r['sha256']:errors.append('raw:'+name)
    print(json.dumps(dict(status='FAIL' if errors else 'PASS',checked=count,errors=errors,full_grasp_certified=False)));raise SystemExit(bool(errors))
if __name__=='__main__':main()
