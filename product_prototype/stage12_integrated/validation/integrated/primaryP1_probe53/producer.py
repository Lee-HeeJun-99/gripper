import sys,json,shutil
from baseline_registry import ROOT,REPO,S1,ref,dump,sha
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder,GeomAbs_Plane
out=ROOT/'validation/integrated/primaryP1_probe53';out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_guide52/summary_corrected.json';d=json.loads(cp.read_text());rows=[]
for name in ['BENCH_ANCHOR_RAIL','BENCH_SUPPORT','BENCH_MOUNT_BOLT_0','BENCH_MOUNT_NUT_0','BENCH_MOUNT_SOCKET_KEY_0']:
 r=d['part_references'][name];assert sha(REPO/r['path'])==r['SHA256'];s=read(REPO/r['path']);ex=TopExp_Explorer(s,TopAbs_FACE);i=0
 while ex.More():
  f=TopoDS.Face_s(ex.Current());a=BRepAdaptor_Surface(f);b=bounds(f);row=dict(part=name,face=i,bounds=b,kind=str(a.GetType()))
  if a.GetType()==GeomAbs_Cylinder:
   c=a.Cylinder();p=c.Location();v=c.Axis().Direction();row.update(radius=c.Radius(),axis=[v.X(),v.Y(),v.Z()],centre=[p.X(),p.Y(),p.Z()])
  if a.GetType()==GeomAbs_Plane:
   c=a.Plane();p=c.Location();v=c.Axis().Direction();row.update(normal=[v.X(),v.Y(),v.Z()],point=[p.X(),p.Y(),p.Z()])
  rows.append(row);i+=1;ex.Next()
dump(out/'summary.json',dict(status='ACTUAL_CAD_SURFACE_EXTRACTION_NOT_RELEASE',candidate=ref(cp),surfaces=rows,whole_system_release=False));print(json.dumps([r for r in rows if r.get('radius') or (r['part']=='BENCH_SUPPORT' and r.get('normal') and r['bounds'][0]<-54 and r['bounds'][3]>-64 and r['bounds'][1]<-53 and r['bounds'][4]>-63)]))
