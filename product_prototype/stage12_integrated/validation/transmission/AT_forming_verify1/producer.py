"""Independent archived STEP reimport, dimensions and collision witness verification."""
import sys,json,math,shutil
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,volume,rotate,bounds,solid_count
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepCheck import BRepCheck_Analyzer
out=ROOT/'validation/transmission/AT_forming_verify1';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
src=ROOT/'validation/transmission/AT_forming_access1/summary.json';d=json.loads(src.read_text());inp=json.loads((REPO/d['inputs']['path']).read_text())
refs=[d['candidate'],d['inputs'],d['producer'],*inp['parts'].values(),*inp['dependencies'],*[r['tool'] for r in d['rows']]]
assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs)
dump(out/'inputs.json',dict(result=ref(src),producer=ref(out/'producer.py'),verified_references=refs))
checks=[]
for r in d['rows']:
 assert not (ROOT/'runtime/STOP').exists()
 tool=read(REPO/r['tool']['path']);local=rotate(tool,-120*r['sector']);bb=bounds(local)
 length=10 if r['phase']=='seated' else 15
 expected=(40-length,40) if r['side']=='left' else (48,48+length)
 # independent exact cylinder dimensions and integral, not a saved success flag
 dims=abs(volume(tool)-math.pi*1.2**2*length)<1e-7
 dims=dims and max(abs(bb[0]-expected[0]),abs(bb[3]-expected[1]),abs(bb[1]+7.3),abs(bb[4]+4.9),abs(bb[2]-23.8),abs(bb[5]-26.2))<1e-6
 witnesses=[]
 for h in r['interferences']:
  part=read(REPO/inp['parts'][h['part']]['path']);op=BRepAlgoAPI_Common(tool,part);op.Build();v=volume(op.Shape())
  witnesses.append(dict(part=h['part'],recomputed_mm3=v,pass_check=v>1e-8 and abs(v-h['common_mm3'])<1e-8))
 checks.append(dict(sector=r['sector'],side=r['side'],phase=r['phase'],local_bounds=bb,expected_axial_bounds=expected,analytic_volume_pass=dims,valid=BRepCheck_Analyzer(tool).IsValid() and solid_count(tool)==1,witnesses=witnesses))
ok=all(c['analytic_volume_pass'] and c['valid'] and all(h['pass_check'] for h in c['witnesses']) for c in checks)
dump(out/'summary.json',dict(status='PASS' if ok else 'FAIL',scope='Input identity, reimported die dimensions/integrals and every reported collision witness; not forming qualification',inputs=ref(out/'inputs.json'),rows=checks,whole_system_release=False));print('saved verification',ok);raise SystemExit(0 if ok else 2)
