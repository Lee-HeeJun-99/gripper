"""Rev AB candidate only: independent rail capture and axially free PET end.
Does NOT adopt free-slip model results as actual candidate dynamics.
"""
import argparse,csv,json,sys,math,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];S1=ROOT.parent/'stage1_manufacturing'
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,sha,box,cut,fuse,volume,common,bounds,overlap,export,rotate
from build_stage1 import compound
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon,BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
from OCP.gp import gp_Pnt,gp_Vec
def pad(sign):
    wire=BRepBuilderAPI_MakePolygon()
    for y,z in [(2.8,-95),(5.8,-95),(5.5,-100),(2.5,-100)]:wire.Add(gp_Pnt(49.98,sign*y,z))
    wire.Close()
    return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(wire.Wire()).Face(),gp_Vec(.32,0,0)).Shape()
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);args=p.parse_args()
    out=ROOT/'revised_cad'/args.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    rows=list(csv.DictReader((S1/'bom/revAA_mbd1/STAGE1_BOM.csv').open()));parts={};refs={}
    for row in rows:
        path=S1/row['STEP'];assert sha(path)==row['STEP_SHA256']
        parts[row['part_ID']]=read(path);refs[row['part_ID']]=dict(path=str(path.relative_to(ROOT.parent)),SHA256=sha(path))
    skin=cut(parts['F0_SKIN'],box(49,-20,-101,3,40,6.6))
    front=fuse(fuse(parts['F0_TERMINAL_FRONT'],pad(1)),pad(-1))
    # Sliding guide lip: clear nominal PET front by0.10mm. Rear constraint
    # is retained actual back body, not an invisible transverse attachment.
    front=fuse(front,box(48.98,-6.6,-95,.92,13.2,5))
    modified={}
    for sector in range(3):
        modified[f'F{sector}_SKIN']=rotate(skin,120*sector)
        modified[f'F{sector}_TERMINAL_FRONT']=rotate(front,120*sector)
    diffs=[]
    for name,s in modified.items():
        assert BRepCheck_Analyzer(s).IsValid()
        base=out/name;export(s,base)
        diffs.append(dict(part=name,old_volume_mm3=volume(parts[name]),new_volume_mm3=volume(s),
            STEP=base.name+'.step',STL=base.name+'.stl',STEP_SHA256=sha(base.with_suffix('.step'))))
        parts[name]=s
    bb={n:bounds(s) for n,s in parts.items()};hits=[];tested=set()
    for name,s in modified.items():
        for other,t in parts.items():
            pair=tuple(sorted([name,other]))
            if name==other or pair in tested:continue
            tested.add(pair)
            if overlap(bb[name],bb[other]):
                v=common(s,t)
                if abs(v)>1e-8:hits.append(dict(a=name,b=other,signed_common_mm3=v))
    # Separate local end-capture coupon envelope. It is NOT motion of the
    # whole sheet or a fabricated dynamic trajectory.
    advance=.000265*math.pi/3*1000+.15 # max thickness offset*60deg +cut/datum allowance
    envelope=box(49.97,-6.44,-94.4-advance,.34,12.88,4.4+advance)
    local=[]
    for n in ['F0_TERMINAL_FRONT','F0_TERMINAL_BACK','F0_RAIL_L','F0_RAIL_R']:
        local.append(dict(part=n,signed_common_mm3=common(envelope,parts[n])))
    writer=STEPControl_Writer();writer.Transfer(compound(parts.values()),STEPControl_AsIs)
    assert writer.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
    result=dict(status='GEOMETRY_PASS' if not hits and all(abs(x['signed_common_mm3'])<1e-8 for x in local) else 'FAIL',
        adoption_status='CANDIDATE ONLY, NOT STAGE1 OR STAGE2 RELEASE',baseline='revAA_heel_relief2',revision='RevAB_sliding_PET',
        part_count=len(parts),modified=diffs,nominal_changed_vs_all_hits=hits,
        local_max_end_envelope=local,nominal_end_gap_mm=.6,travel_and_tolerance_budget_mm=advance,
        remaining_axial_gap_mm=.6-advance,retained_part_references=refs,assembly_SHA256=sha(out/'ASSEMBLY.step'),
        source_SHA256=sha(Path(__file__)),
        mechanism='PET trimmed toZ-94.4, no distal indexing/clamp; integral front pads capture rails directly, finite lip/back channel captures PET transversely while allowing axial end travel',
        exclusions=['actual slip friction','PET peel/out-of-plane buckling','candidate-matched nonlinear FEM','clamp strength','manufacturing fillets','full deformed assembly motion','wire motion','mass/inertia update'],
        next='Candidate-matched unilateral layer/contact and clamp load test; do not transfer old free-slip response into this CAD',
        command='PYTHONPATH=/tmp/regrip_stage1_ocp python scripts/sliding_pet_candidate.py --tag '+args.tag)
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='retained_part_references'},indent=2))
if __name__=='__main__':main()
