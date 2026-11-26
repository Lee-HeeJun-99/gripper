"""Independent STEP reimport and full retained-part collision reproduction."""
import sys,json,math,shutil
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,rotate,volume,bounds,solid_count,overlap
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepCheck import BRepCheck_Analyzer
out=ROOT/'validation/transmission/AU_prehead_verify1';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
src=ROOT/'validation/transmission/AU_prehead_access1/summary.json';d=json.loads(src.read_text());inp=json.loads((REPO/d['inputs']['path']).read_text())
refs=[d['inputs'],inp['candidate'],inp['producer'],*inp['dependencies'],*inp['parts'].values(),*[r['shape'] for r in d['rows']]]
assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs)
dump(out/'inputs.json',dict(result=ref(src),producer=ref(out/'producer.py'),references=refs))
parts={n:read(REPO/r['path']) for n,r in inp['parts'].items()};checks=[]
for r in d['rows']:
 assert not (ROOT/'runtime/STOP').exists()
 s=read(REPO/r['shape']['path']);local=rotate(s,-120*r['sector']);phase=r['phase'];bb=bounds(local)
 if phase.startswith('preform'):
  sweep='sweep' in phase;length=8.7 if sweep else .7
  expected_volume=math.pi*(.9**2*length+.5**2*6.8)
  expected_x=(32 if sweep else 40,47.5);radius=.9
 else:
  right=phase.startswith('right');length=15 if 'approach' in phase else 10;radius=1.2 if right else .9
  expected_volume=math.pi*radius**2*length;expected_x=(48,48+length) if right else (40-length,40)
 dims=max(abs(bb[0]-expected_x[0]),abs(bb[3]-expected_x[1]),abs(bb[1]-(-6.1-radius)),abs(bb[4]-(-6.1+radius)),abs(bb[2]-(25-radius)),abs(bb[5]-(25+radius)))<1e-6 and abs(volume(s)-expected_volume)<1e-7
 hits=[]
 for n,p in parts.items():
  if n==f"F{r['sector']}_IDLER_CROSSPIN":continue
  if overlap(bounds(s),bounds(p)):
   op=BRepAlgoAPI_Common(s,p);op.Build();v=volume(op.Shape())
   if v>1e-8:hits.append(dict(part=n,common_mm3=v))
 old={h['part']:h['common_mm3'] for h in r['interferences']};new={h['part']:h['common_mm3'] for h in hits}
 agreement=old.keys()==new.keys() and all(abs(old[n]-new[n])<1e-8 for n in old)
 checks.append(dict(sector=r['sector'],phase=phase,dimensions_volume_pass=dims,valid=BRepCheck_Analyzer(s).IsValid() and solid_count(s)==1,interferences=hits,collision_reproduction_pass=agreement))
ok=all(c['dimensions_volume_pass'] and c['valid'] and c['collision_reproduction_pass'] for c in checks)
dump(out/'summary.json',dict(status='PASS' if ok else 'FAIL',scope='Identity, analytical preform/sweep/tool volumes and dimensions, independent complete retained-part intersections; reproduction does not qualify forming',inputs=ref(out/'inputs.json'),rows=checks,whole_system_release=False));print('verification',ok);raise SystemExit(0 if ok else 2)
