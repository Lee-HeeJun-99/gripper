"""Read-only audit of ALL newly reachable objects, not just current files."""
import argparse,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
out=ROOT/'validation/integrated'/a.tag;out.mkdir(parents=True,exist_ok=False)
baseline='c0e5dfdc6fe3812b8bbd09ed3392e239a30aca2a'
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
ancestor=subprocess.run(['git','merge-base','--is-ancestor',baseline,head]).returncode==0
objects=subprocess.check_output(['git','rev-list','--objects',baseline+'..'+head],text=True).splitlines()
paths={x.split(' ',1)[0]:x.split(' ',1)[1] if ' ' in x else '' for x in objects}
output=subprocess.check_output(['git','cat-file','--batch-check=%(objectname) %(objecttype) %(objectsize)'],input=('\n'.join(paths)+'\n').encode()).decode().splitlines()
blobs=[]
for line in output:
    h,kind,size=line.split()
    if kind=='blob':blobs.append(dict(SHA=h,bytes=int(size),path=paths[h]))
bad=[x for x in blobs if x['bytes']>=50_000_000]
result=dict(status='PASS' if ancestor and not bad else 'FAIL',audited_HEAD=head,baseline=baseline,baseline_ancestor=ancestor,
    new_blob_count=len(blobs),new_blobs_at_least_50MB=bad,largest=sorted(blobs,key=lambda x:x['bytes'],reverse=True)[:5],
    command='python scripts/new_blob_audit.py --tag '+a.tag)
(out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
