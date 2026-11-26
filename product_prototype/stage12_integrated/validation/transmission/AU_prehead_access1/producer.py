"""One-sided rivet assembly hypothesis: exact prehead insertion sweep and support access."""
import sys,json,shutil
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,cyl,rotate,common,bounds,overlap,export,volume,solid_count
from build_stage1 import fuse
from OCP.BRepCheck import BRepCheck_Analyzer
assert not (ROOT/'runtime/STOP').exists()
out=ROOT/'validation/transmission/AU_prehead_access1';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
src=ROOT/'cad/exports/revAS_riveted1/summary.json';d=json.loads(src.read_text());rr=d['part_references']
assert len(rr)==254 and all(sha(REPO/r['path'])==r['SHA256'] for r in rr.values())
dump(out/'inputs.json',dict(candidate=ref(src),parts=rr,producer=ref(out/'producer.py'),dependencies=[ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/build_stage1.py'),ref(ROOT/'scripts/baseline_registry.py')]))
# Final preform: left head x40..40.7 R.9; shaft40.5..47.5 R.5.
# Exact union over straight translation -8..0: two coaxial cylinders.
preform=fuse(cyl(.9,(40,-6.1,25),.7,(1,0,0)),cyl(.5,(40.5,-6.1,25),7,(1,0,0)))
sweep=fuse(cyl(.9,(32,-6.1,25),8.7,(1,0,0)),cyl(.5,(32.5,-6.1,25),15,(1,0,0)))
contracts=[('preform_seated',preform),('preform_insertion_sweep',sweep),('left_head_support',cyl(.9,(40,-6.1,25),10,(-1,0,0))),('left_support_approach',cyl(.9,(40,-6.1,25),15,(-1,0,0))),('right_forming_die',cyl(1.2,(48,-6.1,25),10,(1,0,0))),('right_die_approach',cyl(1.2,(48,-6.1,25),15,(1,0,0)))]
shapes={n:read(REPO/r['path']) for n,r in rr.items()};rows=[]
for i in range(3):
 for phase,s in contracts:
  assert not (ROOT/'runtime/STOP').exists()
  tool=rotate(s,120*i);name=f'F{i}_{phase}';export(tool,out/name);hits=[];bb=bounds(tool)
  for n,p in shapes.items():
   if n==f'F{i}_IDLER_CROSSPIN':continue
   if overlap(bb,bounds(p)):
    v=common(tool,p)
    if v>1e-8:hits.append(dict(part=n,common_mm3=v))
  rows.append(dict(sector=i,phase=phase,shape=ref(out/(name+'.step')),volume_mm3=volume(tool),valid=BRepCheck_Analyzer(tool).IsValid() and solid_count(tool)==1,interferences=hits))
ok=all(r['valid'] and not r['interferences'] for r in rows)
dump(out/'summary.json',dict(status='PREHEADED_SEQUENCE_GEOMETRY_CLEAR_ONLY' if ok else 'PREHEADED_SEQUENCE_REJECTED',inputs=ref(out/'inputs.json'),rows=rows,contract=dict(insertion_translation_mm=[-8,0],head_radius_mm=.9,shaft_radius_mm=.5,left_support_radius_mm=.9,right_die_radius_mm=1.2,intersection_limit_mm3=1e-8),limitations=['One preheaded pin inserted with other assembled parts fixed; exact constant-section translation sweep, not ordered whole-product assembly','Right plastic head forming, preform volume/process, machine housing, support strength, tolerances and loaded spin unqualified','Preform and tools are analysis geometry only; no candidate CAD/BOM adoption or capacity evidence'],whole_system_release=False,adopted=False));print(json.dumps(dict(pass_geometry=ok,hits=[r for r in rows if r['interferences']])));raise SystemExit(0 if ok else 2)
