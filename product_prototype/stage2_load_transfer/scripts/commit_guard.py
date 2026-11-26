"""Read-only staged blob guard; never stages, deletes or rewrites history."""
import json,subprocess
names=subprocess.check_output(['git','diff','--cached','--name-only','--diff-filter=ACMR','-z']).split(b'\0')
bad=[];largest=[]
for raw in names:
    if not raw:continue
    name=raw.decode();size=int(subprocess.check_output(['git','cat-file','-s',':'+name]))
    largest.append((size,name))
    if size>=50_000_000 or name.rsplit('/',1)[-1] in {'surface.csv','detector.csv','response_rows.csv','layer_pairs.csv'}:bad.append(dict(path=name,bytes=size))
result=dict(status='PASS' if not bad else 'FAIL',bad=bad,largest=sorted(largest,reverse=True)[:8],policy='No NEW staged >=50,000,000-byte blob or raw CSV names')
print(json.dumps(result,indent=2));raise SystemExit(0 if not bad else 2)
