"""Independent actual BRep face dimensions for model-based manufacturing.
No inferred tap from diameter alone: explicit part/axis/coordinate rules.
"""
import argparse,csv,json,math,shutil
from incremental_stage1 import ROOT,read,bounds,sha
from manufacturing_packet import metadata
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder,GeomAbs_Cone,GeomAbs_Torus,GeomAbs_Plane
def xyz(p):return [p.X(),p.Y(),p.Z()]
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'cad/exports'/a.case/'summary.json';idx=json.loads(src.read_text());out=ROOT/'validation'/a.tag;out.mkdir(exist_ok=False);rows=[];parts=[]
 for n,v in idx['parts'].items():
  if n.startswith(('F1_','F2_')):continue
  _,kind,_=metadata(n)
  if kind!='MAKE' and not n.startswith('F0_SWIVEL_BOLT'):continue
  s=read(ROOT/v['path']);it=TopExp_Explorer(s,TopAbs_FACE);j=0
  while it.More():
   j+=1;face=TopoDS.Face_s(it.Current());ad=BRepAdaptor_Surface(face);typ=ad.GetType();r=None;axis=[];point=[];detail={};note='Actual nominal STEP surface; tolerance/thread overrides from manufacturing interface table'
   if typ==GeomAbs_Cylinder:
    c=ad.Cylinder();r=c.Radius();axis=xyz(c.Axis().Direction());point=xyz(c.Axis().Location())
    if 'PEDESTAL' in n and abs(r-8.015)<1e-6:note='CUSTOM16.030+-0.005 bore envelope; paired coax0.010DIAMETER, NOT16H6'
    elif n=='F0_SHAFT' and abs(r-2.493)<1e-6:note='5f6 journal envelope4.982..4.990; common coax0.005DIAMETER; M5x0.5 thread-zone overrides explicitly required'
    elif abs(r-1)<1e-6:
     yaxis=abs(axis[1])>.999;xaxis=abs(axis[0])>.999;zaxis=abs(axis[2])>.999
     if n=='F0_DRUM' and ((yaxis and any(abs(point[0]-x)<1e-5 and abs(point[2]-z)<1e-5 for x,z in ((69,26),(91,26),(80,33)))) or (xaxis and abs(point[1]-2.5)<1e-5 and abs(point[2]-20)<1e-5)):note='M2x0.4-6H TAP; nominal major envelope, CUT drill1.6, gauge6H; NOT drill2.0'
     elif n in ('F0_ROOT_BACK','F0_CASSETTE_BLANK_ADAPTER'):note='M2x0.4-6H TAP at declared dock axes; CUT drill1.6; inspect depth/6H'
     elif n=='F0_DRUM' and yaxis:note='R1 endmill pocket corner, NOT M2 thread; actual rounded-rectangle coordinates'
    elif abs(r-1.5)<1e-6 and ('PEDESTAL' in n and abs(axis[1])>.999 or n=='F0_COUPLING_LOWER' and abs(axis[2])>.999):note='M3x0.5-6H TAP; CUT drill2.5, gauge6H; NOT drill3.0'
    detail=dict(radius_mm=r,diameter_mm=2*r)
   elif typ==GeomAbs_Cone:
    c=ad.Cone();point=xyz(c.Axis().Location());axis=xyz(c.Axis().Direction());detail=dict(reference_radius_mm=c.RefRadius(),included_angle_deg=abs(math.degrees(2*c.SemiAngle())))
   elif typ==GeomAbs_Torus:
    c=ad.Torus();point=xyz(c.Axis().Location());axis=xyz(c.Axis().Direction());detail=dict(major_radius_mm=c.MajorRadius(),minor_radius_mm=c.MinorRadius())
   elif typ==GeomAbs_Plane:
    c=ad.Plane();point=xyz(c.Location());axis=xyz(c.Axis().Direction())
   rows.append(dict(part_ID=n,face_ID=j,surface=str(typ),surface_sense=str(face.Orientation()),axis_or_normal=axis,axis_origin_mm=point,actual_face_bounds_mm=bounds(face),parameters=detail,manufacturing_override=note,STEP=v['path'],STEP_SHA256=v['sha256']))
   it.Next()
  parts.append(dict(part=n,faces=j))
 with (out/'FACE_FEATURES.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 result=dict(status='ACTUAL_FACE_CATALOGUE_GENERATED',case=a.case,parts=parts,face_count=len(rows),input_sha256=sha(src),scope='Actual native CAD face catalogue, not shop approval by itself. All nominal hidden surfaces are available in actual STEP; explicit thread-zone and fit overrides take priority over nominal major cylinders. Physical dimensions NOT MEASURED.',stage1_release=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py');print(json.dumps(dict(parts=len(parts),faces=len(rows))))
if __name__=='__main__':main()
