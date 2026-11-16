"""Isolate return/time error with prescribed geometry, not SOFA free dynamics."""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
 if not a.tag.replace('_','').isalnum():raise ValueError('simple unique tag')
 out=ROOT/'results'/('vector_history_prescribed_'+a.tag);out.mkdir(exist_ok=False)
 sources=[ROOT/f for f in ('models/general_vector_history/Owner.h','models/general_vector_history/AdaptiveMaterialRule.h','tests/test_general_prescribed.cpp','tools/curve_general_prescribed.py')]
 write_json(out/'identity.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(p.relative_to(ROOT)):sha(p)for p in sources},scope='prescribed moving Hermite/sphere friction isolation;NOT SOFA'))
 for p in sources:
  d=out/'sources'/p.relative_to(ROOT);d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,d)
 binary=out/'test.bin';stages={}
 stages['build']=logged(['g++','-std=c++17','-O2','-ffp-contract=off',ROOT/'tests/test_general_prescribed.cpp','-o',binary],out/'build',120)
 if stages['build']['exit_code']:write_json(out/'summary.json',dict(status='FAIL',stages=stages));return
 rows={}
 for n in (20,40,80):
  stages[str(n)]=logged([binary,str(n)],out/str(n),480)
  if stages[str(n)]['exit_code']:break
  rows[n]=list(csv.DictReader((out/str(n)/'stdout.log').open()))
 contrasts=[]
 for i,j in ((20,40),(20,80),(40,80)):
  if i not in rows or j not in rows:continue
  lookup={round(float(r['time']),12):r for r in rows[j]};previous0=previous1=0;phases=[]
  for r in rows[i]:
   u=lookup[round(float(r['time']),12)];x=float(r['plastic_cumulative']);y=float(u['plastic_cumulative']);d0=x-previous0;d1=y-previous1
   phases.append(dict(time=float(r['time']),absolute=abs(d0-d1),relative=abs(d0-d1)/abs(d1)if d1 else(0 if not d0 else None)));previous0=x;previous1=y
  contrasts.append(dict(steps=[i,j],phase_loss=phases,status='PASS'if all(q['relative']is not None and q['relative']<=.001 for q in phases)else'FAIL'))
 write_json(out/'summary.json',dict(process_status='PASS'if len(rows)==3 else'FAIL',time_gate='PASS'if len(contrasts)==3 and all(c['status']=='PASS'for c in contrasts)else'FAIL',contrasts=contrasts,stages=stages,binary_sha256=sha(binary)))
 print(json.dumps(dict(out=str(out),completed=len(rows))))
if __name__=='__main__':main()
