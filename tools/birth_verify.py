"""Read-only new campaign integrity verification."""
import argparse,json
from birth_common import ROOT,identity,sha
def main():
    p=argparse.ArgumentParser();p.add_argument('--raw',action='store_true');a=p.parse_args();m=json.loads((ROOT/'reports/BIRTH_ENERGY_EVIDENCE_MANIFEST.json').read_text());identity();errors=[]
    for name,r in m['files'].items():
        if not a.raw and name.startswith(('results/','build/')):continue
        path=ROOT/name
        if not path.is_file() or path.stat().st_size!=r['bytes'] or sha(path)!=r['sha256']:errors.append(name)
    print(json.dumps(dict(status='FAIL' if errors else 'PASS',errors=errors,entries=len(m['files']),raw=a.raw)));return bool(errors)
if __name__=='__main__':raise SystemExit(main())
