"""Actual R0.35 concave pocket blends, manufacturer stepped end envelope.
NI000032: A stem<=2.8, B>=3, C head<=3.8, totalD<=6.
With stem outlet fixed, union envelope head occupies first3mm of total6;
stem occupies last3. This contains all physically consistent listed B/D.
"""
import math
from incremental_stage1 import bounds
from mechanisms_stage1 import pitch_at
from build_stage1 import cyl,cut,fuse
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.TopExp import TopExp_Explorer
from OCP.TopExp import TopExp
from OCP.TopTools import TopTools_IndexedMapOfShape
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopoDS import TopoDS
from OCP.GeomAbs import GeomAbs_Circle
def beta():return -(math.atan2(117,1)-math.acos(11.25/math.hypot(117,1)))
def fillet_delta(old):
 out={};notes={}
 for name in ('SWIVEL_LOWER','SWIVEL_UPPER'):
  s=pitch_at(old['F0_'+name],-beta(),(43,0,-92));f=BRepFilletAPI_MakeFillet(s);edges=TopTools_IndexedMapOfShape();TopExp.MapShapes_s(s,TopAbs_EDGE,edges);found=0
  for i in range(1,edges.Extent()+1):
   edge=TopoDS.Edge_s(edges.FindKey(i));ad=BRepAdaptor_Curve(edge)
   if ad.GetType()==GeomAbs_Circle:
    c=ad.Circle();p=c.Location()
    if abs(c.Radius()-2.1)<1e-6 and abs(p.X()-43)<1e-6 and abs(p.Y())<1e-6 and any(abs(p.Z()-z)<1e-6 for z in (-82.2,-76)):
     f.Add(.35,edge);found+=1
  assert found==2,(name,found);f.Build();assert f.IsDone(),name
  out[name]=pitch_at(f.Shape(),beta(),(43,0,-92));notes[name]='Actual R0.35 concave end blends in4.2x6.2 split pocket; side-access ballnose0.7D/working reach>=2.2 design, not certified shop tool. Other holes/fastener seats retained.'
 tip=fuse(cyl(1.9,(43,0,-82),3),cyl(1.4,(43,0,-79),3));tip=cut(tip,cyl(.25,(43,0,-83),8))
 out['TIP_FACTORY_NIPPLE']=pitch_at(tip,beta(),(43,0,-92));notes['TIP_FACTORY_NIPPLE']='NI000032 conservative stepped envelope from manufacturer A<=2.8/B>=3/C<=3.8/D<=6; head first3mm/stem last3mm to fixed outlet. NOT an actual swage internal model.'
 drum=fuse(cyl(1.9,(74,0,8.75),3,(1,0,0)),cyl(1.4,(77,0,8.75),3,(1,0,0)));out['DRUM_FACTORY_NIPPLE']=cut(drum,cyl(.25,(73.8,0,8.75),6.4,(1,0,0)));notes['DRUM_FACTORY_NIPPLE']=notes['TIP_FACTORY_NIPPLE']
 return out,notes,[]
