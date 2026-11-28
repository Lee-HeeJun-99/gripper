"""Same P1: finite external cutter radii on actual six integral keeper plugs.
Nominal proposed machining geometry, not measured process or strength certificate.
"""
import sys,json,shutil,itertools
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cut,fuse,canonical,export,bounds,common,overlap,volume,solid_count
from primary_clocked62 import spin
from primary_captive59b import hexz
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCP.TopExp import TopExp_Explorer,TopExp
from OCP.TopTools import TopTools_IndexedMapOfShape
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopoDS import TopoDS
from OCP.BRepCheck import BRepCheck_Analyzer
from build_stage1 import compound
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone

def roundedplug(x,y,z,top,a):
 s=hexz(x,y,z,2.4,top-z+.3);f=BRepFilletAPI_MakeFillet(s);edges=TopTools_IndexedMapOfShape();TopExp.MapShapes_s(s,TopAbs_EDGE,edges);count=0
 for i in range(1,edges.Extent()+1):
  e=TopoDS.Edge_s(edges.FindKey(i));b=bounds(e)
  if b[5]-b[2]>top-z and b[3]-b[0]<1e-6 and b[4]-b[1]<1e-6:f.Add(.15,e);count+=1
 assert count==6;f.Build();assert f.IsDone();return spin(f.Shape(),x,y,a)

def main():
 tag=sys.argv[1];out=ROOT/'cad/exports'/tag;out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_clocked62a/summary.json';old=json.loads(cp.read_text());refs=dict(old['part_references']);assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());parts={n:read(REPO/r['path']) for n,r in refs.items()};groups=json.loads((REPO/old['anchors']['path']).read_text())['groups'];settings=json.loads((REPO/old['settings']['path']).read_text())['settings'];rows=[]
 for g in groups:
  n=g['name'];s=parts[n];before=volume(s)
  for y in g['ys']:
   x=g['x'];z=g['headtop'];a=next(q['clock_angle_deg'] for q in settings if q['keeper']==n and q['y']==y)
   s=cut(s,box(x-1.6,y-1.6,z-1.3,3.2,3.2,g['bridge_bottom_mm']-(z-1.3)))
   s=fuse(s,roundedplug(x,y,z-1.25,g['bridge_bottom_mm'],a))
  # Concave plug/bridge roots: real .10mm ball/end corner radius, retaining bridge/window.
  fil=BRepFilletAPI_MakeFillet(s);edges=TopTools_IndexedMapOfShape();TopExp.MapShapes_s(s,TopAbs_EDGE,edges);cnt=0
  for i in range(1,edges.Extent()+1):
   e=TopoDS.Edge_s(edges.FindKey(i));b=bounds(e)
   if abs(b[2]-g['bridge_bottom_mm'])<1e-6 and abs(b[5]-g['bridge_bottom_mm'])<1e-6 and any(abs((b[1]+b[4])/2-y)<1.6 and abs((b[0]+b[3])/2-g['x'])<1.6 for y in g['ys']):fil.Add(.10,e);cnt+=1
  assert cnt>=12,(n,cnt)
  fil.Build();assert fil.IsDone(),n;s=canonical(fil.Shape());export(s,out/n);s=read(out/(n+'.step'));parts[n]=s;parent=refs[n];refs[n]=ref(out/(n+'.step'));rows.append(dict(part_ID=n,STEP=refs[n],STL=ref(out/(n+'.stl')),parent=parent,geometry_credit=True,valid=bool(BRepCheck_Analyzer(s).IsValid()),solids=solid_count(s),volume_mm3=volume(s),volume_change_mm3=volume(s)-before,external_corner_radius_mm=.15,root_radius_mm=.10,root_edges=cnt))
 bb={n:bounds(s) for n,s in parts.items()};queries=[]
 for n,m in itertools.combinations(parts,2):
  if not any(n==q['part_ID'] or m==q['part_ID'] for q in rows) or not overlap(bb[n],bb[m]):continue
  assert not(ROOT/'runtime/STOP').exists();queries.append(dict(pair=[n,m],intersection_mm3=common(parts[n],parts[m])))
 hits=[q for q in queries if q['intersection_mm3']>1e-8];w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
 bom=json.loads((REPO/old['BOM']['path']).read_text());bom['revision']=tag
 for q in bom['parts']:
  q['STEP']=refs[q['part_ID']]
  if q['part_ID'] in [r['part_ID'] for r in rows]:q['interface']='Custom clocked keeper; external .15mm and concave root .10mm radii. Proposed cutter envelope, process/minimum strength/preload NOT qualified.'
 dump(out/'BOM.json',bom);d=dict(old);d.update(revision=tag,parent=ref(cp),producer=ref(out/'producer.py'),part_references=refs,part_bounds_mm=bb,changed=rows,unchanged_part_STEP_count=80,assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),interferences=hits,changed_pair_queries=queries,status='ACTUAL_P1_ROUNDED_KEEPER_CLEAR_NOT_RELEASE' if not hits and all(q['valid'] and q['solids']==1 for q in rows) else 'ACTUAL_P1_ROUNDED_KEEPER_FAIL',design_change='Same P1 three keeper solids: six rounded external hex plugs .15mm and actual concave plug-root fillets .10mm. No bolt pose changes. Synthetic angles remain unmeasured.',newly_qualified_system_gate_ids=[],whole_system_release=False);dump(out/'summary.json',d);print(json.dumps(dict(status=d['status'],changed=rows,hits=hits)));return 0 if not hits and all(q['valid'] and q['solids']==1 for q in rows) else 2
if __name__=='__main__':sys.exit(main())
