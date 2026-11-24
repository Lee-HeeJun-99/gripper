"""Fail closed on staged detector.csv / >=100MB blobs. Never rewrites history."""
import argparse,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def forbidden(path,size):
 return Path(path).name in {'detector.csv','layer_pairs.csv'} or size>=100_000_000
def staged():
 raw=subprocess.check_output(['git','diff','--cached','--name-only','--diff-filter=ACMR','-z'],cwd=ROOT);rows=[]
 for path in raw.decode().split('\0'):
  if not path:continue
  size=int(subprocess.check_output(['git','cat-file','-s',':'+path],cwd=ROOT));rows.append(dict(path=path,bytes=size,forbidden=forbidden(path,size)))
 return rows
def history(since):
 raw=subprocess.check_output(['git','rev-list','--objects',since+'..HEAD'],cwd=ROOT);output=subprocess.run(['git','cat-file','--batch-check=%(objecttype) %(objectsize) %(rest)'],input=raw,capture_output=True,check=True,cwd=ROOT).stdout.decode().splitlines();bad=[]
 for line in output:
  typ,size,path=(line.split(' ',2)+[''])[:3]
  if typ=='blob' and forbidden(path,int(size)):bad.append(dict(path=path,bytes=int(size)))
 return bad
def main():
 p=argparse.ArgumentParser();p.add_argument('--since');p.add_argument('--stage-results',nargs='+',help='Explicit result folder names;stage only safe files,leave excluded Raw untouched');a=p.parse_args();excluded=[]
 if a.stage_results:
  if any(r['forbidden'] for r in staged()):raise SystemExit('existing staged forbidden blob:refuse additional staging')
  safe=[];results=ROOT/'product_prototype/results'
  for name in a.stage_results:
   if Path(name).name!=name:raise SystemExit('result basename required')
   folder=results/name
   if not folder.is_dir():raise SystemExit('result missing:'+name)
   for f in folder.rglob('*'):
    if f.is_symlink():raise SystemExit('symlink staging not allowed')
    if not f.is_file():continue
    rel=str(f.relative_to(ROOT));size=f.stat().st_size
    if forbidden(rel,size):excluded.append(dict(path=rel,bytes=size))
    else:safe.append(rel)
  if safe:subprocess.run(['git','add','-f','--',*safe],cwd=ROOT,check=True)
 rows=staged();bad=[r for r in rows if r['forbidden']];old=history(a.since) if a.since else [];d=dict(status='FAIL_GIT_BLOB_POLICY' if bad or old else 'PASS_SCOPED_GIT_BLOB_CHECK',staged_files=len(rows),staged_forbidden=bad,excluded_raw_preserved=excluded,history_since=a.since,history_forbidden=old,scope='No history repair or Raw deletion;staging only if explicitly requested');print(json.dumps(d,indent=2));raise SystemExit(bool(bad or old))
if __name__=='__main__':main()
