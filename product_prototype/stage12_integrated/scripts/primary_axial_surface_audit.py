"""Actual P1 Y contact audit before inventing a retention feature; no capacity claim."""
import sys,json,shutil
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds
from primary_motor_bearing_wrenches import patches,faces

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');assert not(ROOT/'runtime/STOP').exists();src=ROOT/'cad/exports/primaryP1_retention20/summary.json';c=json.loads(src.read_text());s={n:read(REPO/c['part_references'][n]['path']) for n in ['F0_ROOT_BACK','F0_MICRO_MOTOR','OPEN_FRAME','MOTOR_CAP']};rows=[]
 # Enumerate ALL actual planarYfaces via geometry,notboundingboxendsonly.
 from OCP.TopExp import TopExp_Explorer
 from OCP.TopAbs import TopAbs_FACE
 from OCP.TopoDS import TopoDS
 from OCP.BRepAdaptor import BRepAdaptor_Surface
 from OCP.GeomAbs import GeomAbs_Plane
 for n,others in [('F0_ROOT_BACK',['OPEN_FRAME']),('F0_MICRO_MOTOR',['OPEN_FRAME','MOTOR_CAP'])]:
  ys=set();it=TopExp_Explorer(s[n],TopAbs_FACE)
  while it.More():
   f=TopoDS.Face_s(it.Current());b=bounds(f)
   if BRepAdaptor_Surface(f).GetType()==GeomAbs_Plane and abs(b[1]-b[4])<1e-6:ys.add(round((b[1]+b[4])/2,7))
   it.Next()
  for m in others:
   for y in sorted(ys):
    cells=patches(s[n],s[m],1,y,[0,1,0],n+'_'+m);rows.append(dict(first=n,second=m,Y_mm=y,area_mm2=sum(r['area_mm2'] for r in cells)))
 result=dict(status='ACTUAL_P1_AXIAL_FACE_AUDIT_NOT_RETENTION_QUALIFICATION',candidate=ref(src),producer=ref(out/'producer.py'),parts={n:c['part_references'][n] for n in s},bounds_mm={n:bounds(q) for n,q in s.items()},Y_faces=rows,nonzero_Y_contacts=[r for r in rows if r['area_mm2']>1e-8],whole_system_release=False,newly_qualified_system_gate_ids=[],scope='Exactcoincidentplanarfacesonly. Gap/friction/curvedcontact/boltholebearing andcase/materialcapacity remainunqualified. Existing6DOFsolveromission isnotproofactualpathabsent; auditfirst.')
 dump(out/'summary.json',result);print(result)
if __name__=='__main__':main()
