"""Actual detector/row/multiplier join at line/face transition;read only."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from contact_provenance_assess import join
def assess(case):
 src=BASE/'results'/case;files=[src/'provenance.features.csv',src/'provenance.children.csv',src/'multipliers.csv',src/'rigid.csv'];data=[]
 for file in files:
  with file.open() as f:data.append(list(csv.DictReader(f)))
 f,c,mm,rr=data;matched=join(f,c,lines=1);assert matched and all(r['match_count']==1 for r in matched);records=[];maxerr=0.
 for t in sorted({r['previous_time_s'] for r in matched}):
  rows=[r for r in matched if r['previous_time_s']==t];m=min(mm,key=lambda r:abs(float(r['time_s'])-t-.0002));r=min(rr,key=lambda r:abs(float(r['time_s'])-t-.0002));assert abs(float(m['time_s'])-t-.0002)<1e-12
  impulses=np.fromstring(m['impulses_Ns'],sep=' ');parts={};N=[];claimed=[]
  for row in rows:
   d=row['detector'];assert d['model1'].startswith('/layer/');n=np.array(row['normal']);I=impulses[row['row']]*n;parts.setdefault(d['model0'],np.zeros(3));parts[d['model0']]+=I;N.append(n);claimed.append(row['row'])
  assert sorted(claimed)==list(range(len(impulses)))
  actual=np.fromstring(r['object_impulse_Ns_Nms'],sep=' ')[:3];err=float(abs(sum(parts.values())-actual).max());maxerr=max(maxerr,err);N=np.array(N);ev=np.linalg.eigvalsh(N@N.T);condition=float(ev[-1]/ev[0]) if ev[0]>0 else None
  records.append(dict(previous_time_s=t,accepted_time_s=float(r['time_s']),response_impulses_Ns=impulses.tolist(),impulse_by_model_Ns={k:v.tolist() for k,v in parts.items()},actual_total_impulse_Ns=actual.tolist(),impulse_join_error_Ns=err,normal_gram_eigenvalues=ev.tolist(),normal_gram_condition=condition,solver_iterations=int(m['iterations']),solver_error=float(m['error'])))
 return dict(case=case,status='PASS_FEATURE_IMPULSE_IDENTITY_ONLY' if maxerr<=1e-12 else 'FAIL_FEATURE_IDENTITY',maximum_impulse_join_error_Ns=maxerr,records=records,input_hashes={str(f.relative_to(BASE)):sha(f) for f in files},scope='Actual row multipliers are impulses Ns. Gram conditioning is independently computed normal geometry,NOT direct Native W observation. Not energy/time/product qualification.')
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);d=dict(status='SCOPED_FEATURE_IMPULSE_DIAGNOSTIC_ONLY',records=[assess(c) for c in ('primitive_center_impulses1247','primitive_offset_impulses1248')],physical_validation='NOT QUALIFIED',source_sha256=sha(Path(__file__)));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in d.items() if k!='records'}));print(json.dumps([{k:v for k,v in r.items() if k not in ('records','input_hashes')} for r in d['records']]))
if __name__=='__main__':main()
