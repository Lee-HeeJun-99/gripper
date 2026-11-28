import sys,json,shutil
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
from primary_keeper_coupled71 import faces
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder
out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_ground65a/summary.json';cad=json.loads(cp.read_text());rows=[]
for name in ['ROOT_SOCKET_KEEPER','ROOT_SOCKET_KEEPER_INSTALLED_SPLIT_PIN','F0_ROOT_BACK','F0_RF0_BOLT','F0_RF1_BOLT']:
 r=cad['part_references'][name];assert sha(REPO/r['path'])==r['SHA256'];rr=[]
 for f in faces(read(REPO/r['path'])):
  a=BRepAdaptor_Surface(f)
  if a.GetType()!=GeomAbs_Cylinder:continue
  c=a.Cylinder();o=c.Location();axis=c.Axis().Direction();rr.append(dict(radius_mm=c.Radius(),axis_point_mm=[o.X(),o.Y(),o.Z()],axis_direction=[axis.X(),axis.Y(),axis.Z()],bounds_mm=bounds(f)))
 rows.append(dict(part_ID=name,STEP=r,cylinders=rr))
dump(out/'summary.json',dict(status='ACTUAL_P1_FINITE_ROOT_BORE_AND_BOLT_GEOMETRY_INVENTORY',candidate=ref(cp),producer=ref(out/'producer.py'),rows=rows,newly_qualified_system_gate_ids=[],whole_system_release=False));print(json.dumps(rows))
