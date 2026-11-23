"""Join actual child normal rows to unique detector outputs, never row-count area."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def vec(s):return np.fromstring(s,sep=' ')
def join(features,children,tol=1e-12):
 groups={}
 for c in children:groups.setdefault((c['previous_time_s'],c['constraint']),[]).append(c)
 records=[]
 for (time,owner),cs in groups.items():
  first=min(int(c['row']) for c in cs)
  for row in sorted({int(c['row']) for c in cs}):
   # Installed BaseContactLagrangianConstraint: normal followed by 2 tangent rows at mu>0.
   if (row-first)%3:continue
   sides={int(c['side']):c for c in cs if int(c['row'])==row}
   # A shared surface state contains other constraints' rows. Require both
   # owner sides before attribution, rather than assigning every child row.
   if len(sides)!=2:continue
   a,b=sides[0],sides[1];matches=[]
   for f in features:
    if f['previous_time_s']!=time:continue
    if not a['state'].startswith(f['model0'].rsplit('/',1)[0]+'/') or not b['state'].startswith(f['model1'].rsplit('/',1)[0]+'/'):continue
    ep=max(float(abs(vec(a['point'])-vec(f['point0'])).max()),float(abs(vec(b['point'])-vec(f['point1'])).max()))
    en=max(float(abs(vec(a['J'])+vec(f['normal'])).max()),float(abs(vec(b['J'])-vec(f['normal'])).max()))
    if ep<=tol and en<=tol:matches.append((f,ep,en))
   r=dict(previous_time_s=float(time),constraint=owner,row=row,match_count=len(matches))
   if len(matches)==1:
    f,ep,en=matches[0];r.update(detector=f,point_match_abs_m=ep,normal_match_abs=en,normal=vec(f['normal']).tolist(),point_separation_m=float(np.linalg.norm(vec(f['point1'])-vec(f['point0']))))
   records.append(r)
 return records
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/contact_provenance_run1222';files=[src/'provenance.features.csv',src/'provenance.children.csv'];f,c=[list(csv.DictReader(x.open())) for x in files];records=join(f,c);all_unique=bool(records) and all(r['match_count']==1 for r in records)
 times=[]
 for t in sorted({r['previous_time_s'] for r in records}):
  rr=[r for r in records if r['previous_time_s']==t];times.append(dict(previous_time_s=t,normal_rows=len(rr),horizontal_normals=sum(abs(r.get('normal',[0,0,9])[2])<1e-10 for r in rr),unique=sum(r['match_count']==1 for r in rr),model_pairs=sorted({r['detector']['model0']+' | '+r['detector']['model1'] for r in rr if 'detector'in r})))
 d=dict(status='PASS_UNIQUE_FEATURE_ROW_PROVENANCE_ONLY' if all_unique else 'FAIL_AMBIGUOUS_PROVENANCE',normal_rows=len(records),all_unique=all_unique,times=times,records=records,identity_matching_tolerance=1e-12,matching_tolerance_scope='read-only coordinate/J identity matching,not contact clearance or time gate',row_layout='installed Native mu=.3 normal,tangent,tangent order;not arbitrary constraint assumption',physical_validation='NOT QUALIFIED',input_hashes={str(x.relative_to(BASE)):sha(x) for x in files},source_sha256=sha(Path(__file__)))
 (out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in d.items() if k!='records'}))
if __name__=='__main__':main()
