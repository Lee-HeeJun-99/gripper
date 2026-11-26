"""Independent conservative radial/Z box exclusion and planar-face area."""
import json,sys,math,shutil,time
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds,cyl,cut
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS

def lower(b):
    near=[max(b[i],0,-b[i+3]) for i in (0,1)]
    rmin=math.hypot(*near);rmax=math.hypot(max(abs(b[0]),abs(b[3])),max(abs(b[1]),abs(b[4])))
    radial=max(rmin-30,20-rmax,0);z=max(b[2]+11.999,-12-b[5],0)
    return math.hypot(radial,z)

def main():
    assert not (ROOT/'runtime/STOP').exists()
    out=ROOT/'validation/transmission/AK_palm_mount_verify1';out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py');start=time.monotonic()
    source=ROOT/'validation/transmission/AK_palm_mount2/summary.json';d=json.loads(source.read_text())
    inputs=json.loads((REPO/d['inputs']['path']).read_text());rows=[]
    for r in (d['candidate'],d['producer'],d['inputs']):assert sha(REPO/r['path'])==r['SHA256']
    for r in d['rows']:
        assert not (ROOT/'runtime/STOP').exists()
        src=inputs['parts'][r['part']];p=REPO/src['path'];assert sha(p)==src['SHA256']
        b=bounds(read(p));bound=lower(b)
        rows.append(dict(part=r['part'],conservative_distance_lower_bound_mm=bound,
            bounds_agree=max(abs(x-y) for x,y in zip(b,r['bounds_mm']))<1e-7,
            no_annular_contact=bound>1e-7,below_exact_distance=bound<=r['distance_to_underside_annular_material_mm']+1e-7))
    src=inputs['parts']['PALM'];assert sha(REPO/src['path'])==src['SHA256'];palm=read(REPO/src['path'])
    # Planar BRep area integration, independent of volume/thickness quotient.
    ring=cut(cyl(30,(0,0,-12.01),.02,(0,0,1)),cyl(20,(0,0,-12.02),.04,(0,0,1)))
    it=TopExp_Explorer(palm,TopAbs_FACE);area=0.;faces=0
    while it.More():
        face=TopoDS.Face_s(it.Current());b=bounds(face)
        if abs(b[2]+12)<1e-7 and abs(b[5]+12)<1e-7:
            inter=BRepAlgoAPI_Common(face,ring).Shape();prop=GProp_GProps();BRepGProp.SurfaceProperties_s(inter,prop)
            area+=prop.Mass();faces+=1
        it.Next()
    controls=dict(intersecting_box_is_not_certified=lower([24,-1,-12,26,1,-11])==0,
        distant_box_certified=lower([40,-1,-12,42,1,-11])>0)
    checks=dict(all234_checked=len(rows)==234,all_boxes_exclude_contact=all(r['no_annular_contact'] for r in rows),
        all_bounds_match=all(r['bounds_agree'] for r in rows),valid_lower_bounds=all(r['below_exact_distance'] for r in rows),
        planar_area_matches=abs(area-d['support_annular_area_mm2'])<1e-5,controls=all(controls.values()))
    ok=all(checks.values());result=dict(status='INDEPENDENT_MOUNT_GEOMETRY_VERIFICATION_PASS' if ok else 'FAIL',source=ref(source),producer=ref(out/'producer.py'),
        checks=checks,controls=controls,rows=rows,planar_intersection_area_mm2=area,underside_faces=faces,
        minimum_conservative_separation_mm=min(r['conservative_distance_lower_bound_mm'] for r in rows),elapsed_s=time.monotonic()-start,whole_system_release=False,
        limitations=['Proves no modeled constituent contacts this annular underside region; does not identify external base support','No support preload/friction/strength or six-DOF constraint certification'])
    dump(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2));raise SystemExit(0 if ok else 2)
if __name__=='__main__':main()
