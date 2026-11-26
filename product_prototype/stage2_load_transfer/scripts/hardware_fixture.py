"""Manufacture-candidate split nipple test grips, NOT certified test hardware."""
import argparse,csv,json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'stage1_manufacturing/scripts'))
from incremental_stage1 import box,cyl,cut,common,export,volume,sha
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.gp import gp_Trsf,gp_Ax1,gp_Pnt,gp_Dir,gp_Vec
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);args=p.parse_args()
    out=ROOT/'hardware_test/fixtures'/args.tag;out.mkdir(parents=True,exist_ok=False)
    # Axis Z. Clearance pockets enclose UNION of manufacturer maximum end
    # envelopes, not nominal-only dimensions. Wire exits at bottom z=-3.
    whole=box(-10,-8,-3,20,16,9)
    whole=cut(whole,cyl(2.1,(0,0,3),3.2),cyl(1.5,(0,0,0),3.1),cyl(.4,(0,0,-3.1),3.2))
    for y in (-5,5):whole=cut(whole,cyl(1.7,(-11,y,1),22,(1,0,0)))
    for x in (-6,6):whole=cut(whole,cyl(2.25,(x,0,-3.1),9.2))
    parts={}
    # Actual kerf .20, clear external loading/removal direction; halves
    # clamped with purchased M3 through-bolts/nuts, NOT threaded polymer.
    for label,x in [('L',.1),('R',-20.1)]:
        half=cut(whole,box(x,-10,-4,20,20,12));parts['GRIP_'+label]=half
    # Opposed second grip, wire outlet towards first grip; specimen free span
    # 60 mm. No tensile machine or actual finished wire is fabricated here.
    T=gp_Trsf();T.SetRotation(gp_Ax1(gp_Pnt(0,0,0),gp_Dir(1,0,0)),3.141592653589793)
    T.SetTranslationPart(gp_Vec(0,0,-66))
    for name,shape in list(parts.items()):parts['OPPOSED_'+name]=BRepBuilderAPI_Transform(shape,T,True).Shape()
    info=[]
    for name,s in parts.items():
        assert BRepCheck_Analyzer(s).IsValid() and volume(s)>0
        export(s,out/name)
        info.append(dict(ID=name,material='303 stainless candidate; actual allowable not yet qualified',quantity=1,
            STEP=name+'.step',STL=name+'.stl',STEP_SHA256=sha(out/(name+'.step')),volume_mm3=volume(s)))
    collisions=[]
    names=list(parts)
    for i,n in enumerate(names):
        for k in names[i+1:]:
            v=common(parts[n],parts[k])
            if v>1e-8:collisions.append(dict(a=n,b=k,volume_mm3=v))
    result=dict(status='GEOMETRY_PASS' if not collisions else 'FAIL',scope='TEST FIXTURE CANDIDATE GEOMETRY ONLY; NOT SAFE LOAD CERTIFICATION',
        parts=info,collisions=collisions,finished_wire_free_span_mm=60,
        axial_path='wire -> factory nipple -> internal finite shoulder -> grip halves -> test-machine adapter bolts',
        unresolved=['actual nipple fit','bolt preload','fixture proof load','machine adapter','calibration','guarding'],
        source_SHA256=sha(Path(__file__)),command='PYTHONPATH=/tmp/regrip_stage1_ocp python scripts/hardware_fixture.py --tag '+args.tag)
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
