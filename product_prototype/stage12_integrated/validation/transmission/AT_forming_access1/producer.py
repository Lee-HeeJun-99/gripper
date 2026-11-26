"""Finite opposing flat forming dies; exact straight swept-envelope access screen."""
import sys,json,shutil
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,cyl,rotate,common,bounds,overlap,export,volume,solid_count
from OCP.BRepCheck import BRepCheck_Analyzer
assert not (ROOT/'runtime/STOP').exists()
out=ROOT/'validation/transmission/AT_forming_access1';out.mkdir(exist_ok=False)
shutil.copyfile(__file__,out/'producer.py')
src=ROOT/'cad/exports/revAS_riveted1/summary.json';d=json.loads(src.read_text());rr=d['part_references']
assert len(rr)==254 and all(sha(REPO/r['path'])==r['SHA256'] for r in rr.values())
dump(out/'inputs.json',dict(candidate=ref(src),parts=rr,producer=ref(out/'producer.py'),dependencies=[ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/build_stage1.py'),ref(ROOT/'scripts/baseline_registry.py')]))
# Tool contract fixed before execution: 2.4mm diameter,10mm axial shank,
# flat working face at outer rivet head;5mm straight approach. No housing omitted
# beyond this explicit idealized tool. The union sweep is exactly a15mm cylinder.
rows=[]
shapes={n:read(REPO/r['path']) for n,r in rr.items()}
for i in range(3):
 for side,start,direction in [('left',40,-1),('right',48,1)]:
  for phase,length,offset in [('seated',10,0),('approach_sweep',15,0)]:
   assert not (ROOT/'runtime/STOP').exists()
   tool=rotate(cyl(1.2,(start,-6.1,25),length,(direction,0,0)),120*i)
   name=f'F{i}_{side}_{phase}';export(tool,out/name);bb=bounds(tool);hits=[]
   for n,s in shapes.items():
    if n==f'F{i}_IDLER_CROSSPIN':continue # intended forming workpiece; no forming simulation
    if overlap(bb,bounds(s)):
     v=common(tool,s)
     if v>1e-8:hits.append(dict(part=n,common_mm3=v))
   rows.append(dict(sector=i,side=side,phase=phase,tool=ref(out/(name+'.step')),valid=BRepCheck_Analyzer(tool).IsValid() and solid_count(tool)==1,volume_mm3=volume(tool),interferences=hits))
blocked=any(r['interferences'] for r in rows)
r=dict(status='FORMING_TOOL_ACCESS_REJECTED' if blocked else 'IDEALIZED_FORMING_TOOL_ACCESS_CLEAR_ONLY',candidate=ref(src),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),tool_contract=dict(diameter_mm=2.4,shank_length_mm=10,approach_mm=5,working_planes_local_x_mm=[40,48],axis_local_yz_mm=[-6.1,25],intersection_limit_mm3=1e-8),rows=rows,whole_system_release=False,adopted=False,forming_force_N=None,limitations=['Rigid final-shape tool access only; no plastic forming process or preform insertion proof','No tool holder/machine housing, strength, tolerances, head pull-through or loaded spin certification','Rejects only this declared flat opposing die architecture, not every possible forming/assembly method'])
dump(out/'summary.json',r);print(json.dumps(dict(status=r['status'],rows=[dict(sector=x['sector'],side=x['side'],phase=x['phase'],hits=x['interferences']) for x in rows])));raise SystemExit(2 if blocked else 0)
