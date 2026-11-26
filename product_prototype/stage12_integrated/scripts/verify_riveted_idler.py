"""Independent reimported signed motion and finite pin-escape tests."""
import sys,json,shutil
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,rotate,common,bounds,overlap,volume,solid_count
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.gp import gp_Trsf,gp_Vec
from OCP.BRepCheck import BRepCheck_Analyzer

def moved(s,x=0,y=0):
 t=gp_Trsf();t.SetTranslation(gp_Vec(x,y,0));return BRepBuilderAPI_Transform(s,t,True).Shape()
assert not (ROOT/'runtime/STOP').exists()
out=ROOT/'validation/transmission/AS_rivet_verify1';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
src=ROOT/'cad/exports/revAS_riveted1/summary.json';d=json.loads(src.read_text());rr=d['part_references']
assert all(sha(REPO/r['path'])==r['SHA256'] for r in rr.values())
dump(out/'inputs.json',dict(candidate=ref(src),parts=rr,producer=ref(out/'producer.py')))
rows=[];shapes={n:read(REPO/r['path']) for n,r in rr.items()}
for i in range(3):
 local={n:rotate(s,-120*i) for n,s in shapes.items()};prefix=f'F{i}_';a=local[prefix+'IDLER_AXLE'];p=local[prefix+'IDLER_CROSSPIN'];w=local[prefix+'IDLER_CLAMP_WASHER'];b=local[prefix+'IDLER_BRACKET']
 stop=[dict(dy_mm=y,pin_washer_mm3=common(moved(p,y=y),w),axle_bracket_mm3=common(moved(a,y=y),b)) for y in (-.11,-.01,0,.09,.11)]
 escape=[]
 for x in (-7,-3,-2,-1,0,1,2,3,7):
  assert not (ROOT/'runtime/STOP').exists()
  q=moved(p,x=x);bb=bounds(q);hits=[]
  for n,s in local.items():
   if n==prefix+'IDLER_CROSSPIN':continue
   if overlap(bb,bounds(s)):
    v=common(q,s)
    if v>1e-8:hits.append(dict(part=n,volume_mm3=v))
  escape.append(dict(dx_mm=x,interferences=hits))
 rows.append(dict(sector=i,valid_single_solids=all(BRepCheck_Analyzer(s).IsValid() and solid_count(s)==1 for s in (a,p)),axle_removed_volume_mm3=volume(read(REPO/json.loads((ROOT/'cad/exports/revAO_root2/summary.json').read_text())['part_references'][prefix+'IDLER_AXLE']['path']))-volume(a),signed_stops=stop,pin_escape_samples=escape))
checks=dict(valid_single_solids=all(r['valid_single_solids'] for r in rows),pin_positive_axial_stop=all(r['signed_stops'][-1]['pin_washer_mm3']>1e-8 for r in rows),sampled_pin_escape_clear=all(not x['interferences'] for r in rows for x in r['pin_escape_samples']))
r=dict(status='RIVET_FORMED_GEOMETRY_ONLY_NOT_QUALIFIED',candidate=ref(src),producer=ref(out/'producer.py'),inputs=ref(out/'inputs.json'),rows=rows,checks=checks,capacity_N=None,whole_system_release=False,conclusion='Post-formed integral heads tested in both pin-axis directions against all actual retained parts. Obstructed extraction also blocks rigid insertion; forming/tool access and capacity remain unqualified. No continuous path certificate. Do not adopt.',missing=['Finite pin end retention','Actual loaded contact/net-section/notch stress and material allowables','Full ordered assembly and loaded free spin','Protected maximum and same-revision system gates'])
dump(out/'summary.json',r);print(json.dumps(dict(status=r['status'],checks=checks)));raise SystemExit(2)
