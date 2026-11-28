"""Same primary P1: real replaceable M3 hex nuts and open-bottom integral cages.
Threaded hole is a major-diameter envelope, not a helical contact or capacity.
"""
import sys,json,math,shutil,time,os
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cyl,cut,fuse,canonical,export,common,bounds,overlap,volume,solid_count
from build_stage1 import compound
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon,BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.gp import gp_Pnt,gp_Vec
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone

def hexz(x,y,z,af,h):
 w=BRepBuilderAPI_MakePolygon();r=af/math.sqrt(3)
 for i in range(6):w.Add(gp_Pnt(x+r*math.cos(i*math.pi/3),y+r*math.sin(i*math.pi/3),z))
 w.Close();return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(w.Wire()).Face(),gp_Vec(0,0,h)).Shape()

def main():
 tag=sys.argv[1];out=ROOT/'cad/exports'/tag;out.mkdir();shutil.copyfile(__file__,out/'producer.py')
 cp=ROOT/'cad/exports/primaryP1_integral55e/summary.json';old=json.loads(cp.read_text());refs=dict(old['part_references']);assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());parts={n:read(REPO/r['path']) for n,r in refs.items()};support=parts['BENCH_SUPPORT'];spec=[]
 for i,y in enumerate([-16,16]):spec.append(dict(nut=f'F0_RF{i}_NUT',bolt=f'F0_RF{i}_BOLT',x=64,y=y,seat=-12,bottom=-14.4,body='F0_ROOT_BACK',headseat=-3))
 for x in [-7,7]:
  for y in [-29.5,-13.5]:spec.append(dict(nut=f'MOTOR_CAP_NUT_{x}_{y}',bolt=f'MOTOR_CAP_BOLT_{x}_{y}',x=x,y=y,seat=11,bottom=8.6,body='MOTOR_CAP',headseat=29))
 for q in spec:
  assert not(ROOT/'runtime/STOP').exists();x,y,z=q['x'],q['y'],q['seat'];boss=box(x-5,y-5,z-2.9,10,10,3.1);support=fuse(support,boss)
  pocket=hexz(x,y,z-3.1,5.6,3.1)
  for i in range(6):
   a=i*math.pi/3;r=5.6/math.sqrt(3);pocket=fuse(pocket,cyl(.6,(x+r*math.cos(a),y+r*math.sin(a),z-3.1),3.1))
  support=cut(support,pocket)
  if q['nut'].startswith('MOTOR_CAP'):
   parts[q['nut']]=canonical(cut(hexz(x,y,q['bottom'],5.5,2.4),cyl(1.5,(x,y,q['bottom']-.1),2.6)))
 support=canonical(support);parts['BENCH_SUPPORT']=support;changed=['BENCH_SUPPORT']+[q['nut'] for q in spec if q['nut'].startswith('MOTOR_CAP')];rows=[]
 for n in changed:
  export(parts[n],out/n);parts[n]=read(out/(n+'.step'));refs[n]=ref(out/(n+'.step'));rows.append(dict(part_ID=n,STEP=refs[n],STL=ref(out/(n+'.stl')),parent=old['part_references'][n],valid=bool(BRepCheck_Analyzer(parts[n]).IsValid()),solids=solid_count(parts[n]),volume_mm3=volume(parts[n])))
 bb={n:bounds(s) for n,s in parts.items()};queries=[]
 for i,n in enumerate(parts):
  for m in list(parts)[i+1:]:
   if not(n in changed or m in changed) or not overlap(bb[n],bb[m]):continue
   assert not(ROOT/'runtime/STOP').exists();v=common(parts[n],parts[m]);q=dict(pair=[n,m],intersection_mm3=v);queries.append(q)
   with (out/'journal.jsonl').open('a') as f:f.write(json.dumps(q)+'\n');f.flush();os.fsync(f.fileno())
 hits=[q for q in queries if abs(q['intersection_mm3'])>1e-8];w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
 bom=json.loads((REPO/old['BOM']['path']).read_text());bom['revision']=tag
 for q in bom['parts']:
  q['STEP']=refs[q['part_ID']]
  if q['part_ID'] in changed:q['interface']='Integral open-bottom AF5.6mm nut pocket, R0.6 corner reliefs, nominal AF5.5 M3 nut. Throughbolt axial setting and thread friction/strength remain UNQUALIFIED.' if q['part_ID']=='BENCH_SUPPORT' else 'M3x0.5 DIN934 nominal hex AF5.5 height2.4. Major-diameter thread envelope ONLY; supplier chamfer/tolerance/grade/helical contact not certified.'
 dump(out/'BOM.json',bom);dump(out/'cages.json',dict(specifications=spec,pocket_AF_mm=5.6,nut_AF_mm=5.5,corner_relief_R_mm=.6,boss_XY_mm=10,boss_depth_mm=2.9,upper_overlap_mm=.2,insertion='Nut from below before installing uppermodule, no tiny formed rivet; unthreaded insertion only, tightening/locking remain unqualified.'))
 d=dict(old);d.update(revision=tag,primary=True,parts=77,part_references=refs,part_bounds_mm=bb,parent=ref(cp),producer=ref(out/'producer.py'),changed=rows,unchanged_part_STEP_count=72,assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),cages=ref(out/'cages.json'),identity_BOM=None,interferences=hits,exact_pairs=len(queries),status='ACTUAL_P1_CAPTIVE_NUT_DESIGN_GEOMETRY_LOCAL_PASS_NOT_RELEASE' if not hits and all(q['valid'] and q['solids']==1 for q in rows) else 'ACTUAL_P1_CAPTIVE_NUT_DESIGN_FAIL',design_change='Same one77part P1: four cylindrical capnut envelopes replaced by standard-size hex; six integral bottom-entry nut cages on actual support. No upstream geometry/extension removed.',capacity_qualified=False,whole_system_release=False,newly_qualified_system_gate_ids=[])
 dump(out/'summary.json',d);print(json.dumps(dict(status=d['status'],changed=rows,hits=hits,queries=len(queries))),flush=True)
 return 0 if not hits and all(q['valid'] and q['solids']==1 for q in rows) else 2
if __name__=='__main__':sys.exit(main())
