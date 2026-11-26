"""Actual AK Palm support topology against all modeled assembly constituents.
A missing modeled support is not proof an external fixture cannot be designed.
"""
import json,sys,shutil,time,math
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds,common,volume,cyl,cut
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS

def main():
    assert not (ROOT/'runtime/STOP').exists()
    out=ROOT/'validation/transmission/AK_palm_mount1';out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py');start=time.monotonic()
    source=ROOT/'cad/exports/revAK_integral2/summary.json';d=json.loads(source.read_text());inputs=d['part_references'];assert len(inputs)==235
    dump(out/'inputs.json',dict(candidate=ref(source),parts=inputs,producer=ref(out/'producer.py')))
    for r in inputs.values():assert sha(REPO/r['path'])==r['SHA256']
    palm=read(REPO/inputs['PALM']['path']);ring=cut(cyl(30,(0,0,-12),.001,(0,0,1)),cyl(20,(0,0,-12.001),.003,(0,0,1)))
    footprint=BRepAlgoAPI_Common(palm,ring).Shape();area=volume(footprint)/.001
    assert abs(area-math.pi*(30**2-20**2))<1e-5,area
    cylinders=[];it=TopExp_Explorer(palm,TopAbs_FACE)
    while it.More():
        face=TopoDS.Face_s(it.Current());s=BRepAdaptor_Surface(face)
        if s.GetType()==GeomAbs_Cylinder:
            c=s.Cylinder();p=c.Axis().Location();a=c.Axis().Direction()
            if abs(a.Z())>1-1e-10 and math.hypot(p.X(),p.Y())<45:
                cylinders.append(dict(radius_mm=c.Radius(),axis_point_mm=[p.X(),p.Y(),p.Z()],axis_direction=[a.X(),a.Y(),a.Z()],face_bounds_mm=bounds(face)))
        it.Next()
    rows=[]
    for name,r in inputs.items():
        if name=='PALM':continue
        assert not (ROOT/'runtime/STOP').exists()
        shape=read(REPO/r['path']);ds=BRepExtrema_DistShapeShape(footprint,shape);ds.Perform();assert ds.IsDone()
        rows.append(dict(part=name,bounds_mm=bounds(shape),distance_to_underside_annular_material_mm=ds.Value()))
    rows.sort(key=lambda r:r['distance_to_underside_annular_material_mm'])
    result=dict(status='ACTUAL_PALM_MOUNT_TOPOLOGY_AUDIT_COMPLETE',candidate=ref(source),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),
        palm_bounds_mm=bounds(palm),support_annular_area_mm2=area,expected_annular_area_mm2=math.pi*500,
        central_vertical_cylindrical_faces=cylinders,other_parts_checked=len(rows),rows=rows,
        touching_parts=[r['part'] for r in rows if r['distance_to_underside_annular_material_mm']<=1e-7],
        minimum_other_part_distance_mm=rows[0]['distance_to_underside_annular_material_mm'],
        numerical_distance_limit_mm=1e-7,elapsed_s=time.monotonic()-start,whole_system_release=False,
        limitations=['A .001mm actual Palm material slice at underside z=-12 used only for distance topology',
        'No external base fixture is specified or analyzed; no claim external mounting is impossible',
        'Central hole or annular available material alone does not establish six-DOF support, clamp preload or friction',
        'No bolt/contact/strength solve; no system release'])
    dump(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2));print(json.dumps(rows[:10]))
if __name__=='__main__':main()
