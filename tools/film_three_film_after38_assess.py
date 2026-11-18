"""Exact-epoch all-pair qualification of the NEW38ms initial value problem."""
import argparse,csv,json,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
def error(x,y):
 x=np.asarray(x);y=np.asarray(y);absolute=float(np.linalg.norm(x-y));scale=max(float(np.linalg.norm(x)),float(np.linalg.norm(y)));relative=100*absolute/scale if scale else 0
 return dict(absolute_error=absolute,relative_error_percent=relative,pass_0p1_percent=relative<=.1)
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs=3,required=True);a=p.parse_args();cases=[]
 for name in a.cases:
  src=ROOT/'results'/('autonomous_film_'+name);meta=json.loads((src/'summary.json').read_text())
  if meta['status']!='PASS' or meta['process']['exit_code'] or meta['duration_s']!=.0064:raise ValueError('complete next-window references required')
  for file,digest in meta['raw_hashes'].items():
   if sha(src/file)!=digest:raise ValueError('immutable reference changed')
  cases.append((meta,list(csv.DictReader((src/'recovery.states.csv').open()))[-1],sha(src/'summary.json')))
 for key in ('actual_checkpoint_sha256','reference_binary_sha256'):
  if len({c[0][key] for c in cases})!=1:raise ValueError('different physical IVP/binary')
 if len({c[0]['metrics']['time'] for c in cases})!=1:raise ValueError('different actual observation epochs')
 pairs=[]
 for i,j in ((0,1),(1,2),(0,2)):
  errors={k:error(float(cases[i][0]['metrics'][k]),float(cases[j][0]['metrics'][k])) for k in ('U_skin','U_rails','U_attachment','K_film','K_body','minimum_gap_mm')}
  for key in ('q','v'):
   left=np.fromstring(cases[i][1][key],sep=' ');right=np.fromstring(cases[j][1][key],sep=' ');nf=(len(left)-6)//3
   if nf!=649 or len(right)!=len(left):raise ValueError('actual reduced topology differs')
   for finger in range(3):errors[f'film{finger}_{key}']=error(left[finger*nf:(finger+1)*nf],right[finger*nf:(finger+1)*nf])
   errors['body_'+key]=error(left[-6:],right[-6:])
  pairs.append(dict(cases=[a.cases[i],a.cases[j]],observables=errors,status='PASS' if all(v['pass_0p1_percent'] for v in errors.values()) else 'FAIL'))
 momentum=all(float(c[0]['metrics']['momentum_Ns'])<=1e-17 for c in cases)
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');result=dict(status='PASS' if momentum and all(p['status']=='PASS' for p in pairs) else 'FAIL',scope='independent38..44.4ms free endpoint subset;NOT actual SOFA extension/full time/recovery/grasp',time_gate_percent=.1,momentum_gate_Ns=1e-17,momentum_pass=momentum,source_summaries={name:c[2] for name,c in zip(a.cases,cases)},comparisons=pairs,actual_owner_scope_unchanged=True)
 write_json(out/'summary.json',result);print(json.dumps(dict(status=result['status'],pairs=[dict(cases=p['cases'],status=p['status'],maximum_percent=max(v['relative_error_percent'] for v in p['observables'].values())) for p in pairs])))
if __name__=='__main__':main()
