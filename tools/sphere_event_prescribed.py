"""Solver-free chord-event reference; phase errors are NOT silently discarded."""
import argparse,csv,io,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--substeps',type=int,default=32,choices=[32,128,512]);a=p.parse_args()
 if not a.tag.replace('_','').isalnum():raise ValueError('tag')
 out=ROOT/'results'/('sphere_event_prescribed_'+a.tag);out.mkdir(exist_ok=False)
 source=ROOT/'diagnostics/temporal_event/Prescribed.cpp';binary=out/'reference'
 sources=list((ROOT/'models').rglob('*.h'))+[source,ROOT/'tools/sphere_event_prescribed.py']
 write_json(out/'identity.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(p.relative_to(ROOT)):sha(p)for p in sources}))
 for p in sources:
  q=out/'sources'/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
 build=logged(['g++','-O2','-std=c++17',source,'-o',binary],out/'build',180)
 if build['exit_code']:raise RuntimeError('compile failure preserved')
 run=logged([binary,str(a.substeps)],out/'run',480)
 if run['exit_code']:raise RuntimeError('run failure preserved')
 rows={}
 for r in csv.DictReader(io.StringIO((out/'run/stdout.log').read_text())):rows.setdefault(int(r['steps']),[]).append(r)
 comparisons=[]
 for c,f in ((20,40),(20,80),(40,80)):
  fine={round(float(r['time']),12):r for r in rows[f]};previous0=previous1=0;errors=[];absolute=[]
  for r in rows[c]:
   v0=float(r['plastic']);v1=float(fine[round(float(r['time']),12)]['plastic']);d0=v0-previous0;d1=v1-previous1
   errors.append(abs(d0-d1)/abs(d1)if d1 else (0 if not d0 else None));absolute.append(abs(d0-d1));previous0=v0;previous1=v1
  comparisons.append(dict(steps=[c,f],max_phase_relative=max((v for v in errors if v is not None),default=0),max_phase_absolute=max(absolute),undefined=any(v is None for v in errors),status='PASS'if all(v is not None and v<=.001 for v in errors)else'FAIL'))
 result=dict(source='independent prescribed mathematics;no SOFA/solver',substeps=a.substeps,binary_sha256=sha(binary),comparisons=comparisons,status='PASS'if all(v['status']=='PASS'for v in comparisons)else'FAIL')
 write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
